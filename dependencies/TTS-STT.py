import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer
import datetime
import os
import numpy as np
from gtts import gTTS
import tempfile
import subprocess
from typing import Dict, Any
import platform
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import os


from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play

# Configuration
CONFIG = {
    "audio": {
        "samplerate": 16000,
        "device": None,  # Default input device
        "channels": 1,
        "dtype": "int16",
        "blocksize": 8000
    },
    "model_path": "model-hi",  # Hindi model
    "output_file": "hindi_conversation_log.txt"
}

class HindiVoiceAssistant:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.q = queue.Queue()
        self.setup_audio_model()
        self.response_modes = {
            "सामान्य": self.normal_response,
            "अनुवाद": self.translate_response,
            "मनोदशा": self.sentiment_response,
            "सहायता": self.help_response
        }
        self.current_mode = "सामान्य"
        
        # Hindi question-answer pairs
        self.qa_pairs = {
            "नमस्ते": "नमस्ते! मैं आपकी कैसे मदद कर सकता हूँ?",
            "तुम कौन हो": "मैं एक हिंदी वॉइस असिस्टेंट हूँ, Python में बनाया गया",
            "धन्यवाद": "आपका स्वागत है! क्या कोई और मदद चाहिए?",
            "समय क्या हुआ है": self.get_current_time,
            "तुम कैसे हो": "मैं ठीक हूँ, धन्यवाद! आप कैसे हैं?",
            "मोड बदलो": self.list_modes,
            "बंद करो": self.shutdown
        }

    def setup_audio_model(self):
        """Initialize Hindi speech recognition model"""
        if not os.path.exists(self.config["model_path"]):
            raise FileNotFoundError(f"Hindi model directory '{self.config['model_path']}' not found")

        self.model = Model(self.config["model_path"])
        self.recognizer = KaldiRecognizer(self.model, self.config["audio"]["samplerate"])
        self.recognizer.SetWords(True)

    

    

    # def text_to_speech(self, text: str):
    #     """Convert text to speech using pydub with proper temp file handling"""
    #     try:
    #         # Create temp file with delete=False and proper permissions
    #         with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
    #             temp_path = f.name
            
    #         # Generate and save audio
    #         tts = gTTS(text=text, lang='hi')
    #         tts.save(temp_path)
            
    #         # Load and play audio
    #         sound = AudioSegment.from_mp3(temp_path)
    #         play(sound)
            
    #     except Exception as e:
    #         print(f"TTS Error: {e}")
    #     finally:
    #         # Ensure cleanup even if errors occur
    #         if os.path.exists(temp_path):
    #             try:
    #                 os.unlink(temp_path)
    #             except PermissionError:
    #                 # File might still be in use, retry after delay
    #                 import time
    #                 time.sleep(0.1)
    #                 os.unlink(temp_path)
    
    def text_to_speech(self, text: str):
        """Convert text to speech without temp files"""
        try:
            # Create in-memory file
            mp3_fp = BytesIO()
            
            # Generate audio directly to memory
            tts = gTTS(text=text, lang='hi')
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)  # Rewind to beginning
            
            # Load and play from memory
            sound = AudioSegment.from_mp3(mp3_fp)
            play(sound)
            
        except Exception as e:
            print(f"TTS Error: {e}")
    

    def audio_callback(self, indata, frames, time, status):
        """Handle audio input"""
        if status:
            print("⚠️", status, flush=True)
        self.q.put(indata.copy())

    def process_audio(self):
        """Process audio stream and return recognized Hindi text"""
        data = self.q.get()
        if self.recognizer.AcceptWaveform(data.tobytes()):
            result = json.loads(self.recognizer.Result())
            return result.get("text", "").strip()
        return None

    def get_current_time(self, text: str = "") -> str:
        """Get current time in Hindi"""
        now = datetime.datetime.now()
        return f"अभी समय है {now.strftime('%H:%M')}"

    def list_modes(self, text: str = "") -> str:
        """List available modes"""
        modes = ", ".join(self.response_modes.keys())
        return f"उपलब्ध मोड: {modes}. मोड बदलने के लिए कहें 'मोड बदलो [मोड नाम]'"

    def shutdown(self, text: str = "") -> str:
        """Shutdown the assistant"""
        self.text_to_speech("असिस्टेंट बंद किया जा रहा है। धन्यवाद!")
        exit()

    def generate_response(self, text: str) -> str:
        """Generate appropriate Hindi response"""
        text = text.lower()
        
        # Check for direct commands first
        for cmd, response in self.qa_pairs.items():
            if cmd.lower() in text:
                if callable(response):
                    return response(text)
                return response

        # Mode switching
        if "मोड बदलो" in text:
            return self.handle_mode_change(text)
        
        # Get response based on current mode
        response_func = self.response_modes.get(self.current_mode, self.normal_response)
        return response_func(text)

    def handle_mode_change(self, text: str) -> str:
        """Change response mode"""
        for mode in self.response_modes:
            if mode in text:
                self.current_mode = mode
                return f"मोड बदला गया: {mode}"
        return "कृपया वैध मोड निर्दिष्ट करें"

    def normal_response(self, text: str) -> str:
        """Default response mode"""
        return "मैंने आपकी बात सुनी। क्या आप और विस्तार से बता सकते हैं?"

    def translate_response(self, text: str) -> str:
        """Translation mode response"""
        return f"(अनुवाद मोड) अंग्रेजी में: '{text}'"

    def sentiment_response(self, text: str) -> str:
        """Sentiment analysis mode"""
        positive_words = ["अच्छा", "शुक्रिया", "धन्यवाद", "बढ़िया"]
        if any(word in text for word in positive_words):
            return "आप सकारात्मक लगते हैं!"
        return "मैं आपकी भावना समझने की कोशिश कर रहा हूँ..."

    def help_response(self, text: str) -> str:
        """Help mode response"""
        return "मैं निम्नलिखित कार्य कर सकता हूँ: समय बताना, मोड बदलना, सामान्य बातचीत"

    def run(self):
        """Main execution loop"""
        self.text_to_speech("हिंदी वॉइस असिस्टेंट शुरू हो रहा है")
        print("🎤 हिंदी वॉइस असिस्टेंट सक्रिय... (रोकने के लिए 'बंद करो' कहें)")
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
                            self.text_to_speech(response)
                            
                            # Log conversation
                            timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
                            log_file.write(f"{timestamp} User: {text}\n")
                            log_file.write(f"{timestamp} Assistant: {response}\n")
                            log_file.flush()

                    except KeyboardInterrupt:
                        self.shutdown()
                    except Exception as e:
                        print(f"त्रुटि: {e}")
                        continue

if __name__ == "__main__":
    try:
        # Verify Hindi model exists
        if not os.path.exists("model-hi"):
            print("कृपया हिंदी मॉडल डाउनलोड करें:")
            print("https://alphacephei.com/vosk/models")
            print("और 'model-hi' नाम के फोल्डर में एक्सट्रैक्ट करें")
        else:
            assistant = HindiVoiceAssistant(CONFIG)
            assistant.run()
    except Exception as e:
        print(f"प्रारंभिक त्रुटि: {e}")