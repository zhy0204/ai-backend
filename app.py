from flask import Flask, jsonify, request
from flask_cors import CORS  # 1. 引入 CORS 套件
import os
import google.generativeai as genai

app = Flask(__name__)
CORS(app)  # 2. 允許跨網域請求，徹底解決前端抓不到後端的問題

# 設定你的 Gemini API 金鑰（請換成你自己的金鑰）
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "你的_GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

@app.route('/api/gemini', methods=['POST'])
def gemini_proxy():
    try:
        data = request.get_json() or {}
        prompt = data.get('prompt', '')
        images = data.get('images', [])
        json_mode = data.get('json_mode', False)

        # 選擇適當的 Gemini 模型
        model_name = 'gemini-1.5-flash'
        generation_config = {}
        if json_mode:
            generation_config["response_mime_type"] = "application/json"

        model = genai.GenerativeModel(model_name)
        
        # 整理傳入的內容（文字與圖片）
        content_parts = [prompt]
        for img_base64 in images:
            if ',' in img_base64:
                img_base64 = img_base64.split(',')[1]
            import base64
            image_bytes = base64.b64decode(img_base64)
            content_parts.append({
                "mime_type": "image/jpeg",
                "data": image_bytes
            })

        response = model.generate_content(content_parts, generation_config=generation_config)
        res_text = response.text

        if json_mode:
            import json
            # 清理 Markdown 標記並轉成 JSON
            cleaned = res_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            res_data = json.loads(cleaned.strip())
            return jsonify({"success": True, "data": res_data})
        else:
            return jsonify({"success": True, "data": res_text})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
