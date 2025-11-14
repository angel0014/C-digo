# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 12:34:29 2024

@author: angperilla
"""


import win32com.client as win32
import os

# Configuración de la cuenta de Outlook
outlook = win32.Dispatch('outlook.application')
namespace = outlook.GetNamespace("MAPI")
cuenta = None

# Buscar la cuenta genérica
for acc in namespace.Accounts:
    if acc.SmtpAddress == 'notificacionessoatmu@segurosmundial.com.co':
        cuenta = acc
        break
print(cuenta)

if cuenta is None:
    raise Exception("No se encontró la cuenta genérica.")

# Lista de destinatarios
destinatarios = ['angperilla@segurosmundial.com.co']

# Carpeta con los documentos adjuntos
carpeta_adjuntos = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Angello\3. Codigo\Codigo Angello\5. Automatizacion Simetrik\PDF'

# Crear y enviar correos
for destinatario in destinatarios:
    mail = outlook.CreateItem(0)
    mail._oleobj_.Invoke(*(64209, 0, 8, 0, cuenta))  # Usar la cuenta genérica
    mail.To = destinatario
    mail.Subject = 'Prueba Desde Correo Generico'
    mail.Body = 'Este es contenido solo de prueba.'
    mail.Send()

print('Correos enviados exitosamente.')
