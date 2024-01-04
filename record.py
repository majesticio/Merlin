import os
import sounddevice as sd
import numpy as np
import keyboard
from datetime import datetime
import wave
import time
import threading
import sys

def record_audio():
    recordings_folder = "recordings"
    if not os.path.exists(recordings_folder):
        os.makedirs(recordings_folder)

    print("Press and hold the space bar to start recording. Release to stop.")
    print("Type 'exit' anytime to stop the program.")

    def check_exit():
        while True:
            if input().lower() == 'exit':
                print("\nExiting program...")
                sd.stop()
                break

    def spinning_cursor():
        while True:
            for cursor in '|/-\\':
                yield cursor

    spinner = spinning_cursor()

    exit_thread = threading.Thread(target=check_exit)
    exit_thread.daemon = True
    exit_thread.start()

    while exit_thread.is_alive():
        try:
            keyboard.wait('space')  # Wait for spacebar press to start recording
            sys.stdout.write("Recording started ")
            sys.stdout.flush()
            frames = []

            def callback(indata, frames_available, time_info, status):
                if status:
                    print(status, file=sys.stderr)
                frames.append(indata.copy())

            with sd.InputStream(callback=callback, samplerate=44100, channels=1, dtype='float32') as stream:
                while keyboard.is_pressed('space'):
                    sys.stdout.write('\r' + next(spinner))  # Use '\r' to overwrite the character
                    sys.stdout.flush()
                    time.sleep(0.1)

                stream.stop()
            print("\rRecording stopped.          ")  # Clear the spinner

            # Save the recording
            audio_data = np.concatenate(frames, axis=0)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(recordings_folder, f"recorded_{timestamp}.wav")
            write_wav(output_file, audio_data, 44100)
            print(f"Audio recording saved as {output_file}")

        except Exception as e:
            print(f"\nAn error occurred: {e}")

def write_wav(filename, data, samplerate):
    data = np.int16(data / np.max(np.abs(data)) * 32767)
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)  # Mono recording
    wf.setsampwidth(2)  # 16-bit depth
    wf.setframerate(samplerate)
    wf.writeframes(data.tobytes())
    wf.close()

if __name__ == "__main__":
    record_audio()
