# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 11:25:07 2024

@author: angperilla
"""

import pandas as pd



ruta_hr = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Angello\3. Codigo\Codigo Angello\7. Reportes\hoja_ruta\HR_20200101_20241001_0.parquet'
df_hr = pd.read_parquet(ruta_hr)


# Filtrar el DataFrame por los valores específicos en la columna 'AMPARO'
amparos = ['GASTOS MEDICOS, QUIRURGICOS, FARMACEUTICOS Y HOSPI', 
                   'GASTOS DE TRANSPORTE Y MOVILIZACION DE VICTIMAS']


df_hr = df_hr[~df_hr['ESTADO ACTUAL FACTURA'].str.contains("ERROR", na=False)]
df_hr = df_hr[df_hr['AMPARO'].isin(amparos) | df_hr['AMPARO'].isna()]


df_hr.info()


df_filtrado = df_hr[pd.to_datetime(df_hr['F.CREA FACTURA'], format='%Y/%m/%d').isin(pd.date_range('01-01-2024','30-09-2024'))]


df_filtrado = df_filtrado.select_dtypes(include=['object'])

df_filtrado.info()



# Columnas Extracto
columnas = [
    "SUCURSAL",
    "PLACA",
    "CLASE VEHICULO",
    "NUMERO FACTURA",
    "CIUDAD RECLAMACION FACTURA",
    "AMPARO",
    "TD RECLA",
    'ID RECLAMANTE', # En el resultado final no se tiene en cuenta
    'RECLAMANTE',
    "F.OCURRENCIA", 
    "ESTADO ACTUAL FACTURA"]

df_filtrado = df_filtrado[columnas]

df_filtrado.to_excel(r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Angello\3. Codigo\Codigo Angello\7. Reportes\hoja_ruta\resultado_informacion_SOAT.xlsx', index=False)
