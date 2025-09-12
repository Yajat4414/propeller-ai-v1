import requests

API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"

def ask_model(user_input, model="anthropic/claude-opus-4.1"):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful AI chatbot."},
            {"role": "user", "content": user_input}
        ],
        "max_tokens": 500
    }

    response = requests.post(API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def get_bot_reply(user_input):
    try:
        return ask_model(user_input, "anthropic/claude-opus-4.1")
    except Exception as e:
        print("Opus failed, trying GPT-3.5…", str(e))
        try:
            return ask_model(user_input, "openai/gpt-3.5-turbo")
        except Exception as e2:
            return f"Error: {str(e2)}"
