# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 11:11:13 2024

@author: angperilla
"""

# Interfaz 
import tkinter as tk
from tkinter import ttk
from tkinter import  messagebox
from tkinter import filedialog

# Conexion azure
from azure.storage.blob import BlobServiceClient

# Manipulación data
import pandas as pd

# # Expresiones Regulares
# import re

# Tiempo
import datetime

# Sistema operativo
import os

# Portapapeles
import pyperclip

# Diccionario
from collections import defaultdict

# # Serialización archivos binarios
# import pickle    

class GestorInvestigacionesAzureApp:
    def __init__(self, root):
        """
        root: Nombre de la ventana de la interfaz de la App
        """
        
        self.root = root
        self.root.title("Investigaciones Azure")
        self.root.geometry("500x500")
        self.root.resizable(False, False)
        
        self.setup_styles()
        self.setup_ui()
        
        
    def setup_styles(self):
        
        style = ttk.Style()
        style.theme_use('clam')

        # Colores principales
        primary_color = "#2E4053"
        secondary_color = "#D5D8DC"
        accent_color = "#1E90FF"
        
        # Estilo para el título etiquetas
        style.configure('TLabelframe.Label', foreground=primary_color, font=('Roboto', 9, "bold"))

        
        # Estilo para el título de la aplicación
        style.configure('Title.TLabel', background=secondary_color, foreground='#2E4053', font=('Roboto', 16, 'bold'))

        # Estilo para los botones
        style.configure('TButton', font=('Roboto', 8))
        style.configure('TButton', background=secondary_color)
        style.map('TButton',
                  foreground=[('pressed', primary_color), ('active', 'white')],
                  background=[('pressed', '!disabled', primary_color), ('active', accent_color)],
                  relief=[('pressed', 'sunken'), ('!pressed', 'raised')])

    def setup_ui(self):
        
        # Etiqueta titulo 
        titulo = ttk.Label(self.root, text="GESTOR INVESTIGACIONES AZURE", style='Title.TLabel')
        titulo.pack(pady=15)

        # Marco superior para contener el frame de proveedores y el botón cargar insumo
        frame_superior = ttk.Frame(self.root)
        frame_superior.pack(fill=tk.X, padx=15, pady=5)

        # Frame para selección de proveedor
        # frame_proveedor = ttk.LabelFrame(frame_superior, text="Seleccione Proveedor", padding="10")
        # frame_proveedor.pack(side=tk.LEFT, padx=160)

        # self.proveedor_mok = tk.BooleanVar()
        # self.proveedor_iq = tk.BooleanVar()

        # ttk.Checkbutton(frame_proveedor, text="MOK", variable=self.proveedor_mok).pack(side=tk.LEFT, padx=5)
        # ttk.Checkbutton(frame_proveedor, text="IQ", variable=self.proveedor_iq).pack(side=tk.LEFT, padx=5)

        # # Botón Cargar Insumo al lado del frame de proveedores
        # ttk.Button(frame_superior, text="Cargar Insumo", command=self.cargar_insumo).pack(side=tk.LEFT, padx=1)

        frame_entrada = ttk.Frame(self.root, padding="10")
        frame_entrada.pack(fill=tk.X, padx=15, pady=5)
        
        # Etiqueta Radicado
        ttk.Label(frame_entrada, text="Consecutivo Investigación:",  font=("Roboto", 9, "bold")).pack(side=tk.LEFT)
        self.entrada_radicado = ttk.Entry(frame_entrada)
        self.entrada_radicado.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Marco para acciones
        self.setup_acciones()

        # Marco para resultados
        frame_resultados = ttk.LabelFrame(self.root, text="Resultados", padding="10")
        frame_resultados.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # Treeview para mostrar resultados
        self.tree_resultados = ttk.Treeview(frame_resultados, columns=("Consecutivo", "Ruta"), show='headings')
        self.tree_resultados.pack(fill=tk.BOTH, expand=True)
        
        # Configurando los encabezados del Treeview
        self.tree_resultados.heading('Consecutivo', text='Consecutivo')
        self.tree_resultados.heading('Ruta', text='Ruta')

    def setup_acciones(self):
        
        frame_acciones = ttk.Frame(self.root, padding="10")
        frame_acciones.pack(padx=10, pady=5)

        frame_individual = ttk.LabelFrame(frame_acciones, text="Individual", padding="10")
        frame_individual.pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_individual, text="   Buscar Imagen  ", command=self.buscar_imagen).pack(pady=2)
        ttk.Button(frame_individual, text="Descargar Imagen", command=self.descargar_imagen).pack(pady=2)

        frame_masivo = ttk.LabelFrame(frame_acciones, text="Masivo", padding="10")
        frame_masivo.pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_masivo, text="   Buscar Masivo  ", command=self.buscar_masivo).pack(pady=2)
        ttk.Button(frame_masivo, text="Descargar Masivo", command=self.descargar_masivo).pack(pady=2)

        frame_copiar = ttk.LabelFrame(frame_acciones, text="Información", padding="10")
        frame_copiar.pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_copiar, text="Copiar Resultados ", command=self.copiar_informacion).pack(pady=2)
        ttk.Button(frame_copiar, text="Limpiar Resultados", command=self.limpiar_informacion).pack(pady=2)
    
    #########################################################################################   
    # - Cargar Insumo
    
    # def validar_seleccion_proveedor(self):
    #    if not self.proveedor_mok.get() and not self.proveedor_iq.get():
    #        messagebox.showerror("Error", "Selecciona un proveedor.")
    #        return False
    #    return True
   
    def seleccionar_archivo(self):
        filepath = filedialog.askopenfilename(
            title="Selecciona el archivo",
            filetypes=[("Todos los archivos", "*.*"),
                       ('Archivos de texto', '*.txt *.csv'), 
                       ('Archivos Excel', '*.xlsx'), 
                       ("Archivos Pickle", "*.pkl")],
            initialdir='/'
        )
       
        return filepath
     
    def cargar_datos_archivo(self, filepath):
        try:
            if filepath.endswith('.xlsx'):
                return pd.read_excel(filepath, header=0)
            elif filepath.endswith('.csv'):
                return pd.read_csv(filepath, delimiter=',', header=0, low_memory=False, encoding='ANSI')
            # Pickle
            elif filepath.endswith('.pkl'):
                return pd.read_pickle(filepath)
            # Parquet
            elif filepath.endswith('.parquet'):
                return pd.read_parquet(filepath)
           
            
        except Exception as e:
            messagebox.showerror("Error", f"Hubo un problema cargando el archivo: {e}.")
        return None
   
    # def verificar_insumo(self, df, proveedor):
    #      """
    #      Verificar si en la ruta está el identificador del proveedor.
    #      """
    #      try:
    #          validacion_ruta = df['Ruta'].iloc[0]
    #          partes_ruta = validacion_ruta.split('/')
             
    #          if self.proveedor_mok.get() and "MOK" in partes_ruta:
    #              return True
    #          elif self.proveedor_iq.get() and "iq" in partes_ruta:
    #              return True
                
    #      except Exception as e:
    #          messagebox.showerror("Error", f"Error al verificar el insumo: {e}")
    #          return False
         
    def cargar_insumo(self):
        # if not self.validar_seleccion_proveedor():
        #     return

        # filepath = self.seleccionar_archivo()
        # if not filepath:
        #     messagebox.showerror("Error", "No se seleccionó ningún archivo.")
            # return

        # df = self.cargar_datos_archivo(filepath)
        # if df is None:
        #     return
        try:

            # proveedor_seleccionado = 'MOK' if self.proveedor_mok.get() else 'IQ'
            
            # if self.proveedor_mok.get():
            #     # print('path', os.path)
            #     # ruta_mok = os.path.join('data', 'mok-imagenes_azure.csv')
            #     # print(ruta_mok)
            #     # df = pd.read_csv(ruta_mok, encoding="ANSI", sep=',')
            #     print('path', os.path)
            #     ruta_mok = os.path.join('data', 'mok-imagenes_azure.parquet')
            #     print(ruta_mok)
            #     df = pd.read_parquet(ruta_mok) 
            
            # elif self.proveedor_iq.get():
            #     ruta_iq = os.path.join('data', 'consolidado_actualizado_iq.pkl')
            #     df = pd.read_pickle(ruta_iq)
                
            # elif self.proveedor_iq.get():
            ruta_iq = os.path.join('data', 'Investigaciones_Azure_Data.parquet')
            df = pd.read_parquet(ruta_iq)
            
            # if not self.verificar_insumo(df, proveedor_seleccionado):
            #     messagebox.showerror("Error", f"El insumo cargado no corresponde al proveedor {proveedor_seleccionado} seleccionado.")
            #     return
    
            self.insumo_df = df
            
            print(df)
            # messagebox.showinfo("Éxito", "Insumo cargado correctamente.")
        except Exception as e:
                  messagebox.showerror("Error", f"Error al verificar el insumo: {e}")
        
    def verificar_carga(self):
        # Verifica si se ha cargado un insumo
        # if not hasattr(self, 'insumo_df'):
        #     messagebox.showerror("Error", "Por favor, carga un insumo antes de seleccionar una opción.")
        
        if not hasattr(self, 'insumo_df') or self.insumo_df.empty:
            messagebox.showerror("Error", "No se ha detectado ningún archivo. Por favor, asegúrate de tener los insumos en tu equipo local. ")
            return
        
    def buscar_masivo(self): 
        # if not self.validar_seleccion_proveedor():
        #     return

        filepath = self.seleccionar_archivo()
        if not filepath:
            messagebox.showerror("Error", "No se ha seleccionado ningún archivo con información de los consecutivos de investigación.")
            return

        df = self.cargar_datos_archivo(filepath)
        if df is None:
            return

        self.radicados_df = df[df.columns[0]].astype(str).tolist()
        self.radicados = self.radicados_df
        messagebox.showinfo("Éxito", " El archivo con los consecutivos se ha cargado correctamente.")
        
        messagebox.showinfo("Búsqueda", "Estamos buscando los consecutivos...")
        
        # Funcion Buscar Imagen
        self.buscar_imagen()
        
 
   # - Fin
   ##########################################################################################
   # - Buscar_Imagen 
   
    # def limpiar_radicado_mok(self, radicado):
    #    radicado_limpio = radicado.strip()[-10:].lstrip('0')
       
    #    return radicado_limpio

    def limpiar_radicado_iq(self, radicado):
        radicado_limpio = radicado.strip()
        # patron = re.compile(r"^[CIRV]\w*\d$")
        
        return radicado_limpio # if patron.match(radicado_limpio) else None

    def buscar_imagen(self):
        
        
        self.cargar_insumo()
        
        
        # Verificar Insumo
        self.verificar_carga()
                
        radicados_buscados =[self.entrada_radicado.get().strip()] if self.entrada_radicado.get().strip() else self.radicados if hasattr(self, 'radicados') else []
        print(radicados_buscados)
        
        
        if not radicados_buscados:
            messagebox.showerror("Error", "Debes ingresar un consecutivo o cargar un archivo con el listado de consecutivos a buscar.")
        
        df_resultado = self.buscar_imagen_funcion(self.insumo_df, radicados_buscados)
                
        
        self.mostar_resultados(df_resultado)
        
    def buscar_imagen_funcion(self, df, radicados):
        # Utilizar un conjunto para almacenar tuplas únicas de (radicado, ruta)
        resultados = set()
    
        if isinstance(radicados, str):
            radicados = [radicados]
            
            print(radicados)
        
        for radicado in radicados:
            radicado_limpio = self.limpiar_radicado_iq(radicado)
            if radicado_limpio:
                df_filtrado = df[df['Ruta'].str.contains(radicado_limpio, case=False, na=False)]
                for ruta in df_filtrado['Ruta']:
                    resultados.add((radicado, ruta))
            
            

        # # Convertir el conjunto de resultados en un DataFrame
        df_coincidencias = pd.DataFrame(list(resultados), columns=['Consecutivo', 'Ruta'])
        
        if df_coincidencias.empty:
            messagebox.showinfo("Información", "No hay información para el consecutivo seleccionado.")
            return
        
        
        return df_coincidencias
    
    def mostar_resultados(self, df_resultado):
    
        # Limpia el Treeview
        for i in self.tree_resultados.get_children():
            self.tree_resultados.delete(i)
        
        for _, row in df_resultado.iterrows():
            self.tree_resultados.insert("", tk.END, values=(row['Consecutivo'], row['Ruta']))
    
    # - Fin   
   #############################################################################################
   # - DESCARGAR IMAGEN
         
    def inicializar_cliente_azure(self):
        # account_key = '?sv=2021-04-10&ss=btqf&srt=sco&st=2023-12-21T14%3A15%3A13Z&se=2024-06-22T14%3A15%3A00Z&sp=rwdla&sig=nFC62A%2FVb98k13OBGy5WxlDii5opj0EOsAh%2F7qdfSOA%3D' # anterior
        account_key = '?sv=2023-01-03&ss=btqf&srt=sco&st=2025-01-02T15%3A59%3A48Z&se=2025-12-31T04%3A59%3A00Z&sp=rwdftlacup&sig=9oorggbD8tYsRT0NqNpfVrINitUMZAhhj3DQD3cuTUk%3D'
        return BlobServiceClient(account_url='https://stea2containeriq2.blob.core.windows.net', credential=account_key)
    
    def obtener_rutas_y_radicados_desde_treeview(self):
        datos_agrupados= defaultdict(list)
        for item in self.tree_resultados.get_children():
            radicado, ruta = self.tree_resultados.item(item, "values")[:2]
            datos_agrupados[radicado].append(ruta)
        return datos_agrupados

    def descargar_imagen(self):
      
        if not self.tree_resultados.get_children():
            messagebox.showerror("Error", "No hay resultados para descargar.")
            return
        
        # self.validar_seleccion_proveedor()

        datos_agrupados = self.obtener_rutas_y_radicados_desde_treeview()
        print(datos_agrupados)
        
        #
        self.descargar_archivos_iq(datos_agrupados)
            

    # def descargar_archivos_mok(self, datos_agrupados):
        
        
    #     try:            
    #         blob_service_client = self.inicializar_cliente_azure()
    #         container_name = 'datos'
            
    #         for radicado, rutas in datos_agrupados.items():
    #             carpeta_radicado = os.path.join(os.getcwd(), radicado)
    #             os.makedirs(carpeta_radicado, exist_ok=True)
                
    #             rutas_descargadas = []
            
                 
    #             for ruta in rutas[:20]:
    #                 partes_ruta = ruta.split('/')
    #                 blob_name = partes_ruta[-1]
    #                 blob_carpeta = '/'.join(partes_ruta[:-1])
            
    #                 try:
    #                     container_client = blob_service_client.get_container_client(container_name)
    #                     blob_client = container_client.get_blob_client(f'{blob_carpeta}/{blob_name}')
    #                     blob_data = blob_client.download_blob()
    #                     ruta_local = os.path.join(carpeta_radicado, blob_name)
                
    #                     with open(ruta_local, 'wb') as archivo_local:
    #                         archivo_local.write(blob_data.readall())
    #                         rutas_descargadas.append(ruta)
    #                         print("rutas_descargadas",rutas_descargadas)
                
    #                 except Exception as e:
    #                     messagebox.showerror("Error de Descarga", f"No se pudo descargar la imagen {blob_name}. Error: {e}")
    #                     continue
    #             # Crear y guardar excel
    #             if rutas_descargadas:
    #                 df = pd.DataFrame(rutas_descargadas, columns=['Rutas'])
    #                 nombre_archivo_excel = f"{radicado}.xlsx"
    #                 ruta_completa_excel = os.path.join(carpeta_radicado, nombre_archivo_excel)
    #                 df.to_excel(ruta_completa_excel, index=False)
                
    #         messagebox.showinfo('Descarga Completa', 'Todas las imagenes han sido descargadas.')
                
    #     except Exception as e:
    #         messagebox.showerror("Error", f"No se pudo establecer conexión con Azure. Error: {e}")
           
    def descargar_archivos_iq(self, datos_agrupados):
        blob_service_client = self.inicializar_cliente_azure()
        container_name = 'datos'
        
        consecutivos_descargados = []
    
        for radicado, rutas in datos_agrupados.items():
            carpeta_destino_local = os.path.join(os.getcwd(), radicado)
            os.makedirs(carpeta_destino_local, exist_ok=True)
            
            # rutas_descargadas = []
     
            for ruta_carpeta_azure in rutas:
                
                # print(ruta_carpeta_azure)
                partes_ruta = ruta_carpeta_azure.split('/')
                blob_name = partes_ruta[-1]
                # print('blob name:',blob_name)
                blob_carpeta = '/'.join(partes_ruta[:-1])
                # print('blob carpeta:',blob_carpeta)
                
                container_client = blob_service_client.get_container_client(container_name)
                blobs = container_client.list_blobs(f'{blob_carpeta}/{blob_name}')
                # print(blobs)
                
                if not blobs or not container_client:
                    messagebox.showerror("Error", "La IP Pública no está habilitada o verifique su conexión a CITRIX.")   
                 
                else:
                    for blob in blobs:
                        blob_client = container_client.get_blob_client(blob=blob.name)
                        ruta_local_completa = os.path.join(carpeta_destino_local, blob.name.split('/')[-1])
                        
                        
                        try:
                            with open(ruta_local_completa, 'wb') as archivo_local:
                                blob_data = blob_client.download_blob().readall()
                                archivo_local.write(blob_data)
                            # rutas_descargadas.append(blob.name)
                            # print(f"Descargado exitosamente: {blob.name}")
                        except Exception as e:
                            messagebox.showerror("Error de Descarga", f"No se pudo descargar el archivo {blob.name}. Error: {e}")
                            continue
                        
                        consecutivos_descargados.append(radicado)
     
        # Generar y guardar el archivo Excel con los consecutivos descargados
        # Obtener la fecha y hora actual
        fecha_hora_actual = datetime.datetime.now()

        # Formatear la fecha y hora como una cadena
        fecha_hora_formateada = fecha_hora_actual.strftime("%Y%m%d_%H%M%S")
        
        df = pd.DataFrame(consecutivos_descargados, columns=['Consecutivo'])
        nombre_archivo_excel = f"Resultado_Investigaciones_{fecha_hora_formateada}.xlsx"
        ruta_completa_excel = os.path.join(os.getcwd(), nombre_archivo_excel)
        df.to_excel(ruta_completa_excel, index=False)
        # print(f"Registro de descargas para {radicado} guardado en: {ruta_completa_excel}")
        
            
        
        messagebox.showinfo('Descarga Completa', "Todas las imágenes han sido descargadas.")
   
    
    def descargar_masivo(self):
        # Verificar insumo_df
        self.verificar_carga()
        
        # # Verificar seleccion proveedor
        # self.validar_seleccion_proveedor()
        
        # Resultado Busqueda
        if not self.tree_resultados.get_children():
            messagebox.showerror("Error", "No hay resultados para descargar.")
            return
        
        # Funcion descargar imagen
        self.descargar_imagen()
        
  # - FIN     
 ###########################################################################################   
    def copiar_informacion(self):
        datos_str = ""
        # Verifica si hay resultados en la lista para copiar
        if not self.tree_resultados.get_children():
            messagebox.showinfo("Información", "No hay resultados para copiar.")
            return
        datos_str = ""
        
        for item in self.tree_resultados.get_children():
            valores = self.tree_resultados.item(item,"values")
            datos_str += ", ".join(valores) + "\n"
    
   
        # Copiar los resultados al portapapeles con pyperclip
        pyperclip.copy(datos_str)
        messagebox.showinfo("Éxito", "La información ha sido copiada al portapapeles.")
        
    def limpiar_informacion(self):
        # # Resetear self.insumo_df a un DataFrame vacío
        self.insumo_df = pd.DataFrame()
    
        # Limpiar los resultados del Treeview
        for item in self.tree_resultados.get_children():
            self.tree_resultados.delete(item)
        
        # Limpiar el contenido de la entrada de radicado
        self.entrada_radicado.delete(0, tk.END)    
        
        # # Deseleccionar los checkboxes
        # self.proveedor_mok.set(False)
        # self.proveedor_iq.set(False)
                
    
        # Opcional: Mostrar un mensaje indicando que la limpieza ha sido realizada
        messagebox.showinfo("Información", "Los resultados anteriores han sido borrados. Estás listo para una nueva búsqueda.")

  
root = tk.Tk()
app = GestorInvestigacionesAzureApp(root)
root.mainloop()
