# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 09:29:32 2024

@author: angperilla
"""



"""
    Script para revisar faltantes del proceso de la Data IQ 2024.
    
    Proceso: Liquidado de acuerdo a <Fecha Liquidación>. Quitando Anulados y
    Manuales esa es la Base Consolidada, es decir la totalidad de los 
    registros segun la HR del perido a evaluar.
    
    Insumos: 
        1. HR Periodo Evaluar
        2. Historico Data IQ 2024 (Mes Diciembre)
"""


import pandas as pd
import os
import chardet
import time


# #######################
#  ===  DIRECTORIOS  ===
# #######################


# RUTAS INSUMOS Y DE EXPORTACION 

directorio_salida = r'C:\Users\angperilla\Scripts\Data IQ\Salidas\Historica'
AÑO ='2025'
MES = '6. Junio'
INSUMO_HISTORICO = os.path.join(directorio_salida, AÑO, MES)
print(INSUMO_HISTORICO)



directorio_faltantes =  r'C:\Users\angperilla\Scripts\Data IQ\Salidas\Faltantes'
RUTA_EXPORTACION = os.path.join(directorio_faltantes, AÑO, MES)
print(RUTA_EXPORTACION)



# INSUMO HR
 
directorio_hr = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Proyectos\HR'
año_hr = '2025'
archivo_hr = 'HR_20200101_20250701_0.parquet'
INSUMO_HR = os.path.join(directorio_hr, año_hr, archivo_hr)
print(INSUMO_HR)

FECHA_LIQUIDACION_INICIO = '01-01-2025' # Enero
FECHA_LIQUIDACION_FIN = '30-06-2025' # Junio



# ########################
# === 1. LECTURA HR  ===
# ########################

# ⏱️ 
start_time = time.time()

# _________ LECTURA
 

data_hr = pd.read_parquet(INSUMO_HR)


print("🧱" * 14)
data_hr.info()


# _________ PRE-PROCESAMIENTO

# CONVERSION FECHAS Y FILTRO DE RENGO INFORMACION

# ____ CONVERSION FECHAS    

data_hr['F.CREA FACTURA'] = pd.to_datetime(data_hr['F.CREA FACTURA'], format='%Y/%m/%d')
data_hr['F.LIQUIDACION'] = pd.to_datetime(data_hr['F.LIQUIDACION'], format='%Y/%m/%d')

# LIQUIDADO 2025
hr_liquidado = data_hr[pd.to_datetime(data_hr['F.LIQUIDACION'], format='%Y/%m/%d').isin(pd.date_range(FECHA_LIQUIDACION_INICIO, FECHA_LIQUIDACION_FIN))]

# # DUPLICADOS LIQUIDADO (*** REVISAR)
# duplicados_liquidado = hr_liquidado[hr_liquidado.duplicated(subset='FACTURA IQ', keep=False)]




# ##########################################
# === 2.  EXCLUIR ANULADOS Y MANUALES  ===
# ##########################################




# _________ ANULADOS
 
df_anulados = pd.read_csv(os.path.join(INSUMO_HISTORICO, "HistoricoAnulados2025.txt"), 
                          sep="|", decimal=".", low_memory=False)

# Encontrar duplicados basados en la columna 'FACTURA'
duplicados_anu = df_anulados[df_anulados.duplicated(subset='NumeroRadicacion', keep=False)]

# Mantener la última ocurrencia de cada duplicado
df_anulados = df_anulados.drop_duplicates(keep='last')

df_anulados = df_anulados.reset_index(drop=True)




# _________ MANUALES

df_manuales = pd.read_csv(os.path.join(INSUMO_HISTORICO, "HistoricoManuales2025.txt"), 
                          sep="|", decimal=".", low_memory=False)

# Encontrar duplicados basados en la columna 'FACTURA'
duplicados_man = df_manuales[df_manuales.duplicated(subset='NumeroRadicacion', keep=False)]

# Mantener la última ocurrencia de cada duplicado
df_manuales = df_manuales.drop_duplicates(keep='last')

df_manuales = df_manuales.reset_index(drop=True)




# _________ VALIDACIONES

# Cruce 
# fal_anu_der = pd.merge(hr_liquidado, df_anulados, left_on='FACTURA IQ', right_on='Numeroradicacion', how='right')


fal_anu = df_anulados[~df_anulados['NumeroRadicacion'].isin(hr_liquidado['FACTURA IQ'])]
print(len(fal_anu))


fal_man = df_manuales[~df_manuales['NumeroRadicacion'].isin(hr_liquidado['FACTURA IQ'])]
print(len(fal_man))



# #########################################
#  === 3.  PROCESO FALTANTES DATA IQ  ===
# #########################################


    

# _________  TABLA PRINCIPAl


# Quitar anulados de mi tabla principal
tabla_principal = hr_liquidado[~hr_liquidado['FACTURA IQ'].isin(df_anulados['NumeroRadicacion'])]


# Quitar manuales de mi tabla principal
tabla_principal = tabla_principal[~tabla_principal['FACTURA IQ'].isin(df_manuales['NumeroRadicacion'])]


usu_reserva = tabla_principal['USUARIO CREADOR RESERVA'].value_counts()
print(usu_reserva)


usu_liquidador = tabla_principal['ANALISTA LIQUIDADOR'].value_counts()
print(usu_liquidador)


df_filtrado = tabla_principal[(tabla_principal['USUARIO CREADOR RESERVA'] != 'PROCESO AUTOMATICO DE SINIESTROS') & (tabla_principal['USUARIO CREADOR RESERVA'] != 'PROCESO AUTOMATICO WS')]
estados_df_filtrado = df_filtrado['ESTADO ACTUAL FACTURA'].value_counts()


# estados_usu_reserva = df_filtrado['USUARIO CREADOR RESERVA'].unique()


# estados_liquidador = df_filtrado['ANALISTA LIQUIDADOR'].unique()
# print(estados_liquidador)



# _________  FILTRO ESTADOS VALIDOS

    
tabla_principal = tabla_principal[~tabla_principal['ESTADO ACTUAL FACTURA'].str.contains("ERROR", na=False) & ~tabla_principal['ESTADO ACTUAL FACTURA'].str.contains("DUPLICADO", na=False)]
estados = tabla_principal['ESTADO ACTUAL FACTURA'].value_counts()
print(estados)


# Encontrar duplicados basados en la columna 'FACTURA'
duplicados_tp = tabla_principal[tabla_principal.duplicated(subset='FACTURA IQ', keep=False)]




# #############################
#   === 4.  DEVOLUCIONES  ===
# #############################



# _________ LECTURA

df_devoluciones = pd.read_csv(
    os.path.join(INSUMO_HISTORICO, "HistoricoDevoluciones2025.txt"), 
    sep="|", 
    decimal=".",
    low_memory=False)



# ------- Revisar Devoluciones

# # rev_dev = df_devoluciones[df_devoluciones['NumeroRadicacion']=='CMVIQ034000001832690']
# rev_fal_dev = tabla_principal[tabla_principal['FACTURA IQ']=='CMVIQ034000001909319']
# rev_fal_dev_2 = hr_liquidado[hr_liquidado['FACTURA IQ']=='CMVIQ034000001909319']

# fal_dev_revisar = df_devoluciones[~df_devoluciones['NumeroRadicacion'].isin(tabla_principal['FACTURA IQ'])]
# print(fal_dev_revisar) # Son Error de Radicacion OK CMVIQ034000001909319 CMVIQ034000001917534




# _________ TOTALES 

estado_comunicacion = tabla_principal[tabla_principal['ESTADO ACTUAL FACTURA'].str.contains("COMUNICACIÓN", na=False)]
estado_comunicacion['Tabla'] = 'PJ_DetalleDevolucionesObjeciones'
total_dev = estado_comunicacion[['FACTURA IQ', 'Tabla', 'F.LIQUIDACION']]
estado_comunicacion.info()




# _________ FALTANTES 

fal_dev = estado_comunicacion[~estado_comunicacion['FACTURA IQ'].isin(df_devoluciones['NumeroRadicacion'])]
fal_dev['Tabla'] = 'PJ_DetalleDevolucionesObjeciones'
fal_dev = fal_dev[['FACTURA IQ', 'Tabla', 'F.LIQUIDACION']]
nombre_faltantes_devoluciones = 'FaltantesDevoluciones2025.xlsx'




# _________ VALIDACIONES

cruce_dev = pd.merge(tabla_principal, df_devoluciones, left_on='FACTURA IQ', right_on='NumeroRadicacion', how='right')
validacion_cruce_dev = cruce_dev[cruce_dev['FACTURA IQ'].isna()]
estado_dev = cruce_dev['ESTADO ACTUAL FACTURA'].unique()
print(estado_dev)




# total_dev.to_excel(os.path.join(RUTA_EXPORTACION, "TotalDevoluciones2025.xlsx"), index=False)



# #############################
#   === 5.  LIQUIDACIONES  ===
# #############################




def comparar_valores_liquidaciones(row):
    # Redondear los valores a 2 decimales (puedes ajustar según sea necesario)
    valor_aprobado = round(row['Valor_Aprobado_Inicial'], 2)
    valor_glosado = round(row['Valor_glosado_Inicial'], 2)
    valor_servicio = round(row['Valor_Servicio'], 2)
    
    return valor_aprobado + valor_glosado == valor_servicio


# _________ LECTURA

df_liquidaciones = pd.read_csv(os.path.join(INSUMO_HISTORICO, "HistoricoLiquidaciones2025.txt"), sep="|", decimal=".", low_memory=False)


liq_agrupado = df_liquidaciones.groupby('Numero_Radicado_Inicial')[['Valor_Servicio', 'Valor_Aprobado_Inicial', 'Valor_glosado_Inicial']].sum().reset_index()
muestra_liq = liq_agrupado.head(5)
df_liquidaciones.info()


liq_agrupado['Validacion'] = liq_agrupado.apply(comparar_valores_liquidaciones, axis=1)
liq_agrupado_validar = liq_agrupado[liq_agrupado['Validacion']==False]


# revision_liq = detalle_liquidacion[detalle_liquidacion['Numero_Radicado_Inicial']=='CMVIQ034000002155538']
# revision_agr = df_agrupado[df_agrupado['Numero_Radicado_Inicial']=='CMVIQ034000002155538']
liq_agrupado.info()


# Definir la función para aplicar la lógica
def aplicar_nombre_tabla_liquidacion(row):
    if row['FACTURA IQ'].startswith('RIQ') or row['FACTURA IQ'].startswith('CIQ'):
        return 'PJ_DetalleLiquidacion_RIQ_CIQ'
    else:
        return 'PJ_DetalleLiquidacion'




# _________ TOTALES 

estado_liquidacion = tabla_principal[(tabla_principal['ESTADO ACTUAL FACTURA']=="LIQUIDADO CON PAGO") | (tabla_principal['ESTADO ACTUAL FACTURA']=="LIQUIDADO SIN PAGO")]
estado_liquidacion['Tabla'] = estado_liquidacion.apply(aplicar_nombre_tabla_liquidacion, axis=1)
estado_liquidacion.info()


total_liq = estado_liquidacion[['FACTURA IQ', 'Tabla', 'F.LIQUIDACION']]
total_liq = total_liq.drop_duplicates()




# _________ FALTANTES 

fal_liq = estado_liquidacion[~estado_liquidacion['FACTURA IQ'].isin(df_liquidaciones['Numero_Radicado_Inicial'])]
columna_liq = 'PJ_DetalleLiquidacion'
fal_liq['Tabla'] = columna_liq
fal_liq = fal_liq[['FACTURA IQ', 'Tabla', 'F.LIQUIDACION']]
nombre_faltantes_liquidaciones = 'FaltantesLiquidaciones2025.xlsx'


# Encontrar duplicados basados en la columna 'FACTURA'
duplicados_liq = fal_liq[fal_liq.duplicated(subset='FACTURA IQ', keep=False)]




# _________ VALIDACIONES

fal_liq_revisar = liq_agrupado[~liq_agrupado['Numero_Radicado_Inicial'].isin(tabla_principal['FACTURA IQ'])]

rev_fal_liq = hr_liquidado[hr_liquidado['FACTURA IQ']=='CIQ03400063190264149']

estados_liq = tabla_principal['ESTADO ACTUAL FACTURA'].value_counts()

# agrupar_fal_liq = fal_liq.groupby('FACTURA IQ')


# total_liq.to_excel(os.path.join(RUTA_EXPORTACION, "TotalLiquidaciones2025.xlsx"), index=False)




# ###################
#   === 6.  RIQ  ===
# ###################




# _________ LECTURA

df_riq = pd.read_csv(os.path.join(INSUMO_HISTORICO, "HistoricoLiquidaciones_RIQ_CIQs2025.txt"), sep="|", decimal=".", low_memory=False)
df_riq.info()


def comparar_valores_riq(row):
    # Redondear los valores a 2 decimales (puedes ajustar según sea necesario)
    valor_glosa_total = round(row['ValorGlosaTotal'], 2)
    valor_AIPS = round(row['ValorAIPS'], 2)
    valor_SRTAIPS = round(row['ValorSRTAIPS'], 2)
    valor_ratificado = round(row['ValorRatificado'], 2)
    valor_aprobado = round(row['ValorAprobado'], 2)
    
    return valor_aprobado + valor_ratificado + valor_SRTAIPS + valor_AIPS == valor_glosa_total


# Agrupar RIQ por Radicado y Valor Glosa Total
riq_agrupado = df_riq.groupby(['NumeroRadicacion_RIQ_CIQ','ValorGlosaTotal'])[['ValorAprobado','ValorAIPS','ValorSRTAIPS', 'ValorRatificado']].sum()
# revisar_riq = df_riq[df_riq['NumeroRadicacion_RIQ_CIQ']=='RIQ03420000001639878']
riq_agrupado = riq_agrupado.reset_index('ValorGlosaTotal')
riq_agrupado = riq_agrupado.reset_index('NumeroRadicacion_RIQ_CIQ')


riq_agrupado['Validacion'] = riq_agrupado.apply(comparar_valores_riq, axis=1)
riq_agrupado_validar = riq_agrupado[riq_agrupado['Validacion']==False]




# _________ FALTANTES 

fal_liq_2 = fal_liq[~fal_liq['FACTURA IQ'].isin(riq_agrupado['NumeroRadicacion_RIQ_CIQ'])]


# Eliminar duplicados
fal_liq_2 = fal_liq_2.drop_duplicates()
fal_liq_sin_procesar = fal_liq
fal_liq = fal_liq_2
fal_liq.info()


# Funcion Nombrar tabla Liq
def aplicar_nombre_tabla_liquidacion(row):
    if row['FACTURA IQ'].startswith('RIQ') or row['FACTURA IQ'].startswith('CIQ'):
        return 'PJ_DetalleLiquidacion_RIQ_CIQ'
    else:
        return 'PJ_DetalleLiquidacion'


# Aplicar la función a cada fila
fal_liq['Tabla'] = fal_liq.apply(aplicar_nombre_tabla_liquidacion, axis=1)


# ??? Preguntar Si se excluye las Devoluciones

# Cruce con tabla RIQ CIQ
fal_dev = fal_dev[~fal_dev['FACTURA IQ'].isin(df_riq['NumeroRadicacion_RIQ_CIQ'])]



# ------- Exportacion

# fal_dev.to_excel(os.path.join(RUTA_EXPORTACION, nombre_faltantes_devoluciones), index=False)
# fal_liq.to_excel(os.path.join(RUTA_EXPORTACION, nombre_faltantes_liquidaciones), index=False)



# #####################
#   === 7.  MAOS  ===
# #####################

df_MAOS = pd.read_csv(os.path.join(INSUMO_HISTORICO, "HistoricoMAOS2025.txt"), sep="|", decimal=".", low_memory=False)
# Agrupar por 'No Radicado' y sumar los valores
grouped_MAOS = df_MAOS.groupby('No Radicado').first().reset_index() # 15526
grouped_MAOS.columns


# Convertir la columna centro_costo a mayúsculas
df_liquidaciones['Centro_de_costo'] = df_liquidaciones['Centro_de_costo'].str.upper().fillna('')
estados_liquidaciones = df_liquidaciones['Centro_de_costo'].value_counts()




# _________ TOTALES 

estado_MAOS = df_liquidaciones[df_liquidaciones['Centro_de_costo'].str.contains('OSTEOS', na=False)]
df_liq_MAOS = estado_MAOS.groupby('Numero_Radicado_Inicial').first().reset_index()
tabla_maos = 'PJ_MAOS'
df_liq_MAOS['Tabla'] = tabla_maos
df_liq_MAOS['FACTURA IQ'] = df_liq_MAOS['Numero_Radicado_Inicial']



total_maos = pd.merge(df_liq_MAOS, tabla_principal, on='FACTURA IQ', how='left')
total_maos = total_maos[['FACTURA IQ', 'Tabla','F.LIQUIDACION']]


df_liq_MAOS.columns




# _________ FALTANTES

# Cruce con tabla RIQ CIQ
fal_maos = df_liq_MAOS[~df_liq_MAOS['Numero_Radicado_Inicial'].isin(df_MAOS['No Radicado'])]
fal_maos = pd.merge(fal_maos, tabla_principal, on='FACTURA IQ', how='left')
fal_maos = fal_maos[['FACTURA IQ', 'Tabla', 'F.LIQUIDACION']]




# _________ EXPORTACION

# fal_maos.to_excel(os.path.join(RUTA_EXPORTACION, 'FaltantesMAOS2025.xlsx'), index=False)




# ###############################
#   === 8.  NOTIFICACIONES  ===
# ###############################

    
df_notificaciones = pd.read_csv(os.path.join(INSUMO_HISTORICO, "HistoricoNotificaciones2025.txt"), sep="|", decimal=".", low_memory=False)
df_notificaciones.info()


df_not_copia = df_notificaciones
# liq_mes_anterior = tabla_principal[tabla_principal['F.LIQUIDACION'].isin(pd.date_range('01-12-2024','31-12-2024'))]



# Supongamos que tienes un DataFrame llamado df y una columna llamada 'fecha'
df_notificaciones['F.NOTIFICACION'] = pd.to_datetime(df_notificaciones['F.NOTIFICACION'], dayfirst=True, errors='coerce')  # Asegúrate de que la columna sea tipo datetime



# Agrupar por año y mes y contar registros
conteo_por_mes = df_notificaciones.groupby(df_notificaciones['F.NOTIFICACION'].dt.to_period('M')).size()

# Si quieres ver el resultado como DataFrame
conteo_por_mes = conteo_por_mes.reset_index(name='cantidad')
conteo_por_mes.columns = ['mes', 'cantidad']

print(conteo_por_mes)





# __________ MES LIQUIDADO ANTERIOR

liq_mes_anterior = data_hr[data_hr['F.LIQUIDACION'].isin(pd.date_range(FECHA_LIQUIDACION_INICIO,FECHA_LIQUIDACION_FIN))]
liq_mes_anterior.info() # Noviembre 886723




# _________ TOTALES

estados_liq_mes_anterior = liq_mes_anterior['ESTADO ACTUAL FACTURA'].value_counts()
print(estados_liq_mes_anterior)
revisar_estado = liq_mes_anterior[liq_mes_anterior['ESTADO ACTUAL FACTURA']=='AUDITADO SIN FINALIZAR PROCESO']
liq_mes_anterior = liq_mes_anterior[liq_mes_anterior['ESTADO ACTUAL FACTURA'] != 'AUDITADO SIN FINALIZAR PROCESO']

tabla_not = 'PJ_Detallenotificación'
liq_mes_anterior['Tabla'] = tabla_not
total_not = liq_mes_anterior[['FACTURA IQ', 'Tabla', 'F.LIQUIDACION']]
total_not = total_not.drop_duplicates()






# _________ FALTANTES

# fal_not = liq_mes_anterior[~liq_mes_anterior['FACTURA IQ'].isin(df_notificaciones['RADICADO'])]
# fal_not = fal_not.drop_duplicates()
# fal_not['Tabla'] = tabla_not
# fal_not = fal_not[['FACTURA IQ', 'Tabla', 'F.LIQUIDACION']]

fal_not = tabla_principal[~tabla_principal['FACTURA IQ'].isin(df_notificaciones['RADICADO'])]
fal_not = fal_not.drop_duplicates()
fal_not['Tabla'] = tabla_not
fal_not = fal_not[['FACTURA IQ', 'Tabla', 'F.LIQUIDACION']]


# _________ VALIDACIONES

rev_fal_not = df_notificaciones[~df_notificaciones['RADICADO'].isin(liq_mes_anterior['FACTURA IQ'])]
fechas_notificacion = rev_fal_not['F.NOTIFICACION'].value_counts()
validacion_not = data_hr[data_hr['FACTURA IQ'].isin(rev_fal_not['RADICADO'])]

rev_fal_Not_2 = hr_liquidado[hr_liquidado['FACTURA IQ']=='CIQ03400063190264148']

# Encontrar duplicados basados en la columna 'FACTURA'
duplicados_not= fal_not[fal_not.duplicated(subset='FACTURA IQ', keep=False)]




# ------- Exportacion

# fal_not.to_excel(os.path.join(RUTA_EXPORTACION, 'FaltantesNotificaciones2025.xlsx'), index=False)
# # total_not.to_excel(os.path.join(RUTA_EXPORTACION, "TotalNotificaciones2025.xlsx"), index=False)




# ###############################
#   === 8.  RECLAMACIONES  ===
# ###############################
    


    
df_reclamaciones = pd.read_csv(
    os.path.join(INSUMO_HISTORICO, "HistoricoReclamaciones2025.txt"), 
    sep="|", 
    decimal=".", 
    low_memory=False)


fal_rec = tabla_principal[~tabla_principal['FACTURA IQ'].isin(df_reclamaciones['NumeroRadicacion'])]
fal_rec_2 = df_reclamaciones[~df_reclamaciones['NumeroRadicacion'].isin(tabla_principal['FACTURA IQ'])]




# ----------Faltantes

tabla_rec = 'PJ_DetalleReclamacion'
fal_rec['Tabla'] = tabla_rec
fal_rec = fal_rec[['FACTURA IQ', 'Tabla', 'F.LIQUIDACION']]




# ##########################
#   === 9.  VICTIMAS  ===
# ##########################
    



df_victimas = pd.read_csv(os.path.join(INSUMO_HISTORICO, "HistoricoVictimas2025.txt"), sep="|", decimal=".", low_memory=False)
fal_vic = tabla_principal[~tabla_principal['FACTURA IQ'].isin(df_victimas['NumeroRadicacion'])]
fal_vic_2 = df_victimas[~df_victimas['NumeroRadicacion'].isin(tabla_principal['FACTURA IQ'])]




# ----------Faltantes

tabla_vic = 'PJ_DetalleVictima'
fal_vic['Tabla'] = tabla_vic
fal_vic = fal_vic[['FACTURA IQ', 'Tabla', 'F.LIQUIDACION']]





# ##########################
#   === 9.  VICTIMAS  ===
# ##########################

    
df_facturas = pd.read_csv(os.path.join(INSUMO_HISTORICO, "HistoricoFacturas2025.txt"), sep="|", decimal=".", low_memory=False)
fal_fac = tabla_principal[~tabla_principal['FACTURA IQ'].isin(df_facturas['numeroradicacion'])]
fal_fac_2 = df_facturas[~df_facturas['numeroradicacion'].isin(tabla_principal['FACTURA IQ'])]

# revisar_fac = data_hr[data_hr['FACTURA IQ']=='IQ03458255814244725'] # ERROR RADICACION

# ----------Faltantes

tabla_fac = 'PJ_DetalleFactura'
fal_fac['Tabla'] = tabla_fac
fal_fac = fal_fac[['FACTURA IQ', 'Tabla', 'F.LIQUIDACION']]


# ------------------------------------

# Faltantes
faltantes = pd.concat([fal_liq, fal_dev, fal_maos, fal_not, fal_rec, fal_vic, fal_fac]).reset_index(drop=True)



with pd.ExcelWriter(os.path.join(RUTA_EXPORTACION, 'Resultado_Faltantes_Data_IQ_2025.xlsx'), engine='openpyxl') as writer:
    faltantes.to_excel(writer, sheet_name='Faltantes', index=False)




# ⏱️ 
print("🧱" * 14)
print(f"Tiempo de ejecución: {time.time() - start_time:.2f} segundos")





















# ::::::::::::::::::::::::::::::::::::::
# ======== Actulizar Dfs Faltantes  
# ::::::::::::::::::::::::::::::::::::::


dfs_dict = {
    'fal_fac':{'dataframe': fal_fac, 'tabla':'PJ_DetalleFactura'},
    'fal_rec':{'dataframe': fal_rec, 'tabla':'PJ_DetalleReclamacion'},
    'fal_vic':{'dataframe': fal_vic, 'tabla':'PJ_DetalleVictima'},
            }


for key, value in dfs_dict.items():
    if value['dataframe'].empty:
        print(key)
        table_name = value['tabla']
        dfs_dict[key]['dataframe'] = pd.DataFrame({'FACTURA IQ': [''], 'Tabla': [table_name], 'F.LIQUIDACION': ['']})
        

# Mostrar el diccionario actualizado
for key, value in dfs_dict.items():
    print(f"Contenido de {key}:")
    print(value['dataframe'])
    print()


fal_fac = dfs_dict['fal_fac']['dataframe']
fal_rec = dfs_dict['fal_rec']['dataframe']
fal_vic = dfs_dict['fal_vic']['dataframe']
        

fal_rec.to_excel(os.path.join(RUTA_EXPORTACION, 'FaltantesReclamaciones2025.xlsx'), index=False) 
fal_vic.to_excel(os.path.join(RUTA_EXPORTACION, 'FaltantesVictimas2025.xlsx'), index=False)       
fal_fac.to_excel(os.path.join(RUTA_EXPORTACION, 'FaltantesFacturas2025.xlsx'), index=False)    
        


# ---------------------------------------




# -------- Totales Tablas


def agregar_tabla(df, valor_tabla):
    df_copy = df.copy()
    df_copy['Tabla'] = valor_tabla
    return df_copy[['FACTURA IQ', 'F.LIQUIDACION','Tabla']]

# Crear una copia de la columna 'FACTURA IQ'
totales_tp = tabla_principal[['FACTURA IQ','F.LIQUIDACION']]

# Agregar la columna 'Tabla' con los valores correspondientes
total_rec = agregar_tabla(totales_tp, 'PJ_DetalleReclamacion')
total_vic = agregar_tabla(totales_tp, 'PJ_DetalleVictima')
total_fac = agregar_tabla(totales_tp, 'PJ_DetalleFactura')



# -----------------------






# #########################################################################
# # _____________________________ NOVEDADES _______________________________
# #########################################################################


# # ???
# # Estandarizar proceso de Novedades
    
# directorio_novedades = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Proyectos\2. Carteras\Salidas\Data IQ\Novedades'
# ruta_novedades = os.path.join(directorio_novedades, año, '11. Noviembre')

# # ::::::::::::::::::::::::::::
# # ====== NOVEDADES MAOS
# # ::::::::::::::::::::::::::::
    
    
# novedades_maos = pd.read_csv(os.path.join(ruta_novedades, "FaltantesMAOSContestadas.txt"), sep="|", decimal=".", encoding='Windows-1252', low_memory=False)

# def detect_encodings(directorio_mes):
#     """
#         Funcion para dectectar por medio de chardet los encodings de los 
#         archivos de un directorio.
        
