import cv2
import numpy as np
from Servo import Servo

# Uso del codigo
hombro = Servo(22)
codo = Servo(17)
wirst = Servo(18)
garra = Servo(27)

def inicial():
	hombro.move_to_angle(90)
	codo.move_to_angle(35)
	wirst.move_to_angle(90)
	garra.move_to_angle(0)

def abrirGarra():
	garra.smooth_move(53,0)

def cerrarGarra():
	garra.smooth_move(0,53)

def agarrarIzquierda():
	hombro.smooth_move(90,115)
	codo.smooth_move(35,130)
	wirst.smooth_move(90,20)
	cerrarGarra()
	wirst.smooth_move(20,90)
	hombro.smooth_move(115,90)
	codo.smooth_move(130,35)
	abrirGarra()

def agarrarMedio():
	hombro.smooth_move(90,80)
	codo.smooth_move(35,130)
	wirst.smooth_move(90,20)
	cerrarGarra()
	wirst.smooth_move(20,90)
	hombro.smooth_move(80,90)
	codo.smooth_move(130,35)
	abrirGarra()

def agarrarDerecha():
	hombro.smooth_move(90,40)
	codo.smooth_move(35,130)
	wirst.smooth_move(90,20)
	cerrarGarra()
	wirst.smooth_move(20,90)
	hombro.smooth_move(40,90)
	codo.smooth_move(130,35)
	abrirGarra()

LOWER_COLOR = np.array([35, 100, 100])  # Ajusta segun sea necesario
UPPER_COLOR = np.array([85, 255, 255])

# Funcion para controlar el brazo con la ubicacion relativa del objeto
def control_robot_arm(position):
    if position == 'Izquierda':
        agarrarIzquierda()
        inicial()
    if position == 'Derecha':
        agarrarDerecha()
        inicial()
    if position == 'Centro':
        agarrarMedio()
        inicial()
inicial()
# Inicializar la camara
cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_width = frame.shape[1]  # Obtener el ancho del frame
        left_threshold = frame_width // 3
        right_threshold = 2 * frame_width // 3

        # Convertir a HSV y aplicar mascara de color
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, LOWER_COLOR, UPPER_COLOR)
        
        # Encontrar contornos del objeto detectado
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        object_position = None  # Inicializar variable para la posicion del objeto
        
        if contours:
            # Seleccionar el contorno ms grande
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            object_x = x + w // 2  # Coordenada X del centro del objeto
            
            # Determinar la posicin del objeto
            if object_x < left_threshold:
                object_position = "Izquierda"
            elif object_x > right_threshold:
                object_position = "Derecha"
            else:
                object_position = "Centro"
            
            # Dibujar rectangulo en el objeto detectado (verde) y un cuadro azul
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.rectangle(frame, (x - 10, y - 10), (x + w + 10, y + h + 10), (255, 0, 0), 2)  # Cuadro azul
            cv2.putText(frame, f"{object_position}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            print(f"Modo Bsqueda - Posicin: {object_position}")
        
        # Verificar si la tecla 'a' fue presionada y hay un objeto detectado
        key = cv2.waitKey(1) & 0xFF
        if key == ord('a') and object_position is not None:
            print("Tecla 'a' presionada, cambiando a modo accion...")
            control_robot_arm(object_position)
        
        # Mostrar la imagen
        cv2.imshow("Frame", frame)
        
        # Salir con la tecla 'q'
        if key == ord('q'):
            print("Saliendo del programa...")
            break
finally:
    cap.release()
    hombro.cleanup()
    cv2.destroyAllWindows()

