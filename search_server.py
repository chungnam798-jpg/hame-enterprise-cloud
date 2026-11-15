# search_server.py
with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

for i, line in enumerate(content.split('\n'), 1):
    if 'auto_engage' in line or 'auto_like' in line or 'automation.' in line:
        print(f"{i}: {line.strip()}")