#     """
#     encodings = {}
    
#     for filename in os.listdir(directorio_mes):
#         if filename.endswith('.txt') or filename.endswith('.csv'):  # Cambia la extensión según tus archivos
#             file_path = os.path.join(directorio_mes, filename)
#             with open(file_path, 'rb') as f:
#                 raw_data = f.read()
#                 result = chardet.detect(raw_data)
#                 encoding = result['encoding']
#                 encodings[filename] = encoding
    
#     return encodings

# # encodings_dict = detect_encodings(ruta_novedades)
# # print(encodings_dict)

# # ------- Faltantes

# # Cruce con tabla novedades MAOS
# fal_maos_2 = fal_maos[~fal_maos['Numero_Radicado_Inicial'].isin(novedades_maos['No Radicado'])]
# fal_maos_sin_procesar = fal_maos
# fal_maos = fal_maos_2
# tabla_maos = 'PJ_MAOS'
# fal_maos['Tabla'] = tabla_maos
# fal_maos['FACTURA IQ'] = fal_maos['Numero_Radicado_Inicial']
# fal_maos = fal_maos[['FACTURA IQ', 'Tabla']]
# nombre_archivo_faltantes_maos = 'FaltantesMAOS.xlsx'


# # :::::::::::::::::::::::::::::::::::
# # ====== NOVEDADES DEVOLUCIONES
# # :::::::::::::::::::::::::::::::::::
    
