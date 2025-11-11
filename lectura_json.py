# -*- coding: utf-8 -*-
"""
Created on Wed Sep  3 09:05:12 2025

@author: angperilla
"""

"""
    Script para leer resultados del archivo .json
"""

import os
import json
import pandas as pd



# Ruta del directorio raíz donde están los JSON
input_dir = r"C:\Users\angperilla\OneDrive - Mundial de Seguros S.A\Escritorio\Proyecto IA\7. Entregables IA\DEEP CLAIMS\Validaciones"
output_file = os.path.join(input_dir, "consolidado_validaciones.xlsx")

rows = []

# Recorrer carpetas y subcarpetas
for root, dirs, files in os.walk(input_dir):
    for file in files:
        if file.lower().endswith(".json"):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    # Verificar si existe la clave 'reclamaciones'
                    if "reclamaciones" in data and isinstance(data["reclamaciones"], list):
                        for item in data["reclamaciones"]:
                            # Concatenar fuentes
                            fuentes_concat = "; ".join(
                                [f"{f['doc']} (Pag: {f['pag']}) - {f['valor']}" for f in item.get('fuentes', [])]
                            )

                            # Crear fila
                            row = {
                                "archivo": file,
                                "id": item.get("id"),
                                "nro": item.get("nro"),
                                "nom": item.get("nom"),
                                "grp": item.get("grp"),
                                "consist": item.get("consist"),
                                "conf": item.get("conf"),
                                "razon_conf": item.get("razon_conf"),
                                "val_fin": item.get("val_fin"),
                                "fuentes": fuentes_concat
                            }
                            rows.append(row)
                    else:
                        print(f"⚠ No se encontró la clave 'reclamaciones' en: {file_path}")
            except Exception as e:
                print(f"❌ Error procesando {file_path}: {e}")

# Crear DataFrame y exportar a Excel
if rows:
    df = pd.DataFrame(rows)
    df.to_excel(output_file, index=False)
    print(f"✅ Archivo Excel consolidado generado: {output_file}")
else:
    print("⚠ No se encontraron datos para procesar.")
