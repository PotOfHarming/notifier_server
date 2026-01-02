import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

BASE_PATH = os.path.dirname(__file__)
FLIGHTS_DIR = os.path.join(BASE_PATH, "flight-stats", "flights")
PORT = 9002

class JSONRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Serve flight list as JSON
        if path == '/flights' or path == '/flights/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.end_headers()
            
            if os.path.exists(FLIGHTS_DIR):
                files = sorted([f for f in os.listdir(FLIGHTS_DIR) if f.endswith('.json')])
                self.wfile.write(json.dumps(files).encode())
            else:
                self.wfile.write(json.dumps([]).encode())
            return
        
        # Serve individual flight file
        if path.startswith('/flights/') and path.endswith('.json'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.end_headers()
            
            hex_code = path.split('/')[-1]
            flight_file = os.path.join(FLIGHTS_DIR, hex_code)
            if os.path.exists(flight_file) and os.path.isfile(flight_file):
                with open(flight_file, 'r') as f:
                    self.wfile.write(f.read().encode())
                return
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
            return
        
        # Serve HTML files
        if path.endswith('.html') or path == '/':
            if path == '/':
                path = '/flights-map.html'
            file_path = os.path.join(BASE_PATH, path.lstrip('/'))
            if os.path.exists(file_path) and os.path.isfile(file_path):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(file_path, 'r') as f:
                    self.wfile.write(f.read().encode())
                return
        
        # Serve other JSON files from www or base path
        if path.endswith('.json'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            file_path = os.path.join(BASE_PATH, 'www', path.lstrip('/'))
            if not os.path.exists(file_path):
                file_path = os.path.join(BASE_PATH, path.lstrip('/'))
            
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, 'r') as f:
                    self.wfile.write(f.read().encode())
                return
        
        # Not found
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

if __name__ == '__main__':
    os.chdir(BASE_PATH)
    server = HTTPServer(('0.0.0.0', PORT), JSONRequestHandler)
    print(f"JSON Server running on port {PORT}")
    print(f"  /flights - list all flight files (JSON)")
    print(f"  /flights/<hex>.json - get specific flight")
    print(f"  /*.json - serve other JSON files")
    print(f"  /*.html - serve HTML files")
    server.serve_forever()
