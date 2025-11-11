# -*- coding: utf-8 -*-
"""
Created on Tue Sep  2 16:09:03 2025

@author: angperilla
"""

"""
    Script para realizar el cruce inventario azure 2024 vs HR
"""

import pandas as pd
import os
import time



#⏱️
begin = time.time()


# =========================================
# 1.______________ INSUMOS
# =========================================


# _______ HR

DIRECTORIO_HR = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Proyectos\HR\2025'

# _____________________________________
ARCHIVO_HR = 'HR_20200101_20251001_0.parquet' # ==> Cambiar
# _____________________________________

# Ruta completa
RUTA_HR = os.path.join(DIRECTORIO_HR, ARCHIVO_HR)
print(RUTA_HR)


# _______ BASE HR 2024

DIRECTORIO_BASE = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Proyectos\1. Imagenes_Azure\Salidas\2024'

# _____________________________________
ARCHIVO_BASE = 'Consolidado_Total_2024.xlsx' # ==> Cambiar
# _____________________________________

# Ruta completa
RUTA_BASE = os.path.join(DIRECTORIO_BASE, ARCHIVO_BASE)
print(RUTA_BASE)


# _______ INVENTARIO AZURE 2024

DIRECTORIO_INVENTARIO = r'C:\Users\angperilla\Scripts\Imagenes_Azure\Salidas\2024\Azure'

# _____________________________________
ARCHIVO_INVENTARIO = 'resultado_inventario_azure_total_2024.csv' # ==> Cambiar
# _____________________________________

# Ruta completa
RUTA_INVENTARIO = os.path.join(DIRECTORIO_INVENTARIO, ARCHIVO_INVENTARIO)
print(RUTA_INVENTARIO)


# _______ EXPORTACION

DIRECTORIO_EXPORTACION = r'C:\Users\angperilla\Scripts\Imagenes_Azure\Salidas\2024\FALTANTES'
ARCHIVO_EXPORTACION = 'Resultado_Faltantes_2024.xlsx'

# Ruta completa
RUTA_EXPORTACION = os.path.join(DIRECTORIO_EXPORTACION, ARCHIVO_EXPORTACION)
print(RUTA_EXPORTACION)



# =========================================
# 2.______________ FUNCIONES
# =========================================


def eliminar_codigos(df_hr, columna):
    """
    Elimina las filas de un DataFrame cuyo RADICADO específico
    comienza con los prefijos 'IQ000000' o 'RIQ000000'.

    Parámetros:
    ----------
    df_hr : pandas.DataFrame
        El DataFrame que contiene los datos a filtrar.

    columna : str
        El nombre de la columna sobre la cual se aplicará el filtro.

    Retorna:
    -------
    pandas.DataFrame
        Un nuevo DataFrame sin las filas que comienzan con los prefijos indicados.
    
    """
    
    # Verificar que la columna existe y es de tipo texto
    if columna not in df_hr.columns:
        raise ValueError(f"La columna '{columna}' no existe en el DataFrame.")
    
    # Convertir a texto por si hay valores no string
    serie = df_hr[columna].astype(str)

    # Crear un filtro que excluya los valores que comienzan con los prefijos dados
    filtro = ~serie.str.startswith(('IQ000000', 'RIQ000000', 'VIQ'))


    # Aplicar el filtro y devolver el DataFrame limpio
    return df_hr.loc[filtro].copy()


def show_time(begin, end):
    """
    Muestra el tiempo transcurrido desde el inicio y fin de la ejecución del 
    Script
    
    Parámetros:
    ----------
    begin : float
        Tiempo de Inicio
    end : float
        Tiempo de finalizacion
    
    """
    duration = end - begin
    if duration < 60:
        print(f"⏱ Tiempo de ejecución: {duration:.2f} seconds")
    elif duration < 3600:
        minutes = duration / 60
        print(f"⏱ Tiempo de ejecución: {minutes:.2f} minutes")
    else:
        hours = duration / 3600
        print(f"⏱ Tiempo de ejecución: {hours:.2f} hours")



# =========================================
# 3.______________ LECTURA BASE 2024
# =========================================