# novedades_devoluciones = pd.read_csv(os.path.join(ruta_novedades, "FaltantesDevolucionesContestadas.txt"), sep="|", decimal=".", encoding='ISO-8859-1', low_memory=False)

# # Cruce con tabla RIQ CIQ
# fal_dev_2 = fal_dev[~fal_dev['FACTURA IQ'].isin(novedades_devoluciones['NumeroRadicacion'])]
# fal_dev = fal_dev_2
# # fal_dev.to_excel(os.path.join(RUTA_EXPORTACION, nombre_faltantes_devoluciones), index=False)


# # :::::::::::::::::::::::::::::::::::
# # ====== NOVEDADES LIQUIDACIONES
# # :::::::::::::::::::::::::::::::::::
    
# novedades_liq = pd.read_csv(os.path.join(directorio_novedades, año, '12. Diciembre', 'FaltantesLiquidacionesContestadas.txt'), sep="|", decimal=".", encoding='ansi' ,low_memory=False)
# # encodings_dict = detect_encodings(os.path.join(directorio_novedades, año, '12. Diciembre'))
# # print(encodings_dict)

# fal_liq_3 = fal_liq[~fal_liq['FACTURA IQ'].isin(novedades_liq['Numero_Radicado_Inicial'])]
# fal_liq = fal_liq_3
# # fal_liq.to_excel(os.path.join(RUTA_EXPORTACION, nombre_faltantes_liquidaciones), index=False)                   

