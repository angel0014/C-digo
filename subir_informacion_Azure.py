# -*- coding: utf-8 -*-
"""
Created on Tue Jul  1 09:06:42 2025

@author: angperilla
"""

"""
    Script para copiar información PDFs en local al blob de Azure
    
"""

import os
from azure.storage.blob import BlobServiceClient, ContentSettings
import time



# ########################
# ====  DIRECTORIOS  ====
# ########################

""" Rutas de información de Inicio y Destino"""



DIRECTORIO_LOCAL = r'C:\Users\angperilla\Scripts\Gestor_Notificaciones\data\Proveedor_472\Transferencia'

PAQUETE = '4 parte'
 

# DIRECTORIO_LOCAL = r'C:\Users\angperilla\Scripts\Gestor_Notificaciones\data\Lleida'


# PAQUETE = '11. Enero_a_Marzo_2023'


# LOCAL_FOLDER = os.path.join(DIRECTORIO_LOCAL, PAQUETE, 'PDFS')

LOCAL_FOLDER = os.path.join(DIRECTORIO_LOCAL, PAQUETE)
# LOCAL_FOLDER = r'C:\Users\angperilla\Scripts\Gestor_Notificaciones\data\Lleida\Octubre_a_Diciembre_2020\PDFS_PRUEBA'
print(LOCAL_FOLDER)


# NOMBRE CARPETA EN AZURE DONDE SE CARGA LA INFORMACION
AZURE_FOLDER = "datos/Notificaciones/2024/"


ERROR = os.path.join(LOCAL_FOLDER, "errores_subida.txt")



# #############################################
# ==== 1.   CONFIGURACION BLOB STORAGE    ====
# #############################################




# ___________  CONFIGURACION 
account_name = 'stea2containeriq2'
account_key = '?sv=2023-01-03&ss=btqf&srt=sco&st=2025-01-02T15%3A59%3A48Z&se=2025-12-31T04%3A59%3A00Z&sp=rwdftlacup&sig=9oorggbD8tYsRT0NqNpfVrINitUMZAhhj3DQD3cuTUk%3D'
container_name = 'datos'


# ___________  BLOB SERVICE CLIENTE (conexion)
blob_service_client = BlobServiceClient(
    account_url=f'https://{account_name}.blob.core.windows.net',
    credential=account_key
)


# ___________  CLIENTE CONTENEDOR (Conectar a datos)
container_client = blob_service_client.get_container_client(container_name)


# ___________  VERIFICAR CONEXION
try:
    props = container_client.get_container_properties()
    print(f"✅ Conexión exitosa al contenedor '{container_name}'.")
except Exception as e:
    print("❌ No se pudo conectar al contenedor. Error:", e)


# # __________  LISTAR CONTENIDO
# blobs = container_client.list_blobs(name_starts_with=AZURE_FOLDER)

# for blob in blobs:
#     print("📄", blob.name)




# #################################################
# ==== 2.   COPIAR ELEMENTOS LOCAL A AZURE    ====
# #################################################




"""
    >>> CONSIDERACIONES:
        root: ruta actual
        dirs: lista subdirectorios dentro de root
        files: lista archivos dentro de root
        En Python, la función os.walk() devuelve una tupla por cada carpeta 
        que recorre. 
        Esa tupla contiene tres elementos:
        Ejemplo: ('C:\\MiProyecto', ['Subcarpeta'], ['archivo1.txt', 'archivo2.csv'])
        ('C:\\MiProyecto\\Subcarpeta', [], ['archivo3.docx'])
"""



# ===  INICIALIZAR LOG DE ERRORES  ===
with open(ERROR, "w", encoding="utf-8") as error_log:
    error_log.write("Errores durante la subida a Azure Blob Storage:\n\n")
    


begin = time.time()


def show_time(begin, end):
    duration = end - begin
    if duration < 60:
        print(f"⏱ Tiempo de ejecución: {duration:.2f} seconds")
    elif duration < 3600:
        minutes = duration / 60
        print(f"⏱ Tiempo de ejecución: {minutes:.2f} minutes")
    else:
        hours = duration / 3600
        print(f"⏱ Tiempo de ejecución: {hours:.2f} hours")



# ===  SUBIDA DE ARCHIVOS PDF  ===
# Recorre todos los PDFs en un directorio y los copia en una carpeta 
# especifica en AZURE

for root, dirs, files in os.walk(LOCAL_FOLDER):
    for file_name in files:
        if file_name.lower().endswith('.pdf'):
            
            # file_path: Ruta completa de la notificación
            file_path = os.path.join(root, file_name)
            
            # Nombre del Blob dentro de "datos"
            blob_name = AZURE_FOLDER + file_name  
            # print(blob_name)

            try:
                with open(file_path, "rb") as data:
                    container_client.upload_blob(
                        name=blob_name,
                        data=data,
                        overwrite=True,  # sobrescribir si ya existe
                        content_settings=ContentSettings(content_type="application/pdf")
                    )
                
            except Exception as e:
                print(f"❌ Error al subir {blob_name}: {e}")
                with open(ERROR, "a", encoding="utf-8") as error_log:
                    error_log.write(f"{blob_name} — {str(e)}\n")

end = time.time()
print("🧱" * 14)
show_time(begin, end)
print("🧱" * 14)
print("✅ Proceso completado.")
print("🧱" * 14)
print(f"📄 Revisa el archivo de errores {ERROR}")

