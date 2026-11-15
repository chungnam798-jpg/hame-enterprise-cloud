import os
import sys
import subprocess

vbs_script = r'''
Set WshShell = CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")

Set oLink1 = WshShell.CreateShortcut(strDesktop & "\FBPoster Enterprise.lnk")
oLink1.TargetPath = "C:\Users\TOSHIBA\.gemini\antigravity\scratch\fb-poster\start_desktop.bat"
oLink1.WorkingDirectory = "C:\Users\TOSHIBA\.gemini\antigravity\scratch\fb-poster"
oLink1.WindowStyle = 1
oLink1.Description = "FBPoster Enterprise v29.0 Squad Edition"
oLink1.Save

Set oLink2 = WshShell.CreateShortcut(strDesktop & "\HAME Squad Matrix Enterprise v29.lnk")
oLink2.TargetPath = "C:\Users\TOSHIBA\.gemini\antigravity\scratch\fb-poster\start_desktop.bat"
oLink2.WorkingDirectory = "C:\Users\TOSHIBA\.gemini\antigravity\scratch\fb-poster"
oLink2.WindowStyle = 1
oLink2.Description = "HAME Squad Matrix Enterprise v29.0 Desktop App"
oLink2.Save
'''

vbs_file = os.path.join(os.path.dirname(__file__), "create_shortcut.vbs")
with open(vbs_file, "w", encoding="utf-8") as f:
    f.write(vbs_script)

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

subprocess.run(["cscript", "//Nologo", vbs_file])
print("Da tao 2 Lối tắt Shortcut Desktop thành công!")