# # -----------------------------------




# #########################################################################
# # _________________________ Exportación Final ___________________________
# #########################################################################


# Faltantes
faltantes = pd.concat([fal_liq, fal_dev, fal_maos, fal_not, fal_rec, fal_vic, fal_fac]).reset_index(drop=True)


# # Totales
# totales = pd.concat([total_liq, total_dev, total_maos, total_not, total_rec, total_vic, total_fac]).reset_index(drop=True)

# # Contar los registros por la columna TABLA para los faltantes
# conteo_faltantes = faltantes['Tabla'].value_counts().sort_index()

# # Contar los registros por la columna TABLA para los totales
# conteo_totales = totales['Tabla'].value_counts().sort_index()


# # Calcular el porcentaje de registros faltantes
# porcentaje_faltantes = (conteo_faltantes / conteo_totales) * 100

# # Crear un DataFrame resumen con la información
# cuadro_resumen = pd.DataFrame({
#     'Tabla': conteo_totales.index,
#     'Registros Faltantes': conteo_faltantes.reindex(conteo_totales.index, fill_value=0).values,
#     'Registros Totales': conteo_totales.values,
#     'Porcentaje Faltantes': porcentaje_faltantes
# }).reset_index(drop=True)


# # # Agregar una fila de total al cuadro resumen
# total_faltantes = cuadro_resumen['Registros Faltantes'].sum()
# total_totales = cuadro_resumen['Registros Totales'].sum()
# total_porcentaje = (total_faltantes / total_totales) * 100


