import os
import time

filepath = 'claude_share_text.txt'
if os.path.exists(filepath):
    stat = os.stat(filepath)
    print(f"File size: {stat.st_size} bytes")
    print(f"Last modified: {time.ctime(stat.st_mtime)}")
    
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    print("--- CONTENT START ---")
    print(content[:2000])
    print("--- CONTENT END ---")
else:
    print("File does not exist.")
