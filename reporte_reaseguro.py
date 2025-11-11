# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 08:46:56 2025

@author: angperilla
"""


"""
    Script para generar reporte de FASECOLDA 
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


EXPORTACION_HR = os.path.join(r'C:\Users\angperilla\Scripts\Reportes\FUCTAS', 'HR_20200101_20251001_0.txt')
print(EXPORTACION_HR)



# _______ PRODUCTO

DIRECTORIO_PROD = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Proyectos\PRODUCTO'


# _____________________________________
ARCHIVO_PROD = 'produccion 2025 salida.parquet' # ==> Cambiar
# _____________________________________


# Ruta completa
RUTA_PROD = os.path.join(DIRECTORIO_PROD, ARCHIVO_PROD)
print(RUTA_PROD)



# =========================================
# 3.______________ FUNCIONES 
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


# Exportar HR
# df_hr.to_csv(EXPORTACION_HR, sep="|", encoding='utf-8')


# Copia
df_hr_copia = df_hr.copy()


# Muestra
muestra_hr = df_hr.tail(50000)


# Info
print(df_hr.info())


# Filtar HR por estados validos
estados_invalidos = ['ERROR', 'DUPLICADO']
df_hr = df_hr[~df_hr['ESTADO ACTUAL FACTURA'].str.contains('|'.join(estados_invalidos), na=False)]


# Convertir la columna de fecha a tipo datetime
df_hr['F.AVISO'] = pd.to_datetime(df_hr['F.AVISO'], format='%Y/%m/%d', errors='coerce')


# Convertir la columna de fecha a tipo datetime
df_hr['F.OCURRENCIA'] = pd.to_datetime(df_hr['F.OCURRENCIA'], format='%Y/%m/%d', errors='coerce')


estados = df_hr['CLASE VEHICULO'].value_counts()
print(estados)


# Asegurarse de que 'VLR RADICACION' sea numérico
df_hr['VLR_APROBADO NUEVO'] = pd.to_numeric(df_hr['VLR APROBADO'], errors='coerce')



# _______ 2025


df_hr_2025 = df_hr[df_hr['F.AVISO'].isin(pd.date_range('2024-12-01', '2025-09-30'))]


df_hr_2025 = df_hr_2025[df_hr_2025['ESTADO ACTUAL FACTURA']=='LIQUIDADO CON PAGO']


# Agrupar por varias columnas y aplicar agregaciones
df_agrupado_hr_1 = (
    df_hr_2025.groupby(['CLASE VEHICULO', 'NRO. POLIZA', 'F.OCURRENCIA', 'SINIESTRO', 'PLACA'])
           .agg(
               valor_pagado=('VLR_APROBADO NUEVO', 'sum'),
               cantidad_victimass=('DOC VICTIMA', 'size')
            
           )
           .reset_index()
)


poliza_hr = df_agrupado_hr_1[df_agrupado_hr_1['NRO. POLIZA']=='84057331']



# ________ SINIESTRO



df_hr_2025['LLAVE'] = (
    df_hr_2025['NRO. POLIZA'].astype(str) + "_" +
    df_hr_2025['PLACA'].astype(str) + "_" +
    df_hr_2025['F.OCURRENCIA'].astype(str) + "_" +
    df_hr_2025['DOC VICTIMA'].astype(str))




# Revisar duplicados por campo (Keep: Marca todas las apariciones duplicadas como True)
duplicados_hr = df_hr_2025[df_hr_2025.duplicated(subset=['LLAVE'], keep=False)]



# Agrupar por varias columnas y aplicar agregaciones
df_agrupado_hr_2 = (
    df_hr_2025.groupby(['CLASE VEHICULO', 'LLAVE'])
           .agg(
               valor_pagado=('VLR_APROBADO NUEVO', 'sum'),
               cantidad_victimass=('DOC VICTIMA', 'size')
            
           )
           .reset_index()
)


with pd.ExcelWriter(r'C:\Users\angperilla\Scripts\Reportes\FASECOLDA\Resultado_Siniestros_Mayor_50_mm.xlsx', engine='openpyxl') as writer:
    df_agrupado_hr_1.to_excel(writer, index=False, sheet_name='Detalle')



with pd.ExcelWriter(r'C:\Users\angperilla\Scripts\Reportes\FASECOLDA\Resultado_Siniestros_Mayor_50_mm2.xlsx', engine='openpyxl') as writer:
    df_agrupado_hr_2.to_excel(writer, index=False, sheet_name='Detalle')





# =========================================
# 4.______________ LECTURA PRODUCTO
# =========================================


# _______ 2025

# Lectura archivo
df_prod_2025 = pd.read_parquet(RUTA_PROD)


# Copia
df_prod_2025_copia = df_prod_2025.copy()


# Muestra
muestra_prod = df_prod_2025.tail(50000)


# Info
print(df_prod_2025.info())



# _______ 2024

# Lectura archivo
df_prod_2024 = pd.read_parquet(os.path.join(DIRECTORIO_PROD, 'produccion 2024 salida.parquet'))


# Info
print(df_prod_2024.info())






# _______ CRUCE

# Conversion Columnas Producto

df_prod_2025 = convertir_a_entero(df_prod_2025, 'POLIZA')
df_prod_2025 = limpiar_alfanumerico(df_prod_2025, 'PLACA')
df_prod_2025['POLIZA'] = df_prod_2025['POLIZA'].astype(str)




