#!/usr/bin/env python3
"""
Jan Nano 4B Q8 クラスター - 日本語複雑質問テスト
3台のサーバーで負荷分散された環境で高度な日本語質問をテストします
"""

import requests
import json
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# クラスター設定
ALB_ENDPOINT = "http://jan-nano-api-alb-979792439.ap-northeast-1.elb.amazonaws.com"
INDIVIDUAL_ENDPOINTS = [
    "http://13.230.95.222:8000",
    "http://35.77.218.93:8000", 
    "http://43.207.37.132:8000"
]

# 複雑な日本語質問セット
COMPLEX_QUESTIONS = [
    {
        "category": "哲学・抽象思考",
        "question": "「存在とは何か」という根本的な問いについて、西洋哲学と東洋哲学の違いを比較し、現代のAIの視点から新しい解釈を提示してください。また、プラトンのイデア論とデカルトの心身二元論を踏まえて論じてください。",
        "keywords": ["存在論", "イデア論", "心身二元論", "AI哲学"]
    },
    {
        "category": "科学・技術の複合問題", 
        "question": "量子コンピューティングが実用化された際の社会への影響を、暗号技術の脆弱性、創薬プロセスの革新、気候変動モデリングの精度向上の3つの観点から分析し、それぞれについて具体的な技術的課題と社会実装上の問題点を述べてください。",
        "keywords": ["量子コンピューター", "暗号", "創薬", "気候変動"]
    },
    {
        "category": "歴史・文化の深層分析",
        "question": "明治維新における「文明開化」が日本の伝統的価値観に与えた影響を、儒教思想、神道、仏教の変容という観点から分析し、現代日本社会における「和魂洋才」の概念の変化と、グローバル化との関係性について論じてください。",
        "keywords": ["明治維新", "文明開化", "儒教", "神道", "仏教", "和魂洋才"]
    },
    {
        "category": "経済・社会システム",
        "question": "デジタル経済における「プラットフォーム資本主義」の特徴を分析し、従来の産業資本主義との違いを明確にした上で、データの私有化問題、労働の変質、格差拡大のメカニズムを説明し、持続可能な経済システムへの転換策を提案してください。",
        "keywords": ["プラットフォーム資本主義", "データ私有化", "労働変質", "格差"]
    },
    {
        "category": "認知科学・心理学",
        "question": "人間の意識における「クオリア」の問題を、神経科学、現象学、計算理論の三つのアプローチから説明し、AIが真の意識を持つ可能性について、中国語の部屋問題とハード・プロブレムを踏まえて議論してください。",
        "keywords": ["クオリア", "意識", "現象学", "中国語の部屋", "ハード・プロブレム"]
    },
    {
        "category": "芸術・美学",
        "question": "日本の美意識における「侘寂（わびさび）」の概念を西洋美学の観点から分析し、不完全性や無常観がなぜ美しさとして感受されるのかを、カントの判断力批判と比較しながら説明し、現代アートにおける「侘寂」の表現について論じてください。",
        "keywords": ["侘寂", "美意識", "無常観", "カント", "判断力批判"]
    },
    {
        "category": "言語学・記号論",
        "question": "日本語の敬語システムが反映する社会構造と権力関係を、ソシュールの記号論とフーコーの権力論を用いて分析し、グローバル化と個人主義の浸透が敬語使用にもたらす変化とその社会的意味について考察してください。",
        "keywords": ["敬語", "社会構造", "ソシュール", "フーコー", "権力論"]
    }
]

