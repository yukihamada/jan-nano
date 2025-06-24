#!/usr/bin/env python3
"""
SSL証明書検証状況監視スクリプト
証明書検証完了時にHTTPSリスナーを自動作成
"""

import boto3
import time
import json

# AWS設定
REGION = 'ap-northeast-1'
CERTIFICATE_ARN = 'arn:aws:acm:ap-northeast-1:495350830663:certificate/5e605155-d948-42df-a70a-2845a0d3bc4e'
LOAD_BALANCER_ARN = 'arn:aws:elasticloadbalancing:ap-northeast-1:495350830663:loadbalancer/app/jan-nano-api-v2/570dd07d7e80ac61'
TARGET_GROUP_ARN = 'arn:aws:elasticloadbalancing:ap-northeast-1:495350830663:targetgroup/jan-nano-targets-v2/c2fe36bb8c5fcfb6'

def check_certificate_status():
    """SSL証明書の検証状況を確認"""
    acm = boto3.client('acm', region_name=REGION)
    
    try:
        response = acm.describe_certificate(CertificateArn=CERTIFICATE_ARN)
        status = response['Certificate']['Status']
        
        print(f"Certificate Status: {status}")
        
        if status == 'ISSUED':
            print("✅ SSL証明書検証完了!")
            return True
        elif status == 'PENDING_VALIDATION':
            print("⏳ SSL証明書検証中...")
            return False
        else:
            print(f"❌ SSL証明書エラー: {status}")
            return False
            
    except Exception as e:
        print(f"❌ 証明書確認エラー: {e}")
        return False

def create_https_listener():
    """HTTPSリスナーを作成"""
    elbv2 = boto3.client('elbv2', region_name=REGION)
    
    try:
        response = elbv2.create_listener(
            LoadBalancerArn=LOAD_BALANCER_ARN,
            Protocol='HTTPS',
            Port=443,
            Certificates=[{
                'CertificateArn': CERTIFICATE_ARN
            }],
            DefaultActions=[{
                'Type': 'forward',
                'TargetGroupArn': TARGET_GROUP_ARN
            }]
        )
        
        print("✅ HTTPSリスナー作成成功!")
        print(f"ListenerArn: {response['Listeners'][0]['ListenerArn']}")
        return True
        
    except Exception as e:
        print(f"❌ HTTPSリスナー作成失敗: {e}")
        return False

def test_https_endpoint():
    """HTTPS接続をテスト"""
    import requests
    
    try:
        url = "https://jan-nano-api.teai.io/"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ HTTPS接続成功!")
            print(f"Response: {response.text}")
            return True
        else:
            print(f"❌ HTTPS接続失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ HTTPS接続テストエラー: {e}")
        return False

def main():
    """メイン監視ループ"""
    print("🔍 SSL証明書検証監視開始...")
    print(f"証明書ARN: {CERTIFICATE_ARN}")
    print(f"監視間隔: 60秒")
    print("-" * 50)
    
    https_created = False
    check_count = 0
    
    while not https_created and check_count < 60:  # 最大60回 (1時間)
        check_count += 1
        print(f"\n[チェック {check_count}/60] {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 証明書状況確認
        if check_certificate_status():
            print("\n🎉 SSL証明書検証完了! HTTPSリスナーを作成します...")
            
            # HTTPSリスナー作成
            if create_https_listener():
                print("\n⏳ HTTPS接続テスト中...")
                time.sleep(30)  # DNS伝播とリスナー起動を待機
                
                # HTTPS接続テスト
                if test_https_endpoint():
                    print("\n🎉 HTTPS設定完了!")
                    print("\n📋 利用可能なエンドポイント:")
                    print("  HTTP:  http://jan-nano-api.teai.io/v1/chat/completions")
                    print("  HTTPS: https://jan-nano-api.teai.io/v1/chat/completions")
                    print("\n✨ Jan Nano 4B Q8 OpenAI互換APIクラスター完全構築完了!")
                    
                    # 使用例を表示
                    print("\n📝 使用例:")
                    print("curl -X POST https://jan-nano-api.teai.io/v1/chat/completions \\")
                    print("  -H 'Content-Type: application/json' \\")
                    print("  -d '{\"messages\":[{\"role\":\"user\",\"content\":\"日本語で答えてください\"}]}'")
                    
                    https_created = True
                else:
                    print("⚠️ HTTPS接続テスト失敗、もう少し待機が必要かもしれません")
            else:
                print("❌ HTTPSリスナー作成失敗")
                break
        else:
            # 60秒待機
            print("次のチェックまで60秒待機...")
            time.sleep(60)
    
    if not https_created:
        print("\n⚠️ タイムアウトまたはエラーのため監視を終了")
        print("手動で証明書状況を確認してください:")
        print(f"aws acm describe-certificate --certificate-arn {CERTIFICATE_ARN} --region {REGION}")

if __name__ == "__main__":
    main()