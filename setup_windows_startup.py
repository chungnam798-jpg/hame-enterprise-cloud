import os, sys

sys.stdout.reconfigure(encoding='utf-8')

startup_dir = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup')
vbs_path = r'C:\Users\TOSHIBA\.gemini\antigravity\scratch\fb-poster\start_invisible_server.vbs'
bat_path = os.path.join(startup_dir, 'HAME_Enterprise_247.bat')

with open(bat_path, 'w', encoding='utf-8') as f:
    f.write(f'@echo off\nwscript.exe "{vbs_path}"\n')

print(f"SUCCESSFULLY INSTALLED WINDOWS STARTUP LAUNCHER AT:\n{bat_path}")
