from __future__ import annotations
from pathlib import Path
import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os


def visualize(frame_bgr: np.ndarray, detection_result) -> np.ndarray:
    if detection_result is None:
        return frame_bgr

    detections = getattr(detection_result, "detections", None) or []
    for detection in detections:
        bbox = getattr(detection, "bounding_box", None)
        if bbox is None:
            continue

        x = int(getattr(bbox, "origin_x", 0))
        y = int(getattr(bbox, "origin_y", 0))
        w = int(getattr(bbox, "width", 0))
        h = int(getattr(bbox, "height", 0))

        x1, y1 = max(0, x), max(0, y)
        x2, y2 = max(0, x + w), max(0, y + h)
        cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)

        label = "objet"
        score = None
        categories = getattr(detection, "categories", None) or []
        if categories:
            cat0 = categories[0]
            label = getattr(cat0, "category_name", None) or getattr(cat0, "display_name", None) or label
            score = getattr(cat0, "score", None)

        text = f"{label}{'' if score is None else f' {score:.2f}'}"
        cv2.putText(
            frame_bgr,
            text,
            (x1, max(0, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

    return frame_bgr


def cv2_imshow(image_bgr: np.ndarray, window_name: str = "Object detection") -> None:
    cv2.imshow(window_name, image_bgr)

def object() -> None:
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'model', 'object_detection', 'efficientdet_lite0.tflite')
    base_options = python.BaseOptions(model_asset_path=str(model_path))
    options = vision.ObjectDetectorOptions(base_options=base_options, score_threshold=0.3)
    detector = vision.ObjectDetector.create_from_options(options)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erreur : impossible d'ouvrir la webcam")
        return

    print("Object detection : appuie sur 'q' pour quitter")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

            detection_result = detector.detect(mp_image)

            annotated = visualize(frame.copy(), detection_result)
            cv2_imshow(annotated)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()