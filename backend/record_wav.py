import sounddevice as sd
import soundfile as sf
import sys
from pathlib import Path

def record_wav(filename='recordings/sample.wav', duration=5, sr=16000):
    Path('recordings').mkdir(parents=True, exist_ok=True)
    print(f"🎤 Recording {duration}s at {sr}Hz -> {filename}")
    data = sd.rec(int(duration*sr), samplerate=sr, channels=1, dtype='int16')
    sd.wait()
    sf.write(filename, data, sr)
    print("✅ Saved:", filename)

if __name__ == "__main__":
    d = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    record_wav(duration=d)
