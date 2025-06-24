# Jan Nano 4B Q8 API - 最終エンドポイント

## ✅ 利用可能なエンドポイント

### 新しいサブドメイン (推奨)
```bash
# HTTPS API (完全動作)
curl -X POST https://jan-api.teai.io/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"こんにちは"}]}'

# HTTP API
curl -X POST http://jan-api.teai.io/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"こんにちは"}]}'
```

### 追加サブドメイン
- `https://api.teai.io/v1/chat/completions`
- `https://jan-nano-api.teai.io/v1/chat/completions`

### 直接Load Balancer (確実)
```bash
# HTTP (確実に動作)
curl -X POST http://jan-nano-api-v2-323468516.ap-northeast-1.elb.amazonaws.com/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"こんにちは"}]}'
```

## 🏗 現在の構成

- **EC2インスタンス**: 1台 (t3.medium)
- **SSL証明書**: ワイルドカード (*.teai.io) ✅
- **Load Balancer**: HTTP/HTTPS対応
- **サブドメイン**: 3つ設定済み

## 💰 月額料金 (削減後)

- EC2 t3.medium × 1台: ~$32
- Application Load Balancer: ~$23
- Route 53: $0.50
- **合計: ~$55-60/月** (67%削減)

## 📋 API仕様

### エンドポイント
- `GET /` - ヘルスチェック
- `GET /v1/models` - モデル一覧
- `POST /v1/chat/completions` - チャット完了

### OpenAI互換
完全にOpenAI APIと互換性があります。

## 🎯 使用例

### Python
```python
import requests

response = requests.post(
    "https://jan-api.teai.io/v1/chat/completions",
    headers={"Content-Type": "application/json"},
    json={
        "model": "jan-nano-4b-q8",
        "messages": [
            {"role": "user", "content": "日本語で回答してください"}
        ],
        "max_tokens": 150
    }
)
print(response.json())
```

### curl
```bash
curl -X POST https://jan-api.teai.io/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "jan-nano-4b-q8",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

## 🔗 GitHubリポジトリ

https://github.com/yukihamada/jan-nano

完全な構築手順、監視ツール、テストスクリプトが含まれています。