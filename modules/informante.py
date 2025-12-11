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
    def graficar(self, reclamos):
        pass

class Informante(ABC):
    @abstractmethod
    def __init__(self,Graficador_torta, Graficador_nube):
        self._Graficador_torta=Graficador_torta
        self._Graficador_nube=Graficador_nube




class GraficadorTorta(Graficardor):
    def graficar (self, reclamos):
        pass

class GraficadorNube(Graficardor):
    def graficar(self, reclamos):
        pass    

    @abstractmethod
    def generar_informe(self, reclamos):
        pass

class InformantePDF(Informante):
    def __init__(self, Graficador_torta, Graficador_nube):
        super().__init__(Graficador_torta, Graficador_nube)

    def generar_informe(self, reclamos):
        pass
class InformanteHTML(Informante):   
    def __init__(self, Graficador_torta, Graficador_nube):
        super().__init__(Graficador_torta, Graficador_nube)

    def generar_informe(self, reclamos):
        pass
    