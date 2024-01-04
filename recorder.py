import os
import sounddevice as sd
import numpy as np
import keyboard
from datetime import datetime
import wave
import time
import threading
import sys
import signal

class AudioRecorder:
    def __init__(self, recordings_folder="recordings", samplerate=44100, channels=1):
        self.recordings_folder = recordings_folder
        self.samplerate = samplerate
        self.channels = channels
        self.frames = []
        self.exit_flag = False
        self.ensure_folder_exists()

    def ensure_folder_exists(self):
        if not os.path.exists(self.recordings_folder):
            os.makedirs(self.recordings_folder)

    def record_audio(self):
        print("\nPress and hold the space bar to start recording. Release to stop.")
        print("Type 'exit' anytime to stop the program.")

        signal.signal(signal.SIGINT, self.signal_handler)

        exit_thread = threading.Thread(target=self.check_exit)
        exit_thread.start()

        spinner = self.spinning_cursor()

        while not self.exit_flag:
            try:
                keyboard.wait('space')  # Wait for spacebar press to start recording
                sys.stdout.write("Recording started...\n ")
                sys.stdout.flush()
                self.frames = []

                with sd.InputStream(callback=self.callback, samplerate=self.samplerate, channels=self.channels, dtype='float32') as stream:
                    while keyboard.is_pressed('space') and not self.exit_flag:
                        sys.stdout.write('\r' + next(spinner))  # Use '\r' to overwrite the character
                        sys.stdout.flush()
                        time.sleep(0.1)

                    stream.stop()
                print("\rRecording stopped.")  # Clear the spinner

                # Save the recording
                self.save_recording()

            except Exception as e:
                print(f"\nAn error occurred: {e}")

    def check_exit(self):
        while not self.exit_flag:
            if input().lower() == 'exit':
                print("\nExiting program...")
                self.exit_flag = True
                sd.stop()

    def spinning_cursor(self):
        while True:
            for cursor in '|/-\\':
                yield cursor

    def callback(self, indata, frames_available, time_info, status):
        if status:
            print(status, file=sys.stderr)
        self.frames.append(indata.copy())

    def save_recording(self):
        audio_data = np.concatenate(self.frames, axis=0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.recordings_folder, f"recorded_{timestamp}.wav")
        try:
            self.write_wav(output_file, audio_data, self.samplerate)
            print(f"Audio recording saved as {output_file}")
        except Exception as e:
            print(f"Failed to save audio recording: {e}")

    @staticmethod
    def write_wav(filename, data, samplerate):
        data = np.int16(data / np.max(np.abs(data)) * 32767)
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(1)  # Mono recording
                wf.setsampwidth(2)  # 16-bit depth
                wf.setframerate(samplerate)
                wf.writeframes(data.tobytes())
        except Exception as e:
            print(f"Error writing WAV file: {e}")

    def signal_handler(self, signum, frame):
        print("\nSignal received, terminating program.")
        self.exit_flag = True
        sd.stop()

if __name__ == "__main__":
    recorder = AudioRecorder()
    recorder.record_audio()
