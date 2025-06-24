#!/bin/bash

# Jan Nano 4B Q8モデルをOpenAI API互換でデプロイするスクリプト
# EC2インスタンス: i-0e25e1dff244332da
# パブリックIP: 13.230.95.222

echo "=== Jan Nano 4B Q8 API Server Setup ==="

# 基本パッケージのインストール
sudo apt-get update
sudo apt-get install -y python3 python3-pip git wget curl

# Python環境の準備
pip3 install --upgrade pip
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip3 install transformers accelerate fastapi uvicorn requests

# Jan Nano 4Bモデルのダウンロード
mkdir -p /home/ubuntu/models
cd /home/ubuntu/models

# HuggingFaceからモデルをダウンロード
git lfs install
git clone https://huggingface.co/jan-hq/jan-nano-4b-q8 jan-nano-4b-q8

# OpenAI API互換サーバーの作成
cat > /home/ubuntu/api_server.py << 'EOF'
import os
import json
import time
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
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

# モデルとトークナイザーの初期化
MODEL_PATH = "/home/ubuntu/models/jan-nano-4b-q8"
tokenizer = None
model = None

def load_model():
    global tokenizer, model
    try:
        logger.info("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        
        logger.info("Loading model...")
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            low_cpu_mem_usage=True
        )
        logger.info("Model loaded successfully!")
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

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

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

@app.on_event("startup")
async def startup_event():
    load_model()

@app.get("/")
async def root():
    return {"message": "Jan Nano 4B Q8 API Server", "status": "running"}

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
    if not model or not tokenizer:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # メッセージを文字列に変換
        conversation = ""
        for message in request.messages:
            if message.role == "user":
                conversation += f"User: {message.content}\n"
            elif message.role == "assistant":
                conversation += f"Assistant: {message.content}\n"
            elif message.role == "system":
                conversation += f"System: {message.content}\n"
        
        conversation += "Assistant: "
        
        # トークン化
        inputs = tokenizer(conversation, return_tensors="pt")
        
        # 生成パラメータ
        generation_kwargs = {
            "max_new_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "do_sample": True,
            "pad_token_id": tokenizer.eos_token_id,
        }
        
        # テキスト生成
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                **generation_kwargs
            )
        
        # 生成されたテキストをデコード
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 元の会話部分を除去
        response_text = generated_text[len(conversation):].strip()
        
        # レスポンス構築
        response = ChatCompletionResponse(
            id=f"chatcmpl-{int(time.time())}",
            created=int(time.time()),
            model=request.model,
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }
            ],
            usage={
                "prompt_tokens": len(inputs.input_ids[0]),
                "completion_tokens": len(outputs[0]) - len(inputs.input_ids[0]),
                "total_tokens": len(outputs[0])
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# systemdサービスの作成
sudo tee /etc/systemd/system/jan-nano-api.service > /dev/null << 'EOF'
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
EOF

# サービスの有効化と開始
sudo systemctl daemon-reload
sudo systemctl enable jan-nano-api
sudo systemctl start jan-nano-api

echo "=== セットアップ完了 ==="
echo "API エンドポイント: http://13.230.95.222:8000"
echo "OpenAI互換エンドポイント: http://13.230.95.222:8000/v1/chat/completions"
echo "モデル一覧: http://13.230.95.222:8000/v1/models"
echo ""
echo "使用例:"
echo "curl -X POST http://13.230.95.222:8000/v1/chat/completions \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"model\": \"jan-nano-4b-q8\","
echo "    \"messages\": ["
echo "      {\"role\": \"user\", \"content\": \"Hello, how are you?\"}"
echo "    ],"
echo "    \"max_tokens\": 100"
echo "  }'"