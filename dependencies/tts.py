import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer
import datetime

samplerate = 16000
q = queue.Queue()

model = Model("model-hi")
rec = KaldiRecognizer(model, samplerate)

def callback(indata, frames, time, status):
    if status:
        print("⚠️", status)
    q.put(indata.copy())

print("🎤 बोलिए... (Press Ctrl+C to stop)\n")

output_file = open("output.txt", "a", encoding="utf-8")

try:
    with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16', callback=callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data.tobytes()):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                if text:
                    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
                    print("🗣️", text)
                    output_file.write(f"{timestamp} {text}\n")
                    output_file.flush()
            else:
                partial = json.loads(rec.PartialResult())
                partial_text = partial.get("partial", "").strip()
                if partial_text:
                    print("⌛", partial_text, end='\r')

except KeyboardInterrupt:
    print("\n🛑 बंद किया गया। धन्यवाद!")
finally:
    output_file.close()
