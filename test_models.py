import urllib.request
import json
import sqlite3

def test():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key='gemini_api_key'")
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row['value']:
        print("API Key not found in DB.")
        return
        
    api_key = row['value'].strip()
    print("Found API key in database.")
    
    # Query models
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        req = urllib.request.Request(url, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode('utf-8'))
            print("Available models:")
            for m in res.get('models', []):
                name = m.get('name')
                methods = m.get('supportedGenerationMethods', [])
                if 'generateContent' in methods:
                    print(f"- {name} (generateContent)")
    except Exception as e:
        print("Error listing models:", e)

if __name__ == '__main__':
    test()
