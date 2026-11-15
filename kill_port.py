import os
import subprocess
import signal

def kill_port(port):
    try:
        output = subprocess.check_output(f"netstat -aon", shell=True).decode('utf-8')
        pids = set()
        for line in output.strip().split('\n'):
            if f":{port}" in line:
                parts = line.split()
                if len(parts) >= 5:
                    pids.add(parts[-1])
        for pid in pids:
            try:
                # Use taskkill on Windows to force kill it
                subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                print(f"Killed process {pid} on port {port}")
            except Exception as e:
                print(f"Could not kill {pid}: {e}")
    except Exception as e:
        print(f"Error checking/killing port {port}: {e}")

if __name__ == '__main__':
    kill_port(5000)
