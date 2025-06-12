
import sounddevice as sd
import soundfile as sf
from vosk import Model, KaldiRecognizer

def test_vosk(text_file="audio.wav"):
    # Record a test file
    fs = 16000
    recording = sd.rec(int(5 * fs), samplerate=fs, channels=1, dtype='int16')
    print("Speak now...")
    sd.wait()
    print("Done recording.")
    sf.write(text_file, recording, fs)
    
    # Test recognition
    model = Model("model-hi")
    rec = KaldiRecognizer(model, fs)
    with open(text_file, "rb") as f:
        data = f.read(4000)
        if rec.AcceptWaveform(data):
            print(rec.Result())
            
            
test_vosk()