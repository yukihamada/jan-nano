#!/usr/bin/env python3
"""
Jan Nano 4B Q8 API テストスクリプト
OpenAI API互換のテストを行います
"""

import requests
import json
import time

API_BASE = "http://13.230.95.222:8000"

def test_health_check():
    """ヘルスチェック"""
    print("=== ヘルスチェック ===")
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_list_models():
    """モデル一覧取得"""
    print("\n=== モデル一覧 ===")
    try:
        response = requests.get(f"{API_BASE}/v1/models")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_chat_completion():
    """チャット完了テスト"""
    print("\n=== チャット完了テスト ===")
    
    payload = {
        "model": "jan-nano-4b-q8",
        "messages": [
            {"role": "user", "content": "Hello! Can you introduce yourself?"}
        ],
        "max_tokens": 150,
        "temperature": 0.7
    }
    
    try:
        print("Sending request...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        
        end_time = time.time()
        
        print(f"Status: {response.status_code}")
        print(f"Response time: {end_time - start_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # メッセージ内容を抽出
            if result.get("choices") and len(result["choices"]) > 0:
                message = result["choices"][0].get("message", {}).get("content", "")
                print(f"\n生成されたメッセージ: {message}")
            
            return True
        else:
            print(f"Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_openai_compatibility():
    """OpenAI互換性テスト"""
    print("\n=== OpenAI互換性テスト ===")
    
    # 複数のメッセージでテスト
    payload = {
        "model": "jan-nano-4b-q8",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of Japan?"},
            {"role": "assistant", "content": "The capital of Japan is Tokyo."},
            {"role": "user", "content": "Tell me more about it."}
        ],
        "max_tokens": 200,
        "temperature": 0.5
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # OpenAI互換性チェック
            required_fields = ["id", "object", "created", "model", "choices", "usage"]
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                print(f"Missing OpenAI fields: {missing_fields}")
                return False
            
            print("✅ OpenAI互換性テスト成功")
            
            # レスポンス内容表示
            if result.get("choices") and len(result["choices"]) > 0:
                message = result["choices"][0].get("message", {}).get("content", "")
                print(f"生成されたメッセージ: {message}")
            
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """メインテスト実行"""
    print("Jan Nano 4B Q8 API テスト開始")
    print("=" * 50)
    
    # APIサーバーが起動するまで待機
    print("APIサーバーの起動を待機中...")
    for i in range(30):  # 最大5分待機
        if test_health_check():
            break
        print(f"待機中... ({i+1}/30)")
        time.sleep(10)
    else:
        print("❌ APIサーバーの起動確認に失敗しました")
        return
    
    # テスト実行
    tests = [
        ("モデル一覧取得", test_list_models),
        ("チャット完了", test_chat_completion),
        ("OpenAI互換性", test_openai_compatibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
        print(f"結果: {'✅ 成功' if success else '❌ 失敗'}")
    
    # 結果サマリー
    print(f"\n{'='*50}")
    print("テスト結果サマリー:")
    for test_name, success in results:
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"  {test_name}: {status}")
    
    successful_tests = sum(1 for _, success in results if success)
    print(f"\n成功: {successful_tests}/{len(results)} テスト")
    
    if successful_tests == len(results):
        print("🎉 すべてのテストが成功しました！")
    else:
        print("⚠️  一部のテストが失敗しました")

if __name__ == "__main__":
    main()