# # Fila Adicional
# totals = pd.DataFrame([{
#     'Tabla': 'Totales',
#     'Registros Faltantes': total_faltantes,
#     'Registros Totales': total_totales,
#     'Porcentaje Faltantes': total_porcentaje
# }])


# cuadro_resumen = pd.concat([cuadro_resumen, totals], ignore_index=True)

# # Reemplazar valores NaN con 0
# cuadro_resumen = cuadro_resumen.fillna(0)


with pd.ExcelWriter(os.path.join(RUTA_EXPORTACION,'Resultado_Faltantes_Data_IQ_2025.xlsx'), engine='openpyxl') as writer:
    faltantes.to_excel(writer, sheet_name='Faltantes', index=False)
        
    # Escribir el cuadro resumen en la hoja "Cuadro Resumen" comenzando desde la celda C4
    workbook  = writer.book
    worksheet = workbook.create_sheet('Resumen')
    writer.sheets['Resumen'] = worksheet
    
    # Escribir encabezados
    for col_num, value in enumerate(cuadro_resumen.columns.values, start=2):
        worksheet.cell(row=4, column=col_num+1, value=value)
    
    # Escribir datos del cuadro resumen sin formato
    for r_idx, row in enumerate(cuadro_resumen.itertuples(), start=4):
        for c_idx, value in enumerate(row[1:], start=2):
            worksheet.cell(row=r_idx+1, column=c_idx+1, value=value)
                
