# HTTPS対応状況

## 現在の状況
❌ **HTTPSはまだ利用できません**

## 理由
- SSL証明書が検証中 (PENDING_VALIDATION)
- DNS検証レコードは正しく設定済み
- 証明書の検証完了まで待機が必要

## 利用可能なエンドポイント

### HTTP (完全動作)
- `http://jan-nano-api-v2-323468516.ap-northeast-1.elb.amazonaws.com/v1/chat/completions` ✅
- `http://jan-nano-api.teai.io/v1/chat/completions` (DNS伝播待ち)

### HTTPS (証明書検証完了後)
- `https://jan-nano-api.teai.io/v1/chat/completions` (準備中)

## 証明書情報
- 新しい証明書ARN: `arn:aws:acm:ap-northeast-1:495350830663:certificate/5e605155-d948-42df-a70a-2845a0d3bc4e`
- 検証方法: DNS検証
- 検証レコード: 設定済み

## 完了予定時間
SSL証明書の検証は通常5-30分で完了します。検証が完了すると自動的にHTTPSアクセスが可能になります。

## 現在のテスト方法
```bash
# HTTP APIテスト (動作中)
curl -X POST http://jan-nano-api-v2-323468516.ap-northeast-1.elb.amazonaws.com/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```