import urllib.request
import json
import sys

# Test different Gemini endpoints to see which one works or if it returns 404
API_KEY = "dummy_key" # We just want to check if the URL exists or returns 404. 
# A 400/403 means URL exists (API key invalid). A 404 means URL does not exist.

endpoints = [
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
    "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
]

for url in endpoints:
    full_url = f"{url}?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": "Hello"}]}]
    }
    print(f"Testing {url}...")
    try:
        req = urllib.request.Request(
            full_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            print("Success:", r.status)
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code} - {e.reason}")
    except Exception as e:
        print(f"Error: {e}")
