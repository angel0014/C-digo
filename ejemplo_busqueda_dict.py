# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 11:22:32 2025

@author: angperilla
"""

import pandas as pd

# 1. DataFrame base con múltiples CONSECUTIVOS por fila
df_base = pd.DataFrame({
    'ID': [1, 2],
    'CONSECUTIVOS': ['OBJ-202101003459; OBJ-202101003460', 'OBJ-202101003461']
})

# 2. DataFrame que será convertido en diccionario agrupado por CONSECUTIVO
not_final = pd.DataFrame({
    'CONSECUTIVO': ['OBJ-202101003459', 'OBJ-202101003460', 'OBJ-202101003460', 'OBJ-202101003461'],
    'RADICADO': ['RAD001', 'RAD002', 'RAD003', 'RAD004'],
    'RECLAMANTE': ['Juan', 'Ana', 'Luis', 'Carlos'],
    'ID RECLAMANTE': [101, 102, 103, 104],
    'NUMERO FACTURA GUIA': ['F001', 'F002', 'F003', 'F004']
})

# 3. Convertir not_final en diccionario agrupado por CONSECUTIVO
diccionario = not_final.groupby('CONSECUTIVO').apply(
    lambda x: x.drop(columns='CONSECUTIVO').to_dict(orient='records')
).to_dict()

# 4. Función para obtener los valores desde el diccionario
def obtener_valores(consecutivos, diccionario):
    claves = [c.strip() for c in consecutivos.split(';')]
    resultados = []
    for clave in claves:
        if clave in diccionario:
            resultados.extend(diccionario[clave])
    return resultados if resultados else None

# 5. Aplicar la función al DataFrame base
df_base['DETALLE'] = df_base['CONSECUTIVOS'].apply(lambda x: obtener_valores(x, diccionario))

# 6. Función para extraer campos específicos
def extraer_campo(lista_dicts, campo):
    if lista_dicts:
        return '; '.join(str(d.get(campo, '')) for d in lista_dicts)
    return None

# 7. Extraer campos deseados
for campo in ['RADICADO', 'RECLAMANTE', 'ID RECLAMANTE', 'NUMERO FACTURA','GUIA', 'F.AVISO', 'F.NOTIFICACION']:
    df_base[campo] = df_base['DETALLE'].apply(lambda x: extraer_campo(x, campo))

# 8. Eliminar columna intermedia si no se necesita
df_base.drop(columns=['DETALLE'], inplace=True)

print(df_base)
