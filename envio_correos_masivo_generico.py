# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 13:55:49 2024

@author: angperilla
"""

import win32com.client
import pandas as pd
import os
import re




# --------------- Configuración de la cuenta de Outlook ----------------- #
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
 
print(cuenta_generica) 
 
# ----------------------------------------------------------------------- #




def leer_destinatarios(filename):
    """
    Lee la lista de destinatarios desde un archivo Excel.
    
    Parámetros:
    filename (str): El nombre del archivo Excel.

    Retorna:
    DataFrame de pandas con la lista de destinatarios.
    """
    try:
        destinatarios = pd.read_excel(filename) 
        print("Lista de destinatarios leída correctamente.")
        return destinatarios
    except Exception as e:
        print(f"Error al leer {filename}: {e}")
        raise


def es_email_valido(email):
    """
    Valida si una dirección de correo electrónico es válida.

    Parámetros:
    email (str): La dirección de correo electrónico a validar.

    Retorna:
    bool: True si el correo es válido, False en caso contrario.
    """
    if pd.isna(email):
        return False
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None


def generar_cuerpo_mensaje(entidad, fecha_ultimo_dia, fecha_corte):
    """
    Genera el cuerpo del mensaje de correo.

    Parámetros:
    entidad (str): El nombre de la entidad.
    fecha_reclamaciones (str): La fecha de las reclamaciones (mes y año).
    fecha_corte (str): La fecha de corte.

    Retorna:
    str: El cuerpo del mensaje de correo.
    """
    cuerpo_mensaje = f"""
    <p>Entidad: <strong><em>{entidad}</em></strong></p>
    
    <p>Seguros Mundial presenta en el archivo adjunto el extracto de información con el estado de las últimas reclamaciones por factura recibidas en {fecha_corte}.</p>

    <p>La información presentada está con corte del {fecha_ultimo_dia}. Únicamente se incluyen datos de reclamaciones con cargo a las pólizas de SOAT de la Aseguradora.</p>

    <p>Queremos recordarte que, a partir del 4 de junio de 2024, todas las solicitudes de cartera y conciliación SOAT, deben ser radicadas exclusivamente a través de nuestra página web <a href="https://sf.segurosmundial.com.co/fspq/s/">https://sf.segurosmundial.com.co/fspq/s/</a>. Es fundamental que tengas en cuenta que nuestro buzón <a href="mailto:carterasoat@segurosmundial.com.co">carterasoat@segurosmundial.com.co</a> no permitirá recepcionar más solicitudes.</p>

    <p>Para asegurar que tu solicitud sea procesada de manera eficiente y segura, te recomendamos utilizar nuestra plataforma. Puedes acceder al formulario en el siguiente enlace: <a href="https://sf.segurosmundial.com.co/fspq/s/">https://sf.segurosmundial.com.co/fspq/s/</a>.</p>

    <p>Saludos cordiales,<br>
    El equipo de Seguros Mundial</p>
    """
    return cuerpo_mensaje


def enviar_correo(destinatario_email, nit, entidad, extracto_ips_excel, fecha_ultimo_dia, fecha_corte):
    """
    Envía un correo electrónico a un destinatario con archivos adjuntos específicos.

    Parámetros:
    destinatario_email (str): El correo electrónico del destinatario.
    nit (str): El NIT del destinatario.
    entidad (str): El nombre de la entidad.
    extracto_ips_excel (str): Nombre archivo excel con la información del extracto ips
    fecha_corte (str): La fecha de corte de la información.

    Retorna:
    dict: Diccionario con el resultado del envío del correo.
    """
   
    
    try:
    
        if not es_email_valido(destinatario_email):
            return {'email': destinatario_email, 'nit': nit, 'entidad': entidad, 'estado': 'Correo Inválido'}
    
  
        # Suponiendo que el nombre del archivo sigue el formato 'Extracto_IPS_<número>_YYYY_MM.xlsx'
        nombre_archivo = os.path.basename(extracto_ips_excel)  # Obtener solo el nombre del archivo
        partes = nombre_archivo.split('_')  # Dividir el nombre del archivo en partes
        fecha = f"{partes[-2]}_{partes[-1]}"  # Extraer la parte 'YYYY_MM' del nombre del archivo
        
        mail = outlook.CreateItem(0)
        mail._oleobj_.Invoke(*(64209, 0, 8, 0, cuenta_generica))  # Usar la cuenta genérica
        mail.To = destinatario_email
        mail.Subject = f"Extracto IPS {entidad} {fecha}"
        cuerpo_mensaje = generar_cuerpo_mensaje(entidad, fecha_ultimo_dia, fecha_corte)
        mail.HTMLBody = cuerpo_mensaje
       
        
        # Definir las rutas de los archivos adjuntos
        base_path = os.getcwd()
        excel_filename = extracto_ips_excel
        pdf_folder_path = os.path.join(base_path, "PDF")
        excel_path = os.path.join(base_path, "EXCEL", excel_filename)
        
        if not os.path.exists(excel_path):
            return {'email': destinatario_email, 'nit': nit, 'entidad': entidad, 'estado': f"Excel no encontrado: {excel_path}"}

        # Adjuntar todos los archivos PDF en la carpeta
        adjuntos_pdf = 0
        if os.path.exists(pdf_folder_path):
            for pdf_file in os.listdir(pdf_folder_path):
                if pdf_file.endswith(".pdf"):
                    pdf_path = os.path.join(pdf_folder_path, pdf_file)
                    mail.Attachments.Add(pdf_path)
                    adjuntos_pdf += 1
        else:
            return {'email': destinatario_email, 'nit': nit, 'entidad': entidad,'estado': f"PDFs no encontrados en {pdf_folder_path}"}
        
        # Adjuntar archivo Excel
        adjuntos_excel = 0
        if os.path.exists(excel_path):
            mail.Attachments.Add(excel_path)
            adjuntos_excel += 1
        else:
            return {'email': destinatario_email, 'nit': nit, 'entidad': entidad, 'estado': f"Excel no encontrado: {excel_path}"}

        # Enviar el correo solo si hay archivos adjuntos
        if adjuntos_pdf > 0 and adjuntos_excel > 0:
            mail.Send()
            return {'email': destinatario_email, 'nit': nit, 'entidad': entidad,'estado': 'Enviado'}  # Correo enviado
        else:
            return {'email': destinatario_email, 'nit': nit, 'entidad': entidad, 'estado': 'No Enviado (sin adjuntos)'}  # No se envió el correo debido a falta de adjuntos

    except Exception as e:
        return {'email': destinatario_email, 'nit': nit, 'entidad': entidad,'estado': f"Error: {e}"}  # Error al enviar el correo
    
    


# Base directorio actual
base_path = os.getcwd()

# Leer la lista de destinatarios
destinatarios = leer_destinatarios(os.path.join(base_path, 'data', 'Destinatarios.xlsx'))

# Filtrar destinatarios con correos nulos
destinatarios_nulos = destinatarios[destinatarios['CorreoPrincipal'].isna()]


# Filtrar destinatarios con correos válidos
destinatarios = destinatarios[destinatarios['CorreoPrincipal'].notna()]
destinatarios.info()


# Crear una lista para registrar los resultados del envío
resultados = []

# Iterar sobre la lista de destinatarios y enviar los correos
for _, row in destinatarios.iterrows():
    resultado = enviar_correo(
        row['CorreoPrincipal'], 
        row['ID RECLAMANTE'], 
        row['RECLAMANTE'], 
        row['NOMBRE EXTRACTO IPS'], 
        row['FECHA ULTIMO DIA MES'], 
        row['FECHA CORTE'] 
    ) 
    resultados.append(resultado)

# Guardar los resultados en un archivo CSV para su revisión
resultados_df = pd.DataFrame(resultados)
resultados_df.to_csv('resultados_envio_correos.csv', index=False)
destinatarios_nulos.to_csv('resultado_destinatarios_nulos.csv', index=False)



print("Proceso de envío de correos completado. Revisa el archivo resultados_envio_correos.csv para más detalles.")