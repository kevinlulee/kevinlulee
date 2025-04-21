import os
import psutil
import os
import sys
import sys
import time
import subprocess
import webbrowser
import logging
from pathlib import Path
import signal
import atexit

# Configuration
SERVER_DIR = os.path.expanduser("~/projects/typst/mathbook/pymathbook/server")
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
URL = f"http://localhost:{SERVER_PORT}"
PID_FILE = os.path.expanduser("/home/kdog3682/mathbook_server.pid")

# Setup logging
def setup_logging():
    log_dir = Path.home() / ".kdog3682" / "mathbook_logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "mathbook_server.log"
    
    logging.basicConfig(
        filename=str(log_file),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return log_file

def is_server_running():
    """Check if the server is already running."""
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            try:
                pid = int(f.read().strip())
                # Check if process with this PID exists
                os.kill(pid, 0)
                return True
            except (ValueError, OSError):
                # PID file exists but process doesn't
                os.remove(PID_FILE)
    return False


def terminate_process(key):
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        pid = proc.info['pid']
        name = proc.info['name']
        if name == key:
            print('terminating', key)
            proc.kill()
            return True
    return False
            


class DebugProcess:
    def __init__(self, debugging = False):
        self.debugging = debugging

    def print(self, message):
        args = [message]
        if self.debugging:
            args.insert(0, '[DEBUGGING]')

    def run(message, callback):
        self.print(message)
        if not self.debugging:
            callback()
    
# process = DebugProcess(debugging)

def run_background_server(debugging = False, toggle = True):
    
    # Check if the server is already running
    a = readfile(PID_FILE)
    if os.path.isfile(a):
        terminate_process('uvicorn')
        if 
        print('closing server')
        return 
    
    writefile(PID_FILE, "ABC")
    print(f"Starting server in background mode...")

    if debugging:
        print('early exit because debugging')
        return 

    script_path = os.path.abspath(__file__)
    
    # Create a detached background process
    subprocess.Popen(
        [sys.executable, script_path, "--background"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        start_new_session=True
    )
    
    # Wait a moment for the server to start
    print("Server starting in background. Waiting for it to be ready...")
    time.sleep(2)  # Give it a few seconds to initialize
    webbrowser.open(URL)


if __name__ == "__main__":
    run_background_server(debugging=True)
