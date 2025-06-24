#!/usr/bin/env python3

import requests
import json

# 直接個別インスタンスをテスト
instances = [
    "http://18.183.244.233:8000",
    "http://54.249.124.196:8000", 
    "http://54.95.55.10:8000"
]

domain = "http://jan-nano-api.teai.io"

print("=== Jan Nano API クイックテスト ===")

# 個別インスタンステスト
for i, instance in enumerate(instances, 1):
    try:
        response = requests.get(f"{instance}/", timeout=5)
        print(f"✅ インスタンス{i}: {response.status_code} - {response.text[:50]}")
    except Exception as e:
        print(f"❌ インスタンス{i}: {str(e)[:50]}")

# ドメインテスト
try:
    response = requests.get(f"{domain}/", timeout=10)
    print(f"✅ ドメイン: {response.status_code} - {response.text[:50]}")
except Exception as e:
    print(f"❌ ドメイン: {str(e)[:50]}")

# チャット完了テスト
try:
    payload = {
        "model": "jan-nano-4b-q8",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 50
    }
    response = requests.post(f"{domain}/v1/chat/completions", json=payload, timeout=15)
    print(f"✅ チャット: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"応答: {result['choices'][0]['message']['content']}")
except Exception as e:
    print(f"❌ チャット: {str(e)[:50]}")