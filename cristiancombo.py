import os
import sys
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor

# --- COLORES ANSI (Bandera de Colombia y Estética Hacker) ---
AMARILLO = "\033[1;33m"
AZUL = "\033[1;34m"
ROJO = "\033[1;31m"
VERDE = "\033[1;32m"
CYAN = "\033[1;36m"
BLANCO = "\033[1;37m"
RESET = "\033[0m"

# --- DATOS LATINOS PRECARGADOS ---
NOMBRES = [
    "Carlos", "Santiago", "Mateo", "Alejandro", "Daniel", "David", "Juan", "Jose",
    "Sebastian", "Samuel", "Lucas", "Nicolas", "Gabriel", "Mateo", "Angel", "Diego",
    "Maria", "Ana", "Sofia", "Valentina", "Camila", "Isabella", "Lucia", "Mariana",
    "Gabriela", "Elena", "Valeria", "Catalina", "Martina", "Victoria", "Sara", "Daniela"
]

APELLIDOS = [
    "Garcia", "Rodriguez", "Gonzalez", "Martinez", "Lopez", "Gonzalez", "Perez",
    "Sanchez", "Ramirez", "Torres", "Flores", "Rivera", "Gomez", "Diaz", "Cruz",
    "Morales", "Reyes", "Gutierrez", "Ortiz", "Silva", "Rojas", "Medina", "Vargas",
    "Castillo", "Jimenez", "Moreno", "Herrera", "Munoz", "Castro", "Alvarez", "Romero"
]

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def efecto_hacker(texto):
    for char in texto:
        sys.stdout.write(f"{VERDE}{char}{RESET}")
        sys.stdout.flush()
        time.sleep(0.01)
    print()

def mostrar_banner():
    limpiar_pantalla()
    print(f"""
{AMARILLO}  ██████╗ ██████╗ ██╗███████╗████████╗██╗ █████╗ ███╗   ██╗
{AMARILLO} ██╔════╝ ██╔══██╗██║██╔════╝╚══██╔══╝██║██╔══██╗████╗  ██║
{AZUL} ██║      ██████╔╝██║███████╗   ██║   ██║███████║██╔██╗ ██║
{AZUL} ██║      ██╔══██╗██║╚════██║   ██║   ██║██╔══██║██║╚██╗██║
{ROJO} ╚██████╗ ██║  ██║██║███████║   ██║   ██║██║  ██║██║ ╚████║
{ROJO}  ╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝   ╚═╝   ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
{BLANCO}        [ C R I S T I A N - COMBO GENERATOR v2.0 ]
{AZUL}========================================================{RESET}
""")

def generar_password(longitud):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(random.choice(chars) for _ in range(longitud))

def worker_generacion(cantidad_por_hilo, tipo, longitud_pass, resultados, lock):
    locales = set()
    while len(locales) < cantidad_por_hilo:
        n1 = random.choice(NOMBRES).lower()
        n2 = random.choice(NOMBRES).lower()
        apellido = random.choice(APELLIDOS).lower()
        
        if tipo == 1: # nombre:nombre
            usuario = f"{n1}:{n2}"
        elif tipo == 2: # nombre+1234
            sufijo = ''.join(random.choices("0123456789", k=4))
            usuario = f"{n1}{sufijo}"
        elif tipo == 3: # nombre+apellido
            usuario = f"{n1}.{apellido}"
        else:
            usuario = f"{n1}"

        pwd = generar_password(longitud_pass)
        combos = f"{usuario}:{pwd}"
        locales.add(combos)
        
    with lock:
        resultados.update(locales)

def menu_interactivo():
    while True:
        mostrar_banner()
        print(f"{CYAN}[1]{RESET} Generar Combos U:P (Nombre : Nombre)")
        print(f"{CYAN}[2]{RESET} Generar Combos U:P (Nombre + Números)")
        print(f"{CYAN}[3]{RESET} Generar Combos U:P (Nombre + Apellido)")
        print(f"{CYAN}[4]{RESET} Salir")
        print(f"{AZUL}========================================================{RESET}")
        
        try:
            opcion = int(input(f"{AMARILLO}Seleccione una opción: {RESET}"))
            if opcion == 4:
                print(f"\n{VERDE}¡Saliendo del sistema! Hasta luego.{RESET}")
                break
            if opcion not in [1, 2, 3]:
                print(f"{ROJO}Opción inválida.{RESET}")
                time.sleep(1)
                continue

            cantidad = int(input(f"{AMARILLO}Cantidad total de combos a generar: {RESET}"))
            longitud_pass = int(input(f"{AMARILLO}Longitud de la contraseña (ej. 6-12): {RESET}"))
            
            print(f"\n{VERDE}[+] Iniciando motores multihilo (Ultra Rápido)...{RESET}")
            
            resultados = set()
            lock = threading.Lock()
            hilos = 8
            cant_por_hilo = max(1, cantidad // hilos)
            
            inicio = time.time()
            with ThreadPoolExecutor(max_workers=hilos) as executor:
                futures = [executor.submit(worker_generacion, cant_por_hilo, opcion, longitud_pass, resultados, lock) for _ in range(hilos)]
                
                # Barra de progreso en tiempo real
                while any(f.running() for f in futures):
                    actual = len(resultados)
                    porcentaje = min(100, int((actual / cantidad) * 100))
                    sys.stdout.write(f"\r{CYAN}[Progreso]: {porcentaje}% ({actual}/{cantidad}){'█' * (porcentaje // 5)}{RESET}   ")
                    sys.stdout.flush()
                    time.sleep(0.1)

            # Ajuste exacto si faltaron por redondeo
            while len(resultados) < cantidad:
                n1 = random.choice(NOMBRES).lower()
                n2 = random.choice(NOMBRES).lower()
                apellido = random.choice(APELLIDOS).lower()
                if opcion == 1: u = f"{n1}:{n2}"
                elif opcion == 2: u = f"{n1}{random.randint(1000,9999)}"
                else: u = f"{n1}.{apellido}"
                resultados.add(f"{u}:{generar_password(longitud_pass)}")

            # Limitar a la cantidad exacta pedida y eliminar duplicados de forma segura
            lista_final = list(resultados)[:cantidad]
            
            # --- GUARDADO AUTOMÁTICO EN RUTA ANDROID (/sdcard/) ---
            ruta_carpeta = "/sdcard/CombosCristian"
            if not os.path.exists(ruta_carpeta):
                os.makedirs(ruta_carpeta)
                
            nombre_archivo = f"combos_{int(time.time())}.txt"
            ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)
            
            with open(ruta_completa, "w", encoding="utf-8") as f:
                f.write("\n".join(lista_final))
                
            print(f"\n\n{VERDE}[✔] ¡Generación completada con éxito!{RESET}")
            print(f"{AMARILLO}[📂] Archivo guardado en: {ruta_completa}{RESET}")
            print(f"{CYAN}[⏱️] Tiempo transcurrido: {round(time.time() - inicio, 2)} segundos{RESET}")
            
            input(f"\n{BLANCO}Presiona ENTER para volver al menú...{RESET}")
            
        except ValueError:
            print(f"{ROJO}[!] Error: Por favor ingrese valores numéricos válidos.{RESET}")
            time.sleep(1.5)
        except Exception as e:
            print(f"{ROJO}[!] Ocurrió un error: {e}{RESET}")
            time.sleep(2)

if __name__ == "__main__":
    menu_interactivo()
