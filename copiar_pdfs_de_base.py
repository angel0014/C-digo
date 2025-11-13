# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 11:40:33 2025

@author: angperilla
"""

"""
    Script para copiar PDFS a otro FOLDER para subirlos a Azure
"""


import os
import pandas as pd
import time
import shutil


#⏱️
begin = time.time()


# =========================================
# 1.______________ INSUMOS
# =========================================


# _______ INPUT

FOLDER_ENTRADA = r'C:\Users\angperilla\Scripts\Gestor_Notificaciones\data\Proveedor_472\Transferencia\3 parte'

# FOLDER_ENTRADA = r'C:\Users\angperilla\Scripts\Gestor_Notificaciones\data\Lleida\10. Octubre_a_Diciembre_2022\PDFS'


# _______ OUTPUT

FOLDER_SALIDA = r'C:\Users\angperilla\Scripts\Gestor_Notificaciones\data\Azure\descargas_azure\PARTE_3'

# FOLDER_SALIDA = r'C:\Users\angperilla\Scripts\Gestor_Notificaciones\data\Lleida\10. Octubre_a_Diciembre_2022\PENDIENTES'


# _______ LISTADO PENDIENTES
RUTA_PENDIENTES = os.path.join(FOLDER_SALIDA, '472_parte3.xlsx')
print(RUTA_PENDIENTES)



# =========================================
# 2.______________ PROCESAMIENTO
# =========================================


# Lectura Pendientes
df_pendientes = pd.read_excel(RUTA_PENDIENTES)
print(df_pendientes.info())


# Pdfs entrada
pdfs_entrada = os.listdir(FOLDER_ENTRADA)



# Iterar sobre cada nombre de archivo en el listado
for nombre_archivo in df_pendientes.iloc[:, 0]:
    ruta_origen = os.path.join(FOLDER_ENTRADA, nombre_archivo)
    
    if os.path.isfile(ruta_origen):
        ruta_destino = os.path.join(FOLDER_SALIDA, nombre_archivo)
        shutil.copy2(ruta_origen, ruta_destino)
        print(f'Archivo copiado: {nombre_archivo}')
    else:
        print(f'Archivo no encontrado: {nombre_archivo}')


 
