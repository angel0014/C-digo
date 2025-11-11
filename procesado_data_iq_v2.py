# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 17:09:45 2025

@author: angperilla
"""

"""
    Script para automatizar el proceso de Lectura de la Data IQ.
    
    Proceso:
        1. Lectura de archivos primarios de IQ de acuerdo a Encoding.
        2. Procesar archivos primarios y exportarlos.
    
"""

import pandas as pd
import os
import chardet



# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# ___________________ Parte 1: Revisar Archivos Primarios IQ ________________
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: 
    
# Directorios
directorio_insumos = r'C:\Users\angperilla\Scripts\Data IQ\Insumos'
año='2025'



# ____________________________________________
#            ACTUALIZAR INFORMACIÓN
# ____________________________________________

# :::::::::::::::::::::::::::::::::::::::::::::::::
# ====== Cambiar información de acuerdo al Mes
# :::::::::::::::::::::::::::::::::::::::::::::::::
   
mes_insumos = '10. Octubre' #### Cambiar Mes de Insumos ####
quincena = 2 #### Cambiar Quincena ####

# _____________________________________________
# _____________________________________________


# Ruta Quincena
if quincena == 1:
    primera_quincena = f"{quincena}.1 {mes_insumos.split(' ')[1]}"
    # Ruta Insumos
    ruta_folder = os.path.join(directorio_insumos, año, mes_insumos, primera_quincena,'Original')
    print(ruta_folder)
   
elif quincena == 2:
    segunda_quincena = f"{quincena-1}.2 {mes_insumos.split(' ')[1]}"
    # Ruta Insumos
    ruta_folder = os.path.join(directorio_insumos, año, mes_insumos, segunda_quincena,'Original')
    print(ruta_folder)
  

# Archivos Requeridos
archivos_requeridos = ['PJ_Anulados.txt', 
                       'PJ_DetalleDevolucionesObjeciones.txt', 
                       'PJ_DetalleFactura Finalizados.txt', 
                       'PJ_DetalleFactura_Obj_Dev.txt', 
                       'PJ_DetalleLiquidacion.txt', 
                       'PJ_DetalleLiquidacion_RIQ_CIQ.txt', 
                       'PJ_DetalleManual.txt', 
                       'PJ_Detallenotificación.txt', 
                       'PJ_DetalleReclamacion Finalizados.txt', 
                       'PJ_DetalleReclamacion Obj-Dev.txt', 
                       'PJ_DetalleVictima.txt', 
                       'PJ_MAOS.txt']


def revisar_archivos_primarios_iq(ruta_folder, archivos_requeridos):
    
    # Obtener lista archivos
    archivos_folder = os.listdir(ruta_folder)
    
    if len(archivos_folder)!=12:
        return False
    
    # Obtener Faltantes
    archivos_faltantes = [file for file in archivos_folder if file not in archivos_requeridos]
    # print(archivos_faltantes)
    
    return not archivos_faltantes

    
# :::::::::::::::::::::::::::::::::::::::::::::::::
# ================== Ejecución
# :::::::::::::::::::::::::::::::::::::::::::::::::

    

resultado = revisar_archivos_primarios_iq(ruta_folder, archivos_requeridos)
print(resultado)

if resultado:
    print("Los nombres de las tablas de IQ están correctos")
else:
    print("Por favor revisar los nombres de las tablas de IQ porque están incorrectos ")


# ========================================================================
# ______________________________ Fin Parte 1 _____________________________
# ========================================================================



# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# ___________________ Parte 2: Revisar Archivos Primarios IQ ______________
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: 
  

def detectar_encoding(file_path):
    """
        Detectar el tipo de encoding en la lectura del archivo.
        
            file_path: Ruta del archivo a leer (str).
        
            return: encoding si es None entonces "ansi"
    """
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    result = chardet.detect(raw_data)
    return result['encoding'] if result['encoding'] is not None else 'ansi'


# Función para leer un archivo y guardarlo en un DataFrame
def leer_archivo(file_path, encoding):
    try:
        return pd.read_csv(file_path, encoding=encoding, sep='|', decimal='.', low_memory=False)   
    except UnicodeDecodeError:
        # Intentar con ANSI si el encoding detectado falla
        return pd.read_csv(file_path, encoding='ansi', sep='|', decimal='.', low_memory=False)
    
   


# Función para aplicar transformaciones a las columnas especificadas en un DataFrame
def convertir_columnas_a_numericas(df, columnas_a_convertir):
    for columna in columnas_a_convertir:
        if columna in df.columns:
            df[columna] = df[columna].astype(str)
            df[columna] = df[columna].str.replace(',', '.')
            df[columna] = pd.to_numeric(df[columna], errors='coerce')
    return df


def procesar_y_exportar_archivo(file_path, output_name, transformaciones, columnas_a_convertir=None):
    encoding = detectar_encoding(file_path)
    df = leer_archivo(file_path, encoding)
    
    # Eliminar columnas "Unnamed"
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Eliminar filas vacías
    df.dropna(how='all', inplace=True)
    
    # Aplicar transformaciones específicas
    for transformacion in transformaciones:
       exec(transformacion)
    
    # Aplicar transformaciones a las columnas especificadas
    if columnas_a_convertir:
        df = convertir_columnas_a_numericas(df, columnas_a_convertir)
    
    df.info()
    df.to_csv(output_name, encoding='utf-8', sep='|', decimal='.', index=False)
    


def concatenar_y_exportar_archivos(file_paths, output_name, transformations, columnas_a_convertir=None):
    dfs = []
    for file_path in file_paths:
        encoding = detectar_encoding(file_path)
        df = leer_archivo(file_path, encoding)
        
        # Eliminar columnas "Unnamed"
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # Eliminar filas vacías
        df.dropna(how='all', inplace=True)
        
        # Aplicar transformaciones específicas
        for transformation in transformations:
            exec(transformation)
        
        # Aplicar transformaciones a las columnas especificadas
        if columnas_a_convertir:
            df = convertir_columnas_a_numericas(df, columnas_a_convertir)
        
        dfs.append(df)
    
    concatenated_df = pd.concat(dfs, ignore_index=True)
    concatenated_df.to_csv(output_name, encoding='utf-8', sep='|', decimal='.', index=False)
    
    

# Archivos Requeridos y sus transformaciones específicas
archivos_transformaciones = {
    'PJ_Anulados.txt': [
        "df.rename(columns={'Numeroradicacion': 'NumeroRadicacion'}, inplace=True)"
    ],
    'PJ_DetalleDevolucionesObjeciones.txt': [],
    # 'PJ_DetalleFactura Finalizados.txt': [],
    # 'PJ_DetalleFactura_Obj_Dev.txt': [],
    'PJ_DetalleLiquidacion.txt': [
        "df.rename(columns={'[Observacion_servicio]': 'Observacion_servicio', '[NotaCredito]': 'NotaCredito', '[Observacion_de_la_glosa]': 'Observacion_de_la_glosa'}, inplace=True)"
    ],
    'PJ_DetalleLiquidacion_RIQ_CIQ.txt': [],
    'PJ_DetalleManual.txt': [
        "df.rename(columns={'FACTURA IQ': 'NumeroRadicacion'}, inplace=True)"],
    'PJ_Detallenotificación.txt': [
        "df.rename(columns={'FECHA NOTIFICACION': 'F.NOTIFICACION'}, inplace=True)"
    ],
    # 'PJ_DetalleReclamacion Finalizados.txt': [],
    # 'PJ_DetalleReclamacion Obj-Dev.txt': [],
    'PJ_DetalleVictima.txt': [],
    'PJ_MAOS.txt': []
}    



# Columnas a convertir para cada archivo
columnas_a_convertir_dict = {
    # 'PJ_DetalleFactura Finalizados.txt': ['Valor'],
    # 'PJ_DetalleFactura_Obj_Dev.txt': ['Valor'],
    'PJ_DetalleLiquidacion.txt': ['Valor_Servicio','Valor_Aprobado_Inicial','Valor_glosado_Inicial', 'ValorAprobado', 'valorGlosaTotal'],
    'PJ_DetalleLiquidacion_RIQ_CIQ.txt': ['Valor_Servicio','ValorGlosaTotal','ValorAprobado', 'ValorAIPS', 'ValorSRTAIPS', 'ValorRatificado'],
    # 'PJ_DetalleReclamacion Finalizados.txt': ['Valor'],
    # 'PJ_DetalleReclamacion Obj-Dev.txt': ['Valor'],
    'PJ_MAOS.txt': ['Valor unitario facturado', 'Valor total facturado']
}



# Nombres de archivos exportados
nombres_exportados = {
    'PJ_Anulados.txt': 'Procesado_Detalle_Anulados_2025.txt',
    'PJ_DetalleDevolucionesObjeciones.txt': 'Procesado_Detalle_Devoluciones_2025.txt',
    # 'PJ_DetalleFactura Finalizados.txt': 'Procesado_Detalle_Factura.txt',
    # 'PJ_DetalleFactura_Obj_Dev.txt': 'Procesado_Detalle_Factura.txt',
    'PJ_DetalleLiquidacion.txt': 'Procesado_Detalle_Liquidacion_2025.txt',
    'PJ_DetalleLiquidacion_RIQ_CIQ.txt': 'Procesado_Detalle_Liquidacion_RIQ_CIQ_2025.txt',
    'PJ_DetalleManual.txt': 'Procesado_Detalle_Manual_2025.txt',
    'PJ_Detallenotificación.txt': 'Procesado_Detalle_Notificacion_2025.txt',
    # 'PJ_DetalleReclamacion Finalizados.txt': 'Procesado_Detalle_Reclamacion.txt',
    # 'PJ_DetalleReclamacion Obj-Dev.txt': 'Procesado_Detalle_Reclamacion.txt',
    'PJ_DetalleVictima.txt': 'Procesado_Detalle_Victima_2025.txt',
    'PJ_MAOS.txt': 'Procesado_Detalle_MAOS_2025.txt'
}



# Procesar archivos individuales con sus transformaciones específicas
print(resultado)

if resultado:

    for archivo, transformaciones in archivos_transformaciones.items():
        
        
        input_path = os.path.join(ruta_folder, archivo)
        
        output_name = os.path.join(ruta_folder, nombres_exportados[archivo])
        
        columnas_a_convertir = columnas_a_convertir_dict.get(archivo, None)
        
        procesar_y_exportar_archivo(input_path, output_name, transformaciones, columnas_a_convertir)
        
    
    # Concatenar y exportar archivos con sus transformaciones específicas
    concatenar_y_exportar_archivos(
        [os.path.join(ruta_folder, 'PJ_DetalleFactura Finalizados.txt'), os.path.join(ruta_folder, 'PJ_DetalleFactura_Obj_Dev.txt')],
        os.path.join(ruta_folder, 'Procesado_Detalle_Factura_2025.txt'),
        [
            "df.rename(columns={'Fecha_Aviso': 'fechaaviso', 'NumeroRadicacion': 'numeroradicacion','Numerofactura': 'numerofactura','FechaFactura': 'fechafactura','Valor': 'valor'}, inplace=True)", "df.rename(columns={'F.AVISO': 'fechaaviso', 'Radicacion': 'numeroradicacion','NUMERO FACTURA': 'numerofactura','F.FACTURA': 'fechafactura','VLR RADICACION': 'valor'}, inplace=True)"
        ], #fechaaviso|numeroradicacion|numerofactura|fechafactura|valor
        ['valor']
    )
    
    concatenar_y_exportar_archivos(
        [os.path.join(ruta_folder, 'PJ_DetalleReclamacion Finalizados.txt'), os.path.join(ruta_folder, 'PJ_DetalleReclamacion Obj-Dev.txt')],
        os.path.join(ruta_folder, 'Procesado_Detalle_Reclamacion_2025.txt'),
        [],
        ['Valor']
    )
    
    print(" ✅Archivos procesados y exportados exitosamente.")
else:
    print("Por favor revisar los nombres de los archivos primarios o la cantidad de los mismos")
    
    
# def rename_and_load_files(dir_path, new_names_dict, output_dir):
#     dataframes_mes = {}

#     # Iterar sobre los archivos en el directorio
#     for original_name, new_name in new_names_dict.items():
#         file_path = os.path.join(dir_path, original_name)
        
#         # Leer el archivo en un DataFrame
#         df = pd.read_csv(file_path, sep='|', encoding='utf-8', decimal='.', low_memory=False)
        
#         # Eliminar columnas "Unnamed"
#         df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
#         # Eliminar filas vacías
#         df.dropna(how='all', inplace=True)
        
#         # Agregar el DataFrame al diccionario con el nuevo nombre
#         dataframes_mes[new_name] = df
        
#         # Exportar el DataFrame con el nuevo nombre en el directorio de salida
#         output_file_path = os.path.join(output_dir, new_name)
#         df.to_csv(output_file_path, sep='|', encoding='utf-8', decimal='.', index=False)

#     return dataframes_mes




# old_names_dict = {
#     'Procesado_Detalle_Anulados_2025.txt':'PJ_Anulados_2025_pro.txt', 
#     'Procesado_Detalle_Devoluciones_2025.txt':'PJ_ReporteObjecionDev_2025_pro.txt', 
#     'Procesado_Detalle_Factura_2025.txt':'PJ_DetalleFactura_2025_pro.txt',
#     'Procesado_Detalle_Liquidacion_2025.txt':'PJ_DetalleLiquidacion_2025_pro.txt', 
#     'Procesado_Detalle_Liquidacion_RIQ_CIQ_2025.txt':'PJ_detalleLiquidacion_RIQ_CIQ_2025_pro.txt', 
#     'Procesado_Detalle_Manual_2025.txt':'PJ_DetalleManual_2025_pro.txt', 
#     'Procesado_Detalle_MAOS_2025.txt':'PJ_MAOS_2025_pro.txt', 
#     'Procesado_Detalle_Notificacion_2025.txt':'PJ_Detallenotificacion_2025_pro.txt', 
#     'Procesado_Detalle_Reclamacion_2025.txt':'PJ_DetalleReclamacion_2025_pro.txt', 
#     'Procesado_Detalle_Victima_2025.txt':'PJ_DetalleVictima_2025_pro.txt'
# }




# dataframes_mes = rename_and_load_files(ruta_folder, old_names_dict, ruta_folder)

