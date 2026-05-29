import cv2
import mediapipe as mp
import math
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

def main():
    cam = input("Choisie la caméra : ")
    try:
        cam_index = int(cam) if cam else 0
    except ValueError:
        cam_index = 0
    # Configuration du détecteur de mains
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'model', 'hand_detection', 'hand_landmarker.task')
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.HandLandmarkerOptions(base_options=base_options,
                                            num_hands=1,
                                            min_hand_detection_confidence=0.5,
                                            min_hand_presence_confidence=0.6,
                                            min_tracking_confidence=0.9)
    detector = vision.HandLandmarker.create_from_options(options)

    # Connexions des points de la main
    HAND_CONNECTIONS = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (0, 5), (5, 6), (6, 7), (7, 8),
        (5, 9), (9, 10), (10, 11), (11, 12),
        (9, 13), (13, 14), (14, 15), (15, 16),
        (13, 17), (17, 18), (18, 19), (19, 20),
        (0, 17)
    ]

    cap = cv2.VideoCapture(cam_index)
    try:
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except Exception:
        pass
    prev_index = None
    curr = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        
        #check on llm
        result = detector.detect(mp_image)
        if result.hand_landmarks:
            for hand_landmarks in result.hand_landmarks:
                for landmark in hand_landmarks:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                for connection in HAND_CONNECTIONS:
                    start_idx, end_idx = connection
                    start = hand_landmarks[start_idx]
                    end = hand_landmarks[end_idx]
                    start_point = (int(start.x * w), int(start.y * h))
                    end_point = (int(end.x * w), int(end.y * h))
                    cv2.line(frame, start_point, end_point, (255, 0, 0), 2)
                thumb = hand_landmarks[4]
                index = hand_landmarks[8]
                dist = math.hypot(thumb.x - index.x, thumb.y - index.y)
                print(dist)
                if dist < 0.06:
                    cv2.putText(frame, "Scroll down", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    # mouse.scroll(0, -1)
                elif dist > 0.25:
                    cv2.putText(frame, "Scroll up", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    # mouse.scroll(0, 1)
                index = hand_landmarks[0]
                curr = (index.x, index.y)
                if prev_index is not None:
                    dx = curr[0] - prev_index[0]
                    dy = curr[1] - prev_index[1]
        cv2.imshow("Hand Tracking", frame)
        prev_index = curr
        key = cv2.waitKey(1) & 0xFF
        if (key == 27):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


# class hand:

#     def __init__(self, hand, nb_hand, x, y):
#         self.hand = hand
#         self.nb_hand = nb_hand
#         self.x = x
#         self.y = y