# audio_recorder/main.py
import sounddevice as sd
import numpy as np
import wave

def record_audio(filename: str, duration: int = 5, samplerate: int = 44100):
    """
    Records audio and saves it as a WAV file.
    :param filename: Output file name.
    :param duration: Duration in seconds.
    :param samplerate: Sampling rate.
    """
    print(f"Recording for {duration} seconds...")
    audio_data = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=2, dtype='int16')
    sd.wait()
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())
    print(f"Recording saved to {filename}")