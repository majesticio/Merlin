import requests
import json

API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "dolphin-mixtral"  # Replace with your model name
PROMPT = "You are a useful assistant who is direct and casual"

# Initial message from the assistant
messages = [
    {
      "role": "assistant",
      "content": "How can I help you?"
    }
]

def declare_model(model, prompt):
    data = {
        "model": model,
        "prompt": prompt
    }
    response = requests.post(API_URL, json=data)
    if response:
        print("Successfully loaded model: ", response.json()["model"])
    else:
        print("Model load error.")

declare_model(MODEL_NAME, PROMPT)

# Opening message
print(f"Assistant: {messages[0]['content']}")

def send_chat_request(message):
    """Sends a chat request to the API and returns the response."""
    # Append the user message to the conversation history
    messages.append(message)

    data = {
        "model": MODEL_NAME,
        "messages": messages
    }
    response = requests.post(API_URL, json=data)

    # Split the response into individual JSON objects
    raw_responses = response.text.strip().split('\n')

    for raw_response in raw_responses:
        try:
            response_json = json.loads(raw_response)
            # Process each JSON object (response from the API)
            if 'message' in response_json:
                # Append the assistant's response to the conversation history
                messages.append(response_json["message"])
                # Print the assistant's response
                print("Assistant:", response_json["message"]["content"])
        except json.JSONDecodeError as e:
            # Log the error for debugging
            print("JSON decoding failed for a part of the response: ", e)
            print("Problematic response part: ", raw_response)

    # Return an empty dictionary or any other meaningful data
    return {}

# Continue with the rest of your script...




# Chat loop
while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit']:
        print("Exiting chat.")
        break
    else:
        # Create a message object for the user input
        user_message = {"role": "user", "content": user_input}
        
        # Send the chat request
        response = send_chat_request(user_message)
        
        # Print the assistant's response
        if 'message' in response:
            print("Assistant:", response["message"]["content"])

# End of script
