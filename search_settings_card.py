# search_settings_card.py
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('static/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'cấu hình hệ thống' in line.lower() or 'id="settings' in line or 'name="gemini_api_key"' in line or 'delay_between_posts' in line:
        print(f"{i}: {line.strip()}")
