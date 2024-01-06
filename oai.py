# Chat with an intelligent assistant in your terminal
import json
from openai import OpenAI

# Configuration
base_url = "http://localhost:1234/v1"
api_key = "not-needed"
history_file = "chat_history.json"
max_history_entries = 100  # Maximum entries in the history file

# Initialize client
client = OpenAI(base_url=base_url, api_key=api_key)

# Load or initialize history
try:
    with open(history_file, "r") as file:
        history = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    history = [
        {"role": "system", "content": "You are an intelligent assistant. You always provide well-reasoned answers that are both correct and helpful."},
        {"role": "user", "content": "Hello, introduce yourself to someone opening this program for the first time. Be concise."},
    ]

while True:
    try:
        completion = client.chat.completions.create(
            model="local-model",
            messages=history[-max_history_entries:],  # Use only recent history
            temperature=0.7,
            stream=True,
        )

        new_message = {"role": "assistant", "content": ""}

        for chunk in completion:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
                new_message["content"] += chunk.choices[0].delta.content

        history.append(new_message)
        
        print()

        user_input = input("> ")
        if user_input.lower() in ['exit', 'quit']:
            break
        history.append({"role": "user", "content": user_input})

        # Save history to file
        with open(history_file, "w") as file:
            json.dump(history[-max_history_entries:], file, indent=2)

    except Exception as e:
        print(f"An error occurred: {e}")
        break

print("Session ended.")
