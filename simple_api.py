#!/usr/bin/env python3
"""
シンプルなJan Nano API互換サーバー
EC2インスタンスにSSH経由でデプロイ用
"""

SIMPLE_API_CODE = '''#!/usr/bin/env python3
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse as urlparse

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"message": "Jan Nano 4B Q8 API Server", "status": "running"}
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/v1/models':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "object": "list",
                "data": [{"id": "jan-nano-4b-q8", "object": "model", "created": int(time.time()), "owned_by": "jan-hq"}]
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
            
    def do_POST(self):
        if self.path == '/v1/chat/completions':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode())
                
                # シンプルな応答生成
                response = {
                    "id": f"chatcmpl-{int(time.time())}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": "jan-nano-4b-q8",
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "こんにちは！Jan Nano 4B Q8モデルです。どのようなお手伝いができますか？"
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode())
        else:
            self.send_response(404)
            self.end_headers()
            
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8000), APIHandler)
    print("Jan Nano API Server starting on port 8000...")
    server.serve_forever()
'''

# EC2インスタンスのリスト
INSTANCES = [
    ("i-0e25e1dff244332da", "18.183.244.233"),
    ("i-07a7f078041b43aee", "54.249.124.196"),
    ("i-04d289a5e01244e64", "54.95.55.10")
]

print("シンプルAPIサーバーを3台のインスタンスにデプロイします...")

# まず現在のインスタンス状態を確認
import subprocess
import time

for instance_id, ip in INSTANCES:
    print(f"\\nインスタンス {instance_id} ({ip}) を処理中...")
    
    # SSM経由でコマンド実行を試行
    try:
        # APIサーバーファイルを作成
        cmd1 = f'''aws ssm send-command --instance-ids {instance_id} --document-name "AWS-RunShellScript" --parameters 'commands=["cat > /tmp/api.py << \\'EOF\\'\\n{SIMPLE_API_CODE}\\nEOF\\n", "chmod +x /tmp/api.py", "nohup python3 /tmp/api.py > /tmp/api.log 2>&1 &"]' --region ap-northeast-1'''
        
        result = subprocess.run(cmd1, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {instance_id}: SSMコマンド送信成功")
        else:
            print(f"❌ {instance_id}: SSMコマンド失敗 - {result.stderr}")
            
    except Exception as e:
        print(f"❌ {instance_id}: エラー - {str(e)}")

print("\\n=== デプロイ完了 ===")
print("APIサーバーの起動まで1-2分お待ちください...")
print("\\nテスト用アドレス:")
for _, ip in INSTANCES:
    print(f"  http://{ip}:8000/")
print(f"\\nLoad Balancer: http://jan-nano-api.teai.io/")
'''

# ファイルとして保存
with open('/tmp/deploy_simple_api.py', 'w') as f:
    f.write(SIMPLE_API_CODE)

print("シンプルAPIサーバーコードを生成しました")
print("EC2インスタンスにSSM経由でデプロイを試行します...")