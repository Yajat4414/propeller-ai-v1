# Updated app.py
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import chatbot
import base64
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
CORS(app)

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB limit

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def get_bot_response():
    try:
        data = request.get_json()
        user_text = data.get("message", "")
        image_data = data.get("image")  # Base64 encoded image
        
        if not user_text and not image_data:
            return jsonify({"error": "No message or image provided"}), 400
        
        # Handle image if provided
        image_path = None
        if image_data:
            try:
                # Remove the data:image/jpeg;base64, prefix if present
                if ',' in image_data:
                    image_data = image_data.split(',')[1]
                
                # Decode base64 image
                image_bytes = base64.b64decode(image_data)
                
                # Generate unique filename
                filename = f"{uuid.uuid4()}.jpg"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Save image
                with open(image_path, 'wb') as f:
                    f.write(image_bytes)
                    
            except Exception as e:
                return jsonify({"error": f"Failed to process image: {str(e)}"}), 400
        
        # Get bot response (pass image path if available)
        bot_reply = chatbot.get_bot_reply(user_text, image_path)
        
        # Clean up temporary image file
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except:
                pass  # Ignore cleanup errors
        
        return jsonify({"reply": bot_reply})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Convert to base64 for frontend
            with open(file_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Clean up
            os.remove(file_path)
            
            return jsonify({
                "success": True,
                "image_data": f"data:image/{filename.split('.')[-1]};base64,{image_data}",
                "filename": filename
            })
        else:
            return jsonify({"error": "Invalid file type"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

# Updated chatbot.py
import requests
import base64

API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"

def ask_model(user_input, model="anthropic/claude-3-sonnet", image_path=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Build the message content
    message_content = []
    
    # Add text if provided
    if user_input:
        message_content.append({
            "type": "text",
            "text": user_input
        })
    
    # Add image if provided
    if image_path:
        try:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Determine image type
            image_ext = image_path.split('.')[-1].lower()
            if image_ext == 'jpg':
                image_ext = 'jpeg'
            
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{image_ext};base64,{image_data}"
                }
            })
        except Exception as e:
            print(f"Error processing image: {e}")

    data = {
        "model": model,
        "messages": [
            {
                "role": "system", 
                "content": "You are a helpful AI assistant that can analyze images and answer questions about them."
            },
            {
                "role": "user", 
                "content": message_content if message_content else user_input
            }
        ],
        "max_tokens": 1000
    }

    response = requests.post(API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def get_bot_reply(user_input, image_path=None):
    try:
        # Try Claude first (supports vision)
        return ask_model(user_input, "anthropic/claude-3-sonnet", image_path)
    except Exception as e:
        print("Claude failed, trying GPT-4 Vision...", str(e))
        try:
            # Fallback to GPT-4 Vision
            return ask_model(user_input, "openai/gpt-4-vision-preview", image_path)
        except Exception as e2:
            print("GPT-4 Vision failed, trying regular GPT-4...", str(e2))
            try:
                # Final fallback to regular GPT-4 (text only)
                text_only_input = user_input if user_input else "Please describe what you see in this image."
                if image_path:
                    text_only_input += " (Note: An image was uploaded but cannot be processed by this model)"
                return ask_model(text_only_input, "openai/gpt-4", None)
            except Exception as e3:
                return f"Error: All models failed. {str(e3)}"