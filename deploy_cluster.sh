#!/bin/bash

# Jan Nano 4B Q8 クラスターデプロイスクリプト
# 3台のEC2インスタンスに同時デプロイ

INSTANCES=(
    "13.230.95.222"  # i-0e25e1dff244332da
    "35.77.218.93"   # i-07a7f078041b43aee
    "43.207.37.132"  # i-04d289a5e01244e64
)

ALB_DNS="jan-nano-api-alb-979792439.ap-northeast-1.elb.amazonaws.com"

echo "=== Jan Nano 4B Q8 クラスターデプロイ開始 ==="
echo "Load Balancer DNS: $ALB_DNS"
echo "インスタンス数: ${#INSTANCES[@]}"

# 各インスタンスに並行してデプロイ
for i in "${!INSTANCES[@]}"; do
    IP="${INSTANCES[$i]}"
    echo "インスタンス $((i+1)): $IP にデプロイ中..."
    
    # バックグラウンドで実行
    (
        # デプロイスクリプトをコピー
        scp -i ~/.ssh/openhands-key.pem -o StrictHostKeyChecking=no \
            /Users/yuki/jan-nano/deploy_script.sh ubuntu@$IP:~/
        
        # デプロイ実行
        ssh -i ~/.ssh/openhands-key.pem -o StrictHostKeyChecking=no \
            ubuntu@$IP 'bash ~/deploy_script.sh'
        
        echo "✅ インスタンス $IP デプロイ完了"
    ) &
done

# すべてのバックグラウンドジョブの完了を待機
wait

echo "=== 全インスタンスデプロイ完了 ==="
echo ""
echo "クラスター情報:"
echo "  Load Balancer: http://$ALB_DNS"
echo "  API エンドポイント: http://$ALB_DNS/v1/chat/completions"
echo "  モデル一覧: http://$ALB_DNS/v1/models"
echo ""
echo "個別インスタンス:"
for i in "${!INSTANCES[@]}"; do
    IP="${INSTANCES[$i]}"
    echo "  インスタンス $((i+1)): http://$IP:8000"
done