print("Los DataFrames y el cuadro resumen se han exportado correctamente a 'Resultado_Faltantes_DataIQ.xlsx'.")


# faltantes.to_excel('FaltantesDataIQ.xlsx', index=False)
totales.to_csv(os.path.join(RUTA_EXPORTACION,'Resultado_Totales_Data_IQ_2025.txt'), encoding= 'utf-8', sep="|", index=False)

# # faltantes.to_excel('FaltantesDataIQ.xlsx', index=False)
# faltantes.to_csv(os.path.join(RUTA_EXPORTACION,'Resultado_Faltantes_DataIQ_2025.xlsx'), sep="|", index=False)


# :::::::::::::::::::::::::::::::::::::::::::
# =========== VALIDACIONES FINALES
# :::::::::::::::::::::::::::::::::::::::::::

    
"""
    Tabla Principal: Todo lo liquidado del 2024. 
        1. Sin Anulados
        2. Sin Radicados Manuales
        3. Sin ERRORES
"""    

tabla_sin_liq = tabla_principal[~tabla_principal['FACTURA IQ'].isin(total_liq['FACTURA IQ'])]
tabla_sin_dev = tabla_sin_liq[~tabla_sin_liq['FACTURA IQ'].isin(total_dev['FACTURA IQ'])]

