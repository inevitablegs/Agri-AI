import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer
import datetime
import sys
import os

# Audio settings - adjusted for your system
samplerate = 44100  # Changed from 16000 to 44100 for better compatibility
device = 2  # Using "Microphone Array (AMD Audio Dev)" based on your list
channels = 1
dtype = 'int16'
blocksize = 8000  # Increased block size for better performance
q = queue.Queue()

# Model configuration
model_path = "model-hi"
if not os.path.exists(model_path):
    print(f"Error: Model directory '{model_path}' not found!")
    print("Please download the Hindi model from https://alphacephei.com/vosk/models")
    print("and extract it in the current directory.")
    sys.exit(1)

# Initialize model and recognizer
try:
    print("Loading model...")
    model = Model(model_path)
    rec = KaldiRecognizer(model, samplerate)
    rec.SetWords(True)  # Enable word-level timestamps
    print("Model loaded successfully")
except Exception as e:
    print(f"Error initializing model: {e}")
    sys.exit(1)

def callback(indata, frames, time, status):
    """Audio callback function with volume monitoring"""
    if status:
        print("⚠️ Audio input status:", status, file=sys.stderr)
    volume_norm = int(np.linalg.norm(indata) * 10)
    print(f"Audio level: {'█' * volume_norm}", end='\r')  # Visual volume indicator
    q.put(indata.copy())

def list_audio_devices():
    """List available audio devices with input capability"""
    print("\nAvailable INPUT devices:")
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"{i}: {dev['name']} (Input channels: {dev['max_input_channels']})")
    print()

def main():
    # List available input devices
    list_audio_devices()
    print(f"Using device #{device}: {sd.query_devices(device)['name']}\n")

    print("🎤 बोलिए... (Press Ctrl+C to stop)")
    print("Waiting for audio input...\n")

    try:
        with open("output.txt", "a", encoding="utf-8") as output_file:
            with sd.InputStream(samplerate=samplerate,
                              channels=channels,
                              dtype=dtype,
                              callback=callback,
                              device=device,
                              blocksize=blocksize) as stream:
                print(f"Audio stream started on {stream.device}")
                print("Speak now... (You should see audio level indicators)")
                
                while True:
                    try:
                        data = q.get(timeout=10)  # Increased timeout
                        if rec.AcceptWaveform(data.tobytes()):
                            result = json.loads(rec.Result())
                            text = result.get("text", "").strip()
                            if text:
                                timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
                                print("\n🗣️", text)
                                output_file.write(f"{timestamp} {text}\n")
                                output_file.flush()
                        else:
                            partial = json.loads(rec.PartialResult())
                            partial_text = partial.get("partial", "").strip()
                            if partial_text:
                                print("⌛", partial_text, end='\r', flush=True)
                    except queue.Empty:
                        print("\nNo audio input detected for 10 seconds. Check your microphone connection.")
                        break
                    except Exception as e:
                        print(f"\nProcessing error: {e}", file=sys.stderr)
                        continue

    except KeyboardInterrupt:
        print("\n🛑 Recording stopped. धन्यवाद!")
    except Exception as e:
        print(f"\nFatal error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    import numpy as np  # Required for volume monitoring
    main()