# Lectura archivo
df_base = pd.read_excel(RUTA_BASE, engine='openpyxl')
print(df_base.info())


# Tipos de Radicados IQ
estados_base = df_base['TIPO'].value_counts()
print(estados_base)


# Filtrar Valores de Radicado Validos
df_base = eliminar_codigos(df_base, 'FACTURA IQ')



# =========================================
# 4.______________ LECTURA INVENTARIO 2024
# =========================================


# Lectura archivo
df_inventario = pd.read_csv(RUTA_INVENTARIO)
print(df_inventario.info())
print(df_inventario.head(100))


# Separar por '/' y expandir en nuevas columnas
df_inventario = df_inventario['Ruta'].str.split('/', expand=True)


# Asignar nombres personalizados a las columnas expandidas
column_names = ['Folder 1', 'Folder 2', 'Año', 'AñoMes', 'AñoMesDia', 'Radicado', 'Archivo']
df_inventario.columns = column_names[:df_inventario.shape[1]]


# Revision df_inventario
print(df_inventario.head())


# Agrupar por AñoMes, AñoMesDia, Radicado (Tabla Dinamica)
df_grouped = (
    df_inventario
    .groupby(['AñoMes', 'AñoMesDia','Radicado'])
    .agg({
        'Archivo': 'count'})).reset_index()


# Revisar duplicados por campo (Keep: Marca todas las apariciones duplicadas como True)
radicados_duplicados = df_grouped[df_grouped.duplicated(subset=['Radicado'], keep=False)]


# Registros Duplicados de mi df
duplicados_completos = df_grouped[df_grouped.duplicated(keep=False)] # No hay


# =========================================
# 5.______________ CRUCE BASE VS INVENTARIO
# =========================================


# df sin duplicados drop_dulicates(keep='last')
df_grouped= df_grouped.drop_duplicates(subset=['Radicado'], keep='last')

# Cruce Base Vs Inventario 2024
df_cruce = pd.merge(df_base, df_grouped, 
                    left_on='FACTURA IQ', 
                    right_on='Radicado', 
                    how='left')


# Revisar duplicados por campo (Keep: Marca todas las apariciones duplicadas como True)
# No Nulos
duplicados_cruce = df_cruce[df_cruce['Radicado'].notna() & df_cruce.duplicated(subset=['Radicado'], keep=False)]


# df sin duplicados drop_dulicates(keep='last')
df_cruce = df_cruce.drop_duplicates(subset=['FACTURA IQ'], keep='last')


# Primer merge por FACTURA IQ
merge1 = df_base.merge(
    df_grouped,
    how='left',
    left_on='FACTURA IQ',
    right_on='Radicado',
    indicator=True)


# Revision colums merg
merge1.columns


# Filtrar lo que no cruzo
sin_cruce = merge1[merge1['_merge'] == 'left_only'].drop(columns=['_merge']).copy()
sin_cruce = sin_cruce[df_base.columns]


# Segundo merge por RADICADO PADRE
merge2 = pd.merge(sin_cruce,
    df_grouped,                # tu DataFrame derecho original
    how='left',
    left_on='RADICADO PADRE',
    right_on='Radicado'
)


# Revision colums merge
merge2.columns


# Combinar los resultados del primer merge exitoso con el segundo
df_resultado = pd.concat([
    merge1[merge1['_merge'] == 'both'],
    merge2
], ignore_index=True)


# Eliminar columna de df_resultado
df_resultado.drop(columns=['_merge'], inplace=True)


# Revisar Faltantes
no_cruzados = df_resultado[df_resultado['Radicado'].isna()]



# =========================================
# 5.______________ EXPORTACIÓN
# =========================================


with pd.ExcelWriter(RUTA_EXPORTACION, engine='openpyxl') as writer:
    df_resultado.to_excel(writer, index=False, sheet_name='Detalle')

print(f"Archivo Excel exportado exitosamente como '{RUTA_EXPORTACION}'")
print('='*14)



#⏱️
end = time.time()


print("🧱" * 14)
show_time(begin, end)
print("🧱" * 14)
print("✅ Proceso completado.")
print("🧱" * 14)