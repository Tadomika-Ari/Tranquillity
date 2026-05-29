import cv2
from ultralytics import YOLO
import wave
from piper import PiperVoice

def Yolo():
    model = YOLO('model/yolo/yolov8n.pt')  
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erreur : impossible d'ouvrir la webcam")
        return
    print("Détection avec YOLO + PyTorch")
    print("Appuyez sur 'q' pour quitter")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        results = model(frame, verbose=False)
        annotated_frame = results[0].plot()
    
        cv2.imshow('YOLO Detection', annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    Yolo()