filtro_radicado = hr_liquidado[hr_liquidado['FACTURA IQ']=='CMVIQ034000002264803']
filtro_radicado_tp = tabla_principal[tabla_principal['FACTURA IQ']=='CMVIQ037000000000265']



    


# # Lista de estados que queremos excluir
# estados_a_excluir = [
#     'FACTURA SIN ASOCIAR A SINIESTRO',
#     'EN PROCESO DE AUDITORIA',
#     'AUDITADO SIN FINALIZAR PROCESO',
#     'GLOSA SIN ASOCIAR A SINIESTROS',
#     'SIN ASIGNAR A SINIESTRO FACTURA LIQUIDADA EN CONCI',
#     'SIN ASIGNAR A SINIESTRO GLOSA LIQUIDADA EN CONCILI'
# ]





# # Filtrar el DataFrame para excluir las filas con los estados especificados
# hr_final = hr_liquidado[~hr_liquidado['ESTADO ACTUAL FACTURA'].isin(estados_a_excluir)]


# # Revisar que en Factura IQ tenga IQ
# revisar_liquidado = hr_liquidado[hr_liquidado['FACTURA IQ'].str.contains('IQ')]



# hr_final.columns

# columnas =['FACTURA IQ',
#            'LOTE IQ',
#            'SINIESTRO',
#            'PLACA',
#            'NRO. POLIZA',
#            'NUMERO FACTURA',
#            'VLR CONSTITUCION RVA',
#            'VLR RADICACION', 
#            'VLR APROBADO', 
#            'VLR GLOSADO',
#            'ID RECLAMANTE', 
#            'RECLAMANTE',
#            'F.OCURRENCIA',
#            'DOC VICTIMA',
#            'VICTIMA',
#            'AMPARO',
#            'F.AVISO',
#            'F.CREA FACTURA',
#            'F.LIQUIDACION',
#            'ESTADO ACTUAL FACTURA',
#            'F. NOTIFICACION',
#            'OPERADOR ADMINISTRADOR']

# hr_final = hr_final[columnas]




#########################################################
# ================= DETALLE LIQUIDACION =================
#########################################################


# detalle_liquidacion = pd.read_csv(os.path.join(ruta, listado_archivos[1]), sep="|", decimal=".", low_memory=False)
# detalle_liquidacion.columns


# Filtrar filas donde la columna 'Codigo_glosa_general_id_RIQ' tiene el valor 0

# filtered_liquidacion = detalle_liquidacion[(detalle_liquidacion['Codigo_glosa_general_id'].isna()) ]


# # Valores del Glosa
# estado_liq = filtered_liquidacion['Valor_glosado_Inicial'].unique() # Valor Unicamente 0

# filtered_df = detalle_liquidacion[(detalle_liquidacion['Codigo_glosa_general_id'] == 0) | (detalle_liquidacion['Codigo_glosa_general_id'].isna()) | (detalle_liquidacion['Codigo_glosa_Especifica_id'].isna())]
# filtered_df.info()
