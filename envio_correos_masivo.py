# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 14:43:12 2024

@author: angperilla
"""

import win32com.client as win32
import logging
import pandas as pd
import os
import re


# ---------------- Configuración Outlook Cuenta Generica ------------------- # 

# Configurar Outlook con cuenta genérica
outlook = win32.Dispatch("Outlook.Application")
namespace = outlook.GetNamespace("MAPI")
cuenta_generica = None


# Buscar cuenta genérica por su nombre
for cuenta in namespace.Folders:
    if 'notificacionessoatmu@segurosmundial.com.co' in cuenta.Name:  
        cuenta_generica = cuenta
        break

print(cuenta_generica)


if cuenta_generica is None:
    raise Exception("No se encontró la cuenta genérica.")
    
 # ------------------------------------------------------------------------- #
    

def configurar_logger():
    """
    Configura el registro de eventos para archivo y consola.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Crear un manejador para la consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Crear un manejador para el archivo de log
    file_handler = logging.FileHandler('envio_correos.log')
    file_handler.setLevel(logging.INFO)

    # Crear un formato común para los manejadores
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Añadir los manejadores al logger si no han sido añadidos previamente
    if not logger.hasHandlers():
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger


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
        logger.info("Lista de destinatarios leída correctamente.")
        return destinatarios
    except Exception as e:
        logger.error(f"Error al leer {filename}: {e}")
        raise


def es_email_valido(email):
    """
    Valida si una dirección de correo electrónico es válida.

    Parámetros:
    email (str): La dirección de correo electrónico a validar.

    Retorna:
    bool: True si el correo es válido, False en caso contrario.
    """
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
    <p><strong>Entidad: {entidad}</strong></p>
    
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
    if not es_email_valido(destinatario_email):
        logger.error(f"Correo electrónico inválido: {destinatario_email}")
        return {'email': destinatario_email, 'nit': nit, 'estado': 'Correo Inválido'}
    
    try:
        # Crear un objeto de la aplicación Outlook
        # outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        
        # Configurar el correo
        mail.To = destinatario_email
        mail.Subject = f"Extracto IPS {entidad} {re.search(r'(\d{4}_\d{2})\.xlsx', extracto_ips_excel).group(1)}"
        cuerpo_mensaje = generar_cuerpo_mensaje(entidad, fecha_ultimo_dia, fecha_corte)
        mail.HTMLBody = cuerpo_mensaje
        mail._oleobj_.Invoke(*(64209, 0, 8, 0, cuenta_generica))  # Establece la cuenta genérica como remitente
        
        
        
        # Definir las rutas de los archivos adjuntos
        base_path = os.getcwd()
        excel_filename = extracto_ips_excel
        pdf_folder_path = os.path.join(base_path, "PDF")
        excel_path = os.path.join(base_path, "EXCEL", excel_filename)

        # Adjuntar todos los archivos PDF en la carpeta
        adjuntos_pdf = 0
        if os.path.exists(pdf_folder_path):
            for pdf_file in os.listdir(pdf_folder_path):
                if pdf_file.endswith(".pdf"):
                    pdf_path = os.path.join(pdf_folder_path, pdf_file)
                    mail.Attachments.Add(pdf_path)
                    adjuntos_pdf += 1
        else:
            logger.warning(f"No se encontró el archivo {pdf_path} para {destinatario_email}")
        
        adjuntos_excel = 0
        if os.path.exists(excel_path):
            mail.Attachments.Add(excel_path)
            adjuntos_excel += 1
        else:
            logger.warning(f"No se encontró el archivo {excel_path} para {destinatario_email}")

        # Enviar el correo solo si hay archivos adjuntos
        if adjuntos_pdf > 0 and adjuntos_excel > 0:
            mail.Send()
            logger.info(f"Correo enviado a {destinatario_email} con NIT {nit}")
            return {'email': destinatario_email, 'nit': nit, 'estado': 'Enviado'}  # Correo enviado
        else:
            logger.warning(f"No se encontraron archivos adjuntos para {destinatario_email}.\nNo se envió el correo.")
            return {'email': destinatario_email, 'nit': nit, 'estado': 'No Enviado (sin adjuntos)'}  # No se envió el correo debido a falta de adjuntos

    except Exception as e:
        logger.error(f"Error al enviar correo a {destinatario_email}: {e}")
        return {'email': destinatario_email, 'nit': nit, 'estado': f'Error: {e}'}  # Error al enviar el correo


# Configurar el logger
logger = configurar_logger()


# Base directorio actual
base_path = os.getcwd()


# Leer la lista de destinatarios
destinatarios = leer_destinatarios(os.path.join(base_path, 'data', 'Destinatarios.xlsx'))


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
resultados_df.to_csv('resultados_envio_correos.txt', index=False)

logger.info("Proceso de envío de correos completado. Revisa el archivo resultados_envio_correos.txt para más detalles.")
