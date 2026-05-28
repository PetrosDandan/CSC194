#!/usr/bin/env python3
import sys
import os
import threading
import time
import subprocess

# Ensure the working directory of the script is in the system path for seamless module importing
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)

try:
    from app import main as start_server
except ImportError as e:
    print(f"[-] Critical error: Could not import 'app.py': {e}")
    print("[-] Please ensure 'app.py' remains in the same directory as 'run.py'.")
    sys.exit(1)

def try_install_webview():
    print("[*] Checking for native desktop rendering library (pywebview)...")
    try:
        import webview
        return webview
    except ImportError:
        print("[*] 'pywebview' not found. Attempting to install automatically via pip for direct desktop execution...")
        try:
            # Try to install pywebview silently
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview"])
            import webview
            print("[+] Successfully installed pywebview.")
            return webview
        except Exception as install_err:
            print(f"[-] Could not install pywebview automatically: {install_err}")
            print("[-] Falling back to standard web browser mode.")
            return None

def start_gui_mode(webview):
    print("[*] Launching simulation in native Python desktop window...")
    try:
        # Create a beautiful native web view window
        # We start the webview loop on the main thread and let it connect to the python backend on localhost:3000
        webview.create_window(
            title="Iligan City Flood Evacuation & Situation Awareness Simulator",
            url="http://localhost:3000",
            width=1366,
            height=850,
            resizable=True
        )
        webview.start()
        print("[*] GUI window closed. Exiting...")
    except Exception as gui_err:
        print(f"[-] Native GUI rendering failed: {gui_err}")
        print("[-] Falling back to default web browser mode...")
        fallback_browser()

def fallback_browser():
    import webbrowser
    url = "http://localhost:3000"
    print(f"[*] Opening system web browser at: {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[-] Could not open default web browser automatically: {e}")

if __name__ == "__main__":
    print("[*] Starting Iligan City Flood Evacuation Simulation Engine...")
    
    # 1. Start the simulation backend server in a daemon thread so it runs concurrently
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Give the backend a moment to spin up and bind to port 3000
    time.sleep(1.0)
    
    # 2. Try to run in true native Python GUI window
    webview_lib = try_install_webview()
    if webview_lib:
        start_gui_mode(webview_lib)
    else:
        # Fall back to launching standard browser
        fallback_browser()
        # Keep the main thread alive since the server runs on a background daemon
        print("[*] Running in background server mode. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[!] Shutting down simulation database server...")
            sys.exit(0)
