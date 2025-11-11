# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 18:02:25 2024

@author: angperilla
"""

"""
    Script para traer la Fecha Notificacion al reporte de FUCTAS.
    
    Insumos:
        1. FUCTAS (Mes Actualizacion)
        2. HistoricoNotificaciones.txt (Más reciente)
        3. HR (Más reciente)
        
    Salidas:
        1. Reporte con la Fecha Notificacion
"""


import pandas as pd
import os
import re
import time

#⏱️
begin = time.time()



# =========================================
# 1.______________ INSUMOS
# =========================================


# _______ FUCTAS


DIRECTORIO_FUCTAS = r'C:\Users\angperilla\Scripts\Reportes\FUCTAS\Insumos\2025'


# _____________________________________
ARCHIVO = 'Validación Fuctas Julio.xlsx' # ==> Cambiar
MES_FUCTAS = '7. Julio' # ==> Cambiar 
# _____________________________________


# Ruta completa
RUTA_FUCTAS = os.path.join(DIRECTORIO_FUCTAS, MES_FUCTAS, ARCHIVO)
print(RUTA_FUCTAS)


# _______ HOJA RUTA


DIRECTORIO_HR = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Proyectos\HR\2025'


# _____________________________________
ARCHIVO_HR = 'HR_20200101_20250901_0.parquet' # ==> Cambiar
# _____________________________________


# Ruta completa
RUTA_HR = os.path.join(DIRECTORIO_HR, ARCHIVO_HR)
print(RUTA_HR)


# _______ NOTIFICACIONES 2025


DIRECTORIO_NOT_2025= r'C:\Users\angperilla\Scripts\Data IQ\Salidas\Historica\2025\7. Julio'


# _____________________________________
ARCHIVO_NOT_2025 = 'HistoricoNotificaciones2025.parquet' # ==> Cambiar
# _____________________________________


# Ruta completa
RUTA_NOT_2025 = os.path.join(DIRECTORIO_NOT_2025, ARCHIVO_NOT_2025)
print(RUTA_NOT_2025)


# _______ NOTIFICACIONES 2024


DIRECTORIO_NOT_2024= r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Proyectos\2. Carteras\Salidas\Data IQ\Historica\2024\12. Diciembre'


# _____________________________________
ARCHIVO_NOT_2024 = 'HistoricoNotificaciones2024.parquet' # ==> Cambiar
# _____________________________________


# Ruta completa
RUTA_NOT_2024 = os.path.join(DIRECTORIO_NOT_2024, ARCHIVO_NOT_2024)
print(RUTA_NOT_2024)


# _______ EXPORTACION

DIRECTORIO_EXPORTACION = r'C:\Users\angperilla\Scripts\Reportes\FUCTAS\Salidas\2025\7. Julio'


ARCHIVO_EXPORTACION = 'Resultado_Fuctas_Jul_2025.xlsx'


# Ruta completa
RUTA_EXPORTACION = os.path.join(DIRECTORIO_EXPORTACION, ARCHIVO_EXPORTACION)


# =========================================
# 2.______________ FUNCIONES
# =========================================


def limpiar_columna(df, columns_name):
    """
        Limpia caracteres especiales en la columna especifica
        
        df: Dataframe (Dataframe)
        
        columns_name: Lista de columnas (list)
        
        return: Columnnas del Dataframe limpias (Dataframe)
    
    """
    for column in columns_name: 
        df[column] = df[column].apply(lambda x: re.sub(r'[^A-Za-z0-9]', '', x).upper())
    return df



# =========================================
# 3.______________ LECTURA FUCTAS 
# =========================================


# Lectura archivo
df_fuctas = pd.read_excel(RUTA_FUCTAS)
print(df_fuctas.shape)
print(df_fuctas.info())


# Conversion columnas a str
df_fuctas['FACTURA'] = df_fuctas['FACTURA'].astype(str)
df_fuctas['POLIZA'] = df_fuctas['POLIZA'].astype(str)


# Aplicar funcion para eliminar caracteres especiales
df_fuctas_final = limpiar_columna(df_fuctas, ['FACTURA', 'POLIZA'])


# Crear llave
df_fuctas_final['LLAVE'] = df_fuctas_final['FACTURA'] + "_" + df_fuctas_final['POLIZA']



# =========================================
# 4.______________ LECTURA HR 
# =========================================


# Lectura archivo
df_hr = pd.read_parquet(RUTA_HR)
print(df_hr.info())


# Copia
df_hr_copia = df_hr.copy()
# df_hr.to_csv(os.path.join(r'C:\Users\angperilla\Scripts\HR','HR_20200101_20250901_0.txt'), sep='|', encoding='utf-8')


# Selección Columnas HR
columnas_depuradas = ['FACTURA IQ',
                      'NRO. POLIZA',
                      'NUMERO FACTURA',
                      'VLR CONSTITUCION RVA',
                      'VLR RADICACION',
                      'VLR APROBADO',
                      'VLR GLOSADO',
                      'F.OCURRENCIA',
                      'F.AVISO',
                      'ESTADO ACTUAL FACTURA',
                      'F. NOTIFICACION',
                      'OPERADOR ADMINISTRADOR' ]

# Filtar df por columnas seleccionadas
df_hr = df_hr[columnas_depuradas]


# Filtar HR por estados validos
estados_invalidos = ['ERROR', 'DUPLICADO']
df_hr = df_hr[~df_hr['ESTADO ACTUAL FACTURA'].str.contains('|'.join(estados_invalidos), na=False)]


# Revisar Estados HR
estados_hr = df_hr['ESTADO ACTUAL FACTURA'].value_counts()
print(estados_hr)


# Conversion columnas a str
df_hr['NUMERO FACTURA'] = df_hr['NUMERO FACTURA'].astype(str)
df_hr['NRO. POLIZA'] = df_hr['NRO. POLIZA'].astype(str)


# Aplicar función de limpieza
df_hr_final = limpiar_columna(df_hr, ['NUMERO FACTURA','NRO. POLIZA'])


# Conversión Fechas
df_hr['F.AVISO'] = pd.to_datetime(df_hr['F.AVISO'], format='%Y/%m/%d')
df_hr['F. NOTIFICACION'] = pd.to_datetime(df_hr['F. NOTIFICACION'], format='%Y/%m/%d')


# Revision Fechas Nulas Notificacion
nulos_not = df_hr[df_hr['F. NOTIFICACION'].isna()]


# Crear Llave
df_hr_final['LLAVE'] = df_hr_final['NUMERO FACTURA'] + "_" + df_hr_final['NRO. POLIZA']


# Ordenar Df por Fechas
df_hr_final = df_hr_final.sort_values(by=[ 'F. NOTIFICACION', 'F.AVISO'], ascending=[False, False])
print(df_hr_final.info())


# Revisar Registros Duplicados de mi df
duplicados_hr = df_hr_final[df_hr_final.duplicated(subset=['FACTURA IQ'], keep=False)] 


# Eliminar de mi df duplicados drop_dulicates(keep='last') mantener el registro mas reciente
df_hr_final = df_hr_final.drop_duplicates(subset=['FACTURA IQ'], keep='first')


# Revisar Registros Duplicados de mi df
duplicados_llave = df_hr_final[df_hr_final.duplicated(subset=['LLAVE'], keep=False)] 



# =========================================
# 4.______________ LECTURA NOTIFICACIONES
# =========================================


# _______ 2024


df_not_2024 = pd.read_parquet(RUTA_NOT_2024)
print(df_not_2024.info())
print(df_not_2024['F.NOTIFICACION'].head(100))


# Copia Columna 
df_not_2024['F. NOTIFICACION NUEVA'] = df_not_2024['F.NOTIFICACION']


# Conversion Fechas
df_not_2024['F.NOTIFICACION'] =  pd.to_datetime(df_not_2024['F.NOTIFICACION'], format='%d/%m/%Y')


# _______ 2025


df_not_2025 = pd.read_parquet(RUTA_NOT_2025)
print(df_not_2025.info())
print(df_not_2025['F.NOTIFICACION'].tail(100))


# Copia Columna 
df_not_2025['F. NOTIFICACION NUEVA'] = df_not_2025['F.NOTIFICACION']


# Conversion Fechas
df_not_2025['F.NOTIFICACION'] =  pd.to_datetime(df_not_2025['F.NOTIFICACION'], format='%d/%m/%Y')


# Revision Fechas Nulas Notificacion
nulos_not_2025 = df_not_2025[df_not_2025['F.NOTIFICACION'].isna()]


# _______ CONCATENAR


if list(df_not_2024.columns) == list(df_not_2025.columns):
    df_not = pd.concat([df_not_2024, df_not_2025], ignore_index=True)
    print("DataFrames unidos correctamente.")
else:
    print("Las columnas no coinciden. No se puede hacer la unión.")


# Ordenar por F.NOTIFICACION
df_not_final = df_not.sort_values(by=[ 'F.NOTIFICACION'], ascending=[False])


# Revisar Registros Duplicados de mi df
duplicados_not = df_not_final[df_not_final.duplicated(subset=['RADICADO'], keep=False)] 


# Eliminar de mi df duplicados drop_dulicates(keep='last') mantener el registro mas reciente
df_not_final = df_not_final.drop_duplicates(subset=['RADICADO'], keep='first')
print(df_not_final)


# =========================================
# 5.______________ CRUCE HR Vs FUCTAS
# =========================================


# Eliminar de mi df duplicados drop_dulicates(keep='last') mantener el primer
df_hr_final = df_hr_final.drop_duplicates(subset=['LLAVE'], keep='first')


fuctas_cruce = pd.merge(df_fuctas_final, df_hr_final, how='left', on=['LLAVE'], indicator=True)
print(fuctas_cruce.info())


# Revisar Registros Duplicados de mi df
duplicados_fuctas = fuctas_cruce[fuctas_cruce.duplicated(subset=['LLAVE'], keep=False)]


# _______ RESULTADO CRUVE VS NOTIFICACIONES 


# Renombrar columnas
df_not_final.columns = [f"{col}_NOT" for col in df_not_final.columns]


df_resultado = pd.merge(fuctas_cruce, df_not_final, how='left', left_on='FACTURA IQ',
                        right_on='RADICADO_NOT')
print(df_resultado.info())


# Crear fecha de certificacion
df_resultado['FECHA_CERTIFICACION'] = df_resultado['F.NOTIFICACION_NOT'].fillna(df_resultado['F. NOTIFICACION']).fillna(df_resultado['F.AVISO'])


# Revision Fechas Nulas Notificacion
nulos_certificacion = df_resultado[df_resultado['FECHA_CERTIFICACION'].isna()]



# =========================================
# 6.______________ EXPORTACION
# =========================================

# Exportación
df_resultado.to_excel(RUTA_EXPORTACION, index=False)


print("😊" *7, "Listonessss!!!")
