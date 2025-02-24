import yaml
import tkinter as tk
import time
import threading
import subprocess
import logging
from datetime import datetime

# Configuración del log
logging.basicConfig(filename="simulador.log", level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Nombres de los botones en orden de izquierda a derecha
boton_nombres = ["0", "1", "2", "3", "4", "⯀", "⧫", "+", "Δ"]

def cargar_yaml():
    try:
        with open("C:/TaxiEmulador/TestFer/taxi.yml", "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logging.error("Archivo taxi.yml no encontrado.")
        return []  # Si no existe, retorna una lista vacía

def alternar_boton(idx):
    for i in range(len(botones)):
        botones[i] = 0
        botones_ui[i].config(bg="red")
    
    botones[idx] = 1
    botones_ui[idx].config(bg="green")
    
    hora_actual = datetime.now().strftime("%H:%M:%S")
    historico.append(f"{hora_actual} - Botón '{boton_nombres[idx]}' presionado")
    actualizar_historial()
    logging.info(f"Botón '{boton_nombres[idx]}' presionado.")

def actualizar_historial():
    historial_lista.delete(0, tk.END)
    for item in historico:
        historial_lista.insert(tk.END, item)
    historial_lista.yview_moveto(1)

def ejecutar_secuencia():
    for secuencia in secuencias:
        if 'button' in secuencia:
            button_states = secuencia['button']
            for idx, state in enumerate(button_states):
                if state == 1:
                    root.after(0, alternar_boton, idx)
                    time.sleep(1)  # Simula el tiempo entre pulsaciones
        if 'wait' in secuencia:
            logging.info(f"Esperando {secuencia['wait']} segundos.")
            time.sleep(secuencia['wait'])

def iniciar_todo():
    logging.info("Iniciando Simulación y NMEA Generator.")
    threading.Thread(target=ejecutar_secuencia, daemon=True).start()
    parametros_nmea = ["python", "NMEAGenerator.py", "C:/TaxiEmulador/TestFer/ruta.csv", "C:/TaxiEmulador/TestFer/taxi.yml", 
                        "--taxi_port=COM4", "--output_trace=1", "--socket_IP=172.17.2.112", 
                        "--socket_PORT=3482", "--repeat=50"]
    logging.info(f'Ejecutando NMEA con {parametros_nmea}')
    subprocess.Popen(parametros_nmea, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

data = cargar_yaml()
secuencias = data if isinstance(data, list) else []

botones = [0] * 9
historico = []

root = tk.Tk()
root.title("Simulador de Taxímetro URBA")

etiqueta_carrusel = tk.Label(root, text="   PRIME TEST EMULADOR   ", font=("Arial", 16, "bold"))
etiqueta_carrusel.grid(row=0, column=0, columnspan=9, pady=10)

botones_ui = []
for i, nombre in enumerate(boton_nombres):
    btn = tk.Button(root, text=nombre, width=10, height=3, bg="red", command=lambda i=i: alternar_boton(i))
    btn.grid(row=1, column=i, padx=5, pady=5)
    botones_ui.append(btn)

frame_historial = tk.Frame(root)
frame_historial.grid(row=2, column=0, columnspan=9, pady=10)

scrollbar = tk.Scrollbar(frame_historial)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

historial_lista = tk.Listbox(frame_historial, width=50, height=10, yscrollcommand=scrollbar.set)
historial_lista.pack(side=tk.LEFT, fill=tk.BOTH)
scrollbar.config(command=historial_lista.yview)

boton_iniciar_todo = tk.Button(root, text="Iniciar Simulación y NMEA", command=iniciar_todo)
boton_iniciar_todo.grid(row=3, column=0, columnspan=9, pady=5)

actualizar_historial()

logging.info("Aplicación iniciada correctamente.")
root.mainloop()