def send_request(endpoint, question_data, test_id):
    """API リクエストを送信"""
    payload = {
        "model": "jan-nano-4b-q8",
        "messages": [
            {
                "role": "system", 
                "content": "あなたは博識で論理的思考力に優れた日本語AIアシスタントです。複雑な質問に対して、学術的で深い洞察を含む回答を日本語で提供してください。"
            },
            {
                "role": "user", 
                "content": question_data["question"]
            }
        ],
        "max_tokens": 800,
        "temperature": 0.7
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{endpoint}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=120
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            response_text = result["choices"][0]["message"]["content"]
            
            return {
                "test_id": test_id,
                "endpoint": endpoint,
                "category": question_data["category"],
                "question": question_data["question"][:100] + "...",
                "response": response_text,
                "response_time": end_time - start_time,
                "keywords": question_data["keywords"],
                "success": True,
                "token_usage": result.get("usage", {})
            }
        else:
            return {
                "test_id": test_id,
                "endpoint": endpoint,
                "category": question_data["category"],
                "error": f"HTTP {response.status_code}: {response.text}",
                "success": False
            }
            
    except Exception as e:
        return {
            "test_id": test_id,
            "endpoint": endpoint,
            "category": question_data["category"],
            "error": str(e),
            "success": False
        }

def evaluate_response_quality(response_text, keywords):
    """回答の質を評価"""
    score = 0
    
    # キーワード含有チェック
    keyword_count = sum(1 for keyword in keywords if keyword in response_text)
    score += (keyword_count / len(keywords)) * 30
    
    # 文字数による複雑さ評価
    char_count = len(response_text)
    if char_count > 1000:
        score += 25
    elif char_count > 500:
        score += 15
    elif char_count > 200:
        score += 10
    
    # 論理的構造の評価（簡易）
    logical_indicators = ["まず", "次に", "さらに", "結論として", "一方で", "しかし", "したがって"]
    logical_count = sum(1 for indicator in logical_indicators if indicator in response_text)
    score += min(logical_count * 5, 25)
    
    # 学術的表現の評価
    academic_terms = ["分析", "考察", "論証", "検討", "仮説", "理論", "概念", "観点"]
    academic_count = sum(1 for term in academic_terms if term in response_text)
    score += min(academic_count * 3, 20)
    
    return min(score, 100)

def test_cluster_performance():
    """クラスター全体のパフォーマンステスト"""
    print("=== Jan Nano 4B Q8 クラスター - 日本語複雑質問テスト ===\n")
    
    # まずALBの稼働確認
    print("1. Load Balancer稼働確認...")
    try:
        response = requests.get(f"{ALB_ENDPOINT}/", timeout=30)
        if response.status_code == 200:
            print("✅ Load Balancer正常稼働")
        else:
            print("❌ Load Balancer応答不良")
            return
    except Exception as e:
        print(f"❌ Load Balancer接続失敗: {e}")
        return
    
    # 個別インスタンスの稼働確認
    print("\n2. 個別インスタンス稼働確認...")
    active_endpoints = []
    for i, endpoint in enumerate(INDIVIDUAL_ENDPOINTS):
        try:
            response = requests.get(f"{endpoint}/", timeout=15)
            if response.status_code == 200:
                print(f"✅ インスタンス{i+1} ({endpoint}) 正常稼働")
                active_endpoints.append(endpoint)
            else:
                print(f"❌ インスタンス{i+1} ({endpoint}) 応答不良")
        except Exception as e:
            print(f"❌ インスタンス{i+1} ({endpoint}) 接続失敗")
    
    if not active_endpoints:
        print("❌ 稼働中のインスタンスがありません")
        return
    
    print(f"\n稼働中インスタンス: {len(active_endpoints)}/3台")
    
    # 複雑な質問テスト実行
    print("\n3. 日本語複雑質問テスト実行...")
    
    test_results = []
    test_id = 1
    
    # 各質問をランダムなエンドポイントに送信
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        
        for question_data in COMPLEX_QUESTIONS:
            # ALBと個別インスタンスの両方でテスト
            for endpoint in [ALB_ENDPOINT] + active_endpoints[:1]:  # ALB + 1個のインスタンス
                future = executor.submit(send_request, endpoint, question_data, test_id)
                futures.append(future)
                test_id += 1
        
        # 結果を収集
        for future in as_completed(futures):
            result = future.result()
            test_results.append(result)
            
            if result["success"]:
                print(f"✅ テスト{result['test_id']}: {result['category']} - {result['response_time']:.2f}秒")
            else:
                print(f"❌ テスト{result['test_id']}: {result['category']} - {result['error']}")
    
    # 結果分析
    print(f"\n{'='*60}")
    print("テスト結果分析")
    print(f"{'='*60}")
    
    successful_tests = [r for r in test_results if r["success"]]
    failed_tests = [r for r in test_results if not r["success"]]
    
    print(f"成功: {len(successful_tests)}/{len(test_results)} テスト")
    print(f"失敗: {len(failed_tests)} テスト")
    
    if successful_tests:
        avg_response_time = sum(r["response_time"] for r in successful_tests) / len(successful_tests)
        print(f"平均応答時間: {avg_response_time:.2f}秒")
        
        # 各カテゴリーの結果
        print(f"\n{'='*40}")
        print("カテゴリー別結果:")
        print(f"{'='*40}")
        
        categories = {}
        for result in successful_tests:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)
        
        for category, results in categories.items():
            print(f"\n📚 {category}")
            print("-" * 50)
            
            for result in results:
                quality_score = evaluate_response_quality(result["response"], result["keywords"])
                endpoint_name = "ALB" if "elb.amazonaws.com" in result["endpoint"] else f"Instance ({result['endpoint'].split('//')[1].split(':')[0]})"
                
                print(f"  エンドポイント: {endpoint_name}")
                print(f"  応答時間: {result['response_time']:.2f}秒")
                print(f"  品質スコア: {quality_score:.1f}/100")
                print(f"  回答preview: {result['response'][:200]}...")
                
                if "token_usage" in result:
                    usage = result["token_usage"]
                    print(f"  トークン使用量: {usage.get('total_tokens', 'N/A')}")
                
                print()
    
    # 失敗したテストの詳細
    if failed_tests:
        print(f"\n{'='*40}")
        print("失敗したテスト:")
        print(f"{'='*40}")
        
        for result in failed_tests:
            print(f"❌ {result['category']}: {result['error']}")
    
    # 総合評価
    success_rate = (len(successful_tests) / len(test_results)) * 100
    print(f"\n{'='*60}")
    print("総合評価")
    print(f"{'='*60}")
    print(f"成功率: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 優秀: クラスターは高度な日本語質問に優れた性能を発揮")
    elif success_rate >= 70:
        print("👍 良好: クラスターは複雑な質問を適切に処理")
    elif success_rate >= 50:
        print("⚠️  普通: 一部の質問で問題あり、調整が必要")
    else:
        print("❌ 不良: 大幅な改善が必要")

if __name__ == "__main__":
    test_cluster_performance()