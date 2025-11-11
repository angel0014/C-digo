# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 14:54:23 2025

@author: angperilla
"""

"""
    Script para generar reporte de FASECOLDA 
"""

import pandas as pd
import os
import time

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



# =========================================
# 2.______________ LECTURA HR 
# =========================================


# Lectura archivo
df_hr = pd.read_parquet(RUTA_HR)



df_hr.to_csv(EXPORTACION_HR, sep="|", encoding='utf-8')


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


# Creación campo Mes y Año
df_hr['MES_AÑO'] = df_hr['F.AVISO'].dt.strftime('%Y-%m')


# Revisar duplicados por campo (Keep: Marca todas las apariciones duplicadas como True)
radicados_duplicados = df_hr[df_hr.duplicated(subset=['FACTURA IQ'], keep=False)]


# df sin duplicados drop_dulicates(keep='last')
df_hr = df_hr.drop_duplicates(subset=['FACTURA IQ'], keep='last')


df_hr['NUEVO VLR RADICACION'] = df_hr['VLR RADICACION']


# Asegurarse de que 'VLR RADICACION' sea numérico
df_hr['VLR RADICACION'] = pd.to_numeric(df_hr['VLR RADICACION'], errors='coerce')


# Agrupar por MES_AÑO y contar los valores en la columna 'factura IQ'
df_agrupado = df_hr.groupby('MES_AÑO').agg({
    'VLR RADICACION': 'sum',
    'FACTURA IQ': 'count'
}).reset_index()



with pd.ExcelWriter(r'C:\Users\angperilla\Scripts\Reportes\FASECOLDA\Resultado_Reclamaciones_historicas.xlsx', engine='openpyxl') as writer:
    df_agrupado.to_excel(writer, index=False, sheet_name='Detalle')
    


# =========================================
# 3.______________ DEVOLUCIONES
# =========================================


# _________ LECTURA DEVOLUCIONES

INSUMO_HISTORICO = r'C:\Users\angperilla\Scripts\Reportes\DEVOLUCIONES'



df_dev_2025 = pd.read_csv(os.path.join(INSUMO_HISTORICO, "HistoricoDevoluciones2025.txt"), sep="|", decimal=".", low_memory=False)


df_dev_2024 = pd.read_csv(os.path.join(INSUMO_HISTORICO, "HistoricoDevoluciones2024.txt"), sep="|", decimal=".", low_memory=False)


df_dev_2023 = pd.read_csv(os.path.join(INSUMO_HISTORICO, "PJ_ReporteObjecionDev_2023_pro.csv"), sep="|", encoding='ansi', decimal=".", low_memory=False)


df_dev_2022 = pd.read_csv(os.path.join(INSUMO_HISTORICO, "PJ_ReporteObjecionDev_2022_pro.csv"), sep="|", encoding='ansi', decimal=".", low_memory=False)


# Totales
devoluciones = pd.concat([df_dev_2025, df_dev_2024, df_dev_2023, df_dev_2022]).reset_index(drop=True)
print(devoluciones.info())


estados = devoluciones['MotivoCausalDevolucionObjecion'].value_counts()
print(estados)


# Filtro Devoluciones
dev_filtrado = devoluciones[devoluciones['MotivoCausalDevolucionObjecion'].str.contains('DEVOL', case=False, na=False)]


# Revisar duplicados por campo (Keep: Marca todas las apariciones duplicadas como True)
dev_duplicados = dev_filtrado[dev_filtrado.duplicated(subset=['NumeroRadicacion'], keep=False)]


# df sin duplicados drop_dulicates(keep='last')
dev_filtrado = dev_filtrado.drop_duplicates(subset=['NumeroRadicacion'], keep='last')



# _________ CRUCE DEVOLUCIONES

cruce_dev = pd.merge(df_hr, dev_filtrado, 
                    left_on='FACTURA IQ', 
                    right_on='NumeroRadicacion', 
                    how='right', indicator=True)


# Agrupar por MES_AÑO y contar los valores en la columna 'factura IQ'
dev_agrupado = cruce_dev.groupby('MES_AÑO').agg({
    'VLR RADICACION': 'sum',
    'FACTURA IQ': 'count'
}).reset_index()



with pd.ExcelWriter(r'C:\Users\angperilla\Scripts\Reportes\FASECOLDA\Resultado_Devoluciones.xlsx', engine='openpyxl') as writer:
    dev_agrupado.to_excel(writer, index=False, sheet_name='Detalle')
    
    
    
# _______ OBJECIONES

# Filtro Devoluciones
obj_filtrado = devoluciones[devoluciones['MotivoCausalDevolucionObjecion'].str.contains('OBJ', case=False, na=False)]


# Revisar duplicados por campo (Keep: Marca todas las apariciones duplicadas como True)
obj_duplicados = obj_filtrado[obj_filtrado.duplicated(subset=['NumeroRadicacion'], keep=False)]


# df sin duplicados drop_dulicates(keep='last')
obj_filtrado = obj_filtrado.drop_duplicates(subset=['NumeroRadicacion'], keep='last')    


with pd.ExcelWriter(r'C:\Users\angperilla\Scripts\Reportes\FASECOLDA\Objeciones.xlsx', engine='openpyxl') as writer:
    obj_filtrado.to_excel(writer, index=False, sheet_name='Detalle')
    

# _________ CRUCE OBJECIONES

cruce_obj = pd.merge(df_hr, obj_filtrado, 
                    left_on='FACTURA IQ', 
                    right_on='NumeroRadicacion', 
                    how='right', indicator=True)


# Agrupar por MES_AÑO y contar los valores en la columna 'factura IQ'
obj_agrupado = cruce_obj.groupby('MES_AÑO').agg({
    'VLR RADICACION': 'sum',
    'FACTURA IQ': 'count'
}).reset_index()



with pd.ExcelWriter(r'C:\Users\angperilla\Scripts\Reportes\FASECOLDA\Resultado_Objeciones.xlsx', engine='openpyxl') as writer:
    obj_agrupado.to_excel(writer, index=False, sheet_name='Detalle')



# _______ DETALLE LIQUIDACIONES


INSUMO_LIQUIDACIONES = r'C:\Users\angperilla\Scripts\Reportes\LIQUIDACIONES'



df_liq_2025 = pd.read_csv(os.path.join(INSUMO_LIQUIDACIONES, "HistoricoLiquidaciones2025.txt"), sep="|", decimal=".", low_memory=False)


df_liq_2024 = pd.read_csv(os.path.join(INSUMO_LIQUIDACIONES, "HistoricoLiquidaciones2024.txt"), sep="|", decimal=".", low_memory=False)


df_liq_2023 = pd.read_csv(os.path.join(INSUMO_LIQUIDACIONES, "PJ_DetalleLiquidacion_2023_pro.csv"), sep="|", encoding='ansi', decimal=".", low_memory=False)
df_liq_2023.columns


df_liq_2022 = pd.read_csv(os.path.join(INSUMO_LIQUIDACIONES, "PJ_DetalleLiquidacion_2022_pro.csv"), sep="|", encoding='ansi', decimal=".", low_memory=False)
df_liq_2022.columns


df_liq_2022.rename(columns={'ï»¿Numero_Radicado_Inicial': 'Numero_Radicado_Inicial'}, inplace=True)


# Totales
liquidaciones = pd.concat([df_liq_2025, df_liq_2024, df_liq_2023, df_liq_2022]).reset_index(drop=True)
print(liquidaciones.info())


revisar_liq = liquidaciones[liquidaciones['Numero_Radicado_Inicial']=='CMVIQ034000001059068']


muestra_liq = liquidaciones.head(50000)
print(muestra_liq)


estados_liq = liquidaciones['Codigo_glosa_general_id'].value_counts()
print(estados_liq)



# Filtro 
liq_filtrado = liquidaciones[liquidaciones['Codigo_glosa_general_id']==3.0]


with pd.ExcelWriter(r'C:\Users\angperilla\Scripts\Reportes\FASECOLDA\liquidaciones.xlsx', engine='openpyxl') as writer:
    liq_filtrado.to_excel(writer, index=False, sheet_name='Detalle')



# Revisar duplicados por campo (Keep: Marca todas las apariciones duplicadas como True)
liq_duplicados = liq_filtrado[liq_filtrado.duplicated(subset=['Numero_Radicado_Inicial'], keep=False)]


# df sin duplicados drop_dulicates(keep='last')
liq_filtrado = liq_filtrado.drop_duplicates(subset=['Numero_Radicado_Inicial'], keep='last') 



# _________ CRUCE LIQUIDACIONES

cruce_liq= pd.merge(df_hr, liq_filtrado, 
                    left_on='FACTURA IQ', 
                    right_on='Numero_Radicado_Inicial', 
                    how='right', indicator=True)




# Agrupar por MES_AÑO y contar los valores en la columna 'factura IQ'
liq_agrupado = cruce_liq.groupby('MES_AÑO').agg({
    'VLR RADICACION': 'sum',
    'FACTURA IQ': 'count'
}).reset_index()



cruce_liq.to_excel(r'C:\Users\angperilla\Scripts\Reportes\FASECOLDA\liquidaciones.xlsx')


