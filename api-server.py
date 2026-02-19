#!/usr/bin/env python3
"""
Simple API server for YieldHarvest dashboard
Serves positions data from positions.json
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse

class YieldHarvestAPI(BaseHTTPRequestHandler):
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Enable CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Route handling
        if parsed_path.path == '/api/positions':
            self.serve_positions()
        elif parsed_path.path == '/api/stats':
            self.serve_stats()
        else:
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def serve_positions(self):
        """Serve positions from JSON file"""
        try:
            positions_file = 'agent/data/positions.json'
            if os.path.exists(positions_file):
                with open(positions_file, 'r') as f:
                    data = json.load(f)
                    self.wfile.write(json.dumps(data).encode())
            else:
                self.wfile.write(json.dumps({"positions": [], "next_id": 0}).encode())
        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def serve_stats(self):
        """Serve aggregated stats"""
        try:
            positions_file = 'agent/data/positions.json'
            if os.path.exists(positions_file):
                with open(positions_file, 'r') as f:
                    data = json.load(f)
                    positions = data.get('positions', [])
                    
                    open_positions = [p for p in positions if p['status'] == 'open']
                    closed_positions = [p for p in positions if p['status'] == 'closed']
                    
                    total_deposited = sum(p['amount'] for p in positions)
                    total_active = sum(p['amount'] for p in open_positions)
                    total_yield = sum(p.get('yield_earned', 0) for p in closed_positions)
                    
                    avg_apy = sum(p['entry_apy'] for p in open_positions) / len(open_positions) if open_positions else 0
                    
                    stats = {
                        "total_deposited": total_deposited,
                        "total_active": total_active,
                        "yield_earned": total_yield,
                        "active_positions": len(open_positions),
                        "closed_positions": len(closed_positions),
                        "average_apy": avg_apy,
                        "positions": open_positions
                    }
                    
                    self.wfile.write(json.dumps(stats).encode())
            else:
                self.wfile.write(json.dumps({
                    "total_deposited": 0,
                    "total_active": 0,
                    "yield_earned": 0,
                    "active_positions": 0,
                    "closed_positions": 0,
                    "average_apy": 0,
                    "positions": []
                }).encode())
        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass


def run_server(port=3001):
    server_address = ('', port)
    httpd = HTTPServer(server_address, YieldHarvestAPI)
    print(f'🚀 YieldHarvest API running on http://localhost:{port}')
    print(f'📊 Endpoints:')
    print(f'   GET /api/positions - All positions')
    print(f'   GET /api/stats - Aggregated statistics')
    print(f'\n✅ Dashboard can now fetch live data!')
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
