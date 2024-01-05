import requests
import json
import os
import time
from datetime import datetime

# API configuration
API_URL = "http://localhost:1234/v1/chat/completions"
HEADERS = {"Content-Type": "application/json"}

# File paths
HISTORY_FILE = "chat_history.json"
RESPONSES_DIR = "responses/"
PROMPTS_DIR = "prompts/"

def load_chat_history():
    """Loads the chat history from a file."""
    try:
        with open(HISTORY_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_chat_history(history):
    """Saves the chat history to a file."""
    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=2)

def save_response(content):
    """Saves the assistant's response to a file with a timestamp."""
    if not os.path.exists(RESPONSES_DIR):
        os.makedirs(RESPONSES_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"{RESPONSES_DIR}{timestamp}.txt", "w") as file:
        file.write(content)

def send_chat_request(message):
    """Sends a chat request to the API and returns the response."""
    messages.append(message)

    data = {
        "messages": messages[-20:],  # Send only the last 20 messages
        "temperature": 0.7,
        "max_tokens": -1,
        "stream": False
    }

    response = requests.post(API_URL, headers=HEADERS, json=data)

    try:
        response_json = response.json()
        if response.status_code == 200 and 'choices' in response_json:
            assistant_message = response_json['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": assistant_message})
            print("Merlin:", assistant_message)
            save_response(assistant_message)
            return assistant_message
        else:
            print("Error:", response.status_code, response.text)
            return None
    except json.JSONDecodeError as e:
        print("JSON decoding failed:", e)
        print("Raw response:", response.text)
        return None

def get_oldest_prompt_file(directory):
    """Gets the oldest file in the specified directory."""
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.txt')]
    if not files:
        return None
    return min(files, key=os.path.getctime)

def voice_mode():
    """Processes text files in the prompts directory as chat input."""
    print("Entering voice mode... Type 'q' to exit.")
    while True:
        prompt_file = get_oldest_prompt_file(PROMPTS_DIR)
        if prompt_file:
            with open(prompt_file, 'r') as file:
                prompt_text = file.read().strip()
            print("Processing:", prompt_text)
            send_chat_request({"role": "user", "content": prompt_text})
            os.remove(prompt_file)
            prompt_file = get_oldest_prompt_file(PROMPTS_DIR)
        else:
            time.sleep(1)  # Wait before checking for new files

# Load chat history
messages = load_chat_history()

# Main loop for voice mode
while True:

    user_input = input("You: ")
    if user_input.lower() == '/voice':
        voice_mode()
    elif user_input.lower() in ['exit', 'quit']:
        print("Exiting chat.")
        save_chat_history(messages)
        break
    else:
        user_message = {"role": "user", "content": user_input}
        send_chat_request(user_message)
