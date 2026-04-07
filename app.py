import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

app = Flask(__name__)
CORS(app)  # 允许前端跨域请求

QWEN_API_KEY = os.getenv("QWEN_API_KEY")

@app.route('/api/fortune', methods=['POST'])
def get_fortune():
    if not QWEN_API_KEY or QWEN_API_KEY == 'your_dashscope_api_key_here':
        return jsonify({"error": "请在 .env 文件中配置 QWEN_API_KEY"}), 500

    data = request.json
    name = data.get('name', '有缘人')
    birth_date = data.get('birthDate', '2000年1月1日')
    sign_type = data.get('signType', '天赐签｜上上')
    inscription = data.get('inscription', '承天纳吉')

    # 根据项目需求编写系统提示词
    system_prompt = """你是一位融合传统命理与现代心理学的AI运势解读师。根据以下用户信息，生成一张完整的运势解读卡。
要求：
1. 整体基调积极正向，即使是下签也要给出"先苦后甜、否极泰来"的正向解读。
2. 签文总结要通俗押韵、朗朗上口。
3. 宜忌内容需采用传统黄历及天干地支术语（如纳财、祈福、动土等），并严格结合用户选择的出生日期进行推算生成。注意：每一个宜/忌事项除了输出黄历术语外，还必须跟随一句简短的针对个人的白话解析（例如：“纳财：今日适合稳健理财”）。
4. 详细运势解读要结合铭文意象展开，让铭文和解读形成呼应。注意：用户为职场人士，无学生参与，只需深度解读“事业运”，绝对不可提及“学业”。
5. 语言风格兼具古风韵味和现代亲切感。

请必须严格按照以下JSON格式返回结果，不要包含任何额外的文本或Markdown标记：
{
  "summary": "运势签文总结（20-30字押韵短句）",
  "yi": ["黄历术语1：个人解析1", "黄历术语2：个人解析2", "黄历术语3：个人解析3"],
  "ji": ["黄历术语1：个人解析1", "黄历术语2：个人解析2", "黄历术语3：个人解析3"],
  "career": "事业运解读（2-3句，仅限事业）",
  "wealth": "财运解读（2-3句）",
  "relationship": "人际/桃花运解读（2-3句）",
  "health": "情绪/健康运解读（2-3句）"
}"""

    user_prompt = f"用户信息：\n昵称：{name}\n出生日期：{birth_date}\n签型：{sign_type}\n签面铭文：{inscription}\n请生成运势解读。"

    headers = {
        'Authorization': f'Bearer {QWEN_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        "model": "qwen-turbo",
        "input": {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        },
        "parameters": {
            "result_format": "message"
        }
    }

    try:
        # 调用通义千问API
        response = requests.post(
            'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result_data = response.json()
        
        # 解析返回的JSON内容
        content = result_data['output']['choices'][0]['message']['content']
        # 尝试清理可能包含的Markdown格式 (例如 ```json ... ```)
        content = content.replace('```json', '').replace('```', '').strip()
        
        fortune_data = json.loads(content)
        return jsonify(fortune_data)

    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {e}")
        return jsonify({"error": "连接大模型API失败"}), 500
    except json.JSONDecodeError as e:
        print(f"解析大模型返回结果失败: {e}\n原文: {content}")
        return jsonify({"error": "大模型返回格式错误"}), 500
    except Exception as e:
        print(f"未知错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500

if __name__ == '__main__':
    print("AI运势算命后端服务已启动！")
    print("请确保已在 .env 文件中填入有效的 QWEN_API_KEY。")
    print("服务器运行地址: http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
