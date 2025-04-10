<h1 align="center">🤖 Brazo Robot</h1>

<p align="center">
    <img src="assets/resultado.gif" alt="brazo funcional" width="60%">
</p>

## 📖 Descripción
<p>Este proyecto de robótica se enfoca en la construcción e implementación de un brazo robótico inteligente. El sistema utiliza una cámara integrada para capturar imágenes en tiempo real, permitiendo identificar objetos basándose en su color RGB mediante procesamiento de imágenes realizado en una Raspberry Pi.

Una vez que el objeto ha sido identificado, se analiza su posición espacial (izquierda, centro o derecha) en el entorno de trabajo. Posteriormente, el sistema calcula y ejecuta la rotación de los servomotores para posicionar correctamente el brazo y proceder con el levantamiento preciso del objeto.</p>

## 📚 Materiales
- Webcam
- Fuente de tensión y corriente regulable 
- Raspberry Pi Foundation
- Motores servo MG995 (4 unidades)
- Cable jumper 10cm M-M, M-H, H-H
- Trupan 60cm x 60cm 3mm y 5mm
- Cierra para cortar trupan 
- Protoboard
- Tornillo M3 x 50mm (5 uds)
- Tornillo M3 x 18mm (5 uds)
- Tornillo M3 x 15mm (5 uds)
- Tornillo M3 x 12mm (6 uds)
- Tornillo M3 x 10mm (14 uds)
- Tuercas de 3mm
- Taladro 
- Broca para madera 3mm 

## 🔗 Enlaces De Referencia
<p>
  ⬇ <a href="./assets/plano.pdf" target="_blank">Archivo PDF de diseño</a>
</p>

(Video) Construcción del brazo<br>

<p align="center">
    <a href="https://www.youtube.com/watch?v=7t7-bZ4KnVc">
        <img src="assets/youtube.png" alt="video" width="60%" target="_blank">
    </a>
</p>

<p align="center">
    <img src="assets/piezas.gif" alt="construccion" width="60%">
</p>

## 🧾 Requisitos de raspberry
- python 10+

## ✨ Cómo usar
Sigue estos pasos para ejecutar la aplicación:

1. Clona el repositorio ejecutando el siguiente comando:
    ```bash
    $ git clone https://github.com/CesarMiranda01/COM520_Robotics_2/tree/main/4.arm_raspberry
    ```
2. Ingresa a la carpeta ejecutando el siguiente comando:
    ```bash
    $ cd 4.arm_raspberry
    ```
3. Instala las dependencias necesarias ejecutando el siguiente comando:
    ```bash
    $ pip install -r requirements.txt
    ```
4. Inicia la aplicación con:
    ```bash
    $ python app.py
    ```
5. Debido a que la inclinación del brazo tiene límites de distancia, es necesario establecer las posiciones para izquierda, centro y derecha. Esto permitirá ubicar el objeto en uno de los puntos y garantizar que el brazo proceda a levantarlo correctamente.

6. Enfoca el área de trabajo con la cámara sobre el brazo robótico. Asegúrate de que el objeto esté visible.

7. Una vez que el área esté correctamente enfocada, presiona la tecla 'a' para que el brazo proceda a detectar, ubicar y levantar el objeto identificado.

## 🦾 Resultado
<p align="center">
    <img src="assets/prueba.gif" alt="resultado" width="60%">
</p>
