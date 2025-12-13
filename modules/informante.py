from abc import ABC, abstractmethod
from modules.databases import Reclamo
from wordcloud import WordCloud, ImageColorGenerator
from nltk.corpus import stopwords
from pdfkit import configuration, from_string
from jinja2 import FileSystemLoader, Environment, Template
from fpdf import FPDF
from flask import send_file

import os
import matplotlib.pyplot as plt
import aspose.words as aw

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class Graficardor(ABC):
    @abstractmethod
    def graficar(self, admin, departamento, ruta_base, tipo):
        pass

class GraficadorPalabrasClave(Graficardor):

    def graficar (self, admin, departamento, ruta_base, tipo):
        """Grafica las palabras que más se repiten en los reclamos"""
        
        if ruta_base == 'default':
            ruta_base = os.path.abspath(os.path.dirname(__file__))
        
        # Construimos la ruta de salida
        ruta_diagramas = os.path.join(ruta_base, "..", "static", "diagramas")
        os.makedirs(ruta_diagramas, exist_ok=True)
        
        # Recolectamos el texto
        reclamos = admin.obtener_reclamos(departamento)
        textos = [f"{r.titulo} {r.descripcion}" for r in reclamos]
        texto_completo = " ".join(textos)
        
        if not texto_completo.strip():
            return None
        
        # Generamos nube de palabras
        from nltk.corpus import stopwords
        palabras_excluir = stopwords.words('spanish')
        
        wordcloud = WordCloud(
            stopwords=palabras_excluir,
            max_words=15,
            background_color="blue",
            width=800,
            height=400
        ).generate(texto_completo)
        
        # Guardamos según el tipo
        nombre_archivo = f"nube_palabras_{departamento}.{tipo}"
        ruta_salida = os.path.join(ruta_diagramas, nombre_archivo)
        
        if tipo == 'svg':
            wordcloud.to_svg(ruta_salida)
            print(f"✅ SVG guardado en: {ruta_salida}")
        else:  # png por defecto
            wordcloud.to_file(ruta_salida)
            print(f"✅ PNG guardado en: {ruta_salida}")
        return ruta_salida
    
#chequear que funcione!!! 

class GraficadorDiagramaCircular(Graficardor):
    def graficar(self, reclamos):
        pass    

class Informante(ABC):
    @abstractmethod
    def __init__(self,GraficadorPalabrasClave,GraficadorDiagramaCircular):
        self._GraficadorPalabrasClave=GraficadorPalabrasClave
        self._GraficadorDiagramaCircular=GraficadorDiagramaCircular

    @abstractmethod
    def generar_informe(self, reclamos):
        pass

class InformantePDF(Informante):
    def __init__(self, GraficadorPalabrasClave, GraficadorDiagramaCircular):
        super().__init__(GraficadorPalabrasClave, GraficadorDiagramaCircular)

    def generar_informe(self, reclamos):
        pass
class InformanteHTML(Informante):   
    def __init__(self, GraficadorPalabrasClave, GraficadorDiagramaCircular):
        super().__init__(GraficadorPalabrasClave, GraficadorDiagramaCircular)

    def generar_informe(self, reclamos):
        pass
    