# search_app_js.py
with open('static/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'delay' in line.lower() or 'gemini' in line.lower() or 'setting-' in line.lower() or 'save_setting' in line.lower():
        print(f"{i}: {line.strip()}")
