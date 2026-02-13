#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pepper Bridge - HTTP Server for Pepper Robot Connection

This script creates an HTTP server that bridges between your modern Python 3
application and the Pepper robot (which requires Python 2.7).

RUN THIS SCRIPT WITH CHOREGRAPHE'S PYTHON 2.7:
    C:\\path\\to\\choregraphe\\bin\\python.exe pepper_bridge.py

Or on the Pepper robot itself:
    python pepper_bridge.py

Then your Python 3 application can send HTTP requests to make Pepper speak.

Author: Aashi
Date: 2025
"""

from __future__ import print_function

import sys
import json
import threading

# Check Python version
if sys.version_info[0] >= 3:
    print("="*50)
    print("ERROR: This script must run with Python 2.7!")
    print("="*50)
    print("")
    print("Run with Choregraphe's Python instead:")
    print("")
    print("Windows:")
    print('  "C:\\Program Files\\Softbank Robotics\\Choregraphe Suite 2.5\\bin\\python.exe" pepper_bridge.py')
    print("")
    print("Or find your Choregraphe installation and use its python.exe")
    print("")
    sys.exit(1)

# Python 2.7 imports
# type: ignore
# pyright: ignore
try:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
except ImportError:
    from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    import qi
except ImportError:
    print("="*50)
    print("ERROR: NAOqi SDK not found!")
    print("="*50)
    print("")
    print("Make sure you're running this with Choregraphe's Python")
    print("which includes the NAOqi SDK.")
    print("")
    sys.exit(1)

# ===========================================
# CONFIGURATION
# ===========================================

# Pepper robot settings
PEPPER_IP = "127.0.0.1"  # Use 127.0.0.1 for virtual robot
PEPPER_PORT = 9559

# HTTP server settings
HTTP_HOST = "127.0.0.1"
HTTP_PORT = 5000

# Global session
pepper_session = None
tts_service = None


# ===========================================
# PEPPER CONNECTION
# ===========================================

def connect_to_pepper():
    """Connect to Pepper robot and return session."""
    global pepper_session, tts_service
    
    try:
        print("Connecting to Pepper at {}:{}...".format(PEPPER_IP, PEPPER_PORT))
        
        pepper_session = qi.Session()
        pepper_session.connect("tcp://{}:{}".format(PEPPER_IP, PEPPER_PORT))
        
        # Get TTS service
        tts_service = pepper_session.service("ALTextToSpeech")
        
        print("Connected to Pepper!")
        return True
        
    except Exception as e:
        print("Failed to connect to Pepper: {}".format(e))
        print("")
        print("Make sure:")
        print("  1. Choregraphe is running with a virtual robot, OR")
        print("  2. You're connected to a real Pepper robot")
        print("  3. The IP and port are correct")
        return False


def make_pepper_speak(text):
    """Make Pepper say the given text."""
    global tts_service
    
    if tts_service is None:
        print("Error: Not connected to Pepper")
        return False
    
    try:
        # Clean the text
        clean_text = text.replace("*", "").replace("#", "").replace("`", "")
        clean_text = clean_text.replace("\n\n", ". ").replace("\n", ". ")
        
        print("Pepper says: {}...".format(clean_text[:50]))
        tts_service.say(str(clean_text))
        return True
        
    except Exception as e:
        print("Error making Pepper speak: {}".format(e))
        return False


# ===========================================
# HTTP SERVER
# ===========================================

class BridgeHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the bridge."""
    
    def log_message(self, format, *args):
        """Override to customize logging."""
        print("[HTTP] {} - {}".format(self.address_string(), format % args))
    
    def send_json_response(self, data, status=200):
        """Send a JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/status":
            # Return status
            connected = pepper_session is not None
            self.send_json_response({
                "status": "ok",
                "connected": connected,
                "pepper_ip": PEPPER_IP,
                "pepper_port": PEPPER_PORT
            })
        
        elif self.path == "/":
            # Return help info
            self.send_json_response({
                "name": "Pepper Bridge",
                "version": "1.0",
                "endpoints": {
                    "GET /status": "Check connection status",
                    "POST /speak": "Make Pepper speak (body: {text: string})",
                    "POST /reconnect": "Reconnect to Pepper"
                }
            })
        
        else:
            self.send_json_response({"error": "Not found"}, 404)
    
    def do_POST(self):
        """Handle POST requests."""
        # Read body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        
        try:
            data = json.loads(body) if body else {}
        except ValueError:
            self.send_json_response({"error": "Invalid JSON"}, 400)
            return
        
        if self.path == "/speak":
            # Make Pepper speak
            text = data.get("text", "")
            
            if not text:
                self.send_json_response({"error": "No text provided"}, 400)
                return
            
            success = make_pepper_speak(text)
            
            if success:
                self.send_json_response({"status": "ok", "spoken": True})
            else:
                self.send_json_response({"error": "Failed to speak"}, 500)
        
        elif self.path == "/reconnect":
            # Try to reconnect
            success = connect_to_pepper()
            
            if success:
                self.send_json_response({"status": "ok", "connected": True})
            else:
                self.send_json_response({"error": "Failed to connect"}, 500)
        
        else:
            self.send_json_response({"error": "Not found"}, 404)


def run_http_server():
    """Run the HTTP server."""
    server = HTTPServer((HTTP_HOST, HTTP_PORT), BridgeHandler)
    print("")
    print("="*50)
    print("Pepper Bridge HTTP Server")
    print("="*50)
    print("Listening on http://{}:{}".format(HTTP_HOST, HTTP_PORT))
    print("")
    print("Endpoints:")
    print("  GET  /status    - Check connection")
    print("  POST /speak     - Make Pepper speak")
    print("  POST /reconnect - Reconnect to Pepper")
    print("")
    print("Press Ctrl+C to stop")
    print("="*50)
    print("")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


# ===========================================
# MAIN
# ===========================================

def main():
    """Main entry point."""
    print("")
    print("="*50)
    print("PEPPER BRIDGE - Python 2.7 HTTP Server")
    print("="*50)
    print("Python version: {}".format(sys.version))
    print("")
    
    # Parse command line arguments
    global PEPPER_IP, PEPPER_PORT, HTTP_PORT
    
    if len(sys.argv) > 1:
        PEPPER_IP = sys.argv[1]
    if len(sys.argv) > 2:
        PEPPER_PORT = int(sys.argv[2])
    if len(sys.argv) > 3:
        HTTP_PORT = int(sys.argv[3])
    
    # Connect to Pepper
    if not connect_to_pepper():
        print("")
        print("WARNING: Could not connect to Pepper.")
        print("The server will start anyway - you can use /reconnect later.")
    
    # Run HTTP server
    run_http_server()


if __name__ == "__main__":
    main()
