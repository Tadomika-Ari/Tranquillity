import cv2
import numpy as np

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def mosaic(img, block_size=15):
    h, w = img.shape[:2]
    if h == 0 or w == 0:
        return img
    small = cv2.resize(img, (max(1, w // block_size), max(1, h // block_size)),
                       interpolation=cv2.INTER_LINEAR)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

def apply_mosaic_face(frame, x, y, w, h, block_size=15):
    x, y = max(0, x), max(0, y)
    x2 = min(frame.shape[1], x + w)
    y2 = min(frame.shape[0], y + h)
    face_roi = frame[y:y2, x:x2]
    frame[y:y2, x:x2] = mosaic(face_roi, block_size)
    return frame

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in faces:
        frame = apply_mosaic_face(frame, x, y, w, h, block_size=20)

    cv2.imshow('Mosaic', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()