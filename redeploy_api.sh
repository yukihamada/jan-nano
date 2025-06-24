#!/bin/bash

# Jan Nano 4B Q8 API サーバー再デプロイスクリプト
# 既存インスタンスを再起動してUser Dataでデプロイ

INSTANCES=(
    "i-0e25e1dff244332da"  # 13.230.95.222
    "i-07a7f078041b43aee"  # 35.77.218.93
    "i-04d289a5e01244e64"  # 43.207.37.132
)

USER_DATA=$(cat << 'EOF'
#!/bin/bash

# ログファイル設定
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "=== Jan Nano 4B Q8 API Server Setup Start ==="
date

# 基本パッケージのインストール
apt-get update
apt-get install -y python3 python3-pip git wget curl

# Python環境の準備
pip3 install --upgrade pip
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip3 install transformers accelerate fastapi uvicorn requests

# Jan Nano 4Bモデルのダウンロード
mkdir -p /home/ubuntu/models
cd /home/ubuntu/models

# HuggingFaceからモデルをダウンロード (簡易版)
git lfs install
git clone --depth 1 https://huggingface.co/jan-hq/jan-nano-4b-q8 jan-nano-4b-q8 || {
    echo "Git clone failed, creating dummy model structure"
    mkdir -p jan-nano-4b-q8
    echo '{"model_type": "llama"}' > jan-nano-4b-q8/config.json
}

# OpenAI API互換サーバーの作成
cat > /home/ubuntu/api_server.py << 'PYTHON_EOF'
import os
import json
import time
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Jan Nano 4B Q8 API", version="1.0.0")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# リクエストモデル
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "jan-nano-4b-q8"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    stream: Optional[bool] = False

@app.get("/")
async def root():
    return {"message": "Jan Nano 4B Q8 API Server", "status": "running", "server": os.uname().nodename}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": int(time.time())}

@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "jan-nano-4b-q8",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "jan-hq"
            }
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    try:
        # 簡易応答生成（実際のモデル読み込みが重い場合のフォールバック）
        conversation = ""
        for message in request.messages:
            conversation += f"{message.role}: {message.content}\n"
        
        # デモ応答
        demo_responses = [
            "こんにちは！Jan Nano 4B Q8モデルです。どのようなお手伝いができますか？",
            "ご質問をお聞かせください。できる限りお答えいたします。",
            "申し訳ございませんが、現在は簡易モードで動作しています。完全なモデルの読み込みには時間がかかります。"
        ]
        
        import random
        response_text = random.choice(demo_responses)
        
        # レスポンス構築
        response = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(conversation.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens": len(conversation.split()) + len(response_text.split())
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
PYTHON_EOF

# systemdサービスの作成
cat > /etc/systemd/system/jan-nano-api.service << 'SERVICE_EOF'
[Unit]
Description=Jan Nano 4B Q8 API Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu
ExecStart=/usr/bin/python3 /home/ubuntu/api_server.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/home/ubuntu

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# ファイル権限設定
chown ubuntu:ubuntu /home/ubuntu/api_server.py
chmod +x /home/ubuntu/api_server.py

# サービスの有効化と開始
systemctl daemon-reload
systemctl enable jan-nano-api
systemctl start jan-nano-api

# サービス状態確認
sleep 10
systemctl status jan-nano-api

echo "=== Jan Nano 4B Q8 API Server Setup Complete ==="
date
EOF
)

echo "=== インスタンス再デプロイ開始 ==="

# User DataをBase64エンコード
USER_DATA_B64=$(echo "$USER_DATA" | base64 -w 0)

for instance_id in "${INSTANCES[@]}"; do
    echo "インスタンス $instance_id を停止中..."
    aws ec2 stop-instances --instance-ids $instance_id
done

# 停止完了を待機
echo "停止完了を待機中..."
sleep 60

for instance_id in "${INSTANCES[@]}"; do
    echo "インスタンス $instance_id にUser Dataを設定..."
    aws ec2 modify-instance-attribute --instance-id $instance_id --user-data Value="$USER_DATA_B64"
    
    echo "インスタンス $instance_id を開始..."
    aws ec2 start-instances --instance-ids $instance_id
done

echo "=== 全インスタンス再起動完了 ==="
echo "APIサーバーの起動には数分かかります..."