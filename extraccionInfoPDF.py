# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 13:21:39 2024

@author: angperilla
"""

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

def pdf_to_images(pdf_path):
    pdf_document = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        images.append(img)
    
    return images

def ocr_image(image):
    text = pytesseract.image_to_string(image)
    return text

def extract_text_from_pdf(pdf_path):
    images = pdf_to_images(pdf_path)
    texts = [ocr_image(img) for img in images]
    return "\n".join(texts)

# Ejemplo de uso
pdf_path = "factura_prueba.pdf"
texto_extraido = extract_text_from_pdf(pdf_path)
print(texto_extraido)
