# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 12:25:14 2024

@author: angperilla
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import subprocess
import pandas as pd
import os
import time
from concurrent.futures import ThreadPoolExecutor



# Obtener el directorio actual
current_dir = os.getcwd()
script_name_1 = "extracto_ips_masivo.py"
script_path_1 = os.path.join(current_dir, script_name_1)


# Obtener el directorio actual
current_dir = os.getcwd()
script_name_2 = "envio_correos_masivo_generico.py"
script_path_2 = os.path.join(current_dir, script_name_2)


# Función para contar archivos Excel en el directorio EXCEL
def contar_archivos_excel():
    ruta_excel = os.path.join(os.getcwd(), 'EXCEL')
    if not os.path.exists(ruta_excel):
        return 0  # Si no existe la carpeta EXCEL
    archivos_excel = [f for f in os.listdir(ruta_excel) if f.endswith('.xlsx')]
    return len(archivos_excel)

# Función para contar registros en el archivo Destinatarios.xlsx
def contar_destinatarios():
    ruta_destinatarios = os.path.join(os.getcwd(), 'data', 'Destinatarios.xlsx')
    if not os.path.exists(ruta_destinatarios):
        return 0  # Si no existe el archivo de destinatarios
    df_destinatarios = pd.read_excel(ruta_destinatarios)
    return len(df_destinatarios)

# Función para ejecutar el Script 1 (Generar Extractos)
def ejecutar_script_1():
    try:
        start_time = time.time()
        subprocess.run(["python", script_path_1], check=True, 
            creationflags=subprocess.CREATE_NO_WINDOW)
        end_time = time.time()
        duration = (end_time - start_time) / 60  # Duración en minutos
        return duration
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al generar los extractos: {str(e)}")
        return None

# Función para ejecutar el Script 2 (Enviar Correos)
def ejecutar_script_2():
    try:
        start_time = time.time()
        subprocess.run(["python", script_path_2], check=True,
            creationflags=subprocess.CREATE_NO_WINDOW)
        end_time = time.time()
        duration = (end_time - start_time) / 60  # Duración en minutos
        return duration
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al enviar los correos: {str(e)}")
        return None

# Función para mostrar resultados después de ejecutar el Script 2
def mostrar_resultados():
    start_time = time.time()
    while not os.path.exists('resultados_envio_correos.csv'):
        if time.time() - start_time > 120:  # Timeout después de 30 segundos
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
        duration1 = future1.result()
        if duration1 is not None:
            progress_bar['value'] = 50
            status_label.config(text="Generación de Extractos Completado.")
            root.update_idletasks()
            
            # Mostrar el conteo de archivos Excel
            total_archivos_excel = contar_archivos_excel()
            messagebox.showinfo("Conteo de Archivos Excel", f"Total Extractos Generados: {total_archivos_excel}")
            
            # Mostrar el conteo de destinatarios
            total_destinatarios = contar_destinatarios()
            messagebox.showinfo("Conteo de Destinatarios", f"Total de destinatarios: {total_destinatarios}")
            
            future2 = executor.submit(ejecutar_script_2)
            duration2 = future2.result()
            if duration2 is not None:
                progress_bar['value'] = 100
                status_label.config(text="Envío de Correos Completado.")
                mostrar_resultados()
                
                # Mostrar tiempos de procesamiento
                total_duration = duration1 + duration2
                messagebox.showinfo("Tiempos de Procesamiento", f"Generación de Extractos: {duration1:.2f} minutos\nEnvío de Correos: {duration2:.2f} minutos\nTiempo Total: {total_duration:.2f} minutos")

root = tk.Tk()
root.title("Generación y Envío de Extractos IPS")
root.geometry("415x380")
# Evitar que la ventana se pueda redimensionar
root.resizable(False, False)

# ------------------------------ Background ------------------------------- #

# Crear un Canvas para la imagen de fondo
canvas = tk.Canvas(root, width=415, height=380)
canvas.pack(fill="both", expand=True)

# # Cargar la imagen de fondo
path_imagen = os.path.join(os.getcwd(), 'data', 'BG.jpg')
imagen_pil = Image.open(path_imagen)


def resize_image(event=None):
    # Obtener el tamaño de la ventana
    width = root.winfo_width()
    height = root.winfo_height()
    
    # Redimensionar la imagen al tamaño de la ventana
    nueva_imagen = imagen_pil.resize((width, height), Image.LANCZOS)
    photo = ImageTk.PhotoImage(nueva_imagen)
    canvas.create_image(0, 0, image=photo, anchor="nw")
    canvas.image = photo  # Guardar una referencia a la imagen para evitar que se destruya por el recolector de basura

# Llamar a la función de redimensionamiento al inicio
root.after(100, resize_image)

# Crear un Frame para los widgets
frame = ttk.Frame(canvas, padding="10", style='TFrame')
canvas.create_window(200, 200, window=frame)

# ------------------------------------------------------------------------- #

# Crear un Frame para los widgets
frame = tk.Frame(canvas, bg='white', bd=2)
frame.place(relx=0.5, rely=0.5, anchor="center")

# Añadir widgets al frame usando pack
title_label = tk.Label(frame, text="Generación y Envío de Extractos IPS", font=('Helvetica', 16, 'bold'))
title_label.pack(pady=40)

run_scripts_button = tk.Button(frame, text="Iniciar Proceso Completo", font=('Helvetica', 12), bg='#4CAF50', fg='white', command=ejecutar_scripts)
run_scripts_button.pack(padx=10, pady=10)

progress_bar = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(padx=10, pady=10)

status_label = tk.Label(frame, text="Estado: Esperando", bg='white', font=('Helvetica', 13))
status_label.pack(padx=10, pady=10)

enviados_label = tk.Label(frame, text="Total Correos Enviados: 0", bg='white', font=('Helvetica', 12, 'bold'))
enviados_label.pack(padx=10, pady=10)

fallidos_label = tk.Label(frame, text="Total Correos Fallidos: 0", bg='white', font=('Helvetica', 12, 'bold'))
fallidos_label.pack(padx=10, pady=10)

root.mainloop()