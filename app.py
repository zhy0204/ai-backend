import base64
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


@app.route("/api/gemini", methods=["POST"])
def gemini_proxy():
  try:
    data = request.json
    prompt = data.get("prompt", "")
    images = data.get("images", [])
    json_mode = data.get("json_mode", False)

    content_parts = [prompt]

    for img_data in images:
      if "," in img_data:
        img_data = img_data.split(",")[1]
      image_bytes = base64.b64decode(img_data)
      content_parts.append({"mime_type": "image/jpeg", "data": image_bytes})

    generation_config = {}
    if json_mode:
      generation_config["response_mime_type"] = "application/json"

    response = model.generate_content(
        content_parts, generation_config=generation_config
    )
    return jsonify({"success": True, "data": response.text})
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
