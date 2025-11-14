# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 12:25:14 2024

@author: angperilla
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import pandas as pd
import os
import time
from concurrent.futures import ThreadPoolExecutor

# Función para ejecutar el Script 1 (Generar Extractos)
def ejecutar_script_1():
    try:
        subprocess.run(["python", "extracto_ips_masivo.py"], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al generar los extractos: {str(e)}")
        return False
    return True

# Función para ejecutar el Script 2 (Enviar Correos)
def ejecutar_script_2():
    try:
        subprocess.run(["python", "envio_correos_masivo_generico.py"], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al enviar los correos: {str(e)}")
        return False
    return True

# Función para mostrar resultados después de ejecutar el Script 2
def mostrar_resultados():
    start_time = time.time()
    while not os.path.exists('resultados_envio_correos.csv'):
        if time.time() - start_time > 30:  # Timeout después de 30 segundos
            messagebox.showerror("Error", "No se encontró el archivo de resultados.")
            return
        time.sleep(1)
    
    try:
        df = pd.read_csv('resultados_envio_correos.csv')
        total_envios = len(df)
        fallidos = len(df[df['estado'] != 'Enviado'])
        total_envios = max(0, total_envios - fallidos)  # Asegurar que no sea negativo
        enviados_label.config(text=f"Total Correos Enviados: {total_envios}")
        fallidos_label.config(text=f"Total Correos Fallidos: {fallidos}")
    except FileNotFoundError:
        messagebox.showerror("Error", "No se encontró el archivo de resultados.")

# Función para manejar la ejecución de los scripts en secuencia
def ejecutar_scripts():
    progress_bar['value'] = 0
    status_label.config(text="Generando archivos...")
    root.update_idletasks()
    
    with ThreadPoolExecutor() as executor:
        future1 = executor.submit(ejecutar_script_1)
        if future1.result():
            progress_bar['value'] = 50
            status_label.config(text="Generación de Extractos Completado.")
            root.update_idletasks()
            
            future2 = executor.submit(ejecutar_script_2)
            if future2.result():
                progress_bar['value'] = 100
                status_label.config(text="Envío de Correos Completado.")
                mostrar_resultados()

root = tk.Tk()
root.title("Generación y Envío de Extractos IPS")

# Estilo moderno
style = ttk.Style()

style.configure('TButton', font=('Helvetica', 12), padding=10)
style.configure('TLabel', font=('Helvetica', 12), padding=10)
style.configure('TFrame', padding=20)

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

title_label = ttk.Label(frame, text="Generación y Envío de Extractos IPS", font=('Helvetica', 16, 'bold'))
title_label.grid(row=0, column=0, columnspan=2, pady=10)

run_scripts_button = ttk.Button(frame, text="Iniciar Proceso Completo", command=ejecutar_scripts)
run_scripts_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

progress_bar = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
progress_bar.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

status_label = ttk.Label(frame, text="Estado: Esperando")
status_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

enviados_label = ttk.Label(frame, text="Total Correos Enviados: 0")
enviados_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

fallidos_label = ttk.Label(frame, text="Total Correos Fallidos: 0")
fallidos_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()

