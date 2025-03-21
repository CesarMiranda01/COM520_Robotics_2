import cv2

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
    
    cv2.imshow("USFX", frame)
    
    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()