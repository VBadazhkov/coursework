from flask import Flask, request, render_template, jsonify
import subprocess
import os
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
from googletrans import Translator
import yake

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'txt'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_keywords(text, top_n=10):
    keyword_extractor = yake.KeywordExtractor(lan="ru", n=1, top=top_n)
    keywords = keyword_extractor.extract_keywords(text)
    return [kw[0] for kw in keywords]

def run_cpp_analyzer(text, sort_mode="frequency", ascending=False, search_target="", case_sensitive=False):
    try:
        cmd = ['./text_analyzer', f'--{sort_mode}']
        if ascending:
            cmd.append('--ascending')
        if case_sensitive:
            cmd.append('--case-sensitive')
        if search_target:
            cmd.extend(['--search', search_target])
        
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate(text)
        
        if proc.returncode != 0:
            return None, stderr
        
        # Парсим текстовый вывод
        result = {}
        lines = stdout.strip().split('\n')
        for line in lines:
            if line.startswith("total_words:"):
                result["total_words"] = int(line.split(": ")[1])
            elif line.startswith("unique_words:"):
                result["unique_words"] = int(line.split(": ")[1])
            elif line.startswith("search_found:"):
                result["search_found"] = line.split(": ")[1] == "true"
            elif '\t' in line:
                word, count = line.split('\t')
                result.setdefault("sorted_words", []).append({
                    "word": word,
                    "count": int(count)
                })
        result["sorted_words"] = result.get("sorted_words", [])[:20]
        return result, None
    
    except Exception as e:
        return None, str(e)

def analyze_sentiment(text):
    translator = Translator()
    
    # Определяем, на каком языке текст (простая проверка кириллицы)
    if any('а' <= ch <= 'я' or 'А' <= ch <= 'Я' for ch in text):
        text = translator.translate(text, src='ru', dest='en').text  # Перевод на английский
    
    sentiment = TextBlob(text).sentiment
    return {
        "polarity": round(sentiment.polarity, 4),  # (-1 до 1) Насколько текст позитивный/негативный
        "subjectivity": round(sentiment.subjectivity, 4)  # (0 до 1) Насколько текст субъективный/объективный
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Обработка файла
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
            
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        os.remove(filepath)  # Удаляем после обработки
    
    # Обработка текста из поля
    elif 'text' in request.form:
        text = request.form['text']
    
    else:
        return jsonify({'error': 'No input provided'}), 400
    
    # Параметры анализа
    sort_mode = request.form.get('sort_mode', 'frequency')
    ascending = request.form.get('ascending', 'false') == 'true'
    search_target = request.form.get('search', '')
    case_sensitive = request.form.get('case_sensitive', 'false') == 'true'
    
    # Анализ текста
    analysis, error = run_cpp_analyzer(text, sort_mode, ascending, search_target, case_sensitive)
    if error:
        return jsonify({'error': error}), 500
    
    # Анализ тональности
    sentiment = analyze_sentiment(text)

    #Выделение ключевых слов
    keywords = extract_keywords(text)
    
    # Генерация облака слов
    filtered_text = " ".join(extract_keywords(text))  # Используем только ключевые слова
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
        'keywords': keywords
    })

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('static', exist_ok=True)
    app.run(debug=True)
