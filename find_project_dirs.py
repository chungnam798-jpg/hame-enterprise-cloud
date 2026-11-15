# find_project_dirs.py
import os

search_paths = [
    r"C:\Users\TOSHIBA\Desktop",
    r"C:\Users\TOSHIBA\Downloads",
    r"C:\Users\TOSHIBA\.gemini\antigravity\scratch"
]

found = []
for path in search_paths:
    if os.path.exists(path):
        for root, dirs, files in os.walk(path):
            if 'server.py' in files and 'automation.py' in files:
                # check if it's the fb-poster project
                found.append(root)
            # Limit depth to avoid scanning forever
            if root.count(os.sep) - path.count(os.sep) > 3:
                dirs.clear() # don't go deeper than 4 levels

print("Found projects:")
for p in found:
    print(p)
