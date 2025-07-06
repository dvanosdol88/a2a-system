#!/usr/bin/env python3
"""
Simple HTTP server for Rubix Cube 3D
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import webbrowser
from pathlib import Path

class CubeHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)

if __name__ == "__main__":
    port = 8080
    server = HTTPServer(('localhost', port), CubeHandler)
    
    print(f"🎮 Rubix Cube 3D Server")
    print(f"📱 Open: http://localhost:{port}")
    print(f"🎯 Built by FlowForge CODEX Agent")
    print(f"🚀 Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