# estados_punto = df_prod_2025['NOM_PUNTO_VENTA'].value_counts()
# print(estados_punto)

# Conversion Columnas HR

df_agrupado_hr_1 = convertir_a_entero(df_agrupado_hr_1, 'NRO. POLIZA')
df_agrupado_hr_1['NRO. POLIZA'] = df_agrupado_hr_1['NRO. POLIZA'].astype(str)



df_resultado = pd.merge(df_agrupado_hr_1, df_prod_2025, left_on='NRO. POLIZA', right_on='POLIZA', how='left')

# df sin duplicados drop_dulicates(keep='last')
df_resultado = df_resultado.drop_duplicates(subset=['NRO. POLIZA'], keep='last')

with pd.ExcelWriter(r'C:\Users\angperilla\Scripts\Reportes\FASECOLDA\Resultado_Siniestros.xlsx', engine='openpyxl') as writer:
    df_resultado.to_excel(writer, index=False, sheet_name='Detalle')





# =========================================
# 4.______________ LECTURA PRODUCTO
# =========================================


# Lectura archivo
df_prod_2025 = pd.read_parquet(RUTA_PROD)


# Copia
df_prod_2025_copia = df_prod_2025.copy()


# Muestra
muestra_prod = df_prod_2025.tail(50000)


# Info
print(df_prod_2025.info())


tarifa = df_prod_2025['COD_TARIFA'].value_counts()
print(tarifa)



estados = df_prod_2025['NOM_CLASE_SOAT'].value_counts()
print(estados)


revisar = df_prod_2025[df_prod_2025['NOM_CLASE_SOAT']=='8']
poliza = df_prod_2025[df_prod_2025['POLIZA_SISE']==600249750.00]


# Filtar HR por estados validos
estados_validos = ['EXPEDICION', 'MODIFICACION SIN COBRO DE PRIMA', 'REHABILITACION']
df_prod_2025_filtro = df_prod_2025[df_prod_2025['MOVIMIENTO'].str.contains('|'.join(estados_validos), na=False)]


df_prod_2025_filtro = df_prod_2025[df_prod_2025['PRIMA'] > 0]


# Revisar duplicados por campo (Keep: Marca todas las apariciones duplicadas como True)
duplicados = df_prod_2025_filtro[df_prod_2025_filtro.duplicated(subset=['POLIZA'], keep=False)]





valores_cod = df_prod_2025['COD_TARIFA'].value_counts()

# Cod Tasa Diferencial
cod_tarifa_descuento = (100,111,121,141,711,721,731,712,722,732,811,911,921)



# Clasificación Cod
df_prod_2025_filtro['CLASIFICACION'] = np.where(df_prod_2025_filtro['COD_TARIFA'].isin(cod_tarifa_descuento), "Descuento", "Sin Descuento")



df_prod_2025_filtro = df_prod_2025_filtro[df_prod_2025_filtro['CLASIFICACION']== "Descuento"]


estados2 = df_prod_2025_filtro['NOM_CLASE_SOAT'].value_counts()
print(estados2)


df_prod_2025_filtro.info()


# Agrupar por varias columnas y aplicar agregaciones
df_agrupado = (
    df_prod_2025_filtro.groupby(['CLASE_SOAT','NOM_CLASE_SOAT', 'ANO_MODELO', 'NOM_SERVICIO', 'CILINDRAJE', 'COD_TARIFA', 'OCUPANTES'])
           .agg(
               valor_polizas=('PRIMA', 'sum'),
               cantidad_polizas=('POLIZA', 'size')
            
           )
           .reset_index()
)


with pd.ExcelWriter(r'C:\Users\angperilla\Scripts\Reportes\FASECOLDA\Resultado_Subsidiadas_2.xlsx', engine='openpyxl') as writer:
    df_agrupado.to_excel(writer, index=False, sheet_name='Detalle')




# Lectura archivo
df_prod_2024 = pd.read_parquet(os.path.join(DIRECTORIO_PROD, 'produccion 2024 salida.parquet'))


# Info
print(df_prod_2024.info())



# _______ CONSOLIDADO

prod_consolidado = pd.concat([df_prod_2025, df_prod_2024]).reset_index(drop=True)


# Info
print(prod_consolidado.info())

muestra_consolidado = prod_consolidado.head(100000)
revisar_consolidado = prod_consolidado[prod_consolidado['POLIZA']==89129988]



# ________ LECTURA SUBSIDIADO

dcto = pd.read_excel(r'C:\Users\angperilla\Scripts\Reportes\FASECOLDA\Subsidiadas.xlsx')
print(dcto.info())



df_fin = pd.merge(dcto, prod_consolidado, left_on='NRO FORMULARIO', right_on='POLIZA', how='left')



# Agrupar por varias columnas y aplicar agregaciones
df_agrupado_1 = (
    df_fin.groupby(['NOM_CLASE_SOAT'])
           .agg(
               valor_polizas=('PRIMA', 'sum'),
               cantidad_polizas=('POLIZA_x', 'size')
            
           )
           .reset_index()
)



with pd.ExcelWriter(r'C:\Users\angperilla\Scripts\Reportes\FASECOLDA\Resultado_Subsidiadas.xlsx', engine='openpyxl') as writer:
    df_fin.to_excel(writer, index=False, sheet_name='Detalle')