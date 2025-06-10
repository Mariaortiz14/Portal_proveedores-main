import re 
from reportlab.pdfgen import canvas
from reportlab.platypus import (SimpleDocTemplate, Paragraph, PageBreak, Image, Spacer, Table, TableStyle)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER, inch, A4
from reportlab.graphics.shapes import Line, LineShape, Drawing
from reportlab.pdfbase import pdfmetrics
from django.http import HttpResponse
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import datetime
from reportlab.lib.colors import Color
import os
from reportlab.lib.units import cm




class ReportePDF(canvas.Canvas):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Reporte.pdf"'
    def __init__(self, path):
        """
        Inicializa el objeto Reporte.

        Args:
            path (str): La ruta para guardar el reporte generado.

        Atributos:
            path (str): La ruta para guardar el reporte generado.
            styleSheet (StyleSheet): La hoja de estilo para el reporte.
            elements (list): La lista de elementos a incluir en el reporte.
            doc (SimpleDocTemplate): La plantilla del documento para el reporte.
            colorFEPCORed0 (Color): El color para FEPCO Rojo 0.
            colorFEPCORed1 (Color): El color para FEPCO Rojo 1.
            colorFEPCORed2 (Color): El color para FEPCO Rojo 2.
        """
        self.path = path
        self.styleSheet = getSampleStyleSheet()
        self.elements = []

        self.doc = SimpleDocTemplate(self.path,
        pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=0.5*cm,bottomMargin=2.5*cm)

        
        self.colorFEPCORed0 = Color(255, 49, 49, 1)
        self.colorFEPCORed1 = Color(255, 154, 151, 1)
        self.colorFEPCORed2 = Color(232, 87, 82, 1)
        

        self.PagesHeader()
        self.remoteSessionTableMaker()

        self.doc.multiBuild(self.elements)

    def PagesHeader(self):
        """
        Método que crea el encabezado de las páginas del reporte.
        """
        logo_path = os.path.join(os.getcwd(), "compras/reporte/img/logo_completo.png")
        logo = Image(logo_path, width=1*inch, height=0.8*inch)

        logo2_path = os.path.join(os.getcwd(), "compras/reporte/img/6.png")
        logo2 = Image(logo2_path, width=0.6*inch, height=0.6*inch)

        # Crear una tabla con tres columnas
        table_data = [[logo, logo2]]
        

        # Estilo de la tabla
        table_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        # Crear la tabla y aplicar el estilo
        table = Table(table_data, colWidths=[1*inch, 1*inch])
        table.setStyle(table_style)
        table.hAlign = "LEFT"

        # Crear el título
        title = Paragraph("Reporte De Inscripción <br /> De Proveedores Y/O Contratistas Nacionales", self.styleSheet["Heading4"])
        date = Paragraph("Fecha: " + str(datetime.date.today()), self.styleSheet["Heading5"])

        text_table_data =[["", title, date]]
        text_table = Table(text_table_data, colWidths=[0.5*inch, 3.2*inch, 2*inch])

        # Crear una nueva tabla que contenga la tabla original y el título
        outer_table_data = [[table, text_table]]
        outer_table = Table(outer_table_data, colWidths=[1.5*inch, 5*inch])

        # Agregar la tabla externa a los elementos
        self.elements.append(outer_table)
        self.elements.append(Spacer(0, 0))

        # Agregar la línea de división
        d = Drawing(500, 1)
        line = Line(-15, 0, 483, 0)
        line.strokeWidth = 1
        d.add(line)
        self.elements.append(d)
    
    def remoteSessionTableMaker(self):        
        spacer = Spacer(10, 22)
        self.elements.append(spacer)
        t_persona= Paragraph("tipo de persona: Persona Natural", self.styleSheet["Heading4"])
        self.elements.append(t_persona)
        d = []
        textData = ["No.", "Proveedor", "Fecha registro", ""]
                
        fontSize = 8
        centered = ParagraphStyle(name="centered", alignment=TA_CENTER)
        for text in textData:
            ptext = "<font size='%s'><b>%s</b></font>" % (fontSize, text)
            titlesTable = Paragraph(ptext, centered)
            d.append(titlesTable)        

        data = [d]
        lineNum = 1
        formattedLineData = []

        alignStyle = [ParagraphStyle(name="01", alignment=TA_CENTER),
                      ParagraphStyle(name="02", alignment=TA_LEFT),
                      ParagraphStyle(name="03", alignment=TA_CENTER),
                      ParagraphStyle(name="04", alignment=TA_CENTER),
                      ParagraphStyle(name="05", alignment=TA_CENTER)]

        for row in range(10):
            lineData = [str(lineNum), "X Company", "2021-01-01", "Aceptado"]
            #data.append(lineData)
            lineNum = lineNum + 1
            columnNumber = 0
            for item in lineData:
                ptext = "<font size='%s'>%s</font>" % (fontSize-1, item)
                p = Paragraph(ptext, alignStyle[columnNumber])
                formattedLineData.append(p)
                columnNumber = columnNumber + 1
            data.append(formattedLineData)
            formattedLineData = []
            
        # Row for total
        totalRow = ["Total de Horas", "", "", "", "30:15"]
        for item in totalRow:
            ptext = "<font size='%s'>%s</font>" % (fontSize-1, item)
            p = Paragraph(ptext, alignStyle[1])
            formattedLineData.append(p)
        data.append(formattedLineData)
        
        #print(data)
        table = Table(data, colWidths=[50, 200, 80, 80, 80])
        tStyle = TableStyle([ #('GRID',(0, 0), (-1, -1), 0.5, grey),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                #('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ("ALIGN", (1, 0), (1, -1), 'RIGHT'),
                ('LINEABOVE', (0,0), (-1,0), 1, self.colorFEPCORed0),
                ])
        table.setStyle(tStyle)
        self.elements.append(table)

if __name__ == "__main__":
   
    reporte = ReportePDF("reporte.pdf")

