Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\TOSHIBA\.gemini\antigravity\scratch\fb-poster"
WshShell.Run "pythonw.exe server.py", 0, False
