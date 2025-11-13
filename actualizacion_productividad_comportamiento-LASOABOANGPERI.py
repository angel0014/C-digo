# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 08:01:13 2024

@author: angperilla
"""

"""
    Script para actualizar el dash de Productividad 2024
    
    Insumos:
        1. Reportes productividad IQ
        2. Lista Auditores
        3. Reporte Metas Productividades
        4. Listado Festivos 2024
        
    Salidas:
        Información consolidada y cruzada de los insumos iniciales
"""
import pandas as pd
from datetime import datetime
import os
import glob
# import holidays

# import matplotlib.pyplot as plt


# Obtener la ruta actual
ruta_actual = os.getcwd()

# Obtener ruta al directorio data
ruta_data  = os.path.join(ruta_actual, 'data')

# Obtiene la fecha y hora actual
fecha_actual = datetime.now()

# Extrae el mes actual como un número
# mes_actual = fecha_actual.month
# print(mes_actual)

mes_actual = 12

def listar_archivos_xlsx_en_data(ruta_data):
    """
        Lista todos los archivos .xlsx en la carpeta 'data' dentro de la ruta actual.
        
        Returns:
        list: Una lista de nombres de archivos .xlsx encontrados en la carpeta 'data'.
        
    """

    # Verificar si la carpeta 'data' existe
    if not os.path.exists(ruta_data):
        print("La carpeta 'data' no existe.")
        return []
    
    # Buscar todos los archivos .xlsx en el directorio 'data'
    archivos_xlsx = glob.glob(os.path.join(ruta_data, "*.xlsx"))
   
    # Devolver la lista de archivos .xlsx encontrados
    return archivos_xlsx


# Listar archivos .xlsx en la carpeta 'data'
archivos = listar_archivos_xlsx_en_data(ruta_data)

# Almacenar los DataFrames
dataframes = []


if len(archivos) == mes_actual: 
    # Iterar sobre el listado de archivos de Excel
    for archivo in archivos:
        
        # Ruta completa del archivo
        ruta_archivo = os.path.join(ruta_data, archivo)
        # print(ruta_archivo)
        
        # Lee cada archivo Excel a partir de la fila 4
        df = pd.read_excel(ruta_archivo, skiprows=3)
        
        # Añade el DataFrame a la lista
        dataframes.append(df)
    print('Archivos leídos correctamente')
        
else:
    print(f"El número de archivos ({len(archivos)}) no coincide con el mes actual ({mes_actual}).")
    
# Concatena todos los DataFrames en uno solo
df_productividad = pd.concat(dataframes, ignore_index=True)
print(df_productividad.info())

#============================================================================
#__________________________ Transformaciones Df______________________________
#============================================================================

# Convertir las columnas a tipo datetime
df_productividad['fechainicioNormal'] = pd.to_datetime(df_productividad['fechainicio'])
df_productividad['fechafinNormal'] = pd.to_datetime(df_productividad['fechafin'])


# Convertir las columnas a tipo datetime
df_productividad['fechainicioNormal'] = df_productividad['fechainicioNormal'].dt.date
df_productividad['fechafinNormal'] = df_productividad['fechafinNormal'].dt.date


# Extraer la hora y guardarla en nuevas columnas
df_productividad['fechainicioHora'] = df_productividad['fechainicio'].dt.strftime('%H:%M:%S')
df_productividad['fechafinHora'] = df_productividad['fechafin'].dt.strftime('%H:%M:%S')


# Calcular la diferencia en minutos entre fechainicioHora y fechafinHora
df_productividad['diferencia_minutos'] = (df_productividad['fechafin'] - df_productividad['fechainicio']).dt.total_seconds() / 60


# Filtrar las filas que tengan una diferencia de más de 60 minutos
df_filtrado = df_productividad[df_productividad['diferencia_minutos'] > 60]
print(df_filtrado)


# Definir los festivos de Colombia
# co_holidays = holidays.Colombia(years=2024)


# # Identificar si la fecha es un festivo
# df_productividad['es_festivo'] = df_productividad['fechafinNormal'].isin(co_holidays)
# festivos_df = df_productividad[df_productividad['es_festivo']]

# # Filtra las filas donde el mes es agosto (8) usando la nueva columna
# df_agosto = df_productividad[df_productividad['fechainicioNormal'].dt.month == 8]   


# Ver estadísticas descriptivas del DataFrame
estadisticas = df.describe()


#=============================================================================
#________________________________ Cruces Df __________________________________
#=============================================================================


# Crear una llave única combinando las columnas 'numeroradicacion', 'Usuario' y 'Modulo'
df_productividad['llave'] = df_productividad['numeroradicacion'].astype(str) + '_' + df_productividad['Usuario'] + '_' + df_productividad['Modulo']



#__________________________ Cruce Tabla Auditores ___________________________


df_auditores = pd.read_excel(os.path.join(ruta_actual, 'Tabla_Auditores.xlsx'))
df_auditores.info()


# Cruce 
df_merged = pd.merge(df_productividad, df_auditores, how='left', left_on='Usuario', right_on='Usuario IQ') 


# revisar duplicados
revisar_merged = df_merged[df_merged['numeroradicacion']=='CMVIQ036000000196912']

# # Quitar duplicados del DataFrame df_merged
# df_merged = df_merged.drop_duplicates(subset=['llave'])


# Ordenar el DataFrame por 'fechafin' en orden descendente
df_merged = df_merged.sort_values(by='fechafin', ascending=False)


# Eliminar duplicados por la columna 'llave', manteniendo el primer registro
df_merged = df_merged.drop_duplicates(subset='llave', keep='first')


# Mostrar el DataFrame resultante
print(df_merged)


# # Revisar los valores duplicados por llaves
duplicados_merged = df_merged[df_merged.duplicated(subset=['llave'], keep=False)]



#=============================================================================
#________________________________ Exportar __________________________________
#=============================================================================

df_tecnico = df_merged[df_merged['Modulo']=='EvaluacionTecnicaApp']
df_tecnico.to_excel('resultado_productividad_tecnicos.xlsx', index=False, float_format="%.2f")


# Exportar el DataFrame filtrado a un archivo Excel
df_merged.to_excel('resultado_productividad_comportamiento.xlsx', index=False, float_format="%.2f")

print("El DataFrame filtrado se ha exportado correctamente!")




#_________________________ Grafica Comportamiento Horas _____________________


# # Extraer la hora en formato HH
# df_productividad['fechainicioHora'] = df_productividad['fechainicio'].dt.hour
# df_productividad['fechafinHora'] = df_productividad['fechafin'].dt.hour

# # Crear histogramas
# plt.figure(figsize=(12, 6))

# plt.subplot(1, 2, 1)
# plt.hist(df_productividad['fechainicioHora'], bins=24, edgecolor='black')
# plt.title('Distribución de fechainicioHora')
# plt.xlabel('Hora')
# plt.ylabel('Frecuencia')

# plt.subplot(1, 2, 2)
# plt.hist(df_productividad['fechafinHora'], bins=24, edgecolor='black')
# plt.title('Distribución de fechafinHora')
# plt.xlabel('Hora')
# plt.ylabel('Frecuencia')

# plt.tight_layout()
# plt.show()

#____________________________________________________________________________


