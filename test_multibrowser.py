import sys
sys.stdout.reconfigure(encoding='utf-8')

import multibrowser_engine

print("=== TESTING LAUNCH ALL BROWSERS ===")
res = multibrowser_engine.launch_all_browsers()
print("LAUNCH RESULT:", res)
