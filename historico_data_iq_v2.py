# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 21:21:12 2025

@author: angperilla
"""

"""
    Script para automatizar data historica de iq.
    
    Insumos:
        1. Data procesada iq (10 Archivos)
        
    Salidas:
        1. Data Historica por Tabla iq (10 Archivos)
"""


import pandas as pd
import os


# ::::::::::::::::::::::::::::::::::::::::::::
# ================ Directorios
# ::::::::::::::::::::::::::::::::::::::::::::

    
# Entrada    
# Data Iq Procesada
directorio_insumos = r'C:\Users\angperilla\Scripts\Data IQ\Insumos'
año_2025 = '2025'


# Salida
# Data Historica
directorio_historico = r'C:\Users\angperilla\Scripts\Data IQ\Salidas\Historica'


def nombre_mes(mes):
    # Diccionario de meses
    meses = {
        1: "1. Enero",
        2: "2. Febrero",
        3: "3. Marzo",
        4: "4. Abril",
        5: "5. Mayo",
        6: "6. Junio",
        7: "7. Julio",
        8: "8. Agosto",
        9: "9. Septiembre",
        10: "10. Octubre",
        11: "11. Noviembre",
        12: "12. Diciembre"
    }
    # Devolver el nombre del mes correspondiente al número dado
    return meses.get(mes, "Mes inválido")


#  ___________________________________________
#               ACTUALIZAR DATA
#  ___________________________________________

# Aquí es la información de insumos de lo procesado

#####################################

mes_insumos = '10. Octubre' 
quincena = 2


#####################################


# Mes historico de la Data
mes_historico = nombre_mes(int(f'{mes_insumos.split(" ")[0].replace(".", "")}')-2) # Agosto (-2)
print(mes_historico)




# _____________________________________________
# _____________________________________________


# Ruta Quincena
if quincena == 1:
    primera_quincena = f'{quincena}.1 {mes_insumos.split(" ")[1]}'
    # Ruta Insumos
    ruta_folder = os.path.join(directorio_insumos, año_2025, mes_insumos)
    print(ruta_folder)
   
elif quincena == 2:
    segunda_quincena = f'{quincena-1}.2 {mes_insumos.split(" ")[1]}'
    # Ruta Insumos
    ruta_folder = os.path.join(os.path.join(directorio_insumos, año_2025, mes_insumos))
    print(ruta_folder)


# _____________________________________________
# _____________________________________________

ruta_procesados = ruta_folder
print(ruta_procesados)


# ruta_historicos = os.path.join(directorio_historico, año_2025, mes_historico, '01')
# print(ruta_historicos)

ruta_historicos = os.path.join(directorio_historico, año_2025, mes_historico)
print(ruta_historicos)

ruta_exportacion = os.path.join(directorio_historico, año_2025, mes_insumos)
print(ruta_exportacion)


# Diccionario con los nombres de los archivos
files_dict = {
    'Procesado_Detalle_Anulados_2025.txt': ('HistoricoAnulados2025.txt', 'PJ_Anulados_2025_pro.txt', 'PJ_Anulados_2025_pro.parquet', 'HistoricoAnulados2025.parquet'), 
    'Procesado_Detalle_Devoluciones_2025.txt': ('HistoricoDevoluciones2025.txt', 'PJ_ReporteObjecionDev_2025_pro.txt', 'PJ_ReporteObjecionDev_2025_pro.parquet', 'HistoricoDevoluciones2025.parquet'), 
    'Procesado_Detalle_Factura_2025.txt': ('HistoricoFacturas2025.txt', 'PJ_DetalleFactura_2025_pro.txt', 'PJ_DetalleFactura_2025_pro.parquet', 'HistoricoFacturas2025.parquet'),
    'Procesado_Detalle_Liquidacion_2025.txt': ('HistoricoLiquidaciones2025.txt', 'PJ_DetalleLiquidacion_2025_pro.txt', 'PJ_DetalleLiquidacion_2025_pro.parquet', 'HistoricoLiquidaciones2025.parquet'), 
    'Procesado_Detalle_Liquidacion_RIQ_CIQ_2025.txt': ('HistoricoLiquidaciones_RIQ_CIQs2025.txt', 'PJ_detalleLiquidacion_RIQ_CIQ_2025_pro.txt', 'PJ_detalleLiquidacion_RIQ_CIQ_2025_pro.parquet', 'HistoricoLiquidaciones_RIQ_CIQs2025.parquet'), 
    'Procesado_Detalle_Manual_2025.txt': ('HistoricoManuales2025.txt', 'PJ_DetalleManual_2025_pro.txt', 'PJ_DetalleManual_2025_pro.parquet', 'HistoricoManuales2025.parquet'), 
    'Procesado_Detalle_MAOS_2025.txt': ('HistoricoMAOS2025.txt', 'PJ_MAOS_2025_pro.txt', 'PJ_MAOS_2025_pro.parquet', 'HistoricoMAOS2025.parquet'), 
    'Procesado_Detalle_Notificacion_2025.txt': ('HistoricoNotificaciones2025.txt', 'PJ_Detallenotificacion_2025_pro.txt', 'PJ_Detallenotificacion_2025_pro.parquet', 'HistoricoNotificaciones2025.parquet'), 
    'Procesado_Detalle_Reclamacion_2025.txt': ('HistoricoReclamaciones2025.txt', 'PJ_DetalleReclamacion_2025_pro.txt', 'PJ_DetalleReclamacion_2025_pro.parquet', 'HistoricoReclamaciones2025.parquet'), 
    'Procesado_Detalle_Victima_2025.txt': ('HistoricoVictimas2025.txt', 'PJ_DetalleVictima_2025_pro.txt', 'PJ_DetalleVictima_2025_pro.parquet', 'HistoricoVictimas2025.parquet')
}


# Lista para almacenar archivos que no se pudieron concatenar y sus diferencias de columnas
no_concatenados = []

for procesado, (historico, anterior_txt, anterior_parquet, historico_parquet) in files_dict.items():
    # Leer archivo procesado
    archivo_procesado = os.path.join(ruta_procesados, procesado)
    df_procesado = pd.read_csv(archivo_procesado, sep='|', encoding='utf-8', low_memory=False, decimal='.')
    
    # Leer archivo histórico
    archivo_historico = os.path.join(ruta_historicos, historico)
    df_historico = pd.read_csv(archivo_historico, sep='|', encoding='utf-8', low_memory=False, decimal='.')
    
    # Concatenar DataFrames procesado e histórico si tienen las mismas columnas o si la diferencia de columnas es de tamaño 1
    diferencia_columnas = set(df_procesado.columns).symmetric_difference(set(df_historico.columns))
    
    if len(diferencia_columnas) == 0:
        df_concatenado = pd.concat([df_procesado, df_historico])
        
        # Exportar DataFrame concatenado en formato .txt con el nombre original en la ruta de exportación
        df_concatenado.to_csv(os.path.join(ruta_exportacion, historico), sep='|', encoding='utf-8', index=False)
        
        # Exportar DataFrame concatenado en formato .txt con el nombre original en la ruta de exportación
        df_concatenado.to_csv(os.path.join(ruta_exportacion, anterior_txt), sep='|', encoding='utf-8', index=False)
        
        # Exportar DataFrame con nombres modificados en formato .parquet en la ruta de exportación
        df_concatenado.to_parquet(os.path.join(ruta_exportacion, anterior_parquet), index=False)
        
        # Exportar DataFrame con nombres modificados en formato .parquet en la ruta de exportación
        df_concatenado.to_parquet(os.path.join(ruta_exportacion, historico_parquet), index=False)
    
    elif len(diferencia_columnas) == 1:
        print(f"Archivos {procesado} y {historico} tienen una diferencia de una columna: {diferencia_columnas}.")
        df_concatenado = pd.concat([df_procesado, df_historico])
        
        # Exportar DataFrame concatenado en formato .txt con el nombre original en la ruta de exportación
        df_concatenado.to_csv(os.path.join(ruta_exportacion, historico), sep='|', encoding='utf-8', index=False)
        
        # Exportar DataFrame concatenado en formato .txt con el nombre original en la ruta de exportación
        df_concatenado.to_csv(os.path.join(ruta_exportacion, anterior_txt), sep='|', encoding='utf-8', index=False)
        
        # Exportar DataFrame con nombres modificados en formato .parquet en la ruta de exportación
        df_concatenado.to_parquet(os.path.join(ruta_exportacion, anterior_parquet), index=False)
        
        # Exportar DataFrame con nombres modificados en formato .parquet en la ruta de exportación
        df_concatenado.to_parquet(os.path.join(ruta_exportacion, historico_parquet), index=False)
    
    else:
        # Almacenar el nombre del archivo y la diferencia de columnas
        no_concatenados.append((procesado, historico, diferencia_columnas))

# Imprimir archivos que no se pudieron concatenar y sus diferencias de columnas
for item in no_concatenados:
    print(f"No se pudo concatenar {item[0]} con {item[1]}. Diferencia de columnas: {item[2]}")

print(" ✅ Proceso completado. Archivos exportados exitosamente.")



# =========================================================================
# =========================================================================
# =========================================================================



# # Directorios
# directorio_insumos = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Proyectos\2. Carteras\Insumos\Data IQ'
# año='2025'



# #  ___________________________________________
# #               ACTUALIZAR DATA
# #  ___________________________________________


# mes_insumos = '1. Enero' #### Cambiar Mes de Insumos ####
# quincena = 1 #### Cambiar Quincena ####


# # ____________________________________________
# # ____________________________________________


# if quincena == 1:
#     primera_quincena = f"{mes_insumos.split(' ')[0]}1 {mes_insumos.split(' ')[1]}"
#     # Ruta Insumos
#     ruta_folder = os.path.join(directorio_insumos, año, mes_insumos, primera_quincena)
#     print(ruta_folder)
   
# elif quincena == 2:
#     segunda_quincena = f"{mes_insumos.split(' ')[0]}2 {mes_insumos.split(' ')[1]}"
#     # Ruta Insumos
#     ruta_folder = os.path.join(directorio_insumos, año, mes_insumos, segunda_quincena)
#     print(ruta_folder)
  
    
# # Ruta Historico

# directorio_historico = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Proyectos\2. Carteras\Salidas\Data IQ\Historica'
# ruta_historico = os.path.join(directorio_historico, año, mes_insumos)
# print(ruta_historico)


# # Codigo para manejar historico primer Mes donde la data Procesada es la misma historica
# for procesado, (historico, nombre_txt, nombre_parquet) in files_dict.items():
    
#     # Ruta archivo procesado
#     archivo_procesado = os.path.join(ruta_folder, procesado)
#     print(archivo_procesado)
    
#     # lectura df
#     df_procesado = pd.read_csv(archivo_procesado, sep='|', encoding='utf-8', low_memory=False, decimal='.')
    
#     # Rutas Exportacion
#     ruta_exportar_txt = os.path.join(ruta_historico, nombre_txt)
#     ruta_exportar_parquet = os.path.join(ruta_historico, nombre_parquet)
    
#     # Exporta txt
#     df_procesado.to_csv(ruta_exportar_txt, sep='|', encoding='utf-8', index=False)
    
#     # Exportar parquet
#     df_procesado.to_parquet(ruta_exportar_parquet, index=False)
    
    
    
    
    
    
    
    






