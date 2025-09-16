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
            {"role": "system", "content": "You are a helpful ai assistant and your name is Propeller AI. You are built for the purpose of helping users with their questions."},
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
