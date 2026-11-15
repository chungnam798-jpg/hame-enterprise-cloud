# find_terms.py
import re

terms = ['10', 'recent', 'ngày', 'date', 'time', 'autofeed', 'feed', 'filter', 'days']
with open('automation.py', 'r', encoding='utf-8') as f:
    content = f.read()

out_lines = []
for i, line in enumerate(content.split('\n'), 1):
    matched = [t for t in terms if t in line.lower()]
    if matched:
        out_lines.append(f"{i}: {line.strip()} (matches: {', '.join(matched)})\n")

with open('search_results.txt', 'w', encoding='utf-8') as out:
    out.writelines(out_lines)

print(f"Done search, found {len(out_lines)} lines.")
