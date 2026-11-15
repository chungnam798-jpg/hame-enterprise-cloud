import os
import sys

startup_dir = os.path.expanduser(r'~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup')
os.makedirs(startup_dir, exist_ok=True)
vbs_path = os.path.join(startup_dir, 'HAME_Enterprise_Startup.vbs')
bat_path = r'C:\Users\TOSHIBA\.gemini\antigravity\scratch\fb-poster\start_desktop.bat'
work_dir = r'C:\Users\TOSHIBA\.gemini\antigravity\scratch\fb-poster'

vbs_lines = [
    'Set WshShell = CreateObject("WScript.Shell")\n',
    f'WshShell.CurrentDirectory = "{work_dir}"\n',
    f'WshShell.Run "{bat_path}", 0, False\n'
]

with open(vbs_path, 'w', encoding='utf-8') as f:
    f.writelines(vbs_lines)

print('SUCCESSFULLY CREATED WINDOWS HIDDEN STARTUP SCRIPT AT:', vbs_path)
