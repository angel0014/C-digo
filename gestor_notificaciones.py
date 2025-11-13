# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 11:53:27 2025

@author: angperilla
"""

"""
     Proyecto para extraer texto de los documentos .PDF de las notificaciones 
     de envio del proveedor 472.
"""


import pandas as pd
from pathlib import Path
from collections import defaultdict
import os
import fitz
import re
import time
import shutil

import warnings
warnings.filterwarnings("ignore")


# =====================
# === DATOS ENTRADA ===
# =====================


# # Data Noticicaciones del Proveedor de Envio
# DIRECTORIO = Path(r"C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Proyectos\10. Notificaciones_472\data\Bloque 01.01.2023-31.05.2023\Bloque 01.01.2023-31.05.2023")



# Data Noticicaciones del Proveedor de Envio
DIRECTORIO = Path(r"C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Proyectos\10. Notificaciones_472\data\Bloque 01.06.2023-31.12.2023\Bloque 01.06.2023-31.12.2023")



# Directorio donde quedan los PDFs renombrados PARTE FINAL
DIRECTORIO_EXPORTACION = Path(r'C:\Users\angperilla\Scripts\Gestor_Notificaciones\Salidas\Proveedor_472\2023\lote_5')



# ==================================
# === CARACTERISTICAS DE LA DATA === 
# ==================================


"""
    Permite obtener las caracteristicas de la data de Notificaciones            
