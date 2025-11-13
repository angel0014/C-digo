# -*- coding: utf-8 -*-
"""
Created on Mon Aug 25 15:33:09 2025

@author: angperilla
"""

import pandas as pd

# DataFrame con llaves dinámicas
df_origen = pd.DataFrame({
    'llaves': [
        'OBJ-202010001456',
        'OBJ-202010001457;OBJ-202010001458',
        'OBJ-202010001459;OBJ-202010001460;OBJ-202010001461',
        'OBJ-202010001462;OBJ-202010001463;OBJ-202010001464;GIN-IQ202000005181;OBJ-202010001786;OBJ-202010001787;OBJ-202010001788;OBJ-202010001789;OBJ-20201000179'
    ]
})

# DataFrame base con información adicional
df_base = pd.DataFrame({
    'llave': [
         'OBJ-202010001457', 'OBJ-202010001458', 'OBJ-202010001459',
        'OBJ-202010001460', 'OBJ-202010001461', 'OBJ-202010001462', 'OBJ-202010001463',
        'OBJ-202010001464', 'GIN-IQ202000005181', 'OBJ-202010001786', 'OBJ-202010001787',
        'OBJ-202010001788', 'OBJ-202010001789'
    ],
    'descripcion': [
        'Desc A', 'Desc B', 'Desc C', 'Desc D', 'Desc E', 'Desc F', 'Desc G', 'Desc H',
        'Desc I', 'Desc J', 'Desc K', 'Desc L', 'Desc M'
    ],
    'categoria': [
        'Cat 1', 'Cat 1', 'Cat 2', 'Cat 2', 'Cat 3', 'Cat 3', 'Cat 4', 'Cat 4',
        'Cat 5', 'Cat 6', 'Cat 7', 'Cat 7', 'Cat 8'
    ]
})

# Diccionarios para búsqueda rápida
lookup_descripcion = dict(zip(df_base['llave'], df_base['descripcion']))
lookup_categoria = dict(zip(df_base['llave'], df_base['categoria']))

# Función para cruzar llaves y traer columnas agrupadas
def cruzar_llaves(campo):
    llaves = campo.split(';')
    descripciones = [lookup_descripcion.get(llave) for llave in llaves if llave in lookup_descripcion]
    categorias = [lookup_categoria.get(llave) for llave in llaves if llave in lookup_categoria]
    return pd.Series({
        'descripcion': ';'.join(descripciones),
        'categoria': ';'.join(categorias)
    })

# Aplicar la función
df_origen[['descripcion', 'categoria']] = df_origen['llaves'].apply(cruzar_llaves)

# Mostrar resultado
print(df_origen)

