from gtts import gTTS
from pydub import AudioSegment

# Step 1: Create Hindi audio
text = "नमस्ते, मेरा नाम गणेश है। मैं एक किसान सहायक बना रहा हूँ।"
tts = gTTS(text=text, lang='hi')
tts.save("audio.mp3")

# Step 2: Convert MP3 to WAV (16000 Hz mono)
audio = AudioSegment.from_mp3("audio.mp3")
audio = audio.set_frame_rate(16000).set_channels(1)
audio.export("audio.wav", format="wav")

print("✅ audio.wav file created successfully!")
