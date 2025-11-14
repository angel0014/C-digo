# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 21:04:33 2024

@author: angperilla
"""

import subprocess
import os

# Obtener el directorio actual
current_dir = os.getcwd()
script_name = "envio_correos_masivo_generico.py"
script_path = os.path.join(current_dir, script_name)

print(f"Ejecutando script en: {script_path}")
result = subprocess.run(["python", script_path], capture_output=True, text=True)

# Imprimir la salida del script2.py
print("Salida de script2.py:")
print(result.stdout)
print("Errores de script2.py (si los hay):")
print(result.stderr)
