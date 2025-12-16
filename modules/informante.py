from abc import ABC, abstractmethod
from modules.databases import Reclamo
from wordcloud import WordCloud, ImageColorGenerator
from nltk.corpus import stopwords
from pdfkit import configuration, from_string
from jinja2 import FileSystemLoader, Environment, Template
from datetime import datetime
from flask import send_file

import os
import matplotlib.pyplot as plt
import aspose.words as aw

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4

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
            background_color="white",
            colormap="viridis",
            width=800,
            height=400
        ).generate(texto_completo)
        
        # Guardamos según el tipo

        nombre_limpio = departamento.lower().replace(' ', '_')
        nombre_archivo = f"nube_palabras_{nombre_limpio}.{tipo}"
        ruta_salida = os.path.join(ruta_diagramas, nombre_archivo)


        if tipo == 'svg':
            svg_content= wordcloud.to_svg()
            with open(ruta_salida, "w", encoding="utf-8") as f:
                    f.write(svg_content)
        else:  # png por defecto
            wordcloud.to_file(ruta_salida)
        return ruta_salida
    


class GraficadorDiagramaCircular(Graficardor):
    def graficar(self, admin, departamento, ruta_base, tipo):
        """"Genera diagrama circular"""

        if ruta_base == 'default':
            ruta_base = os.path.abspath(os.path.dirname(__file__))
        
        ruta_diagramas = os.path.join(ruta_base, "..", "static", "diagramas")
        os.makedirs(ruta_diagramas, exist_ok=True)

        plt.figure(figsize=[10,8])
        estados_reclamos=["pendiente", "en proceso", "resuelto", "inválido"]
        reclamos_enproceso, reclamos_pendiente, reclamos_resuelto, reclamos_invalido = admin.obtener_reclamos_departamento_estado(departamento)

        cantidades=[len(reclamos_pendiente),
                    len(reclamos_enproceso),
                    len(reclamos_resuelto), 
                    len(reclamos_invalido)]
        
        plt.style.use("ggplot")
        plt.title("Estados de los reclamos")
        plt.pie(x=cantidades, labels=estados_reclamos, autopct="%.2f%%", labeldistance=None)              
        plt.legend(loc="upper left")
        plt.axis("equal")
        
        nombre_limpio = departamento.lower().replace(' ', '_')
        nombre_archivo = f"diagrama_circular_{nombre_limpio}.{tipo}"
        ruta_salida = os.path.join(ruta_diagramas, nombre_archivo)
      
        if tipo.lower() == 'svg':
            # Formato vectorial
            plt.savefig(ruta_salida, bbox_inches='tight', format='svg')
        else:
            # png por defecto
            plt.savefig(ruta_salida, dpi=300, bbox_inches='tight')
        
        plt.close()

class Informante(ABC):
    @abstractmethod
    def __init__(self,GraficadorPalabrasClave,GraficadorDiagramaCircular):
        self._GraficadorPalabrasClave=GraficadorPalabrasClave
        self._GraficadorDiagramaCircular=GraficadorDiagramaCircular

    @abstractmethod
    def generar_informe(self, reclamos):
        pass

