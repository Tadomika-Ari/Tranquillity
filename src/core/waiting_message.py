import requests
from ollama import chat
import wave
from piper import PiperVoice
import subprocess
import threading
import queue
import tempfile
import os
import json

MODEL = "llama3.2:3b"
VOICE_PATH = "model/tts/glados/fr_FR-glados-medium.onnx"
PERSONALITY_PATH = "src/personality/personality.json"

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

def waiting_message():
    with open(PERSONALITY_PATH, "r", encoding="utf-8") as f:
        personnality = json.load(f)
    history = [personnality]
    message = "l'utilisateur est inactif, dit une phrase pas trop longue concernant sont inactivité alors que tu es allumé."
    history.append({"role": "user", "content": message.strip()})

    voice = PiperVoice.load(VOICE_PATH)
    audio_q: "queue.Queue[str | None]" = queue.Queue()
    t = threading.Thread(target=player_worker, args=(audio_q,), daemon=True)
    t.start()
    buf = ""
    reponse = ""
    stream = chat(
        model=MODEL,
        messages=history,
        stream=True,
    )
    for chunk in stream:
        token = chunk.get("message", {}).get("content", "")
        if not token:
            continue
        buf += token
        reponse += token
        reponse += " "
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
    history.append({"role": "assistant", "content": reponse.strip()})
    reponse = ""


if __name__ == "__main__":
    waiting_message()