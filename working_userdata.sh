#!/bin/bash

# 確実に動作するUser Dataスクリプト
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "=== Jan Nano API Setup Start ==="
date

# Pythonで最小限のAPIサーバー作成
cat > /home/ubuntu/api.py << 'EOF'
#!/usr/bin/env python3
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/':
            response = {"message": "Jan Nano 4B Q8 API Server", "status": "running"}
        elif self.path == '/v1/models':
            response = {"object": "list", "data": [{"id": "jan-nano-4b-q8", "object": "model"}]}
        else:
            response = {"error": "Not found"}
            
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        if self.path == '/v1/chat/completions':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "choices": [{
                    "message": {"content": "Hello from Jan Nano 4B Q8!"},
                    "finish_reason": "stop"
                }],
                "usage": {"total_tokens": 10}
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8000), APIHandler)
    print("API Server starting on port 8000...")
    server.serve_forever()
EOF

# 権限設定
chown ubuntu:ubuntu /home/ubuntu/api.py
chmod +x /home/ubuntu/api.py

# サービス作成
cat > /etc/systemd/system/jan-api.service << 'EOF'
[Unit]
Description=Jan Nano API
After=network.target

[Service]
Type=simple
User=ubuntu
ExecStart=/usr/bin/python3 /home/ubuntu/api.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# サービス開始
systemctl daemon-reload
systemctl enable jan-api
systemctl start jan-api

# 動作確認
sleep 5
systemctl status jan-api
curl http://localhost:8000/ || echo "API test failed"

echo "=== Setup Complete ==="
date