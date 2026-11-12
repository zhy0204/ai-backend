import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# 從 Render 環境變數取得 API Key 並初始化
API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

@app.route('/api/gemini', methods=['POST'])
def gemini_proxy():
    try:
        if not API_KEY:
            return jsonify({"success": False, "error": "伺服器未設定 GOOGLE_API_KEY 環境變數"}), 500

        data = request.json or {}
        prompt = data.get('prompt', '')
        images = data.get('images', [])
        json_mode = data.get('json_mode', False)

        # 使用支援的 gemini-2.5-flash 模型
        generation_config = {}
        if json_mode:
            generation_config["response_mime_type"] = "application/json"

        model = genai.GenerativeModel('gemini-2.5-flash', generation_config=generation_config)

        # 整理傳入的內容（包含圖片與文字）
        content_parts = [prompt]
        for img_data in images:
            if img_data.startswith('data:'):
                try:
                    header, encoded = img_data.split(',', 1)
                    mime_type = header.split(';')[0].replace('data:', '')
                    import base64
                    image_bytes = base64.b64decode(encoded)
                    content_parts.append({
                        'mime_type': mime_type,
                        'data': image_bytes
                    })
                except Exception as img_err:
                    print(f"圖片解析失敗: {img_err}")

        # 呼叫 Gemini AI
        response = model.generate_content(content_parts)
        
        # 嘗試解析回傳結果
        res_text = response.text
        if json_mode:
            import json
            try:
                # 試著轉成 JSON 物件回傳給前端
                res_text = json.loads(res_text)
            except:
                pass

        return jsonify({"success": True, "data": res_text})

    except Exception as e:
        print(f"API 錯誤: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/')
def index():
    return "AIDC 后端代理服務運行中", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
