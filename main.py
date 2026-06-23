import json
import queue
import sys
import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel
import yaml
from rapidfuzz import fuzz
import random

SetLogLevel(-1)  # Supprime les logs verbeux de Vosk

MODEL_PATH = "model/vosk/vosk-model-small-fr/vosk-model-small-fr-0.22"  # adapte le chemin
SAMPLE_RATE = 16000
BLOCK_SIZE = 4000

audio_queue = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(bytes(indata))

def check_respons(dico, text):
    best_score = 0
    for entry in dico:
        for trigger in entry["trigger"]:
            score = fuzz.partial_ratio(text, trigger)
            if score > best_score:
                best_score = score
    if best_score > 70:
        return random.choice(entry["respons"])

def main():
    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, SAMPLE_RATE)

    with open("test.yaml", "r") as file:
        dico = yaml.safe_load(file)
    print(dico)
    print("\n")

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
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                if text:
                    print(f"[final] {text}")
                    print("\n")
                    respons = check_respons(dico, text)
                    print(respons)
            else:
                partial = json.loads(rec.PartialResult())
                p = partial.get("partial", "").strip()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nArrêt.")
