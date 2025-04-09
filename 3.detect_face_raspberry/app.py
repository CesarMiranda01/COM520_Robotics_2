import cv2
import os

# Evitar problemas con Qt en Raspberry Pi
os.environ["QT_QPA_PLATFORM"] = "xcb"

# Cargar el clasificador de Haar para la deteccion de rostros
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Iniciar captura de video desde la camara
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: No se pudo abrir la camara.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al capturar el frame de la camara.")
        break
    
    # Convertir a escala de grises para la deteccion de caras
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detectar caras en la imagen
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Dibujar un rectangulo rojo alrededor de las caras detectadas
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Color rojo (BGR)

    cv2.imshow("USFX - Deteccion de Rostros", frame)
    
    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
