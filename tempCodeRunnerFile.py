def run_cpp(text, sort_mode="frequency", ascending=False, search_target="", case_sensitive=False):
    try:
        cmd = ['./text_analyzer', f'--{sort_mode}']