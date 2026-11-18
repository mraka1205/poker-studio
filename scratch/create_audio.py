import wave
import struct
import math
from pathlib import Path

audio_dir = Path("g:/poker-studio/projects/ep01-sample/audio")
audio_dir.mkdir(parents=True, exist_ok=True)

# Generate a pleasant short chime sound for each segment
def generate_tone(filename, freq=440.0, duration=1.5):
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    with wave.open(str(filename), 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        for i in range(n_samples):
            # decay envelope
            env = math.exp(-3.0 * i / n_samples)
            sample = int(32767.0 * 0.3 * env * math.sin(2.0 * math.pi * freq * (i / sample_rate)))
            data = struct.pack('<h', sample)
            w.writeframesraw(data)

freqs = [440, 523, 659, 784, 880, 587, 698]
for idx, f in enumerate(freqs, 1):
    wav_path = audio_dir / f"seg_0{idx}.wav"
    generate_tone(wav_path, freq=f, duration=2.0)
    print(f"Created {wav_path}")

print("Audio placeholders created!")
