# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 16:39:56 2025

@author: angperilla
"""


from azure.storage.blob import BlobServiceClient
import pandas as pd
import os

# CONFIGURACIÓN DE AZURE
account_name = 'stea2containeriq2'
account_key = '?sv=2023-01-03&ss=btqf&srt=sco&st=2025-01-02T15%3A59%3A48Z&se=2025-12-31T04%3A59%3A00Z&sp=rwdftlacup&sig=9oorggbD8tYsRT0NqNpfVrINitUMZAhhj3DQD3cuTUk%3D'
container_name = 'datos'

# CONEXIÓN AL SERVICIO BLOB
blob_service_client = BlobServiceClient(
    account_url=f'https://{account_name}.blob.core.windows.net',
    credential=account_key
)
container_client = blob_service_client.get_container_client(container_name)

# RUTA LOCAL BASE DONDE GUARDAR LOS ARCHIVOS
ruta_local_base = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Escritorio\Proyecto IA\7. Entregables IA\IA TECNICA'
os.makedirs(ruta_local_base, exist_ok=True)

# LEER LISTADO DE RADICADOS DESDE EXCEL
excel_file = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Escritorio\Proyecto IA\7. Entregables IA\IA TECNICA\radicados_muestra.xlsx'
df = pd.read_excel(excel_file, engine='openpyxl')
radicados = df['RADICADOS AZURE'].astype(str).str.strip().tolist()

# PREFIJO BASE EN AZURE
prefijo_base = 'datos/Imagenes/2025/202508/20250801'

# RECORRER CADA RADICADO Y DESCARGAR SU CARPETA COMPLETA
for radicado in radicados:
    carpeta_azure = f'{prefijo_base}/{radicado}/'
    ruta_local_radicado = os.path.join(ruta_local_base, radicado)
    os.makedirs(ruta_local_radicado, exist_ok=True)

    print(f"\n📂 Descargando carpeta completa: {carpeta_azure}")

    blobs = container_client.list_blobs(name_starts_with=carpeta_azure)
    archivos_encontrados = False

    for blob in blobs:
        archivos_encontrados = True
        ruta_relativa = blob.name.replace(carpeta_azure, '')
        ruta_local = os.path.join(ruta_local_radicado, ruta_relativa)
        os.makedirs(os.path.dirname(ruta_local), exist_ok=True)

        try:
            blob_client = container_client.get_blob_client(blob.name)
            with open(ruta_local, 'wb') as archivo_local:
                contenido = blob_client.download_blob()
                archivo_local.write(contenido.readall())
            print(f"✅ Archivo descargado: {blob.name}")
        except Exception as e:
            print(f"⚠️ Error al descargar '{blob.name}': {e}")

    if not archivos_encontrados:
        print(f"⚠️ No se encontró contenido en la carpeta: {carpeta_azure}")
