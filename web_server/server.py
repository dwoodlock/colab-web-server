"""
web_server.server
-----------------
Lightweight helper utilities for teaching demos in Colab.
Provides:
    - reset(): cleanly stops old ngrok and port 8000 processes
    - start(): launches HTTP server in background + ngrok tunnel
    - stop(): stops both
"""

import os
import sys
import time
import threading
import http.server
import socketserver
import subprocess
from functools import partial
from pyngrok import ngrok


# Globals for reuse
httpd = None
server_thread = None
tunnel = None
PORT = 8000


def reset(port: int = PORT):
    """Terminate any previous ngrok tunnels or port-8000 processes."""
    print("🔄 Resetting environment...")
    try:
        for t in ngrok.get_tunnels():
            try:
                ngrok.disconnect(t.public_url)
            except Exception:
                pass
        ngrok.kill()
    except Exception:
        pass

    subprocess.run("pkill -f ngrok || true", shell=True)
    subprocess.run(f"fuser -k {port}/tcp || true", shell=True)
    subprocess.run(f"lsof -ti:{port} | xargs -r kill -9 || true", shell=True)
    print(f"✅ Reset complete (port {port} cleared).")


def start(web_root="./Metric-Treadmill-2017", port: int = PORT, ngrok_token=None):
    """Start a local HTTP server + ngrok tunnel from the specified directory."""
    global httpd, server_thread, tunnel

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    def start_server():
        global httpd
        handler = partial(http.server.SimpleHTTPRequestHandler, directory=web_root)
        httpd = ReusableTCPServer(("", port), handler)
        print(f"📂 Serving directory: {os.path.abspath(web_root)}")
        print(f"🖥️  Server starting on http://localhost:{port}")
        httpd.serve_forever()

    # Ngrok setup
    if ngrok_token is None:
        ngrok_token = os.environ.get("NGROK_TOKEN")
    if ngrok_token:
        ngrok.set_auth_token(ngrok_token)

    # Start server thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    # Start ngrok tunnel
    tunnel = ngrok.connect(port)
    public_url = str(tunnel.public_url)
    print("✅ Website is live!")
    print(f"🔗 Public URL: {public_url}  →  http://localhost:{port}")
    return public_url


def stop():
    """Stop the HTTP server and ngrok tunnel."""
    global httpd, server_thread, tunnel
    print("🛑 Stopping server and tunnels...")
    try:
        if tunnel:
            ngrok.disconnect(tunnel.public_url)
            tunnel = None
    except Exception:
        pass

    try:
        ngrok.kill()
    except Exception:
        pass

    if httpd:
        httpd.shutdown()
        httpd.server_close()
        httpd = None

    if server_thread and server_thread.is_alive():
        server_thread.join(timeout=2)

    print("✅ Clean shutdown complete.")
