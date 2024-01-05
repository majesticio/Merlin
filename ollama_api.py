import requests
import json
import os
import time
from datetime import datetime

API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "dolphin-mixtral"  # Replace with your model name
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
        "model": MODEL_NAME,
        "messages": messages[-20:],  # Send only the last 20 messages
        "stream": False  # Set to non-streaming mode
    }

    response = requests.post(API_URL, json=data)

    try:
        response_json = response.json()
        if 'message' in response_json and response_json['message']['role'] == 'assistant':
            messages.append(response_json["message"])
            full_response_content = response_json["message"]["content"]
            print("Merlin:", full_response_content)
            save_response(full_response_content)
            return full_response_content
    except json.JSONDecodeError as e:
        print("JSON decoding failed: ", e)
        print("Raw response: ", response.text)
        return None

def get_oldest_prompt_file(directory):
    """Gets the oldest file in the specified directory based on the filename timestamp."""
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.txt')]
    if not files:
        return None
    return min(files, key=os.path.getctime)

def voice_mode():
    """Process the oldest text files in the prompts directory and send them to chat."""
    print("Entering voice mode... Type 'q' to exit.")
    while True:
        prompt_file = get_oldest_prompt_file(PROMPTS_DIR)
        while prompt_file:
            with open(prompt_file, 'r') as file:
                prompt_text = file.read()
            send_chat_request({"role": "user", "content": prompt_text})
            os.remove(prompt_file)  # Remove the file after processing
            prompt_file = get_oldest_prompt_file(PROMPTS_DIR)

        print("No prompts found. Waiting for new files...")
        time.sleep(1)  # Wait for 1 second before checking again

# Load chat history
messages = load_chat_history()

# Chat loop
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