"""

# # crear dict para contar extensiones
# cantidades = defaultdict(int)
# tamaño = defaultdict(int)
# #print(extensiones)

# # Iterar sobre elementos de mi Directorio
# for elemento in DIRECTORIO.iterdir():
#     #print(elemento)
#     if elemento.is_file():
#         ext = elemento.suffix or '[sin extensión]'
#         cantidades[ext]+=1
#         tamaño[ext]+=elemento.stat().st_size


# # Convertir bytes a gigabytes

# def convertir_tamaño(bytes_):
#     gb = bytes_ / (1024 ** 3)
#     mb = bytes_ / (1024 ** 2)
#     kb = bytes_ / 1024
#     return gb, mb, kb


# # Mostrar resultados
# for ext, cantidad in cantidades.items():
#     total_bytes = tamaño[ext]
#     total_gb, total_mb, total_kb = convertir_tamaño(total_bytes)
#     promedio_gb = total_gb / cantidad
#     promedio_mb = total_mb / cantidad
#     promedio_kb = total_kb / cantidad
    
#     print("🧱" * 14)
#     print(f"Extensión: {ext}")
#     print(f"📄 Total archivos: {cantidad}")
#     print(f"💾 Tamaño total: {total_gb:.3f} GB ({total_mb:.1f} MB / {total_kb:.0f} KB)")
#     print(f"📊 Promedio por archivo: {promedio_gb:.6f} GB ({promedio_mb:.2f} MB / {promedio_kb:.0f} KB)")
#     print("🧱" * 14)



# ========================
# === EXTRACCION TEXTO ===
# ========================

def extract_info_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    num_pages = pdf_document.page_count
    data = {}

    # Leer todo el contenido del PDF
    texto = ""
    for page_num in range(num_pages):
        texto += pdf_document[page_num].get_text()

    # Extraer metadatos
    id_mensaje = re.search(r"Id mensaje:\s*(\d+)", texto)
    emisor = re.search(r"Emisor:\s*(.*)", texto)
    destinatario = re.search(r"Destinatario:\s*(.*(?:\n.*)?)", texto)
    asunto = re.search(r"Asunto:\s*(.*(?:\n.*)?)", texto)
    fecha_envio = re.search(r"Fecha envío:\s*(.*)", texto)
    estado_actual = re.search(r"Estado actual:\s*(.*)", texto)

    if id_mensaje:
        data["Id mensaje"] = id_mensaje.group(1)
    if emisor:
        data["Emisor"] = emisor.group(1).strip()
    if destinatario:
        data["Destinatario"] = destinatario.group(1).replace('\n', ' ').strip()
    if asunto:
        data["Asunto"] = asunto.group(1).replace('\n', ' ').strip()
    if fecha_envio:
        data["Fecha envío"] = fecha_envio.group(1).strip()
    if estado_actual:
        data["Estado actual"] = estado_actual.group(1).strip()

    # Extraer adjuntos válidos
    adjuntos = re.search(r"Adjuntos\s*Nombre\s*Suma de Verificación \(SHA-256\)\s*(.*?)\s*Descargas", texto, re.DOTALL)
    if adjuntos:
        lineas = [line.strip() for line in adjuntos.group(1).split('\n') if line.strip()]
        # print(lineas)
        extensiones_validas = {".pdf", ".xlsx", ".csv"}
        archivos_validos = []
        i = 0
        while i < len(lineas):
            actual = lineas[i]
            if any(actual.lower().endswith(ext) for ext in extensiones_validas):
                archivos_validos.append(actual)
            elif i + 1 < len(lineas):
                combinado = actual + lineas[i + 1]
                if any(combinado.lower().endswith(ext) for ext in extensiones_validas):
                    archivos_validos.append(combinado)
                    i += 1
            i += 1
        data["Adjuntos"] = "; ".join(archivos_validos)

    return data



def process_directory(directory_path):
    all_data = []
    error_files = []
    for pdf_path in Path(directory_path).iterdir():
        if pdf_path.is_file() and pdf_path.suffix.lower() == ".pdf":
            try:
                data = extract_info_from_pdf(pdf_path)
                data["Archivo"] = pdf_path.name
                all_data.append(data)
            except Exception as e:
                error_files.append((pdf_path, str(e)))
    df = pd.DataFrame(all_data)
    return df, error_files




# Función para extraer llave, radicado y NIT sin sensibilidad a mayúsculas
def extract_info_from_df(adjunto):
    
    if not isinstance(adjunto, str):
        return None, None, None 


    adjunto_upper = adjunto.upper()

    # Buscar llave (LIQ, DEV, OBJ, GIN)
    llave_match = re.match(r'(LIQ|DEV|OBJ|GIN)(-[A-Z]+)?-\d+', adjunto_upper)
    llave = llave_match.group(0) if llave_match else None


    # Buscar radicado (CMVIQ, VIQ, IQ, RIQ, RCMVIQ)
    radicado_match = re.match(r'(CMVIQ|VIQ|IQ|RIQ|RCMVIQ)(\d+)', adjunto_upper)
    radicado = radicado_match.group(0) if radicado_match else None

    # Buscar NIT (8 o 9 seguido de 8 dígitos antes de .pdf)
    nit_match = re.search(r'-(8\d{8}|9\d{8})\.PDF$', adjunto_upper)
    nit = nit_match.group(1) if nit_match else None

    return llave, radicado, nit



def clean(consecutivo):
    # Convertir a cadena y manejar valores nulos
    if pd.isna(consecutivo):
        return ''
    consecutivo_str = str(consecutivo)
    # Usar una expresión regular para quitar todos los caracteres especiales excepto el '-'
    consecutivo_limpio = re.sub(r'[^a-zA-Z0-9-]', '', consecutivo_str)
    # Convertir a mayúsculas
    return consecutivo_limpio.upper()



def float_to_str(valor):
    try:
        num = float(valor)
        return str(int(num)) if num.is_integer() else str(num)
    except:
        return str(valor)



def get_final_value(value1, value2):
    if pd.notna(value1) and value1 != "":
        return value1
    elif pd.notna(value2) and value2 != "":
        return value2
    else:
        return ""


def rename_pdf(df):
    df['Nombre PDF Resultado'] = df.apply(
        lambda row: f"{row['Id mensaje']}_{row['NIT FINAL']}_{row['RADICADO FINAL'].split(';')[0]}.pdf"
        if pd.notna(row['NIT FINAL']) and row['NIT FINAL'] != ""
        else "",
        axis=1
    )
    return df

def set_status(df):
    df['Estado Notificación'] = df['Nombre PDF Resultado'].apply(
        lambda x: "OK" if isinstance(x, str) and x.count('_') == 2 else "PENDIENTE"
    )
    return df




def rename_and_copy_pdfs(df_cruce_fin, DIRECTORIO, DIRECTORIO_EXPORTACION):
    # Crear la carpeta de destino si no existe
    destination_folder = DIRECTORIO_EXPORTACION
    os.makedirs(destination_folder, exist_ok=True)
    
    # Lista para almacenar errores
    errors = []
    
    # Iterar sobre cada fila del DataFrame
    for index, row in df_cruce_fin.iterrows():
        source_file = DIRECTORIO / row['Archivo']
        destination_file = destination_folder / row['Nombre PDF Resultado']
        
        try:
            if source_file.exists():
                shutil.copyfile(source_file, destination_file)
            else:
                errors.append({'Archivo': row['Archivo'], 'Error': 'Archivo no encontrado'})
        except Exception as e:
            errors.append({'Archivo': row['Archivo'], 'Error': str(e)})
    
    # Crear un DataFrame con los errores
    df_errors = pd.DataFrame(errors)
    
    # Retornar el DataFrame con los errores
    return df_errors




if __name__ == "__main__":
    
    start_time = time.time()

    # # Directorio Masivo
    directorio = DIRECTORIO
    df_resultado, errores = process_directory(DIRECTORIO)
    
    
    # Directorio Prueba
    # directorio = r"C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Proyectos\10. Notificaciones_472\Insumos\Muestra_Data"
    # df_resultado, errores = process_directory(directorio)

    # # Exportar a CSV
    # df_resultado.to_csv(r"C:\Users\angperilla\Scripts\Gestor_Notificaciones\resultado_pruebas_1000.txt", index=False, encoding="utf-8-sig", sep="|")
    # errores.to_csv(r"C:\Users\angperilla\Scripts\Gestor_Notificaciones\resultado_errores.txt", index=False, encoding="utf-8-sig", sep="|")
    # print(df_resultado)
    
    
    ##############################
    #########  Fase II   #########
    ##############################
    
    """
        Procesamiento información extraída del PDF.
    """
    
    
    # ======================================
    # ===  Lectura Resultado 41525 PDFs  ===
    # ======================================
    
    # LECTURA df_resultado
    # salida = r"C:\Users\angperilla\Scripts\Gestor_Notificaciones\resultado_gestor_notificaciones.txt"
    # df_resultado = pd.read_csv(salida, low_memory=False, encoding="utf-8-sig", sep="|")
    
    
    # Aplicar la función al DataFrame
    df_resultado[['Llave', 'Radicado', 'NIT']] = df_resultado['Adjuntos'].apply(lambda x: pd.Series(extract_info_from_df(x)))
    # Mostrar resultado
    print(df_resultado)
    df_resultado.info()
    
    
    
    # ==============================
    # ===      Notficaciones     ===
    # ==============================
    
    not_2021 = pd.read_excel(r"C:\Users\angperilla\Scripts\Gestor_Notificaciones\Notificaciones2021.xlsx")
    not_2022 = pd.read_excel(r"C:\Users\angperilla\Scripts\Gestor_Notificaciones\Notificaciones2022.xlsx")
    not_2023 = pd.read_excel(r"C:\Users\angperilla\Scripts\Gestor_Notificaciones\Notificaciones2023.xlsx")
    
    not_final = pd.concat([not_2021, not_2022, not_2023], ignore_index=True)
    not_final.info()
    
    # Limpiar Consecutivo
    not_final['CONSECUTIVO CARTA'] = not_final['CONSECUTIVO CARTA'].apply(clean)
    
    
    
    
    # ========================================
    # ===   Procesamiento Notificaciones   ===
    # ========================================
    
    # --------------------------
    "1. Ordenar Notificaciones"
    # ---------------------------
    
    
    # Convertir usando inferencia de formato
    not_final['FECHA AVISO'] = pd.to_datetime(not_final['FECHA AVISO'], errors='coerce', infer_datetime_format=True)
    
    # Filtrar filas con fechas no válidas
    filas_invalidas = not_final[not_final['FECHA DE ENTREGA NOTIFICACIÓN'].isna()]
    
    # Ordenar df (Más reciente)
    not_final_ordenado = not_final.sort_values(by=['CONSECUTIVO CARTA', 'FECHA AVISO', 'FECHA DE ENTREGA NOTIFICACIÓN','RADICADO'], ascending=[False, False, False, False])
    
    # Validar Orden
    revisar_orden = not_final_ordenado[not_final_ordenado['CONSECUTIVO CARTA']=='LIQ-202303012787']
    
    # Filtrar filas Vacias
    revisar_vacios = not_final_ordenado[not_final_ordenado['CONSECUTIVO CARTA'].isna() | (not_final_ordenado['CONSECUTIVO CARTA'] == '')]
    
    # Imputar valores vacíos o nulos con 'NA' => 50 valores con NA
    not_final_ordenado['CONSECUTIVO CARTA'] = not_final_ordenado['CONSECUTIVO CARTA'].replace('', 'NA').fillna('NA')



    # ---------------------------------------
    "2. Agrupamiento por CONSECUTIVO CARTA"
    # ---------------------------------------
    
    
    # Agrupar el DataFrame por "CONSECUTIVO" y mantener los demás campos
    agrupado = not_final_ordenado.groupby("CONSECUTIVO CARTA").agg(
        NUMERO_FACTURA_NOT=("NO. FACTURA", lambda x: ";".join(x.astype(str))),
        RADICADO_NOT=("RADICADO", lambda x: ";".join(x.astype(str))),
        ID_RECLAMANTE_NOT=("ID RECLAMANTE", "first"),
        RECLAMANTE_NOT=("RECLAMANTE", "first"),
        FECHA_AVISO_NOT=("FECHA AVISO", "first"),
        GUIA_NOT=("NO DE GUIA", "first"),
        CORREO_NOT=("CORREO DE DESTINO", "first"),
        F_NOTIFICACION_NOT=("FECHA DE ENTREGA NOTIFICACIÓN", "first"),
        PERIODO_NOT=("PERIODO", "first")
    ).reset_index()
    
    
    
    # =================================
    # ===   Cruce Notificaciones    ===
    # =================================
    
    # Crear la columna 'LLAVE FINAL'
    
    df_resultado['Radicado'] = df_resultado['Radicado'].apply(clean)
    df_resultado['LLAVE FINAL'] = df_resultado.apply(lambda row: row['Llave'] if row['Llave'] else row['Radicado'], axis=1)
    df_resultado['LLAVE FINAL'] = df_resultado['LLAVE FINAL'].apply(clean)
    
   
    df_cruce = pd.merge(df_resultado, agrupado, left_on='LLAVE FINAL', right_on='CONSECUTIVO CARTA', how='left')    
    df_cruce.info()
    
    # df_cruce.to_csv(r"C:\Users\angperilla\Scripts\Gestor_Notificaciones\resultado_completo_gestor_notificaciones.txt", index=False, encoding="utf-8-sig", sep="|")
    
    
    # =================================
    # ===    Cruce HR Historica     ===
    # =================================
    
    directorio_hr = r'C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Documentos\Proyectos\HR'
    año_2025 = '2025'
    archivo_hr = 'HR_20200101_20250601_0.parquet'

    ruta_hr = os.path.join(directorio_hr, año_2025, archivo_hr)

    # Lectura
    data_hr = pd.read_parquet(ruta_hr)
    data_hr.info()
    
    columnas_hr = ['FACTURA IQ', 'SINIESTRO', 'PLACA','NRO. POLIZA', 
                   'NUMERO FACTURA', 'ID RECLAMANTE', 'RECLAMANTE',
                   'DOC VICTIMA', 'VICTIMA', 'ESTADO ACTUAL FACTURA']
    
    
    # Filtrar el DataFrame
    data_hr_nuevo = data_hr[columnas_hr]
    
    # Eliminar duplicados por 'FACTURA IQ'
    data_hr_nuevo = data_hr_nuevo.drop_duplicates(subset='FACTURA IQ')
    
    # Agregar sufijo
    data_hr_nuevo.columns = [col + '_HR' for col in data_hr_nuevo.columns]
    data_hr_nuevo.info()
    

    df_cruce_fin = pd.merge(df_cruce, data_hr_nuevo, left_on='LLAVE FINAL', right_on='FACTURA IQ_HR', how='left')    
    df_cruce_fin.info()
    
    
    
    
    # ========================================
    # ===     Procesamiento Cruce Final    ===
    # ========================================
    
    # Crear columnas 'NT FINAL' y 'RADICADO FINAL'

    df_cruce_fin['NIT FINAL'] = df_cruce_fin.apply(
    lambda row: get_final_value(row['ID_RECLAMANTE_NOT'], row['ID RECLAMANTE_HR']), axis=1)

    df_cruce_fin['RADICADO FINAL'] = df_cruce_fin.apply(
    lambda row: get_final_value(row['RADICADO_NOT'], row['FACTURA IQ_HR']), axis=1)

    
    df_cruce_fin['Id mensaje'] = df_cruce_fin['Id mensaje'].apply(float_to_str)
    df_cruce_fin['NIT FINAL'] = df_cruce_fin['NIT FINAL'].apply(float_to_str)
    df_cruce_fin['RADICADO FINAL'] = df_cruce_fin['RADICADO FINAL'].astype(str)
    df_cruce_fin.info()
    
    # Aplicar la función renombre
    df_cruce_fin = rename_pdf(df_cruce_fin)
    
    # Aplicar Validacion Final
    df_cruce_fin = set_status(df_cruce_fin)

    # Exportar información a 
    df_cruce_fin.to_csv(r"C:\Users\angperilla\Scripts\Gestor_Notificaciones\resultado_notificaciones_bloque_2.txt", index=False, encoding="utf-8-sig", sep="|")
    
    # Renombrar PDFs
    rename_and_copy_pdfs(df_cruce_fin, DIRECTORIO, DIRECTORIO_EXPORTACION)
    
    print("🧱" * 14)
    print(f"Tiempo de ejecución: {time.time() - start_time:.2f} segundos")

    print("🧱" * 14)
    print("✅ Extracción de texto y renombramiento de PDFs completada")
    print("🧱" * 14)
    
