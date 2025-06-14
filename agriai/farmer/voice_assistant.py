# Create a new file agriai/farmer/voice_assistant.py
from django.conf import settings
import os
import json
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue

class HindiVoiceAssistant:
    def __init__(self):
        self.model_path = os.path.join(settings.BASE_DIR, 'dependencies', 'model-hi')
        self.config = {
            "audio": {
                "samplerate": 16000,
                "device": None,
                "channels": 1,
                "dtype": "int16",
                "blocksize": 8000
            }
        }
        self.q = queue.Queue()
        self.setup_model()

    def setup_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Hindi model not found at {self.model_path}")
        self.model = Model(self.model_path)
        self.recognizer = KaldiRecognizer(self.model, self.config["audio"]["samplerate"])

    def audio_callback(self, indata, frames, time, status):
        self.q.put(indata.copy())

    def process_audio(self):
        data = self.q.get()
        if self.recognizer.AcceptWaveform(data.tobytes()):
            result = json.loads(self.recognizer.Result())
            return result.get("text", "").strip()
        return None

    def listen(self):
        with sd.InputStream(**self.config["audio"], callback=self.audio_callback):
            while True:
                text = self.process_audio()
                if text:
                    return text