class InformantePDF(Informante):
    def __init__(self, graficador_torta, graficador_nube):
        """
        Inicializa el informante PDF
        
        Args:
            graficador_torta: GraficadorDiagramaCircular
            graficador_nube: GraficadorPalabrasClave
        """
        self._graficador_torta = graficador_torta
        self._graficador_nube = graficador_nube

    def generar_informe(self, departamento, admin_datos):
        """Genera un informe PDF con gráficos"""
        
        print(f"📄 Generando informe PDF para: {departamento}")
        
        # 1. Generar gráficos
        try:
            self._graficador_torta.graficar(
                admin_datos, 
                departamento, 
                'default', 
                'png'
            )
            self._graficador_nube.graficar(
                admin_datos, 
                departamento, 
                'default', 
                'png'
            )
            print("✅ Gráficos generados")
        except Exception as e:
            print(f"❌ Error al generar gráficos: {e}")
            return None
        
        # 2. Construir rutas de los gráficos
        ruta_base = os.path.abspath(os.path.dirname(__file__))
        ruta_diagramas = os.path.join(ruta_base, "..", "static", "diagramas")
        
        nombre_limpio = departamento.lower().replace(' ', '_')
        
        ruta_diagrama = os.path.join(ruta_diagramas, f"diagrama_circular_{nombre_limpio}.png")
        ruta_nube = os.path.join(ruta_diagramas, f"nube_palabras_{nombre_limpio}.png")
        
        print(f"🔍 Buscando diagrama: {ruta_diagrama}")
        print(f"🔍 Buscando nube: {ruta_nube}")
        
        # 3. Verificar que existen
        if not os.path.exists(ruta_diagrama):
            print(f"⚠️  No existe: {ruta_diagrama}")
            ruta_diagrama = None
        
        if not os.path.exists(ruta_nube):
            print(f"⚠️  No existe: {ruta_nube}")
            ruta_nube = None
        
        # 4. Crear directorio para PDFs
        ruta_docs = os.path.join(ruta_base, "..", "static", "docs")
        os.makedirs(ruta_docs, exist_ok=True)
        
        # Nombre único del PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_pdf = f"Informe_{nombre_limpio}_{timestamp}.pdf"
        ruta_pdf = os.path.join(ruta_docs, nombre_pdf)
        
        print(f"📄 Creando PDF en: {ruta_pdf}")
        
        # 5. Crear el PDF
        try:
            c = canvas.Canvas(ruta_pdf, pagesize=A4)
            width, height = A4
            
            # Título
            c.setFont('Helvetica-Bold', 20)
            c.drawString(50, height - 50, f"Informe de Reclamos")
            
            c.setFont('Helvetica', 14)
            c.drawString(50, height - 80, f"Departamento: {departamento}")
            
            c.setFont('Helvetica', 10)
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            c.drawString(50, height - 100, f"Fecha: {fecha}")
            
            # Línea separadora
            c.line(50, height - 110, width - 50, height - 110)
            
            y_pos = height - 140
            
            # Insertar diagrama circular
            if ruta_diagrama and os.path.exists(ruta_diagrama):
                c.setFont('Helvetica-Bold', 12)
                c.drawString(50, y_pos, "Estado de Reclamos:")
                y_pos -= 20
                
                try:
                    c.drawImage(ruta_diagrama, 50, y_pos - 250, width=250, height=250)
                    y_pos -= 270
                    print("✅ Diagrama insertado")
                except Exception as e:
                    print(f"❌ Error al insertar diagrama: {e}")
                    c.drawString(50, y_pos, "Error al cargar diagrama")
                    y_pos -= 20
            
            # Insertar nube de palabras
            if ruta_nube and os.path.exists(ruta_nube):
                if y_pos < 300:  # Nueva página si no hay espacio
                    c.showPage()
                    y_pos = height - 50
                
                c.setFont('Helvetica-Bold', 12)
                c.drawString(50, y_pos, "Palabras Clave:")
                y_pos -= 20
                
                try:
                    c.drawImage(ruta_nube, 50, y_pos - 250, width=250, height=250)
                    print("✅ Nube insertada")
                except Exception as e:
                    print(f"❌ Error al insertar nube: {e}")
                    c.drawString(50, y_pos, "Error al cargar nube")
            
            # Guardar PDF
            c.save()
            print(f"✅ PDF guardado: {ruta_pdf}")
            
            # ✅ ESTO ES CRÍTICO: Retornar send_file()
            return send_file(
                ruta_pdf,
                as_attachment=True,
                download_name=nombre_pdf,
                mimetype='application/pdf'
            )
        
        except Exception as e:
            print(f"❌ Error al crear PDF: {e}")
            import traceback
            traceback.print_exc()
            return None

    
        
