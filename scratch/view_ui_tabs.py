import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('static/index.html', encoding='utf-8') as f:
    for i, l in enumerate(f):
        if 'id="tab-' in l:
            print(f"{i+1}: {l.strip()}")
