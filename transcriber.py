import os
import whisper
import time
from datetime import datetime

# Load Whisper model
model = whisper.load_model("small")

recordings_folder = "recordings"

def get_earliest_file(directory):
    """Get the earliest file in the directory based on the timestamp in the filename."""
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if not files:
        return None

    earliest_file = min(files, key=lambda x: datetime.strptime(x.replace('.wav', ''), '%Y%m%d_%H%M%S'))
    return os.path.join(directory, earliest_file)

while True:
    try:
        earliest_filename = get_earliest_file(recordings_folder)

        # Transcribe the earliest recording if it exists
        if earliest_filename:
            result = model.transcribe(earliest_filename, fp16=False)
            print("Transcribing:", earliest_filename)
            transcription = result['text']
            print(transcription)

            # Delete the file after transcription
            try:
                os.remove(earliest_filename)
                print(f"Deleted file: {earliest_filename}")
            except OSError as e:
                print(f"Error deleting file {earliest_filename}: {e}")

            continue
        else:
            print("No recordings found. Waiting for new files...")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting program...")
        break

# translation = model.transcribe(filename, fp16=False, task="translate")["text"]
# print(translation)
