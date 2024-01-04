import sounddevice as sd
import numpy as np
import keyboard
from datetime import datetime
import wave
import time
import threading

def record_audio():
    print("Press and hold the space bar to start recording. Release to stop.")
    print("Type 'exit' anytime to stop the program.")

    def check_exit():
        while True:
            if input().lower() == 'exit':
                print("Exiting program...")
                sd.stop()
                break

    exit_thread = threading.Thread(target=check_exit)
    exit_thread.daemon = True
    exit_thread.start()

    while exit_thread.is_alive():
        try:
            keyboard.wait('space')  # Wait for spacebar press to start recording
            print("Recording started.")
            frames = []

            def callback(indata, frames_available, time_info, status):
                if status:
                    print(status, file=sys.stderr)
                frames.append(indata.copy())

            with sd.InputStream(callback=callback, samplerate=44100, channels=1, dtype='float32') as stream:
                while True:
                    time.sleep(0.1)
                    if not keyboard.is_pressed('space'):
                        break

                stream.stop()
            print("Recording stopped.")

            # Save the recording
            audio_data = np.concatenate(frames, axis=0)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"recorded_{timestamp}.wav"
            write_wav(output_file, audio_data, 44100)
            print(f"Audio recording saved as {output_file}")

        except Exception as e:
            print(f"An error occurred: {e}")

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
