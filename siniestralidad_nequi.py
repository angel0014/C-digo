# -*- coding: utf-8 -*-
"""
Created on Mon Oct  6 11:36:13 2025

@author: angperilla
"""


import pandas as pd
import os
import time
import numpy as np

#⏱️
begin = time.time()



# =========================================
# 1.______________ INSUMOS
# =========================================



# _______ HOJA RUTA


DIRECTORIO_HR = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Proyectos\HR\2025'


# _____________________________________
ARCHIVO_HR = 'HR_20200101_20251001_0.parquet' # ==> Cambiar
# _____________________________________


# Ruta completa
RUTA_HR = os.path.join(DIRECTORIO_HR, ARCHIVO_HR)
print(RUTA_HR)




# _______ PRODUCTO

DIRECTORIO_PROD = r'C:\Users\angperilla\Scripts\PRODUCTO'


# _____________________________________
ARCHIVO_PROD = 'produccion 2025 salida.parquet' # ==> Cambiar
# _____________________________________


# Ruta completa
RUTA_PROD = os.path.join(DIRECTORIO_PROD, ARCHIVO_PROD)
print(RUTA_PROD)



# =========================================
# 2.______________ LECTURA HR 
# =========================================



def limpiar_alfanumerico(df, nombre_columna):
    """
    Elimina todos los caracteres que no sean letras o números de una columna específica.
    
    Parámetros:
    - df: DataFrame de pandas
    - nombre_columna: nombre de la columna a limpiar (string)
    
    Retorna:
    - DataFrame con la columna limpia
    """
    df[nombre_columna] = df[nombre_columna].str.replace(r'[^A-Za-z0-9]', '', regex=True)
    return df


def convertir_a_entero(df, columna):
    """
    Reemplaza '.00' y '.0' por '' en una columna tipo object y la convierte a entero.
    
    Parámetros:
    - df: DataFrame de pandas
    - columna: nombre de la columna a procesar (str)
    
    Retorna:
    - DataFrame con la columna convertida a entero
    """
    df[columna] = df[columna].replace({'.00': '', '.0': ''}, regex=True)
    df[columna] = pd.to_numeric(df[columna], errors='coerce')
    df[columna] = df[columna].astype('Int64')  # permite nulos

    return df





# =========================================
# 3.______________ LECTURA HR 
# =========================================


# Lectura archivo
df_hr = pd.read_parquet(RUTA_HR)


# Copia
df_hr_copia = df_hr.copy()


# Muestra
muestra_hr = df_hr.tail(50000)


# Info
print(df_hr.info())


# Filtar HR por estados validos
estados_invalidos = ['ERROR', 'DUPLICADO']
df_hr = df_hr[~df_hr['ESTADO ACTUAL FACTURA'].str.contains('|'.join(estados_invalidos), na=False)]


# _______ Siniestralidad HR


# Convertir la columna de fecha a tipo datetime
df_hr['F.AVISO'] = pd.to_datetime(df_hr['F.AVISO'], format='%Y/%m/%d', errors='coerce')


# Filtro
df_hr_filtro = df_hr[df_hr['F.AVISO'] >= pd.Timestamp('2025-01-01')]


# Agrupación
df_hr_agrupada = df_hr_filtro.groupby('SINIESTRO').size()





# =========================================
# 4.______________ LECTURA PRODUCTO
# =========================================


# Lectura archivo
df_prod = pd.read_parquet(RUTA_PROD)


# Copia
df_prod_copia = df_prod.copy()


# Muestra
muestra_prod = df_hr.tail(50000)


# Info
print(df_prod.info())




# =========================================
# 5.______________ PROCESAMIENTO
# =========================================


# Conversion Columnas Producto

df_prod = convertir_a_entero(df_prod, 'POLIZA')
df_prod = limpiar_alfanumerico(df_prod, 'PLACA')
df_prod['POLIZA'] = df_prod['POLIZA'].astype(str)


df_prod['LLAVE'] = df_prod['POLIZA'] + "_" + df_prod['PLACA']

estados_punto = df_prod['NOM_PUNTO_VENTA'].value_counts()
print(estados_punto)

# Conversion Columnas HR

df_hr = convertir_a_entero(df_hr, 'NRO. POLIZA')
df_hr = limpiar_alfanumerico(df_hr, 'PLACA')
df_hr['NRO. POLIZA'] = df_hr['NRO. POLIZA'].astype(str)


df_hr['LLAVE'] = df_hr['NRO. POLIZA'] + "_" + df_hr['PLACA']


# _______ PRODUCTO


# # Filtrar Nequi 
# nequi = df_prod.apply(lambda fila: fila.astype(str).str.contains('nequi', case=False).any(), axis=1)
# df_nequi = df_prod[nequi]


# # Exportar
# df_nequi.to_excel(r'C:\Users\angperilla\Scripts\Reportes\SINIESTRALIDAD NEQUI\resultado_nequi.xlsx')


# Punto Venta NEQUI
df_prod_nequi = df_prod[df_prod['NOM_PUNTO_VENTA']=='NEQUI NUEVO']



# =========================================
# 6.______________ CRUCE
# =========================================


df_prod_nequi = df_prod_nequi.drop_duplicates()

df_resultado = pd.merge(df_prod_nequi, df_hr, on='LLAVE', how='left', indicator=True)

# Revisar duplicados por campo (Keep: Marca todas las apariciones duplicadas como True)
duplicados = df_resultado[df_resultado.duplicated(subset=['LLAVE'], keep=False)]


df_resultado.to_excel(r'C:\Users\angperilla\Scripts\Reportes\SINIESTRALIDAD NEQUI\resultado_siniestralidad_nequi.xlsx')



