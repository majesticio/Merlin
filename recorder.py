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
    def __init__(self, recordings_folder="recordings", samplerate=44100, channels=1, normalization_mode='peak'):
        self.recordings_folder = recordings_folder
        self.samplerate = samplerate
        self.channels = channels
        self.normalization_mode = normalization_mode
        self.frames = []
        self.exit_flag = False
        self.ensure_folder_exists()

    def ensure_folder_exists(self):
        if not os.path.exists(self.recordings_folder):
            os.makedirs(self.recordings_folder)

    def record_audio(self):
        print("Press Ctrl+C anytime to stop the program.")
        print("\nPress and hold the space bar to start recording. Release to stop.")

        spinner = self.spinning_cursor()

        while True:
            try:
                keyboard.wait('space')
                sys.stdout.write("Recording started...\n ")
                sys.stdout.flush()
                self.frames = []

                with sd.InputStream(callback=self.callback, samplerate=self.samplerate, channels=self.channels, dtype='float32') as stream:
                    while keyboard.is_pressed('space'):
                        sys.stdout.write('\r' + next(spinner))
                        sys.stdout.flush()
                        time.sleep(0.1)
                    stream.stop()
                print("\rRecording stopped.")

                self.save_recording()

            except KeyboardInterrupt:
                print("\nExiting program...")
                break
            except Exception as e:
                print(f"\nAn error occurred: {e}")
            finally:
                sd.stop()


        sys.exit(0)

    def check_exit(self):
        print("check_exit: Thread started")  # Start of the check_exit function
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
            self.write_wav(output_file, audio_data)
            print(f"Audio recording saved as {output_file}")
        except Exception as e:
            print(f"Failed to save audio recording: {e}")

    def normalize_audio(self, data):
        if self.normalization_mode == 'peak':
            return self.normalize_peak(data)
        elif self.normalization_mode == 'rms':
            return self.normalize_rms(data)
        elif self.normalization_mode == 'lufs':
            return self.normalize_lufs(data)
        elif self.normalization_mode == 'off':
            return data  # Bypasses normalization
        else:
            raise ValueError("Invalid normalization mode")

    def normalize_peak(self, data):
        peak = np.max(np.abs(data))
        return data / peak if peak != 0 else data

    def normalize_rms(self, data, target_rms=0.1):
        current_rms = np.sqrt(np.mean(data**2))
        return data * (target_rms / current_rms) if current_rms != 0 else data

    def normalize_lufs(self, data):
        import pyloudnorm as pyln
        meter = pyln.Meter(self.samplerate)  # create BS.1770 meter
        loudness = meter.integrated_loudness(data)
        target_lufs = -23.0
        return pyln.normalize.loudness(data, loudness, target_lufs)

    def write_wav(self, filename, data):
        normalized_data = self.normalize_audio(data)
        scaled_data = np.int16(normalized_data / np.max(np.abs(normalized_data)) * 32767)
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.samplerate)
            wf.writeframes(scaled_data.tobytes())

    def signal_handler(self, signum, frame):
        print("\nSignal received, terminating program.")
        self.exit_flag = True
        sd.stop()

if __name__ == "__main__":
    recorder = AudioRecorder(normalization_mode='lufs')  # Choose from 'peak', 'rms', 'lufs', or 'off'
    recorder.record_audio()