class InformanteHTML(Informante):   

    def __init__(self, graficador_torta, graficador_nube):
        self._graficador_torta = graficador_torta
        self._graficador_nube = graficador_nube


    def generar_informe(self, departamento,admin_datos):
        print(f"📄 Generando informe HTML para: {departamento}")

        # 1. Generar gráficos (Formato SVG para HTML para mejor calidad)
        try:
            self._graficador_torta.graficar(
                admin_datos, 
                departamento, 
                'default', 
                'svg'
            )
            self._graficador_nube.graficar(
                admin_datos, 
                departamento, 
                'default', 
                'svg'
            )
            print("✅ Gráficos SVG generados")
        except Exception as e:
            print(f"❌ Error al generar gráficos: {e}")
            return None

        # 2. Construir rutas (Igual que en InformantePDF)
        ruta_base = os.path.abspath(os.path.dirname(__file__))
        ruta_diagramas = os.path.join(ruta_base, "..", "static", "diagramas")
        ruta_docs = os.path.join(ruta_base, "..", "static", "docs")
        
        # Asegurar que existe el directorio de documentos
        os.makedirs(ruta_docs, exist_ok=True)

        # Nombre limpio para los archivos
        nombre_limpio = departamento.lower().replace(' ', '_')

        # Rutas específicas de los gráficos generados
        ruta_diagrama = os.path.join(ruta_diagramas, f"diagrama_circular_{nombre_limpio}.svg")
        ruta_nube = os.path.join(ruta_diagramas, f"nube_palabras_{nombre_limpio}.svg")

        # 3. Leer contenido de los SVG para incrustarlos
        torta_content = "<div>No se pudo cargar el diagrama circular</div>"
        nube_content = "<div>No se pudo cargar la nube de palabras</div>"

        if os.path.exists(ruta_diagrama):
            try:
                with open(ruta_diagrama, 'r', encoding='utf-8') as file:
                    torta_content = file.read()
            except Exception as e:
                print(f"⚠️ Error leyendo diagrama circular: {e}")
        else:
            print(f"⚠️ Archivo no encontrado: {ruta_diagrama}")

        if os.path.exists(ruta_nube):
            try:
                with open(ruta_nube, 'r', encoding='utf-8') as file:
                    nube_content = file.read()
            except Exception as e:
                print(f"⚠️ Error leyendo nube de palabras: {e}")
        else:
            print(f"⚠️ Archivo no encontrado: {ruta_nube}")

        # 4. Obtener datos de reclamos
        reclamos = admin_datos.ObtenerReclamos(departamento)
        
        # Construir items de la lista
        items_html = ""
        for reclamo in reclamos:
            items_html += f"        <li class='list-group-item'>{reclamo.titulo} | <strong>{reclamo.estado}</strong></li>\n"

        # 5. Construir el HTML completo
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Informe de Reclamos - {departamento}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        .meta {{ color: #777; font-size: 0.9em; margin-bottom: 30px; }}
        .charts-container {{ display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin-bottom: 40px; }}
        .chart-box {{ border: 1px solid #ddd; padding: 10px; border-radius: 8px; width: 45%; min-width: 300px; text-align: center; }}
        .reclamos-list {{ max-width: 800px; margin: 0 auto; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ background: #f9f9f9; border-bottom: 1px solid #eee; padding: 10px; margin-bottom: 5px; }}
        li:hover {{ background: #f1f1f1; }}
    </style>
</head>
<body>
    <h1>Informe de Reclamos: {departamento}</h1>
    <div class="meta">Generado el: {fecha}</div>

    <div class="charts-container">
        <div class="chart-box">
            <h3>Estado de Reclamos</h3>
            {torta_content}
        </div>
        <div class="chart-box">
            <h3>Palabras Clave</h3>
            {nube_content}
        </div>
    </div>

    <div class="reclamos-list">
        <h3>Detalle de Reclamos</h3>
        <ul>
            {items_html}
        </ul>
    </div>
</body>
</html>"""

        # 6. Guardar y Retornar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"Informe_{nombre_limpio}_{timestamp}.html"
        ruta_salida_html = os.path.join(ruta_docs, nombre_archivo)

        try:
            with open(ruta_salida_html, 'w', encoding='utf-8') as informe:
                informe.write(html_template)
            
            print(f"✅ Informe HTML guardado en: {ruta_salida_html}")

            return send_file(
                ruta_salida_html, 
                as_attachment=True,
                download_name=nombre_archivo,
                mimetype='text/html'
            )
        except Exception as e:
            print(f"❌ Error al guardar/enviar HTML: {e}")
            return None