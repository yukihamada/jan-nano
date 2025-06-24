# EC2インスタンス削除記録

## 🗑️ 削除完了

**削除日時**: 2025-06-24 17:10 JST

**削除されたリソース:**
- ✅ EC2インスタンス: `i-03a06cfa84872d84b` (18.182.60.148)
- ✅ ターゲットグループから除去済み
- ✅ API サービス停止確認済み

## 🔍 削除確認

### インスタンス状態
```
InstanceId: i-03a06cfa84872d84b
State: terminated
```

### API アクセス状況
- `https://jan-api.teai.io/` → 503 Service Temporarily Unavailable ✅
- Load Balancer は稼働中だが、バックエンドなし

## 💰 コスト削減効果

**削除前の月額費用:**
- EC2 t3.medium × 1台: ~$32/月
- Application Load Balancer: ~$23/月
- Route 53: $0.50/月
- **合計: ~$55-60/月**

**削除後の月額費用:**
- EC2インスタンス: $0/月 ✅
- Application Load Balancer: ~$23/月 (維持)
- Route 53: $0.50/月 (維持)
- **合計: ~$23-25/月**

**節約効果: 約$30-35/月 (約60%削減)**

## 🏗️ 残存インフラ

以下のリソースは維持されています:
- ✅ Application Load Balancer
- ✅ Target Group (空)
- ✅ SSL証明書 (*.teai.io)
- ✅ Route 53 DNS設定
- ✅ セキュリティグループ

## 🔄 再起動方法

必要に応じて以下で再起動可能:
```bash
# 新しいインスタンス作成
aws ec2 run-instances \
  --image-id ami-0d52744d6551d851e \
  --count 1 \
  --instance-type t3.medium \
  --security-group-ids sg-0afbbd8ad1ee54b97 \
  --key-name openhands-key \
  --user-data file://startup.sh

# ターゲットグループに登録
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:ap-northeast-1:495350830663:targetgroup/jan-nano-targets-v2/c2fe36bb8c5fcfb6 \
  --targets Id=NEW_INSTANCE_ID
```

## 📊 現在の状況

- **API サービス**: ❌ 停止中
- **インフラ**: ✅ 維持中
- **ドメイン**: ✅ 解決可能
- **SSL証明書**: ✅ 有効