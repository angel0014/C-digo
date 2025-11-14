# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 14:50:23 2024

@author: angperilla
"""

import win32com.client
import os
import re

# Configuración de la cuenta de Outlook
outlook = win32com.client.Dispatch('outlook.application')
namespace = outlook.GetNamespace("MAPI")
cuenta_generica = None

# Buscar la cuenta genérica
for acc in namespace.Accounts:
    if acc.SmtpAddress == 'notificacionessoatmu@segurosmundial.com.co':
        cuenta_generica = acc
        break

if cuenta_generica is None:
    raise Exception("No se encontró la cuenta genérica.")

# Función para generar el cuerpo del mensaje (debes definir esta función)
def generar_cuerpo_mensaje(entidad, fecha_ultimo_dia, fecha_corte):
    return f"<p>Estimado/a,</p><p>Adjunto encontrará el extracto IPS de {entidad} correspondiente al periodo hasta {fecha_corte}.</p>"

# Lista de destinatarios y otros datos
destinatarios = ['angperilla@segurosmundial.com.co']
entidad = 'Nombre de la Entidad'
fecha_ultimo_dia = '2024-09-30'
fecha_corte = '2024-10-15'
extracto_ips_excel = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Angello\3. Codigo\Codigo Angello\5. Automatizacion Simetrik\EXCEL\Extracto_IPS_900849021_2024_05.xlsx'

# Crear y enviar correos
for destinatario_email in destinatarios:
    try:
        mail = outlook.CreateItem(0)
        mail._oleobj_.Invoke(*(64209, 0, 8, 0, cuenta_generica))  # Usar la cuenta genérica
        mail.To = destinatario_email
        mail.Subject = f"Extracto IPS {entidad} {re.search(r'(\d{4}_\d{2})\.xlsx', extracto_ips_excel).group(1)}"
        cuerpo_mensaje = generar_cuerpo_mensaje(entidad, fecha_ultimo_dia, fecha_corte)
        mail.HTMLBody = cuerpo_mensaje

        # Adjuntar archivos
        mail.Attachments.Add(extracto_ips_excel)

        mail.Send()
        print(f"Correo enviado a {destinatario_email}")
    except Exception as e:
        print(f"Error al enviar correo a {destinatario_email}: {e}")

print('Proceso de envío de correos completado.')
