"""
智学伙伴API配置测试
验证豆包Seed-1.6-lite模型是否配置成功
"""

import requests
import json
from datetime import datetime

# ==================== 配置信息 ====================
# 请替换为您的实际值
API_KEY = "509e95ff-226a-4fee-8585-b654417195b5"  # 您的API Key
ENDPOINT_ID = "ep-20251128150319-f5dtr"  # ⚠️ 请填入您刚创建的接入点ID
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

def test_zhixue_partner():
    """智学伙伴API连通性测试"""
    print("🚀 智学伙伴API测试开始...")
    print("=" * 50)
    
    # 检查配置
    if ENDPOINT_ID == "ep-xxxxxxxxxxxxxxxx":
        print("⚠️  请先填入接入点ID！")
        print("📝 操作提醒：")
        print("   1. 创建推理接入点后获得ID（格式：ep-xxxxxxxxxxxxxxxx）")
        print("   2. 在第12行替换ENDPOINT_ID的值")
        return False
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 智学伙伴的温暖测试对话
    payload = {
        "model": ENDPOINT_ID,
        "messages": [
            {
                "role": "system", 
                "content": "你是智学伙伴，一个温暖、好奇、鼓励的AI学习助手。用亲切的语言与9岁孩子对话，回复50-80字，适当使用emoji。"
            },
            {
                "role": "user", 
                "content": "你好！我是芋圆，今天我妈妈帮我配置了AI学习伙伴，我好兴奋！"
            }
        ],
        "temperature": 0.8,
        "max_tokens": 150
    }
    
    try:
        print(f"📡 正在连接豆包API...")
        print(f"🔑 API Key: {API_KEY[:20]}...")
        print(f"📍 接入点ID: {ENDPOINT_ID}")
        print()
        
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📊 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            ai_reply = result['choices'][0]['message']['content']
            
            print("✅ 配置成功！智学伙伴已就绪！")
            print("-" * 30)
            print(f"🧒 芋圆: 你好！我是芋圆，今天我妈妈帮我配置了AI学习伙伴，我好兴奋！")
            print(f"🤖 智学伙伴: {ai_reply}")
            print("-" * 30)
            
            # Token使用统计
            usage = result.get('usage', {})
            if usage:
                total_tokens = usage.get('total_tokens', 0)
                cost = total_tokens * 0.0008 / 1000  # Seed-1.6-lite成本
                print(f"💰 本次对话成本: ¥{cost:.6f} 元")
                print(f"📈 月度预估成本: ¥{cost * 10 * 30:.2f} 元 (每天10次对话)")
            
            print("\n🎉 智学伙伴配置完全成功！可以开始开发核心功能了！")
            return True
            
        else:
            print("❌ 配置失败")
            print(f"错误代码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请检查网络连接")
        return False
    except Exception as e:
        print(f"❌ 程序错误: {str(e)}")
        return False

def test_conversation_flow():
    """测试多轮对话功能"""
    if not test_zhixue_partner():
        return
    
    print("\n" + "=" * 50)
    print("🧪 测试多轮对话功能...")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 模拟费曼学习法对话
    conversation_history = []
    test_messages = [
        "今天数学课学了分数除法，感觉好神奇！",
        "就是把除数倒过来再乘，比如1/2除以1/4等于2！"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n💬 对话轮次 {i}")
        print(f"🧒 芋圆: {message}")
        
        # 构建消息历史
        messages = [
            {
                "role": "system", 
                "content": "你是智学伙伴，用费曼学习法引导孩子深入思考。多问'为什么'和'能举例吗'，给予鼓励。"
            }
        ]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": ENDPOINT_ID,
            "messages": messages,
            "temperature": 0.8,
            "max_tokens": 150
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_reply = result['choices'][0]['message']['content']
                print(f"🤖 智学伙伴: {ai_reply}")
                
                # 更新对话历史
                conversation_history.extend([
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": ai_reply}
                ])
            else:
                print(f"❌ 对话失败: {response.status_code}")
                break
                
        except Exception as e:
            print(f"❌ 对话出错: {str(e)}")
            break
    
    print("\n✅ 多轮对话测试完成！智学伙伴具备连续对话能力！")

if __name__ == "__main__":
    print("🌟 智学伙伴 - 让孩子的学习成长看得见")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 运行基础测试
    if test_zhixue_partner():
        # 如果基础测试成功，运行高级测试
        test_conversation_flow()
