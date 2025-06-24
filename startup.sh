#!/bin/bash
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo "=== Jan Nano API Setup Start ==="
date

# Python APIサーバーを作成
cat > /home/ubuntu/api.py << 'EOF'
#!/usr/bin/env python3
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

class JanNanoAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/':
            response = {"message": "Jan Nano 4B Q8 API Server", "status": "running"}
        elif self.path == '/health':
            response = {"status": "healthy"}
        elif self.path == '/v1/models':
            response = {"object": "list", "data": [{"id": "jan-nano-4b-q8", "object": "model"}]}
        else:
            response = {"error": "Not found"}
            
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_POST(self):
        if self.path == '/v1/chat/completions':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            response = {
                "choices": [{
                    "message": {"content": "こんにちは！Jan Nano 4B Q8モデルです。"},
                    "finish_reason": "stop"
                }],
                "usage": {"total_tokens": 10}
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8000), JanNanoAPIHandler)
    server.serve_forever()
EOF

# 権限設定
chown ubuntu:ubuntu /home/ubuntu/api.py
chmod +x /home/ubuntu/api.py

# systemdサービス作成
cat > /etc/systemd/system/jan-api.service << 'EOF'
[Unit]
Description=Jan Nano API
After=network.target

[Service]
Type=simple
User=ubuntu
ExecStart=/usr/bin/python3 /home/ubuntu/api.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# サービス開始
systemctl daemon-reload
systemctl enable jan-api
systemctl start jan-api

# 動作確認
sleep 10
systemctl status jan-api
curl http://localhost:8000/ || echo "Local test failed"

echo "=== Setup Complete ==="
date