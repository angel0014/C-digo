# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 15:55:48 2025

@author: angperilla
"""

import pandas as pd
import os
import time



# ########################
# === DATOS ENTRADA ===
# ########################

#⏱️
begin = time.time()


"""============================="""
#   Paquete Octubre - Dic 2020
"""============================="""


DIRECTORIO_PDFS = r'C:\Users\angperilla\Scripts\Gestor_Notificaciones\data\Lleida\Julio_a_Septiembre_2020\PDFS'

INSUMO = r'C:\Users\angperilla\Scripts\Gestor_Notificaciones\data\BaseRenombrarPDFSLleida.xlsx'

EXPORTACION_PDFS = r'C:\Users\angperilla\Scripts\Gestor_Notificaciones\data\Lleida\Julio_a_Septiembre_2020\PDFS_RENOMBRADOS'

EXPORTACION_RESULTADO = r'C:\Users\angperilla\Scripts\Gestor_Notificaciones\data\BaseDatosRenombradaJulSep2020.xlsx'



# ______________ PROCESAMIENTO  

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



# Cargar la base de datos
df = pd.read_excel(INSUMO)
df.info()


# Lista para registrar el estado
registro = []

# Inicializar columna de estado
df['estado_renombrado'] = 'Pendiente'


# Obtener lista de archivos PDF sin la extensión .pdf
pdfs_en_directorio = [os.path.splitext(f)[0] for f in os.listdir(DIRECTORIO_PDFS) if f.lower().endswith('.pdf')]


# Filtrar la base de datos para los archivos que están en el directorio
df_filtrada = df[df['file_name'].isin(pdfs_en_directorio)]


# Asegurar columna de estado
if 'estado_renombrado' not in df.columns:
    df['estado_renombrado'] = ''

# Renombrar y mover archivos
for idx, fila in df_filtrada.iterrows():
    try:
        nuevo_nombre = f"{fila['file_name']}_{fila['GUIA_LLAVE']}_{fila['ID_RECLAMANTE_NOT']}.pdf"
        ruta_origen = os.path.join(DIRECTORIO_PDFS, fila['file_name'] + '.pdf')
        ruta_destino = os.path.join(EXPORTACION_PDFS, nuevo_nombre)

        if not os.path.exists(ruta_origen):
            df.at[idx, 'estado_renombrado'] = 'Archivo no encontrado'
            continue

        os.replace(ruta_origen, ruta_destino)  # Sobrescribe si ya existe
        df.at[idx, 'estado_renombrado'] = 'Renombrado'

    except Exception as e:
        df.at[idx, 'estado_renombrado'] = f'Error: {str(e)}'
        continue

# Guardar la base de datos actualizada
df.to_excel(EXPORTACION_RESULTADO, index=False)


#⏱️
end = time.time()
print("🧱" * 14)
show_time(begin, end)
print("🧱" * 14)
print("✅Renombramiento de PDFs completada")
print("🧱" * 14)
