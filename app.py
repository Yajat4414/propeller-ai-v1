from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  # Install with: pip install flask-cors
import chatbot

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def get_bot_response():
    try:
        data = request.get_json()
        user_text = data.get("message")
        
        if not user_text:
            return jsonify({"error": "No message provided"}), 400
            
        bot_reply = chatbot.get_bot_reply(user_text)
        return jsonify({"reply": bot_reply})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)