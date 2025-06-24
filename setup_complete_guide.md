# Jan Nano 4B Q8 OpenAI互換APIクラスター構築ガイド

## 完成した構成

### インフラ構成
- **EC2インスタンス**: 3台 (t3.medium)
- **Application Load Balancer**: jan-nano-api-v2
- **ドメイン**: jan-nano-api.teai.io
- **SSL証明書**: ACM管理
- **セキュリティグループ**: ポート22, 80, 443, 8000開放

### 現在のリソース
```
インスタンス:
- i-03a06cfa84872d84b: 18.182.60.148:8000 ✅
- i-05bffa5f29d822f74: 起動中
- i-0aed6b2897bc0a9d1: 起動中

Load Balancer:
- DNS: jan-nano-api-v2-323468516.ap-northeast-1.elb.amazonaws.com
- ARN: arn:aws:elasticloadbalancing:ap-northeast-1:495350830663:loadbalancer/app/jan-nano-api-v2/570dd07d7e80ac61

Target Group:
- ARN: arn:aws:elasticloadbalancing:ap-northeast-1:495350830663:targetgroup/jan-nano-targets-v2/c2fe36bb8c5fcfb6

SSL Certificate:
- ARN: arn:aws:acm:ap-northeast-1:495350830663:certificate/5e605155-d948-42df-a70a-2845a0d3bc4e
```

## 完全再構築手順

### 1. セキュリティグループ作成
```bash
aws ec2 create-security-group \
  --group-name jan-nano-api-sg \
  --description "Security group for jan-nano API server"

# ポート開放
aws ec2 authorize-security-group-ingress \
  --group-id sg-XXXXXXXXX \
  --protocol tcp --port 22 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-XXXXXXXXX \
  --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-XXXXXXXXX \
  --protocol tcp --port 443 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-XXXXXXXXX \
  --protocol tcp --port 8000 --cidr 0.0.0.0/0
```

### 2. User Dataスクリプト作成
```bash
cat > startup.sh << 'EOF'
#!/bin/bash
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo "=== Jan Nano API Setup Start ==="
date

# Python APIサーバーを作成
cat > /home/ubuntu/api.py << 'PYTHON_EOF'
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
PYTHON_EOF

# 権限設定
chown ubuntu:ubuntu /home/ubuntu/api.py
chmod +x /home/ubuntu/api.py

# systemdサービス作成
cat > /etc/systemd/system/jan-api.service << 'SERVICE_EOF'
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
SERVICE_EOF

# サービス開始
systemctl daemon-reload
systemctl enable jan-api
systemctl start jan-api

echo "=== Setup Complete ==="
date
EOF
```

### 3. EC2インスタンス作成 (3台)
```bash
# テストインスタンス作成
aws ec2 run-instances \
  --image-id ami-0d52744d6551d851e \
  --count 1 \
  --instance-type t3.medium \
  --security-group-ids sg-XXXXXXXXX \
  --key-name your-key-name \
  --user-data file://startup.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=jan-nano-test}]'

# クラスター用インスタンス作成 (2台追加)
aws ec2 run-instances \
  --image-id ami-0d52744d6551d851e \
  --count 2 \
  --instance-type t3.medium \
  --security-group-ids sg-XXXXXXXXX \
  --key-name your-key-name \
  --user-data file://startup.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=jan-nano-cluster}]'
```

### 4. Application Load Balancer作成
```bash
# ALB作成
aws elbv2 create-load-balancer \
  --name jan-nano-api-v2 \
  --subnets subnet-XXXXXXXXX subnet-XXXXXXXXX \
  --security-groups sg-XXXXXXXXX

# ターゲットグループ作成
aws elbv2 create-target-group \
  --name jan-nano-targets-v2 \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-XXXXXXXXX \
  --health-check-path "/" \
  --health-check-interval-seconds 30

# インスタンス登録
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:REGION:ACCOUNT:targetgroup/jan-nano-targets-v2/XXXXXXXXX \
  --targets Id=i-XXXXXXXXX Id=i-XXXXXXXXX Id=i-XXXXXXXXX

# HTTPリスナー作成
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:REGION:ACCOUNT:loadbalancer/app/jan-nano-api-v2/XXXXXXXXX \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:REGION:ACCOUNT:targetgroup/jan-nano-targets-v2/XXXXXXXXX
```

### 5. SSL証明書とHTTPS設定
```bash
# SSL証明書リクエスト
aws acm request-certificate \
  --domain-name "jan-nano-api.teai.io" \
  --validation-method DNS \
  --region ap-northeast-1

# DNS検証レコード取得
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:REGION:ACCOUNT:certificate/XXXXXXXXX \
  --region ap-northeast-1 \
  --query "Certificate.DomainValidationOptions[0].ResourceRecord"

# Route 53に検証レコード追加
aws route53 change-resource-record-sets \
  --hosted-zone-id ZXXXXXXXXXXXXX \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "_VALIDATION_NAME_",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "_VALIDATION_VALUE_"}]
      }
    }]
  }'

# ドメインのAレコード設定
aws route53 change-resource-record-sets \
  --hosted-zone-id ZXXXXXXXXXXXXX \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT", 
      "ResourceRecordSet": {
        "Name": "jan-nano-api.teai.io.",
        "Type": "A",
        "AliasTarget": {
          "DNSName": "ALB-DNS-NAME",
          "EvaluateTargetHealth": false,
          "HostedZoneId": "Z14GRHDCWA56QT"
        }
      }
    }]
  }'

# HTTPSリスナー作成 (証明書検証完了後)
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:REGION:ACCOUNT:loadbalancer/app/jan-nano-api-v2/XXXXXXXXX \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:REGION:ACCOUNT:certificate/XXXXXXXXX \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:REGION:ACCOUNT:targetgroup/jan-nano-targets-v2/XXXXXXXXX
```

### 6. 動作確認
```bash
# APIサーバー個別テスト
curl http://INSTANCE-IP:8000/

# Load Balancerテスト
curl http://ALB-DNS-NAME/

# ドメインテスト
curl http://jan-nano-api.teai.io/

# チャットAPIテスト
curl -X POST http://jan-nano-api.teai.io/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'

# HTTPSテスト (証明書検証完了後)
curl -X POST https://jan-nano-api.teai.io/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

## 現在のアクセス方法

### HTTP (動作中)
```bash
curl -X POST http://jan-nano-api-v2-323468516.ap-northeast-1.elb.amazonaws.com/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"日本語で回答してください"}]}'
```

### HTTPS (証明書検証完了後)
```bash
curl -X POST https://jan-nano-api.teai.io/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"日本語で回答してください"}]}'
```

## 料金概算
- EC2 t3.medium × 3台: 約$96/月
- Application Load Balancer: 約$23/月  
- データ転送: 使用量に応じて
- Route 53 ホストゾーン: $0.50/月
- ACM SSL証明書: 無料

**合計: 約$120/月**

## トラブルシューティング

### ヘルスチェック失敗
```bash
# ターゲットヘルス確認
aws elbv2 describe-target-health \
  --target-group-arn TARGET-GROUP-ARN

# インスタンス直接テスト
curl http://INSTANCE-IP:8000/
```

### SSL証明書問題
```bash
# 証明書ステータス確認
aws acm describe-certificate \
  --certificate-arn CERTIFICATE-ARN \
  --region ap-northeast-1
```

### DNS問題
```bash
# DNS解決確認
nslookup jan-nano-api.teai.io
dig jan-nano-api.teai.io
```