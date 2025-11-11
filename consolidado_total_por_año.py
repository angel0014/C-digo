# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 08:48:18 2025

@author: angperilla
"""

"""
    Proyecto Imágenes Azure:
    Script para revisión HR con el fin de contar radicados por Fechas de 
    Crea Factura y Fecha de Aviso y cruzar vs información consolidada de 
    radicados con imágenes reportados por IQ
    
"""

import pandas as pd
import os


# ###############################
# ====  1. DATOS ENTRADA   =====
# ###############################


# _____________ HR

DIRECTORIO_HR = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Proyectos\HR'
AÑO_HR = '2025'
ARCHIVO_HR = 'HR_20200101_20250901_0.parquet'



# ____________ ANULADOS Y MANUALES

DIRECTORIO_DATA = r'C:\Users\angperilla\Scripts\Data IQ\Insumos'
AÑOS = ['2021', '2020', '2019']
ARCHIVOS = ['PJ_Anulados_', 'PJ_DetalleManual_']

print(ARCHIVOS[0].split("_"))

dict_rutas = {}

for año in AÑOS:
    dict_archivos = {}
    for archivo in ARCHIVOS:
        clave = archivo.split("_")[1] # Anulados o DetalleManual
        ruta = os.path.join(DIRECTORIO_DATA, año, archivo + año + '_pro.csv')
        dict_archivos[clave] = ruta
 
    dict_rutas[año] = dict_archivos

# Ejemplo       
print(dict_rutas['2020'])        
        
        

DIRECTORIO_2024 = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Proyectos\2. Carteras\Salidas\Data IQ\Historica\2024\12. Diciembre'
DIRECTORIO_2025 = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Proyectos\2. Carteras\Salidas\Data IQ\Historica\2025\2. Febrero'


ANULADOS_2024 = 'HistoricoAnulados.txt'
MANUALES_2024 = 'HistoricoManuales.txt'


ANULADOS_2025 = 'HistoricoAnulados2025.txt'
MANUALES_2025 = 'HistoricoManuales2025.txt'


    
# ##################################
# ====  2. PROCESAMIENTO HR   =====
# ##################################



data_hr = pd.read_parquet(os.path.join(DIRECTORIO_HR, AÑO_HR, ARCHIVO_HR))
data_hr.info()



# Conversión Fechas
data_hr['F.CREA FACTURA'] = pd.to_datetime(data_hr['F.CREA FACTURA'], format='%Y/%m/%d')
data_hr['F.LIQUIDACION'] = pd.to_datetime(data_hr['F.LIQUIDACION'], format='%Y/%m/%d')
data_hr['F.AVISO'] = pd.to_datetime(data_hr['F.AVISO'], format='%Y/%m/%d')


data_hr['F.AVISO'].tail(50)
data_hr['F.CREA FACTURA'].tail(50)


# Validar Informacion
revisar_rad = data_hr[data_hr['FACTURA IQ']=='RIQ03430000501280550']



# Quitar estados de ERRORES en HR
data_hr = data_hr[~data_hr['ESTADO ACTUAL FACTURA'].str.contains("ERROR", na=False) & ~data_hr['ESTADO ACTUAL FACTURA'].str.contains("DUPLICADO", na=False)]
estados = data_hr['ESTADO ACTUAL FACTURA'].value_counts()
print(estados)



filtro_rad = data_hr[data_hr['FACTURA IQ']=='RIQ03445659001269634']



# #############################################
# ====  3. LECTURA ANULADOS Y MANUALES   =====
# #############################################



# # ____________ 2024 

# df_anulados_2024 = pd.read_csv(os.path.join(DIRECTORIO_2024, ANULADOS_2024)) 
# df_manuales_2024 = pd.read_csv(os.path.join(DIRECTORIO_2024, MANUALES_2024)) 



# # ____________ 2025

# df_anulados_2025 = pd.read_csv(os.path.join(DIRECTORIO_2025, ANULADOS_2025)) 
# df_manuales_2025 = pd.read_csv(os.path.join(DIRECTORIO_2025, MANUALES_2025)) 


# ____________ 2021

df_anulados = pd.read_csv(dict_rutas['2020']['Anulados']) 
df_manuales = pd.read_csv(dict_rutas['2020']['DetalleManual']) 




# ###############################
# ====  4. PROCESAMIENTO   =====
# ###############################



columnas = ['FACTURA IQ', 'F.AVISO', 'F.CREA FACTURA', 
            'ESTADO ACTUAL FACTURA', 'OPERADOR ADMINISTRADOR']



# _____________ FECHA AVISO

hr_fa = data_hr[data_hr['F.AVISO'].isin(pd.date_range('2020-01-01', '2020-12-31'))]


# Quitar Anulados
hr_fa = hr_fa[~hr_fa['FACTURA IQ'].isin(df_anulados['NumeroRadicacion'])]

# Quitar Manuales
hr_fa = hr_fa[~hr_fa['FACTURA IQ'].isin(df_manuales['NumeroRadicacion'])]

# Quitar radicados que empiecen por CIQ
hr_fa = hr_fa[~hr_fa['FACTURA IQ'].str.startswith('CIQ')]

# Filtar Columnas
hr_fa = hr_fa[columnas]

# Revisar duplicados
duplicados_fa = hr_fa[hr_fa.duplicated(subset='FACTURA IQ', keep=False)]

# Eliminar duplicados en la columna 'FACTURA IQ'
hr_fa = hr_fa.drop_duplicates(subset=['FACTURA IQ'])

# Agregar Mes
hr_fa['MES'] = hr_fa['F.AVISO'].dt.to_period('M')

# Agrupar por mes y contar el número de 'FACTURA IQ'
df_grouped_fa = hr_fa.groupby(hr_fa['F.AVISO'].dt.to_period('M')).agg({'FACTURA IQ': 'count'}).reset_index()

# Exportar
hr_fa.to_excel(r'C:\Users\angperilla\Scripts\Imagenes_Azure\Salidas\2020\Consolidado_Total_2020.xlsx', index=False)


df_grouped_fa.to_excel(r'C:\Users\angperilla\Scripts\Imagenes_Azure\Salidas\2020\Resultado_agrupado_fecha_aviso_2020.xlsx')


hr_fa.info()


# =================================================================



# _____________ F.CREA FACTURA

# hr_2024_ff = data_hr[data_hr['F.CREA FACTURA'].isin(pd.date_range('2024-01-01', '2024-12-31'))]

# # Quitar Anulados
# hr_2024_ff = hr_2024_ff[~hr_2024_ff['FACTURA IQ'].isin(df_anulados['NumeroRadicacion'])]

# # Quitar Manuales
# hr_2024_ff = hr_2024_ff[~hr_2024_ff['FACTURA IQ'].isin(df_manuales['NumeroRadicacion'])]

# # Filtar Columnas
# hr_2024_ff = hr_2024_ff[columnas]

# # Revisar duplicados
# duplicados_ff = hr_2024_ff[hr_2024_ff.duplicated(subset='FACTURA IQ', keep=False)]

# # Eliminar duplicados en la columna 'FACTURA IQ'
# hr_2024_ff = hr_2024_ff.drop_duplicates(subset=['FACTURA IQ'])

# # Agrupar por mes y contar el número de 'FACTURA IQ'
# df_grouped_ff = hr_2024_ff.groupby(hr_2024_ff['F.CREA FACTURA'].dt.to_period('M')).agg({'FACTURA IQ': 'count'}).reset_index()

# # Exportar
# hr_2024_ff.to_excel('Base_total_por_fecha_factura.xlsx', index=False)
# df_grouped_ff.to_excel('resultado_agrupado_fecha_factura.xlsx')


# hr_2024_ff.info()


# ================================================================


