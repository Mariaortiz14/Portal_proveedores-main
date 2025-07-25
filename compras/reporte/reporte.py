from reportlab.platypus import (SimpleDocTemplate, Paragraph, Image, Spacer, Table, TableStyle)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4, inch
from reportlab.graphics.shapes import Line, Drawing
from reportlab.lib.colors import Color
from reportlab.lib.units import cm
from io import BytesIO
import datetime
import os


class ReportePDF:
    def __init__(self, buffer):
        self.buffer = buffer
        self.styleSheet = getSampleStyleSheet()
        self.elements = []

        self.doc = SimpleDocTemplate(self.buffer,
                                     pagesize=A4,
                                     leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                                     topMargin=0.5 * cm, bottomMargin=2.5 * cm)

        self.colorFEPCORed0 = Color(255, 49, 49, 1)
        self.colorFEPCORed1 = Color(255, 154, 151, 1)
        self.colorFEPCORed2 = Color(232, 87, 82, 1)

        self.PagesHeader()
        self.generar_tabla_proveedores()

        self.doc.build(self.elements)

    def PagesHeader(self):
        logo_path = os.path.join(os.getcwd(), "compras/reporte/img/logo_completo.png")
        logo2_path = os.path.join(os.getcwd(), "compras/reporte/img/6.png")

        logo = Image(logo_path, width=1 * inch, height=0.8 * inch)
        logo2 = Image(logo2_path, width=0.6 * inch, height=0.6 * inch)

        table_data = [[logo, logo2]]
        table = Table(table_data, colWidths=[1 * inch, 1 * inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        table.hAlign = "LEFT"

        title = Paragraph("Reporte De Inscripción <br /> De Proveedores Y/O Contratistas Nacionales", self.styleSheet["Heading4"])
        date = Paragraph("Fecha: " + str(datetime.date.today()), self.styleSheet["Heading5"])

        text_table = Table([["", title, date]], colWidths=[0.5 * inch, 3.2 * inch, 2 * inch])
        outer_table = Table([[table, text_table]], colWidths=[1.5 * inch, 5 * inch])

        self.elements.append(outer_table)
        self.elements.append(Spacer(0, 0))

        d = Drawing(500, 1)
        d.add(Line(-15, 0, 483, 0))
        self.elements.append(d)

    def generar_tabla_proveedores(self):
        self.elements.append(Spacer(10, 22))
        self.elements.append(Paragraph("tipo de persona: Persona Natural", self.styleSheet["Heading4"]))

        fontSize = 8
        centered = ParagraphStyle(name="centered", alignment=TA_CENTER)
        left = ParagraphStyle(name="lefted", alignment=TA_LEFT)

        headers = ["No.", "Proveedor", "Fecha registro", "Estado"]
        data = [[Paragraph(f"<b>{h}</b>", centered) for h in headers]]

        for i in range(10):
            row = [str(i+1), "X Company", "2021-01-01", "Aceptado"]
            formatted_row = [Paragraph(f"<font size='{fontSize}'>{cell}</font>", centered if idx != 1 else left) for idx, cell in enumerate(row)]
            data.append(formatted_row)

        table = Table(data, colWidths=[50, 200, 100, 80])
        table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, self.colorFEPCORed0),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        self.elements.append(table)


# Ejemplo de uso en una vista Django:
# from django.http import FileResponse
# def generar_reporte(request):
#     buffer = BytesIO()
#     ReportePDF(buffer)
#     buffer.seek(0)
#     return FileResponse(buffer, as_attachment=True, filename="Reporte.pdf")
