import cv2
import mediapipe as mp
import math
import os
import csv
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

DATASET_FILE = "model/gesture_detection/gesture_dataset.csv"

def normalize_landmarks(landmarks):
    # Use wrist (0) as origin
    wrist = landmarks[0]
    norm = []
    for lm in landmarks:
        norm.append(lm.x - wrist.x)
        norm.append(lm.y - wrist.y)
        norm.append(lm.z - wrist.z)

    # Scale so max distance = 1
    max_dist = 0
    for i in range(0, len(norm), 3):
        d = math.sqrt(norm[i]**2 + norm[i+1]**2 + norm[i+2]**2)
        if d > max_dist:
            max_dist = d

    if max_dist > 0:
        norm = [v / max_dist for v in norm]

    return norm

def main():
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

    cap = cv2.VideoCapture(0)

    print("Press number keys to record a gesture:")
    print("1 = fist")
    print("2 = open hand")
    print("3 = thumbs up")
    print("4 = ok")
    print("5 = Wii Pointer")
    print("6 = thumb+smol")
    print("ESC = quit")

    with open(DATASET_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)

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

                for lm in hand_landmarks:
                    x = int(lm.x * w)
                    y = int(lm.y * h)
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

                norm_landmarks = normalize_landmarks(hand_landmarks)

            cv2.imshow("Dataset Collector", frame)
            key = cv2.waitKey(1) & 0xFF

            # ESC quits
            if key == 27:
                break

            # Save on key press 1-9
            if key >= ord('1') and key <= ord('9'):
                if result.hand_landmarks:
                    label = int(chr(key))
                    row = norm_landmarks + [label]
                    writer.writerow(row)
                    print(f"Saved sample for gesture {label}")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()