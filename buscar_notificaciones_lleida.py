# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 12:24:21 2025

@author: angperilla
"""

import pandas as pd
import os
import numpy as np


# =========================================
# 1.______________ INSUMOS
# =========================================


DIRECTORIO = r'C:\Users\angperilla\Scripts\Gestor_Notificaciones\data'


# Base Notificaciones
BASE = 'BaseDatosResultado2.xlsx'


# Radicados
RADICADOS =  'RadicadosBusqueda.xlsx'


EXPORTACION = 'resultado_170925.xlsx'

# =========================================
# 2.______________ LECTURA
# =========================================


df_radicados = pd.read_excel(os.path.join(DIRECTORIO, RADICADOS))
df_base = pd.read_excel(os.path.join(DIRECTORIO, BASE))



# =========================================
# 3.______________ FUNCIONES
# =========================================



# Normalizar columnas en df_base
df_base['consecutivos'] = df_base['consecutivos'].fillna('').astype(str)
df_base['RADICADO_NOT'] = df_base['RADICADO_NOT'].fillna('').astype(str)

# Lista para almacenar resultados
resultados = []

# Iterar sobre cada radicado
for radicado in df_radicados['RADICADO'].astype(str):
    # Buscar en 'consecutivos'
    mask_consecutivos = df_base['consecutivos'].apply(lambda x: radicado in x.split(';'))
    if mask_consecutivos.any():
        resultados.append(df_base.loc[mask_consecutivos, 'file_name'].iloc[0])
        continue  # Si se encuentra en 'consecutivos', no buscar en 'RADICADO_NOT'

    # Buscar en 'RADICADO_NOT'
    mask_radicado_not = df_base['RADICADO_NOT'].apply(lambda x: radicado in x.split(';'))
    if mask_radicado_not.any():
        resultados.append(df_base.loc[mask_radicado_not, 'file_name'].iloc[0])
    else:
        resultados.append(np.nan)

# Añadir resultados al DataFrame original
df_radicados['filename_en_base'] = resultados

df_radicados.to_excel(os.path.join(DIRECTORIO, EXPORTACION))