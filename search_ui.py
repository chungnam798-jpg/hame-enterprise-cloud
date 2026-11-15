# search_ui.py
with open('static/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

for i, line in enumerate(content.split('\n'), 1):
    if 'headless' in line or 'ẩn' in line or 'trình duyệt' in line or 'chrome' in line:
        print(f"{i}: {line.strip()}")
