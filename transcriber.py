import os
import whisper
import time
from datetime import datetime

# WHISPER: models include tiny, base, small, medium, and large (lil bit to load)
model = whisper.load_model("tiny")

# Define directories
recordings_folder = "recordings"
prompts_folder = "prompts"

# Ensure prompts directory exists
if not os.path.exists(prompts_folder):
    os.makedirs(prompts_folder)

def get_earliest_file(directory):
    """Get the earliest file in the directory based on the timestamp in the filename."""
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if not files:
        return None

    earliest_file = min(files, key=lambda x: datetime.strptime(x.replace('.wav', ''), '%Y%m%d_%H%M%S'))
    return os.path.join(directory, earliest_file)

def save_transcription(text):
    """Save the transcription to a file in the prompts folder with a timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(prompts_folder, f"transcription_{timestamp}.txt")
    with open(file_path, 'w') as file:
        file.write(text)
    print(f"Transcription saved to {file_path}")

while True:
    try:
        earliest_filename = get_earliest_file(recordings_folder)

        # Transcribe the earliest recording if it exists
        if earliest_filename:
            result = model.transcribe(earliest_filename, fp16=False)
            print("Transcribing:", earliest_filename)
            transcription = result['text']
            print(transcription)

            # Save the transcription
            save_transcription(transcription)

            # Delete the file after transcription
            try:
                os.remove(earliest_filename)
                print(f"Deleted file: {earliest_filename}")
            except OSError as e:
                print(f"Error deleting file {earliest_filename}: {e}")

            continue
        else:
            # print("No recordings found. Waiting for new files...")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting program...")
        break


# translation = model.transcribe(filename, fp16=False, task="translate")["text"]
# print(translation)
