#include <Pixy2.h>

class PixyTracker {
private:
    Pixy2 pixy;

    int windowSize;   // Tamaño del filtro de suavizado
    int minWidth;     // Tamaño mínimo de objeto válido
    int maxWidth;     // Tamaño máximo antes de ignorar
    int maxMisses;    // Frames sin detección antes de detener

    int *xValues;     // Buffer dinámico para suavizar X
    int index;
    int missCount;

    // Método de suavizado (Promedio Móvil)
    int smoothX(int newX) {
        xValues[index] = newX;
        index = (index + 1) % windowSize;

        int sum = 0;
        for (int i = 0; i < windowSize; i++) {
            sum += xValues[i];
        }
        return sum / windowSize;
    }

public:
    // Constructor con parámetros configurables (con valores por defecto)
    PixyTracker(int _windowSize = 5, int _minWidth = 10, int _maxWidth = 200, int _maxMisses = 10) 
        : windowSize(_windowSize), minWidth(_minWidth), maxWidth(_maxWidth), maxMisses(_maxMisses), index(0), missCount(0) {
        
        // Crear el buffer dinámico con el tamaño de windowSize
        xValues = new int[windowSize];
        for (int i = 0; i < windowSize; i++) {
            xValues[i] = 0;
        }
    }

    // Destructor para liberar memoria
    ~PixyTracker() {
        delete[] xValues;
    }

    void begin() {
        pixy.init();
    }

    // Método para obtener la coordenada X del objeto más grande en el eje X
    int getSmoothedX() {
        pixy.ccc.getBlocks();

        if (pixy.ccc.numBlocks > 0) {
            int maxWidthFound = 0;
            int targetX = 0;

            for (int i = 0; i < pixy.ccc.numBlocks; i++) {
                int xRaw = pixy.ccc.blocks[i].m_x;
                int width = pixy.ccc.blocks[i].m_width;

                // Filtrar objetos demasiado pequeños o demasiado grandes
                if (width < minWidth || width > maxWidth) {
                  missCount++;
                    continue;
                }

                // Seleccionar el objeto con el mayor ancho
                if (width > maxWidthFound) {
                    maxWidthFound = width;
                    targetX = xRaw;
                }
            }

            if (maxWidthFound > 0) { // Se encontró un objeto válido
                missCount = 0;  // 🔹 Reiniciamos el contador porque sí hay detección

                int xMapped = map(targetX, 0, 316, -100, 100);
                return smoothX(xMapped); // Retorna el valor suavizado
            }
        } else {
            missCount++;  // 🔹 Aumentamos el contador si no se detecta nada
        }

        // Si ha fallado demasiadas veces, detener el coche
        if (missCount >= maxMisses) {
            return 999;  // Código especial para detenerse
        }

        return 0;  // Mantiene el último valor si sigue sin detectar
    }
};
