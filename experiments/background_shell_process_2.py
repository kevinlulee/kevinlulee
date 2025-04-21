import os
import psutil
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
PID_FILE = os.path.expanduser("~/mathbook_server.pid")

# Setup logging
def setup_logging():
    log_dir = Path.home() / "mathbook_logs"
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

def run_server():
    """Run the server in background mode."""
    os.chdir(SERVER_DIR)
    logging.info("Starting Uvicorn server...")
    
    # Write PID file
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    
    # Register cleanup function
    def cleanup():
        logging.info("Shutting down server...")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    
    atexit.register(cleanup)
    
    # Handle termination signals
    def signal_handler(sig, frame):
        logging.info(f"Received signal {sig}")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start the server
    try:
        server_process = subprocess.Popen(
            ["uvicorn", "main:app", "--host", SERVER_HOST, "--port", str(SERVER_PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Monitor server output to determine when it's ready
        for line in iter(server_process.stderr.readline, b''):
            line_str = line.decode('utf-8').strip()
            logging.info(f"Server: {line_str}")
            if "Application startup complete" in line_str:
                logging.info("Server is ready!")
                break
        
        # Keep the server running
        server_process.wait()
    except Exception as e:
        logging.error(f"Error running server: {e}")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

def start_background_server():
    """Start the server as a background process and open the web browser."""
    log_file = setup_logging()
    
    # Check if we're already in background mode
    if len(sys.argv) > 1 and sys.argv[1] == "--background":
        logging.info("Running server in background mode")
        run_server()
        return
    
    # Check if the server is already running
    if is_server_running():
        print(f"Server is already running. Opening {URL} in browser...")
        webbrowser.open(URL)
        return
    
    # Launch the server in background mode
    print(f"Starting server in background mode...")
    print(f"Logs will be written to: {log_file}")
    
    script_path = os.path.abspath(__file__)
    
    # Create a detached background process
    if os.name == 'nt':  # Windows
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen(
            [sys.executable, script_path, "--background"],
            creationflags=DETACHED_PROCESS,
            close_fds=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    else:  # Unix/Linux/Mac
        subprocess.Popen(
            [sys.executable, script_path, "--background"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            start_new_session=True
        )
    
    # Wait a moment for the server to start
    print("Server starting in background. Waiting for it to be ready...")
    time.sleep(3)  # Give it a few seconds to initialize
    
    # Open the browser
    print(f"Opening {URL} in web browser...")
    webbrowser.open(URL)

def stop_server():
    """Stop the currently running server."""
    if not os.path.exists(PID_FILE):
        print("Server is not running.")
        return
    
    with open(PID_FILE, 'r') as f:
        try:
            pid = int(f.read().strip())
            print(f"Stopping server with PID {pid}...")
            if os.name == 'nt':  # Windows
                os.kill(pid, signal.SIGTERM)
            else:  # Unix/Linux/Mac
                os.kill(pid, signal.SIGTERM)
            print("Server stopped.")
        except (ValueError, OSError) as e:
            print(f"Error stopping server: {e}")
    
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)


def terminate_process(key):
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        pid = proc.info['pid']
        name = proc.info['name']
        if name == key:
            print('terminating', key)
            proc.kill()
            return True
    return False
            
def runner():
    
    if os.path.isfile(PID_FILE):
        stop_server()
        terminate_process('uvicorn')
    else:
        start_background_server()
if __name__ == "__main__":
    # Handle command line arguments
    runner()
