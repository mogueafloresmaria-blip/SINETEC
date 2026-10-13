# -*- coding: utf-8 -*-
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Import data
from scripts.generar_documentos_md_html import (
    TITULO, SUBTITULO, INSTITUCION, SECCIONES_DATA, DOCS_DIR
)

# Registrar fuentes TrueType de Windows
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Italic', 'C:/Windows/Fonts/ariali.ttf'))

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        if self._pageNumber == 1:
            return
        self.saveState()
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor("#666666"))
        
        # Encabezado
        self.drawString(54, 11 * inch - 36, "EduNova - SINETEC | Documentación Técnica de Producción")
        self.setStrokeColor(colors.HexColor("#D4A373"))
        self.setLineWidth(0.5)
        self.line(54, 11 * inch - 40, 8.5 * inch - 54, 11 * inch - 40)
        
        # Pie de página
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(8.5 * inch - 54, 36, page_text)
        self.drawString(54, 36, "Confidencial - Uso Académico e Institucional EduNova")
        self.line(54, 46, 8.5 * inch - 54, 46)
        self.restoreState()

def build_pdf_documentation(pdf_path):
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=17,
        leading=21,
        textColor=colors.HexColor('#3D2314'),
        alignment=1,
        spaceAfter=14
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Arial-Italic',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#8C5835'),
        alignment=1,
        spaceAfter=25
    )
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=11.5,
        leading=14.5,
        textColor=colors.HexColor('#3D2314'),
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#222222'),
        spaceAfter=5
    )
    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#3D2314')
    )
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#222222')
    )

    story = []

    # PORTADA
    story.append(Spacer(1, 30))
    story.append(Paragraph(INSTITUCION, ParagraphStyle('CoverPre', parent=styles['Normal'], fontName='Arial-Bold', fontSize=10.5, leading=14, textColor=colors.HexColor('#8C5835'), alignment=1, spaceAfter=18)))
    story.append(Paragraph(TITULO.replace(': ', ':<br/>'), title_style))
    story.append(Paragraph(SUBTITULO, subtitle_style))
    story.append(Spacer(1, 15))

    meta_table_data = [
        [Paragraph("<b>Proyecto:</b>", table_cell_style), Paragraph("EduNova - SINETEC", table_cell_style)],
        [Paragraph("<b>Tipo de Documento:</b>", table_cell_style), Paragraph("Manual Técnico Formal de Despliegue en Producción", table_cell_style)],
        [Paragraph("<b>Destinatario / Evaluación:</b>", table_cell_style), Paragraph("Sustentación Docente / Entrega de Proyecto", table_cell_style)],
        [Paragraph("<b>Versión del Software:</b>", table_cell_style), Paragraph("2.4.0 (Listo para Producción)", table_cell_style)],
        [Paragraph("<b>Pila de Producción:</b>", table_cell_style), Paragraph("Django 5.x | Python 3.13 | MySQL 8.0 | Gunicorn | Nginx", table_cell_style)],
        [Paragraph("<b>Fecha:</b>", table_cell_style), Paragraph("Octubre de 2026", table_cell_style)]
    ]
    t_meta = Table(meta_table_data, colWidths=[2.2*inch, 4.3*inch])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#FAEDCD')),
        ('BACKGROUND', (1,0), (1,-1), colors.HexColor('#FDFBF7')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D4A373')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_meta)
    story.append(PageBreak())

    # ÍNDICE
    story.append(Paragraph("ÍNDICE GENERAL DE CONTENIDOS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#8C5835'), spaceBefore=2, spaceAfter=8))
    
    for sec in SECCIONES_DATA:
        f_style = ParagraphStyle(
            'TOCItem',
            parent=styles['Normal'],
            fontName='Arial-Bold',
            fontSize=8,
            leading=10.5,
            textColor=colors.HexColor('#3D2314')
        )
        story.append(Paragraph(f"{sec['num']}. {sec['title']}", f_style))
    story.append(PageBreak())

    def add_code(block):
        lines = block.strip().split('\n')
        html_code = "<br/>".join([l.replace(" ", "&nbsp;") for l in lines])
        p = Paragraph(html_code, code_style)
        t = Table([[p]], colWidths=[6.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F5EFE6')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#D4A373')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        return t

    for sec in SECCIONES_DATA:
        story.append(Paragraph(f"{sec['num']}. {sec['title']}", h1_style))
        paragraphs = sec['content'].split('\n\n')
        for par in paragraphs:
            if any(par.strip().startswith(cmd) for cmd in [
                'sudo ', 'pip ', 'python ', 'git ', 'chmod ', 'chown ', 'cd ',
                '[Unit]', 'server {', '#!/bin/bash', 'CREATE ', '-- '
            ]):
                story.append(add_code(par))
                story.append(Spacer(1, 3))
            else:
                formatted_par = par.replace('\n', '<br/>')
                story.append(Paragraph(formatted_par, body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Documento PDF regenerado en: {pdf_path}")

if __name__ == "__main__":
    target_pdf = os.path.join(DOCS_DIR, "Documentacion_Tecnica_Instalacion_Despliegue_EduNova.pdf")
    build_pdf_documentation(target_pdf)
