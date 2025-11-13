# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 11:56:48 2025

@author: angperilla
"""

"""
    Script para renombrar información de notificaciones PDFs de Lleida para 
    subida en repositorio en Azure.
"""

import pandas as pd
import os
import time
import re


# ########################
# === DATOS ENTRADA ===
# ########################

#⏱️
begin = time.time()


DIRECTORIO = r'C:\Users\angperilla\Scripts\Gestor_Notificaciones'

INSUMO = r'C:\Users\angperilla\Scripts\Gestor_Notificaciones\data\BaseDatos.xlsx'

HISTORICO_NOTIFICACIONES = r'C:\Users\angperilla\Scripts\Gestor_Notificaciones\Notificaciones2021_2024.parquet'

NOT_2020 = os.path.join(DIRECTORIO,'PJ_Detallenotificacion_2020_pro.csv')

NOT_2019 = os.path.join(DIRECTORIO,'PJ_Detallenotificacion_2019_pro.csv')

NOT_2018 = os.path.join(DIRECTORIO,'PJ_Detallenotificacion_2018_pro.csv')



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



def clean(consecutivo):
    # Convertir a cadena y manejar valores nulos
    if pd.isna(consecutivo):
        return ''
    consecutivo_str = str(consecutivo)
    # Usar una expresión regular para quitar todos los caracteres especiales excepto el '-'
    consecutivo_limpio = re.sub(r'[^a-zA-Z0-9-]', '', consecutivo_str)
    # Convertir a mayúsculas
    return consecutivo_limpio.upper()



def extraer_valor(valor):
    if pd.isna(valor) or valor == '':
        return None
    return valor.split(';')[0].strip()




# ______________ LECTURA

df_data = pd.read_excel(INSUMO)
df_data.info()

# # Extraer el primer código válido según el tipo
# df_data['consecutivo'] = df_data['subject'].str.extract(patron_consecutivo, expand=False)
# df_data['radicado'] = df_data['subject'].str.extract(patron_radicado, expand=False)




# ______________ CONSECUTIVOS

# Expresión regular para extraer consecutivos que comienzan con LIQ, DEV, OBJ o GIN
patron_consecutivo = r'(?:LIQ|DEV|OBJ|GIN)[-]?\w*?\d{6,}'


# Aplicar la extracción a cada fila
df_data['consecutivos'] = df_data['subject'].apply(lambda x: re.findall(patron_consecutivo, x))


# Convertir la lista a texto separado por punto y coma
df_data['consecutivos'] = df_data['consecutivos'].apply(lambda x: '; '.join(x))


# Crear una nueva columna con el valor extraído
df_data['consecutivo'] = df_data['consecutivos'].apply(extraer_valor)



# _______________ RADICADOS

# Expresión regular para capturar radicados con las palabras clave dadas
patron_radicado = r'(?:CMVIQ|VIQ|IQ|RIQ|RCMVIQ)[-]?\w*\d+'


# Aplicar la extracción
df_data['radicados'] = df_data['subject'].apply(lambda x: re.findall(patron_radicado, x))


# Convertir la lista a texto separado por punto y coma
df_data['radicados'] = df_data['radicados'].apply(lambda x: '; '.join(x))


# Crear una nueva columna con el valor extraído
df_data['radicado'] = df_data['radicados'].apply(extraer_valor)


df_data.info()



# _____________ LLAVE

df_data['llave'] = df_data.apply(lambda row: row['consecutivo'] if row['consecutivo'] else row['radicado'], axis=1)
df_data['llave'] = df_data['llave'].apply(clean)


# ____________ LECTURA NOTIFICACIONES

not_final = pd.read_parquet(HISTORICO_NOTIFICACIONES)


# Diccionario de mapeo de nombres de columnas
nuevos_nombres = {
    'NO. FACTURA': 'NUMERO FACTURA',
    'FECHA AVISO': 'F.AVISO',
    'CONSECUTIVO CARTA': 'CONSECUTIVO',
    'NO DE GUIA': 'GUIA',
    'CORREO DE DESTINO': 'CORREO',
    'FECHA DE ENTREGA NOTIFICACIÓN': 'F.NOTIFICACION'
}


# Renombrar columnas
not_final = not_final.rename(columns=nuevos_nombres)
not_final.info()
not_final.columns



not_2020 = pd.read_csv(NOT_2020, encoding='ansi', sep='|', decimal='.', low_memory=False)
not_2020.info()

not_2019 = pd.read_csv(NOT_2019, encoding='ansi', sep='|', decimal='.', low_memory=False)
not_2019.info()

not_2018 = pd.read_csv(NOT_2018, encoding='ansi', sep='|', decimal='.', low_memory=False)
not_2018.info()


# # Función para limpiar y formatear fechas
# def limpiar_formato_fecha(fecha):
#     if pd.isna(fecha):
#         return fecha
#     fecha = str(fecha).replace(';;', '').strip()
#     try:
#         return pd.to_datetime(fecha, dayfirst=True).strftime('%d/%m/%Y')
#     except:
#         return fecha


# # Aplicar a not_2018
# not_2018['F.NOTIFICACION'] = not_2018['F.NOTIFICACION'].apply(limpiar_formato_fecha)

not_2018['F.NOTIFICACION'] = pd.to_datetime(not_2018['F.NOTIFICACION'], dayfirst=True, errors='coerce')
not_2018['F.AVISO'] = pd.to_datetime(not_2018['F.AVISO'], dayfirst=True, errors='coerce')



# Aplicar a not_2019
not_2019['F.NOTIFICACION'] = pd.to_datetime(not_2019['F.NOTIFICACION'], dayfirst=True, errors='coerce')
not_2019['F.AVISO'] = pd.to_datetime(not_2019['F.AVISO'], dayfirst=True, errors='coerce')


# Aplicar a not_2020
not_2020['F.NOTIFICACION'] = pd.to_datetime(not_2020['F.NOTIFICACION'], dayfirst=True, errors='coerce')
not_2020['F.AVISO'] = pd.to_datetime(not_2020['F.AVISO'], dayfirst=True, errors='coerce')


def crear_periodo(df):
    df['PERIODO'] = df['F.NOTIFICACION'].dt.strftime('%Y%m')
    return df


not_2018 = crear_periodo(not_2018)
not_2019 = crear_periodo(not_2019)
not_2020 = crear_periodo(not_2020)


def limpiar_columna_mixta(valor):
    try:
        return str(int(float(valor)))
    except:
        return valor  # deja el valor original si no se puede convertir


not_2018['GUIA'] = not_2018['GUIA'].apply(limpiar_columna_mixta)
not_2019['GUIA'] = not_2019['GUIA'].apply(limpiar_columna_mixta)
not_2020['GUIA'] = not_2020['GUIA'].apply(limpiar_columna_mixta)


not_2018['GUIA_LLAVE'] = not_2018['GUIA'].str.replace(r'[-/]S$', '', regex=True)
not_2018['GUIA_LLAVE'] = not_2018['GUIA_LLAVE'].fillna('NA')
not_2018['GUIA_LLAVE'] = not_2018['GUIA_LLAVE'].apply(clean)


not_2019['GUIA_LLAVE'] = not_2019['GUIA'].str.replace(r'[-/]S$', '', regex=True)
not_2019['GUIA_LLAVE'] = not_2019['GUIA_LLAVE'].fillna('NA')
not_2019['GUIA_LLAVE'] = not_2019['GUIA_LLAVE'].apply(clean)


not_2020['GUIA_LLAVE'] = not_2020['GUIA'].str.replace(r'[-/]S$', '', regex=True)
not_2020['GUIA_LLAVE'] = not_2020['GUIA_LLAVE'].fillna('NA')
not_2020['GUIA_LLAVE'] = not_2020['GUIA_LLAVE'].apply(clean)


not_final['GUIA'] = not_final['GUIA'].apply(limpiar_columna_mixta)
not_final['GUIA_LLAVE'] = not_final['GUIA'].str.replace(r'[-/]S$', '', regex=True)
not_final['GUIA_LLAVE'] = not_final['GUIA_LLAVE'].fillna('NA')
not_final['GUIA_LLAVE'] = not_final['GUIA_LLAVE'].apply(clean)


# Faltantes
df_notificaciones = pd.concat([not_2018, not_2019, not_2020, not_final]).reset_index(drop=True)




# --------------------------
"1. Ordenar Notificaciones"
# ---------------------------


# # Convertir usando inferencia de formato
# df_notificaciones['FECHA AVISO'] = pd.to_datetime(df_notificaciones['FECHA AVISO'], errors='coerce', infer_datetime_format=True)


# Filtrar filas con fechas no válidas
filas_invalidas = df_notificaciones[df_notificaciones['F.NOTIFICACION'].isna()]


# Ordenar df (Más reciente)
df_notificaciones_ordenado = df_notificaciones.sort_values(by=['CONSECUTIVO', 'F.AVISO', 'F.NOTIFICACION','RADICADO'], ascending=[False, False, False, False])


# Validar Orden
revisar_orden = df_notificaciones_ordenado[df_notificaciones_ordenado['CONSECUTIVO']=='LIQ-202303012787']


# Filtrar filas Vacias
revisar_vacios = df_notificaciones_ordenado[df_notificaciones_ordenado['CONSECUTIVO'].isna() | (df_notificaciones_ordenado['CONSECUTIVO'] == '')]


# Imputar valores vacíos o nulos con 'NA' => 50 valores con NA
df_notificaciones_ordenado['CONSECUTIVO CARTA'] = df_notificaciones_ordenado['CONSECUTIVO'].replace('', 'NA').fillna('NA')



# ---------------------------------------
"2. Agrupamiento por CONSECUTIVO CARTA"
# ---------------------------------------


# Agrupar el DataFrame por "CONSECUTIVO" y mantener los demás campos
agrupado = df_notificaciones_ordenado.groupby("GUIA_LLAVE").agg(
    NUMERO_FACTURA_NOT=("NUMERO FACTURA", lambda x: ";".join(x.astype(str))),
    RADICADO_NOT=("RADICADO", lambda x: ";".join(x.astype(str))),
    ID_RECLAMANTE_NOT=("ID RECLAMANTE", "first"),
    RECLAMANTE_NOT=("RECLAMANTE", "first"),
    FECHA_AVISO_NOT=("F.AVISO", "first"),
    CONSECUTIVO_NOT=("CONSECUTIVO", lambda x: ";".join(x.astype(str))),
    GUIA_NOT=("GUIA", "first"),
    CORREO_NOT=("CORREO", "first"),
    F_NOTIFICACION_NOT=("F.NOTIFICACION", "first"),
    PERIODO_NOT=("PERIODO", "first")
).reset_index()



# =================================
# ===   Cruce Notificaciones    ===
# =================================

# ______________ LLAVE BASE

df_data['GUIA_LLAVE'] = df_data['file_uid'].str.replace(r'[-/]S$', '', regex=True)
df_data['GUIA_LLAVE'] = df_data['GUIA_LLAVE'].fillna('NA')
df_data['GUIA_LLAVE'] = df_data['GUIA_LLAVE'].apply(clean)


estados_agrupado = df_data['GUIA_LLAVE'].value_counts()
print(estados_agrupado)

cruce_not = pd.merge(df_data, agrupado, on='GUIA_LLAVE', how='left')    
cruce_not['TIPO'] = cruce_not['llave'].astype(str).str[:3]
cruce_not.info()



# _______________ EXPORTACION

cruce_not.to_excel(r'C:\Users\angperilla\Scripts\Gestor_Notificaciones\data\BaseDatosResultado2.xlsx')



#⏱️
end = time.time()
print("🧱" * 14)
show_time(begin, end)
print("🧱" * 14)
print("✅Renombramiento de PDFs completada")
print("🧱" * 14)
