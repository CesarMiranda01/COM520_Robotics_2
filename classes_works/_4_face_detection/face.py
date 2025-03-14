import cv2

cap = cv2.VideoCapture(1)  # Usa 0 si solo tienes una cámara

if not cap.isOpened():
    print("❌ No se pudo acceder a la cámara")
    exit()

caras_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

while True:
    ret, frame = cap.read()

    if not ret or frame is None:
        print("❌ No se pudo capturar el fotograma")
        break

    # Convertir a escala de grises
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detección de caras
    caras = caras_cascade.detectMultiScale(gris, 1.3, 5)

    # Dibujar rectángulos en las caras detectadas
    for (x, y, w, h) in caras:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("Detección de Rostros", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
