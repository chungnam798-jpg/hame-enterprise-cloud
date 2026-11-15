import os
import zipfile
import shutil

source_dir = r"C:\Users\TOSHIBA\.gemini\antigravity\scratch\fb-poster"
target_zip = r"C:\Users\TOSHIBA\.gemini\antigravity\brain\c050bea8-7aa0-45d9-94d5-fdecb0128454\fb-poster.zip"
static_zip = os.path.join(source_dir, "static", "fb-poster.zip")

print(f"Zipping {source_dir} to {target_zip}...")

exclude_dirs = {'__pycache__', '.git', '.idea', 'venv', 'env'}
exclude_files = {'zip_project.py'}

with zipfile.ZipFile(target_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file in exclude_files or file.endswith('.zip'):
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, source_dir)
            if 'screenshots' in rel_path and file.endswith('.png'):
                continue
            zipf.write(full_path, rel_path)

print("Zipping complete!")

print(f"Copying {target_zip} to {static_zip}...")
shutil.copy2(target_zip, static_zip)
print("Copy to static complete!")

