import cv2
import mediapipe as mp
import math
import os
import torch
import torch.nn as nn
import numpy as np
import wave
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from piper import PiperVoice
import subprocess
import threading
import queue
import tempfile

MODEL_FILE = "model/gesture_detection/gesture_model.pth"
VOICE_PATH = "model/tts/glados/fr_FR-glados-medium.onnx"


# ---- Neural network definition (same as training) ----
class GestureNet(nn.Module):
    def __init__(self, input_size, num_classes):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes)
        )

    def forward(self, x):
        return self.net(x)

# ---- Normalize landmarks (MUST match dataset script) ----
def normalize_landmarks(landmarks):
    wrist = landmarks[0]
    norm = []
    for lm in landmarks:
        norm.append(lm.x - wrist.x)
        norm.append(lm.y - wrist.y)
        norm.append(lm.z - wrist.z)

    max_dist = 0
    for i in range(0, len(norm), 3):
        d = math.sqrt(norm[i]**2 + norm[i+1]**2 + norm[i+2]**2)
        if d > max_dist:
            max_dist = d

    if max_dist > 0:
        norm = [v / max_dist for v in norm]

    return np.array(norm, dtype=np.float32)

def speak(voice, text: str):
    def _run():
        fd, path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        with wave.open(path, "wb") as wav_file:
            voice.synthesize_wav(text, wav_file)
        subprocess.run(["mpv", "--no-terminal", "--really-quiet", path])
        os.remove(path)
    threading.Thread(target=_run, daemon=True).start()

def main():
    # ---- Load trained model ----
    checkpoint = torch.load(MODEL_FILE, weights_only=False)
    num_classes = len(checkpoint["label_encoder"])
    input_size = 63  # 21 landmarks * 3 coords

    model = GestureNet(input_size, num_classes)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    labels = checkpoint["label_encoder"]  # original gesture IDs

    # ---- MediaPipe setup ----
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'model', 'hand_detection', 'hand_landmarker.task')

    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.9
    )

    detector = vision.HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(2)

    voice = PiperVoice.load(VOICE_PATH)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        result = detector.detect(mp_image)

        if result.hand_landmarks:
            hand_landmarks = result.hand_landmarks[0]

            # draw landmarks
            for lm in hand_landmarks:
                x = int(lm.x * w)
                y = int(lm.y * h)
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

            # ---- Predict gesture ----
            norm = normalize_landmarks(hand_landmarks)
            inp = torch.tensor(norm).unsqueeze(0)

            with torch.no_grad():
                out = model(inp)
                probs = torch.softmax(out, dim=1)
                conf, pred = torch.max(probs, dim=1)

            gesture_id = labels[pred.item()]
            confidence = conf.item()

            if confidence > 0.7:
                text = f"Gesture: {gesture_id} ({confidence*100:.1f}%)"
                speak(voice, "trouver")
            else:
                text = "Gesture: ?"

            cv2.putText(frame, text, (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Hand Gesture AI", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()