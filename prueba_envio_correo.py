# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 14:43:12 2024

@author: angperilla
"""

import win32com.client as win32
import logging

# Configurar el registro de eventos para archivo y consola
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Crear un manejador para la consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Crear un manejador para el archivo de log
file_handler = logging.FileHandler('envio_correos.log')
file_handler.setLevel(logging.INFO)

# Crear un formato común para ambos manejadores
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Añadir los manejadores al logger si no han sido añadidos previamente
if not logger.hasHandlers():
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

# Prueba para verificar la configuración de Outlook
try:
    # Crear un objeto de la aplicación Outlook
    outlook = win32.Dispatch('outlook.application')
    logger.info("Outlook está configurado correctamente.")

    # Crear un nuevo correo
    mail = outlook.CreateItem(0)
    mail.To = "angperilla@segurosmundial.com.co" 
    mail.Subject = "Prueba de configuración de Outlook"
    mail.Body = "Este es un correo de prueba para verificar la configuración de Outlook."
    
    # Enviar el correo
    mail.Send()
    logger.info("Correo de prueba enviado correctamente.")

except Exception as e:
    # Registrar un error si ocurre un problema
    logger.error(f"Error al interactuar con Outlook: {e}")
