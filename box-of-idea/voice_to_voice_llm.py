import vosk
import sounddevice as sd
import json
import requests
from ollama import chat
import wave
from piper import PiperVoice
import subprocess
import threading
import queue
import tempfile
import os

VOSK_MODEL_PATH = "./model/vosk/vosk-model-small-fr/vosk-model-small-fr-0.22"
MIC_DEVICE = None
MODEL = "llama3.2:3b"
VOICE_PATH = "model/tts/glados/fr_FR-glados-medium.onnx"


def listen() -> str:
    model = vosk.Model(VOSK_MODEL_PATH)
    rec = vosk.KaldiRecognizer(model, 16000)

    print("🎤 Écoute...")

    with sd.RawInputStream(samplerate=16000, blocksize=8000,
                           dtype="int16", channels=1, device=None) as stream:
        while True:
            data, _ = stream.read(4000)
            if rec.AcceptWaveform(bytes(data)):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                if text:
                    print(f">>> {text}")
                    return text

def should_flush(buf: str) -> bool:
    buf = buf.strip()
    if not buf:
        return False
    if buf.endswith((".", "!", "?", "…", "\n")):
        return True
    if len(buf) >= 140 and " " in buf:
        return True
    return False

def player_worker(q: "queue.Queue[str | None]"):
    while True:
        path = q.get()
        if path is None:
            return
        subprocess.run(["mpv", "--no-terminal", "--really-quiet", path])
        try:
            os.remove(path)
        except OSError:
            pass

def llm(text: str):
    message = text
    if (message == "fermer"):
        exit()
    if not message:
        print("No message\n")
        return
    voice = PiperVoice.load(VOICE_PATH)
    audio_q: "queue.Queue[str | None]" = queue.Queue()
    t = threading.Thread(target=player_worker, args=(audio_q,), daemon=True)
    t.start()
    buf = ""
    stream = chat(
        model=MODEL,
        messages=[{"role": "user", "content": message}],
        stream=True,
    )
    for chunk in stream:
        token = chunk.get("message", {}).get("content", "")
        if not token:
            continue
        print(token, end="", flush=True)
        buf += token
        if should_flush(buf):
            text = buf.strip()
            buf = ""
            fd, path = tempfile.mkstemp(prefix="tts_", suffix=".wav")
            os.close(fd)
            with wave.open(path, "wb") as wav_file:
                voice.synthesize_wav(text, wav_file)
            audio_q.put(path)
    if buf.strip():
        fd, path = tempfile.mkstemp(prefix="tts_", suffix=".wav")
        os.close(fd)
        with wave.open(path, "wb") as wav_file:
            voice.synthesize_wav(buf.strip(), wav_file)
        audio_q.put(path)
    audio_q.put(None)
    t.join()
    print("\n")


def main():
    while (True):
        text = listen()
        llm(text)

main()