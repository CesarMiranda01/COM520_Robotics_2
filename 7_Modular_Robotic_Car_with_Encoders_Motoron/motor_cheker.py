# motor_checker.py
# Un script de diagnóstico simple para verificar la conexión, dirección y
# respuesta del encoder de cada motor individualmente.

import time
import sys
import RPi.GPIO as GPIO
import motoron

# Importamos solo la clase Encoder, ya que no necesitamos la lógica PID aquí.
from models import Encoder

# --- Configuración ---
# Potencia a aplicar durante la prueba. Debe ser baja pero suficiente para mover la rueda.
TEST_POWER = 300
# Duración de cada prueba de giro en segundos.
TEST_DURATION = 3

# --- Script Principal de Verificación ---

if __name__ == "__main__":
    
    # Copia aquí la configuración base de tus motores desde tuner.py o main.py
    BASE_CONFIG = {
        'MOTORON_ADDR_LEFT': 16,
        'MOTORON_ADDR_RIGHT': 17,
        'MOTORS': {
            'fl': {'controller': 'left', 'id': 2, 'encoder_a': 5, 'encoder_b': 6},
            'bl': {'controller': 'left', 'id': 3, 'encoder_a': 13, 'encoder_b': 19},
            'fr': {'controller': 'right','id': 2, 'encoder_a': 26, 'encoder_b': 12},
            'br': {'controller': 'right','id': 3, 'encoder_a': 16, 'encoder_b': 20},
        }
    }

    print("--- SCRIPT DE VERIFICACIÓN DE MOTORES Y ENCODERS ---")
    print("\n¡ADVERTENCIA! Este script moverá las ruedas del robot.")
    print("Por favor, asegúrate de que el robot esté levantado y las ruedas puedan girar libremente.")
    if input("¿Estás listo para continuar? (y/n): ").lower() != 'y':
        sys.exit("Verificación cancelada.")

    try:
        GPIO.setmode(GPIO.BCM)
        mc_left = motoron.MotoronI2C(address=BASE_CONFIG['MOTORON_ADDR_LEFT'])
        mc_right = motoron.MotoronI2C(address=BASE_CONFIG['MOTORON_ADDR_RIGHT'])

        # Limpiar cualquier estado previo de los controladores
        for mc in [mc_left, mc_right]:
            mc.reinitialize()
            mc.clear_reset_flag()

        for motor_name, cfg in BASE_CONFIG['MOTORS'].items():
            print(f"\n{'='*50}\n--- PROBANDO MOTOR: {motor_name.upper()} ---\n{'='*50}")
            
            mc = mc_left if cfg['controller'] == 'left' else mc_right
            encoder = Encoder(cfg['encoder_a'], cfg['encoder_b'])
            
            # --- Prueba hacia ADELANTE ---
            input(f"Presiona Enter para probar el motor '{motor_name}' hacia ADELANTE...")
            
            pos_inicial = encoder.get_position()
            mc.set_speed(cfg['id'], TEST_POWER)
            time.sleep(TEST_DURATION)
            mc.set_speed(cfg['id'], 0)
            time.sleep(0.2) # Pausa para que el encoder se estabilice
            pos_final = encoder.get_position()
            
            delta = pos_final - pos_inicial
            
            print("\n--- RESULTADOS (ADELANTE) ---")
            print(f"Posición del encoder: Inicial={pos_inicial}, Final={pos_final}")
            print(f"Cambio en los ticks: {delta}")
            
            # Diagnóstico automático
            if delta > 10:
                print("✅ DIAGNÓSTICO: ¡CORRECTO! El motor gira hacia adelante y el encoder cuenta positivamente.")
            elif delta < -10:
                print("❌ ERROR: ¡DIRECCIÓN INVERTIDA! El motor gira hacia atrás cuando debería ir hacia adelante.")
                print("   SOLUCIÓN 1 (Encoder): Intercambia los cables A y B del encoder.")
                print("   SOLUCIÓN 2 (Motor): Intercambia los dos cables de alimentación del motor.")
            else:
                print("❌ ERROR: ¡NO HAY MOVIMIENTO o es muy poco!")
                print("   SOLUCIÓN: Verifica el cableado del motor, la alimentación, y si TEST_POWER es suficiente.")
            
            # --- Prueba hacia ATRÁS ---
            input(f"\nPresiona Enter para probar el motor '{motor_name}' hacia ATRÁS...")

            pos_inicial = encoder.get_position()
            mc.set_speed(cfg['id'], -TEST_POWER)
            time.sleep(TEST_DURATION)
            mc.set_speed(cfg['id'], 0)
            time.sleep(0.2)
            pos_final = encoder.get_position()

            delta = pos_final - pos_inicial
            
            print("\n--- RESULTADOS (ATRÁS) ---")
            print(f"Posición del encoder: Inicial={pos_inicial}, Final={pos_final}")
            print(f"Cambio en los ticks: {delta}")

            # Diagnóstico automático
            if delta < -10:
                print("✅ DIAGNÓSTICO: ¡CORRECTO! El motor gira hacia atrás y el encoder cuenta negativamente.")
            elif delta > 10:
                print("❌ ERROR: ¡DIRECCIÓN INVERTIDA! El motor gira hacia adelante cuando debería ir hacia atrás.")
                print("   Este error debería ser consistente con la prueba anterior. Revisa las soluciones de arriba.")
            else:
                print("❌ ERROR: ¡NO HAY MOVIMIENTO o es muy poco!")
                print("   Verifica el cableado y la alimentación.")

            if input("\n¿Continuar con el siguiente motor? (y/n): ").lower() != 'y':
                break

    except KeyboardInterrupt:
        print("\nVerificación interrumpida por el usuario.")
    except Exception as e:
        print(f"\nOcurrió un error inesperado: {e}")
    finally:
        print("Deteniendo todos los motores y limpiando pines GPIO...")
        # Asegurarse de que todos los motores están parados al salir
        try:
            for mc in [mc_left, mc_right]:
                for i in range(1, 4): # Suponiendo hasta 3 motores por controlador
                    mc.set_speed(i, 0)
            GPIO.cleanup()
        except Exception as final_e:
            print(f"Error durante la limpieza: {final_e}")
            GPIO.cleanup() # Intentar limpiar de todas formas