from flask import Flask, request, render_template, jsonify
import subprocess
import os
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
from yake import KeywordExtractor
import textract
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {'txt', 'docx', 'pptx', 'pdf'}

def clean_text(text):
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_text_from_docx(file_path):
    try:
        text = textract.process(file_path, encoding='utf-8')
        return text.decode('utf-8')
    except Exception as e:
        return f"Ошибка при textract: {str(e)}"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_keywords(text, top_n=10):
    keyword_extractor = KeywordExtractor(lan="ru", n=1, top=top_n)
    keywords = keyword_extractor.extract_keywords(text)
    return [kw[0] for kw in keywords]

def run_cpp(text, sort_mode="frequency", ascending=False, search_target="", case_sensitive=False):
    try:
        cmd = ['./text_analyzer', f'--{sort_mode}']
        if ascending:
            cmd.append('--ascending')
        if case_sensitive:
            cmd.append('--case-sensitive')

        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )
        stdout, stderr = proc.communicate(text)
        
        if proc.returncode != 0:
            return None, stderr
        
        result = {}
        lines = stdout.strip().split('\n')
        for line in lines:
            if line.startswith("total_words:"):
                result["total_words"] = int(line.split(": ")[1])
            elif line.startswith("unique_words:"):
                result["unique_words"] = int(line.split(": ")[1])
            elif '\t' in line:
                word, count = line.split('\t')
                result.setdefault("sorted_words", []).append({
                    "word": word,
                    "count": int(count)
                })
        result["sorted_words"] = result.get("sorted_words", [])[:15]

        if search_target:
            search_word = ''.join(c for c in search_target if c.isalnum())
            if not case_sensitive:
                search_word = search_word.lower()
            
            words_in_text = [''.join(c for c in w if c.isalnum()) for w in text.split()]
            if not case_sensitive:
                words_in_text = [w.lower() for w in words_in_text]
            
            result["search_found"] = search_word in words_in_text
        
        return result, None
    
    except Exception as e:
        return None, str(e)

def analyze_sentiment(text):
    blob = TextBlob(text)
    
    sentiment = blob.sentiment
    return {
        "polarity": round(sentiment.polarity, 4),
        "subjectivity": round(sentiment.subjectivity, 4)
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    text = ""
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if filename.endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8', errors="replace") as f:
                text = f.read()
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(filepath)
        else:
            return jsonify({'error': 'Неподдерживаемый тип файла'}), 400

        os.remove(filepath)

    elif 'text' in request.form and request.form['text'].strip():
        text = request.form['text']

    else:
        return jsonify({'error': 'Введите текст или загрузите файл'}), 400

    text = clean_text(text)
    sort_mode = request.form.get('sort_mode', 'frequency')
    ascending = request.form.get('ascending', 'false') == 'true'
    search_target = request.form.get('search', '').strip()
    case_sensitive = request.form.get('case_sensitive', 'false') == 'true'

    analysis, error = run_cpp(text, sort_mode, ascending, search_target, case_sensitive)
    if error:
        return jsonify({'error': error}), 500

    sentiment = analyze_sentiment(text)

    keywords = extract_keywords(text)

    filtered_text = " ".join(extract_keywords(text))

    if not filtered_text.strip():
        wordcloud_path = None
    else:
        wordcloud = WordCloud(background_color="white", contour_color="black").generate(filtered_text)

        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")

        wordcloud_path = os.path.join('static', 'wordcloud.png')
        plt.savefig(wordcloud_path)

    return jsonify({
        'wordcloud': wordcloud_path,
        'analysis': analysis,
        'sentiment': sentiment,
        'keywords': keywords,
        'search_result': analysis.get('search_found', None)
    })

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('static', exist_ok=True)
    app.run(debug=False)
