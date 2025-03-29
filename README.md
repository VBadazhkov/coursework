Информация по установке приложения

1. Клонируйте репозиторий
Для этого можете использовать code - download zip, извлеките файлы и откройте в своей среде разработки

2. Настройте пути к модулю анализа текста
Найдите файл "text_analyzer.exe" и скопируйте его путь
В app.py в 27 строке найдите фрагмент:

def run_cpp(text, sort_mode="frequency", ascending=False, search_target="", case_sensitive=False):
    try:
        cmd = ['./text_analyzer', f'--{sort_mode}']

Вставьте вместо './text_analyzer' ваш путь к файлу с припиской r. Пример:

def run_cpp_analyzer(text, sort_mode="frequency", ascending=False, search_target="", case_sensitive=False):
    try:
        cmd = ["C:/Users/vlad/Downloads/kursach_private-main/kursach_private-main/text_analyzer.exe", f'--{sort_mode}']

3. Запуск приложения
Запустите app.py и перейдите по ссылке