import os
import time
import threading
from datetime import datetime
from TTS.api import TTS
from pydub import AudioSegment
from pydub.playback import play
import torch

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Define the model path
MODEL_NAME = "tts_models/en/jenny/jenny"
# Set base directory for the wave files
WAV_DIR = "../speaker/"
# Set the responses directory
RESPONSES_DIR = "responses/"

# Initialize TTS model
tts_engine = TTS(model_name=MODEL_NAME, progress_bar=False).to(device)

# Ensure speaker directory exists
if not os.path.exists(WAV_DIR):
    os.makedirs(WAV_DIR)

def speak(text, out_path):
    """
    Synthesize speech from the given text using the specified TTS model and play it.
    """
    tts_engine.tts_to_file(text=text, file_path=out_path)
    audio = AudioSegment.from_wav(out_path)
    play(audio)
    os.remove(out_path)  # Remove the WAV file after playing

def process_file(file_path):
    """
    Read the text from the file, synthesize and play the speech in a new thread.
    """
    with open(file_path, 'r') as file:
        text = file.read()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    wav_file_path = f"{WAV_DIR}response_{timestamp}.wav"

    # Start a new thread to handle speech synthesis and playback
    threading.Thread(target=speak, args=(text, wav_file_path)).start()
    os.remove(file_path)  # Remove the text file after reading

def get_oldest_file(directory):
    """
    Gets the oldest file in the specified directory based on the filename timestamp.
    """
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.txt')]
    if not files:
        return None
    return min(files, key=os.path.getctime)

while True:
    oldest_file = get_oldest_file(RESPONSES_DIR)
    if oldest_file:
        process_file(oldest_file)
    else:
        time.sleep(1)  # Wait for 1 second before checking again
