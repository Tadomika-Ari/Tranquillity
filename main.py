import json
import queue
import sys
import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel
import yaml
from rapidfuzz import fuzz
import random
from piper import PiperVoice
import queue
import threading
import subprocess
import tempfile
import os
import wave


SetLogLevel(-1)

VOICE_PATH = "model/tts/glados/fr_FR-glados-medium.onnx"
MODEL_PATH = "model/vosk/vosk-model-small-fr/vosk-model-small-fr-0.22"
SAMPLE_RATE = 16000
BLOCK_SIZE = 4000

audio_queue = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(bytes(indata))

def check_respons(dico, text):
    best_score = 0
    best_entry = None
    for entry in dico:
        for trigger in entry["trigger"]:
            score = fuzz.partial_ratio(trigger.lower(), text)
            print(score)
            if score > best_score:
                best_score = score
                best_entry = entry
    if best_score > 80 and best_entry:
        return random.choice(best_entry["respons"])
    return None

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

def main():
    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    on_use = False

    with open("test.yaml", "r") as file:
        dico = yaml.safe_load(file)
    print(dico)
    print("\n")

    # init phase for tts (for test)
    voice = PiperVoice.load(VOICE_PATH)

    print("En écoute... (Ctrl+C pour arrêter)")

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        while True:
            data = audio_queue.get()
            audio_q: "queue.Queue[str | None]" = queue.Queue()
            t = threading.Thread(target=player_worker, args=(audio_q,), daemon=True)
            t.start()
            
            if rec.AcceptWaveform(data) and on_use == False:
                on_use = True
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                if text:
                    print(f"[final] {text}")
                    print("\n")
                    text_lower = text.lower()
                    respons = check_respons(dico, text_lower)
                    print(respons)
                    if respons:
                        fd, path = tempfile.mkstemp(prefix="tts_", suffix=".wav")
                        os.close(fd)
                        with wave.open(path, "wb") as wav_file:
                            voice.synthesize_wav(respons, wav_file)
                        audio_q.put(path)


            else:
                partial = json.loads(rec.PartialResult())
                p = partial.get("partial", "").strip()
            audio_q.put(None)
            t.join()
            on_use = False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nArrêt.")
