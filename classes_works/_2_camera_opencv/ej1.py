import cv2

# imagen =cv2.imread("img2.jpg", -1) # Colores
# imagen =cv2.imread("img2.jpg", 0) # Blanco y negro
imagen =cv2.imread("img/logo.png", 1) # Colores: cada pixel tiene 4 valores: rgb + alpha(transparencia)
cv2.imshow("USFX",imagen)
cv2.waitKey(0)
cv2.destroyAllWindows()