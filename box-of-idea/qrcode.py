import cv2
import numpy as np
import webbrowser

cap = cv2.VideoCapture(2)
detector = cv2.QRCodeDetector()
a = None

while (True):
    _, image = cap.read()
    image = cv2.flip(image, 1)
    data, one, _ = detector.detectAndDecode(image)
    if one is not None:
        corners = one.astype(int).reshape((-1, 1, 2))
        cv2.polylines(image, [corners], isClosed=True, color=(0, 255, 0), thickness=3)
        label = data if data else "QR détecté"
    if data:
        a = data
        cv2.imshow('qrcode', image)
        cv2.waitKey(500)
        print("trouver !")
    cv2.imshow('qrcode', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
print("ok !")
if a:
    webbrowser.open(str(a))
cap.release()
cv2.destroyAllWindows()
