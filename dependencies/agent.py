import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer
import datetime
import os
import numpy as np
from typing import Dict, Any
import random

# Configuration
CONFIG = {
    "audio": {
        "samplerate": 44100,
        "device": 2,  # Your microphone array
        "channels": 1,
        "dtype": "int16",
        "blocksize": 8000
    },
    "model_path": "model-hi",
    "output_file": "conversation_log.txt"
}

class VoiceAssistant:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.q = queue.Queue()
        self.setup_audio_model()
        self.response_modes = {
            "echo": self.echo_response,
            "qa": self.qa_response,
            "translate": self.translate_response,
            "sentiment": self.sentiment_response
        }
        self.current_mode = "qa"
        self.qa_pairs = {
            "नमस्ते": "नमस्ते! मैं कैसे आपकी मदद कर सकता हूँ?",
            "तुम कौन हो": "मैं एक आवाज सहायक हूँ जिसे Python में बनाया गया है।",
            "धन्यवाद": "आपका स्वागत है! कोई और सहायता?",
            "समय क्या हुआ है": f"अभी समय है {datetime.datetime.now().strftime('%H:%M')}"
        }

    def setup_audio_model(self):
        """Initialize speech recognition model"""
        if not os.path.exists(self.config["model_path"]):
            raise FileNotFoundError(f"Model directory '{self.config['model_path']}' not found")

        self.model = Model(self.config["model_path"])
        self.recognizer = KaldiRecognizer(self.model, self.config["audio"]["samplerate"])
        self.recognizer.SetWords(True)

    def audio_callback(self, indata, frames, time, status):
        """Handle audio input"""
        if status:
            print("⚠️", status, flush=True)
        self.q.put(indata.copy())

    def process_audio(self):
        """Process audio stream and return recognized text"""
        data = self.q.get()
        if self.recognizer.AcceptWaveform(data.tobytes()):
            result = json.loads(self.recognizer.Result())
            return result.get("text", "").strip()
        return None

    def generate_response(self, text: str) -> str:
        """Generate appropriate response based on mode and input"""
        text = text.lower()
        
        # Mode switching commands
        if "मोड बदलो" in text:
            return self.handle_mode_change(text)
        
        # Get response based on current mode
        response_func = self.response_modes.get(self.current_mode, self.qa_response)
        return response_func(text)

    def handle_mode_change(self, text: str) -> str:
        """Change response mode"""
        for mode in self.response_modes:
            if mode in text:
                self.current_mode = mode
                return f"मोड बदला गया: {mode}"
        return "कृपया वैध मोड निर्दिष्ट करें (echo, qa, translate, sentiment)"

    def echo_response(self, text: str) -> str:
        """Simply repeat the input"""
        return f"आपने कहा: {text}"

    def qa_response(self, text: str) -> str:
        """Answer questions from predefined pairs"""
        for question, answer in self.qa_pairs.items():
            if question.lower() in text:
                return answer
        return "मैं इस प्रश्न का उत्तर नहीं जानता। क्या आप इसे अलग तरीके से पूछ सकते हैं?"

    def translate_response(self, text: str) -> str:
        """Simulate translation (would connect to real API in production)"""
        return f"(अनुवाद मोड) अंग्रेजी में यह होगा: '{text}'"

    def sentiment_response(self, text: str) -> str:
        """Analyze sentiment (simplified version)"""
        positive_words = ["अच्छा", "शुक्रिया", "धन्यवाद", "बढ़िया"]
        if any(word in text for word in positive_words):
            return "आप सकारात्मक लगते हैं!"
        return "मैं आपकी भावना समझने की कोशिश कर रहा हूँ..."

    def run(self):
        """Main execution loop"""
        print("🎤 आवाज सहायक सक्रिय... (रोकने के लिए Ctrl+C दबाएँ)")
        print(f"वर्तमान मोड: {self.current_mode}\n")

        with sd.InputStream(**self.config["audio"], callback=self.audio_callback):
            with open(self.config["output_file"], "a", encoding="utf-8") as log_file:
                while True:
                    try:
                        text = self.process_audio()
                        if text:
                            print(f"\nआप: {text}")
                            response = self.generate_response(text)
                            print(f"सहायक: {response}")
                            
                            # Log conversation
                            timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
                            log_file.write(f"{timestamp} User: {text}\n")
                            log_file.write(f"{timestamp} Assistant: {response}\n")
                            log_file.flush()

                    except KeyboardInterrupt:
                        print("\n🛑 सहायक बंद किया जा रहा है...")
                        break
                    except Exception as e:
                        print(f"त्रुटि: {e}")
                        continue

if __name__ == "__main__":
    try:
        assistant = VoiceAssistant(CONFIG)
        assistant.run()
    except Exception as e:
        print(f"प्रारंभिक त्रुटि: {e}")