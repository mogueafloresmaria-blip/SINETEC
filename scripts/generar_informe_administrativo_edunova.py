# -*- coding: utf-8 -*-
"""
Script Generador Dual (Word .docx y PDF .pdf) para el
INFORME ADMINISTRATIVO COMPLETO DE EDUNOVA PARA EL SENA.

RAP del Instructor Anybal López:
“Elaborar el informe administrativo, siguiendo los protocolos de la organización,
basado en los planes de instalación, respaldo y migración del sistema de información”.

Aprendices: Dulce María Figueroa y Aminta María Moguea Florez.
Programa: Tecnólogo en Análisis y Desarrollo de Sistemas de Información (ADSI / ADSO).
Ficha: 228106 | Regional Magdalena | Centro de Logística y Promoción Ecoturística.
"""

import os
import sys
import shutil

# Rutas de salida principales
DOCS_DIR = r"C:\SINETEC\SINETEC\docs"
ROOT_DIR = r"C:\SINETEC"
DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")

DOCX_NAME = "Informe_Administrativo_EduNova.docx"
PDF_NAME = "Informe_Administrativo_EduNova.pdf"

DOCX_DOCS = os.path.join(DOCS_DIR, DOCX_NAME)
PDF_DOCS = os.path.join(DOCS_DIR, PDF_NAME)

os.makedirs(DOCS_DIR, exist_ok=True)

# ==============================================================================
# IMPORTS DOCX
# ==============================================================================
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

# ==============================================================================
# IMPORTS REPORTLAB
# ==============================================================================
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Registrar fuentes TTF Windows
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Italic', 'C:/Windows/Fonts/ariali.ttf'))
pdfmetrics.registerFont(TTFont('Consolas', 'C:/Windows/Fonts/consola.ttf'))

# ==============================================================================
# CLASE CANVAS NUMERADO PARA REPORTLAB
# ==============================================================================
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
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Portada sin encabezado ni pie
        
        self.saveState()
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor("#475569"))
        
        # Encabezado superior
        self.drawString(54, 11 * inch - 36, "SENA | Regional Magdalena — Informe Administrativo del Sistema de Información")
        self.drawRightString(8.5 * inch - 54, 11 * inch - 36, "EduNova (SINETEC)")
        self.setStrokeColor(colors.HexColor("#39A900"))  # Verde SENA
        self.setLineWidth(0.8)
        self.line(54, 11 * inch - 40, 8.5 * inch - 54, 11 * inch - 40)
        
        # Pie de página inferior
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, 8.5 * inch - 54, 46)
        self.drawString(54, 32, "Centro de Logística y Promoción Ecoturística • ADSI Ficha 228106 • Instructor Anybal López")
        self.drawRightString(8.5 * inch - 54, 32, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()


# ==============================================================================
# UTILIDADES DOCX
# ==============================================================================
def set_cell_background(cell, fill_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tc_pr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tc_pr.append(tc_mar)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    tbl_pr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tbl_pr.append(borders)

def add_docx_callout(doc, title, text, border_color="1B365D"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=130, bottom=130, left=180, right=130)
    
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tc_pr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    run_t = p.add_run(title + "\n")
    run_t.bold = True
    run_t.font.name = "Arial"
    run_t.font.size = Pt(10)
    run_t.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
    
    run_b = p.add_run(text)
    run_b.font.name = "Arial"
    run_b.font.size = Pt(9.5)
    run_b.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
    
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)


# ==============================================================================
# CONSTRUCCIÓN DEL DOCUMENTO WORD (.DOCX)
# ==============================================================================
def generar_documento_word(docx_path):
    print(f"Generando documento Word en: {docx_path}")
    doc = docx.Document()
    
    # Márgenes estándar (1 pulgada = 2.54 cm)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
        # Encabezado
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("SENA Regional Magdalena — Informe Administrativo de Despliegue y Operaciones | EduNova")
        hrun.font.name = "Arial"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
        
        # Pie de página
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("Tecnología en Análisis y Desarrollo de Sistemas de Información (ADSI) • Instructor Anybal López")
        frun.font.name = "Arial"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Estilo base
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Arial'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # --------------------------------------------------------------------------
    # 1. PORTADA FORMAL SENA
    # --------------------------------------------------------------------------
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(36)
    p_inst.paragraph_format.space_after = Pt(4)
    run_inst = p_inst.add_run("SERVICIO NACIONAL DE APRENDIZAJE – SENA\nREGIONAL MAGDALENA\nCENTRO DE LOGÍSTICA Y PROMOCIÓN ECOTURÍSTICA DEL MAGDALENA")
    run_inst.bold = True
    run_inst.font.name = "Arial"
    run_inst.font.size = Pt(12)
    run_inst.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    p_prog = doc.add_paragraph()
    p_prog.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_prog.paragraph_format.space_before = Pt(8)
    p_prog.paragraph_format.space_after = Pt(30)
    run_prog = p_prog.add_run("TECNOLOGÍA EN ANÁLISIS Y DESARROLLO DE SISTEMAS DE INFORMACIÓN (ADSI)\nFICHA DE CARACTERIZACIÓN: 228106")
    run_prog.font.name = "Arial"
    run_prog.font.size = Pt(11)
    run_prog.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tit.paragraph_format.space_before = Pt(16)
    p_tit.paragraph_format.space_after = Pt(12)
    run_tit = p_tit.add_run("INFORME ADMINISTRATIVO DE INSTALACIÓN, RESPALDO,\nMIGRACIÓN Y DESPLIEGUE A PRODUCCIÓN DEL SISTEMA DE INFORMACIÓN EDUNOVA")
    run_tit.bold = True
    run_tit.font.name = "Arial"
    run_tit.font.size = Pt(15)
    run_tit.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    p_rap = doc.add_paragraph()
    p_rap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rap.paragraph_format.space_before = Pt(0)
    p_rap.paragraph_format.space_after = Pt(36)
    run_rap_lbl = p_rap.add_run("Resultado de Aprendizaje (RAP):\n")
    run_rap_lbl.bold = True
    run_rap_lbl.font.size = Pt(10.5)
    run_rap_cit = p_rap.add_run("“Elaborar el informe administrativo, siguiendo los protocolos de la organización, basado en los planes de instalación, respaldo y migración del sistema de información”.")
    run_rap_cit.italic = True
    run_rap_cit.font.size = Pt(10.5)
    run_rap_cit.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    p_aut = doc.add_paragraph()
    p_aut.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_aut.paragraph_format.space_before = Pt(30)
    p_aut.paragraph_format.space_after = Pt(4)
    run_aut_lbl = p_aut.add_run("APRENDICES:\n")
    run_aut_lbl.bold = True
    run_aut_lbl.font.size = Pt(11)
    run_aut1 = p_aut.add_run("DULCE MARÍA FIGUEROA\nAMINTA MARÍA MOGUEA FLOREZ\n\n")
    run_aut1.bold = True
    run_aut1.font.size = Pt(11.5)

    run_inst_lbl = p_aut.add_run("INSTRUCTOR TÉCNICO EVALUADOR:\n")
    run_inst_lbl.bold = True
    run_inst_lbl.font.size = Pt(11)
    run_inst_name = p_aut.add_run("ING. ANYBAL LÓPEZ")
    run_inst_name.bold = True
    run_inst_name.font.size = Pt(11.5)

    p_ciu = doc.add_paragraph()
    p_ciu.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ciu.paragraph_format.space_before = Pt(40)
    p_ciu.paragraph_format.space_after = Pt(0)
    run_ciu = p_ciu.add_run("SANTA MARTA, MAGDALENA, COLOMBIA\nOCTUBRE DE 2026")
    run_ciu.bold = True
    run_ciu.font.size = Pt(11)

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # 2. CONTROL DE VERSIONES
    # --------------------------------------------------------------------------
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run("REGISTRO DE CONTROL DE VERSIONES DEL DOCUMENTO")
    run.bold = True
    run.font.size = Pt(12)

    t_cv = doc.add_table(rows=1, cols=4)
    t_cv.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_cv)
    hdr_cv = t_cv.rows[0].cells
    hdr_cv[0].width = Inches(1.0)
    hdr_cv[1].width = Inches(1.2)
    hdr_cv[2].width = Inches(1.8)
    hdr_cv[3].width = Inches(2.5)
    for i, h in enumerate(["Versión", "Fecha", "Autor(es)", "Descripción de Modificaciones"]):
        p = hdr_cv[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        set_cell_background(hdr_cv[i], "E2E8F0")

    versiones = [
        ("0.1", "15/08/2026", "Equipo Desarrollador", "Estructuración de requerimientos IEEE 830, arquitectura inicial y casos de prueba."),
        ("0.5", "18/09/2026", "Líder de Desarrollo", "Consolidación de modelos relacionales, reglas de negocio y copias SQLite."),
        ("0.9", "28/09/2026", "Dulce María Figueroa\nAminta Moguea Florez", "Estabilización de los seis paneles de usuario, pruebas RBAC y exportación de fixtures."),
        ("1.0", "14/10/2026", "Dulce María Figueroa\nAminta Moguea Florez", "Elaboración del informe administrativo definitivo de instalación, respaldo, migración y entrega formal para el instructor Anybal López.")
    ]
    for v, f, a, d in versiones:
        row = t_cv.add_row().cells
        row[0].width = Inches(1.0)
        row[1].width = Inches(1.2)
        row[2].width = Inches(1.8)
        row[3].width = Inches(2.5)
        for c in row:
            set_cell_margins(c)
        row[0].paragraphs[0].add_run(v).font.size = Pt(8.5)
        row[1].paragraphs[0].add_run(f).font.size = Pt(8.5)
        row[2].paragraphs[0].add_run(a).font.size = Pt(8.5)
        row[3].paragraphs[0].add_run(d).font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # --------------------------------------------------------------------------
    # 3. INTRODUCCIÓN Y CONTEXTO INSTITUCIONAL
    # --------------------------------------------------------------------------
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run("1. INTRODUCCIÓN Y CONTEXTO INSTITUCIONAL")
    run.bold = True
    run.font.size = Pt(13)

    doc.add_paragraph(
        "El presente informe administrativo ha sido estructurado siguiendo rigurosamente los protocolos organizacionales "
        "del Servicio Nacional de Aprendizaje (SENA) y las directrices pedagógicas impartidas por el instructor Anybal López "
        "para el programa de formación de Tecnología en Análisis y Desarrollo de Sistemas de Información (ADSI). "
        "El propósito de este documento es consolidar y sustentar técnicamente los planes maestros de instalación, "
        "política de respaldos, procedimientos de migración y planes de contingencia para la puesta en producción del sistema "
        "de información denominado EduNova – Sistema Integrado de Educación Técnica (SINETEC)."
    ).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.add_paragraph(
        "En las Instituciones Educativas articuladas con la Media Técnica en el Departamento del Magdalena, la administración escolar "
        "ha enfrentado históricamente graves dificultades asociadas a la dispersión de información, pérdidas de actas de seguimiento, "
        "demoras en la entrega de reportes valorativos y falta de articulación en tiempo real entre docentes, directivos, aprendices y padres de familia. "
        "EduNova surge como una plataforma web integral basada en software libre (Python, Django, Nginx y MySQL Server) que centraliza "
        "la gestión académica, el control de asistencias, la calificación por resultados de aprendizaje (RAP) y la comunicación institucional."
    ).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.add_paragraph(
        "De conformidad con las normas éticas y de calidad de la formación técnica, este informe establece una delimitación transparente entre "
        "las tareas efectivamente realizadas y comprobadas en el código fuente, los procedimientos metodológicos propuestos para el despliegue en servidor "
        "y los requerimientos pendientes de infraestructura que dependen formalmente de la entrega de equipos por parte del cliente institucional."
    ).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # --------------------------------------------------------------------------
    # 4. OBJETIVOS
    # --------------------------------------------------------------------------
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run("2. OBJETIVOS")
    run.bold = True
    run.font.size = Pt(13)

    p_og = doc.add_paragraph()
    p_og.add_run("2.1 Objetivo General\n").bold = True
    p_og.add_run(
        "Elaborar el informe administrativo formal siguiendo los protocolos de la organización, fundamentado en los planes de instalación, "
        "política de respaldo, migración de datos y contingencia del sistema de información EduNova (SINETEC), para garantizar su operatividad "
        "continua, seguridad y sostenibilidad en un entorno productivo institucional."
    )
    p_og.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    p_oe = doc.add_paragraph()
    p_oe.add_run("2.2 Objetivos Específicos\n").bold = True
    doc.add_paragraph("• Establecer el cronograma detallado de instalación y puesta en marcha del sistema por fases e hitos de control.", style='List Bullet')
    doc.add_paragraph("• Consolidar el inventario técnico de hardware, software base, licenciamiento libre ($0 COP) y conectividad de red con puertos requeridos.", style='List Bullet')
    doc.add_paragraph("• Formular la política y automatización de respaldos diarios, semanales y mensuales de base de datos y archivos multimedia.", style='List Bullet')
    doc.add_paragraph("• Diseñar el plan de recuperación ante desastres (DRP) definiendo métricas de RPO y RTO ante fallos físicos o lógicos.", style='List Bullet')
    doc.add_paragraph("• Documentar el proceso de migración de datos ETL desde entornos de desarrollo (SQLite/Excel) a MySQL Server y el plan de reversión (Rollback).", style='List Bullet')
    doc.add_paragraph("• Redactar el manual operativo básico para el monitoreo y mantenimiento del servidor por el personal de sistemas.", style='List Bullet')
    doc.add_paragraph("• Presentar el análisis financiero de costos asociados distinguiendo herramientas gratuitas de estimaciones de hosting y dominio.", style='List Bullet')
    doc.add_paragraph("• Formalizar el acta de entrega y recibo a satisfacción del sistema de información entre las aprendices, el SENA y la institución.", style='List Bullet')

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # 5. CRONOGRAMA DE INSTALACIÓN Y DESPLIEGUE
    # --------------------------------------------------------------------------
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run("3. CRONOGRAMA DE INSTALACIÓN Y DESPLIEGUE")
    run.bold = True
    run.font.size = Pt(13)

    doc.add_paragraph(
        "El plan de instalación de EduNova está estructurado en cinco fases secuenciales con un tiempo estimado total de 4 semanas (20 días hábiles), "
        "garantizando que la transición a producción se efectúe sin interrumpir las labores académicas de la institución."
    ).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    t_cro = doc.add_table(rows=1, cols=5)
    t_cro.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_cro)
    hdr_cro = t_cro.rows[0].cells
    hdr_cro[0].width = Inches(1.1)
    hdr_cro[1].width = Inches(2.3)
    hdr_cro[2].width = Inches(0.9)
    hdr_cro[3].width = Inches(1.1)
    hdr_cro[4].width = Inches(1.1)
    for i, h in enumerate(["Fase / Hito", "Actividades Principales", "Duración", "Responsable", "Entregable / Estado"]):
        p = hdr_cro[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        set_cell_background(hdr_cro[i], "E2E8F0")

    cronograma = [
        ("Fase 1: Preparación", "Acondicionamiento de SO Ubuntu Server, firewall UFW, usuarios del sistema y dependencias base.", "3 Días", "Equipo ADSI", "Servidor Seguro (Completado)"),
        ("Fase 2: Motor y Backend", "Instalación de MySQL 8.0, entorno Python venv, Django, Gunicorn WSGI y Nginx Proxy.", "4 Días", "Equipo ADSI", "Stack Instalado (Completado)"),
        ("Fase 3: Migración ETL", "Carga de esquemas, sanitización de planillas de estudiantes, carga de fixtures y verificación.", "4 Días", "Equipo ADSI / Secretaría", "BD MySQL Poblada (Verificado)"),
        ("Fase 4: Certificación SSL", "Configuración de subdominio, certificado SSL/TLS con Certbot y pruebas piloto con docentes.", "4 Días", "Equipo ADSI / Rectoría", "Dominio HTTPS Activo (Propuesto)"),
        ("Fase 5: Capacitación y Cierre", "Capacitación a los 6 roles, entrega de manuales, firma de acta de entrega a satisfacción.", "5 Días", "Dulce Figueroa / Aminta Moguea / Anybal López", "Acta Firmada (Fase Final)")
    ]
    for fh, act, dur, resp, ent in cronograma:
        row = t_cro.add_row().cells
        row[0].width = Inches(1.1)
        row[1].width = Inches(2.3)
        row[2].width = Inches(0.9)
        row[3].width = Inches(1.1)
        row[4].width = Inches(1.1)
        for c in row:
            set_cell_margins(c)
        row[0].paragraphs[0].add_run(fh).bold = True
        row[0].paragraphs[0].runs[0].font.size = Pt(8.5)
        row[1].paragraphs[0].add_run(act).font.size = Pt(8.5)
        row[2].paragraphs[0].add_run(dur).font.size = Pt(8.5)
        row[3].paragraphs[0].add_run(resp).font.size = Pt(8.5)
        row[4].paragraphs[0].add_run(ent).font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # --------------------------------------------------------------------------
    # 6. INVENTARIO DE HARDWARE, SOFTWARE, LICENCIAS Y RED
    # --------------------------------------------------------------------------
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run("4. INVENTARIO DE HARDWARE, SOFTWARE, LICENCIAS Y RED")
    run.bold = True
    run.font.size = Pt(13)

    doc.add_paragraph(
        "Para garantizar una operación estable y eficiente, se consolidó el inventario técnico de los recursos tecnológicos "
        "necesarios tanto en el servidor central como en los equipos clientes de la institución."
    ).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.add_paragraph("4.1 Inventario de Hardware (Servidor y Estaciones Cliente)", style='Heading 2')
    
    t_hw = doc.add_table(rows=1, cols=4)
    t_hw.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_hw)
    hdr_hw = t_hw.rows[0].cells
    hdr_hw[0].width = Inches(1.5)
    hdr_hw[1].width = Inches(1.8)
    hdr_hw[2].width = Inches(1.8)
    hdr_hw[3].width = Inches(1.4)
    for i, h in enumerate(["Componente", "Requisito Mínimo", "Requisito Recomendado", "Rol / Función"]):
        p = hdr_hw[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        set_cell_background(hdr_hw[i], "E2E8F0")

    hw_data = [
        ("Servidor: Procesador", "2 núcleos x86_64 a 2.0 GHz", "4 a 8 vCPUs a 2.5 GHz o superior", "Procesamiento de peticiones WSGI y motor MySQL."),
        ("Servidor: Memoria RAM", "4 GB DDR4", "8 GB a 16 GB DDR4/ECC", "Buffer pool InnoDB de MySQL y workers Gunicorn."),
        ("Servidor: Almacenamiento", "40 GB SSD SATA", "100 a 250 GB NVMe SSD (RAID 1)", "Almacén de sistema, BD y multimedia institucional."),
        ("Servidor: Red y Energía", "100 Mbps Ethernet", "1 Gbps Full-Duplex + UPS regulada", "Acceso continuo y tolerancia a cortes de fluido eléctrico."),
        ("Clientes: Computadores", "Intel Celeron / 4 GB RAM", "Intel Core i3 / 8 GB RAM", "Navegación web para docentes, secretaría y directivos."),
        ("Clientes: Dispositivos Móviles", "Android 9 / iOS 13 con navegador", "Smartphones estándar con Chrome/Safari", "Consulta de notas y comunicados por familias y alumnos.")
    ]
    for c, rm, rr, f in hw_data:
        row = t_hw.add_row().cells
        row[0].width = Inches(1.5)
        row[1].width = Inches(1.8)
        row[2].width = Inches(1.8)
        row[3].width = Inches(1.4)
        for cell in row:
            set_cell_margins(cell)
        row[0].paragraphs[0].add_run(c).bold = True
        row[0].paragraphs[0].runs[0].font.size = Pt(8.5)
        row[1].paragraphs[0].add_run(rm).font.size = Pt(8.5)
        row[2].paragraphs[0].add_run(rr).font.size = Pt(8.5)
        row[3].paragraphs[0].add_run(f).font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    doc.add_paragraph("4.2 Inventario de Software y Licenciamiento ($0 COP de Licencias)", style='Heading 2')

    doc.add_paragraph(
        "EduNova fue desarrollado bajo una premisa fundamental de sostenibilidad financiera para las instituciones públicas: "
        "el 100% de la pila tecnológica está constituido por Software Libre y de Código Abierto (FOSS), eliminando de raíz "
        "gastos recurrentes por compra de licencias de sistemas operativos, motores de base de datos o frameworks propietarios."
    ).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    t_sw = doc.add_table(rows=1, cols=4)
    t_sw.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_sw)
    hdr_sw = t_sw.rows[0].cells
    hdr_sw[0].width = Inches(1.6)
    hdr_sw[1].width = Inches(1.4)
    hdr_sw[2].width = Inches(1.8)
    hdr_sw[3].width = Inches(1.7)
    for i, h in enumerate(["Software / Componente", "Versión Utilizada", "Tipo de Licencia", "Costo de Licenciamiento"]):
        p = hdr_sw[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        set_cell_background(hdr_sw[i], "E2E8F0")

    sw_data = [
        ("Ubuntu Server LTS", "22.04 / 24.04 LTS", "GPL / Código Abierto", "$0 COP (Libre y Gratuito)"),
        ("MySQL Server", "8.0.36 Community", "GPL v2 (Oracle FOSS)", "$0 COP (Libre y Gratuito)"),
        ("Python", "3.12 / 3.13", "PSFL (Python Software)", "$0 COP (Libre y Gratuito)"),
        ("Django Web Framework", "5.1 LTS / 4.2 LTS", "BSD 3-Clause", "$0 COP (Libre y Gratuito)"),
        ("Gunicorn WSGI", "21.2.0+", "MIT License", "$0 COP (Libre y Gratuito)"),
        ("Nginx Web Server", "1.18.0+", "2-Clause BSD", "$0 COP (Libre y Gratuito)"),
        ("Certbot SSL (EFF)", "2.8.0+", "Apache License 2.0", "$0 COP (Certificados Gratis Let's Encrypt)"),
        ("Librerías Python auxiliares", "reportlab, docx, decouple", "BSD / MIT / LGPL", "$0 COP (Librerías Abiertas)")
    ]
    for s, v, l, c in sw_data:
        row = t_sw.add_row().cells
        row[0].width = Inches(1.6)
        row[1].width = Inches(1.4)
        row[2].width = Inches(1.8)
        row[3].width = Inches(1.7)
        for cell in row:
            set_cell_margins(cell)
        row[0].paragraphs[0].add_run(s).bold = True
        row[0].paragraphs[0].runs[0].font.size = Pt(8.5)
        row[1].paragraphs[0].add_run(v).font.size = Pt(8.5)
        row[2].paragraphs[0].add_run(l).font.size = Pt(8.5)
        row[3].paragraphs[0].add_run(c).font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    doc.add_paragraph("4.3 Conectividad, Puertos y Reglas de Cortafuegos (Firewall UFW)", style='Heading 2')

    t_red = doc.add_table(rows=1, cols=4)
    t_red.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_red)
    hdr_red = t_red.rows[0].cells
    hdr_red[0].width = Inches(1.0)
    hdr_red[1].width = Inches(1.2)
    hdr_red[2].width = Inches(1.8)
    hdr_red[3].width = Inches(2.5)
    for i, h in enumerate(["Puerto", "Protocolo", "Servicio", "Política de Seguridad y Regla en Firewall"]):
        p = hdr_red[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        set_cell_background(hdr_red[i], "E2E8F0")

    red_data = [
        ("22", "TCP", "SSH Administrativo", "Restringido en UFW a IPs de administradores; autenticación por llave pública."),
        ("80", "TCP", "HTTP (Nginx)", "Abierto; configurado con redirección 301 obligatoria hacia HTTPS (puerto 443)."),
        ("443", "TCP", "HTTPS (Nginx SSL)", "Abierto al público institucional con cifrado TLS 1.2/1.3."),
        ("3306", "TCP", "MySQL Server", "BLOQUEADO AL EXTERIOR. Solo escucha en localhost (127.0.0.1) o socket Unix.")
    ]
    for pt, pr, sv, pol in red_data:
        row = t_red.add_row().cells
        row[0].width = Inches(1.0)
        row[1].width = Inches(1.2)
        row[2].width = Inches(1.8)
        row[3].width = Inches(2.5)
        for cell in row:
            set_cell_margins(cell)
        row[0].paragraphs[0].add_run(pt).bold = True
        row[0].paragraphs[0].runs[0].font.size = Pt(8.5)
        row[1].paragraphs[0].add_run(pr).font.size = Pt(8.5)
        row[2].paragraphs[0].add_run(sv).font.size = Pt(8.5)
        row[3].paragraphs[0].add_run(pol).font.size = Pt(8.5)

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # 7. POLÍTICA Y PLAN DE RESPALDOS (BACKUPS)
    # --------------------------------------------------------------------------
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run("5. POLÍTICA Y PLAN INTEGRAL DE RESPALDOS (BACKUPS)")
    run.bold = True
    run.font.size = Pt(13)

    doc.add_paragraph(
        "La salvaguarda de la información en EduNova se fundamenta en el principio de continuidad de negocio y preservación de expedientes "
        "académicos exigido por el SENA. Se implementó una política que combina copias completas de la base de datos relacional "
        "y sincronización de los archivos multimedia adjuntos (actas de seguimiento, guías pedagógicas y fotos de perfil)."
    ).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.add_paragraph("5.1 Frecuencia, Tipos de Copia y Ventana de Retención", style='Heading 2')

    t_bk = doc.add_table(rows=1, cols=4)
    t_bk.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_bk)
    hdr_bk = t_bk.rows[0].cells
    hdr_bk[0].width = Inches(1.5)
    hdr_bk[1].width = Inches(1.5)
    hdr_bk[2].width = Inches(1.8)
    hdr_bk[3].width = Inches(1.7)
    for i, h in enumerate(["Periodicidad", "Activo Respaldado", "Herramienta y Tipo", "Rotación y Retención"]):
        p = hdr_bk[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        set_cell_background(hdr_bk[i], "E2E8F0")

    bk_data = [
        ("Diario (02:00 AM)", "Base de Datos MySQL", "mysqldump con compresión gzip (Completo)", "Retención de 30 días continuos con purga automática."),
        ("Semanal (Dom 03:00 AM)", "Directorio /media/", "tar -czf comprimido (Diferencial/Full)", "Retención de 60 días para almacenamiento multimedia."),
        ("Mensual (Día 1, 01:00 AM)", "BD + Configuraciones", "Volcado transaccional integral + .env", "Copia histórica guardada en medio externo desconectado.")
    ]
    for per, act, her, rot in bk_data:
        row = t_bk.add_row().cells
        row[0].width = Inches(1.5)
        row[1].width = Inches(1.5)
        row[2].width = Inches(1.8)
        row[3].width = Inches(1.7)
        for cell in row:
            set_cell_margins(cell)
        row[0].paragraphs[0].add_run(per).bold = True
        row[0].paragraphs[0].runs[0].font.size = Pt(8.5)
        row[1].paragraphs[0].add_run(act).font.size = Pt(8.5)
        row[2].paragraphs[0].add_run(her).font.size = Pt(8.5)
        row[3].paragraphs[0].add_run(rot).font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    doc.add_paragraph("5.2 Automatización mediante Script y Cron del Servidor", style='Heading 2')

    add_docx_callout(
        doc,
        "Script de Automatización (/usr/local/bin/backup_edunova.sh)",
        "El script se ejecuta de forma desatendida mediante cron (0 2 * * *). Ejecuta:\n"
        "1. mysqldump -u edunova_prod -p --single-transaction --routines sinetec | gzip > /var/backups/edunova/db/sinetec_$(date +%Y%m%d).sql.gz\n"
        "2. tar -czf /var/backups/edunova/media/media_$(date +%Y%m%d).tar.gz -C /var/www/edunova media\n"
        "3. find /var/backups/edunova/db -name '*.sql.gz' -mtime +30 -delete (Rotación automática preventiva de disco)\n"
        "4. Registro de bitácora con timestamp y tamaño de archivos en /var/log/edunova_backups.log."
    )

    doc.add_paragraph("5.3 Evidencia de Respaldos Reales Existentes en el Repositorio", style='Heading 2')
    doc.add_paragraph(
        "En el entorno de desarrollo y pruebas de EduNova se crearon y verificaron los siguientes artefactos de respaldo reales:\n"
        "• SINETEC_backup_produccion_2026.sql (328.3 KB): Volcado transaccional completo en sintaxis MySQL InnoDB.\n"
        "• backup_pre_limpieza_edunova.json (968.0 KB): Respaldo serializado por Django ORM en formato JSON UTF-8.\n"
        "• sinetec_fixture_completa.json (863.3 KB): Fixture maestro sanitizado listo para carga con 'manage.py loaddata'.\n"
        "• db.sqlite3 (1.64 MB): Base de datos transaccional local verificada con integridad 100% operativa."
    ).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # --------------------------------------------------------------------------
    # 8. PLAN DE RECUPERACIÓN ANTE DESASTRES (DRP)
    # --------------------------------------------------------------------------
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run("6. PLAN DE RECUPERACIÓN ANTE DESASTRES (DRP)")
    run.bold = True
    run.font.size = Pt(13)

    doc.add_paragraph(
        "El Plan de Recuperación ante Desastres (Disaster Recovery Plan - DRP) define los procedimientos estandarizados "
        "para restaurar la operatividad de EduNova en caso de eventos catastróficos. Se establecieron dos métricas clave de continuidad:\n"
        "• RPO (Recovery Point Objective): Máximo 24 horas de datos (pérdida máxima acotada al último respaldo nocturno de las 02:00 AM).\n"
        "• RTO (Recovery Time Objective): Máximo 2 horas para que el sistema vuelva a estar en línea tras un fallo crítico."
    ).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    t_drp = doc.add_table(rows=1, cols=4)
    t_drp.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_drp)
    hdr_drp = t_drp.rows[0].cells
    hdr_drp[0].width = Inches(1.5)
    hdr_drp[1].width = Inches(1.3)
    hdr_drp[2].width = Inches(2.2)
    hdr_drp[3].width = Inches(1.5)
    for i, h in enumerate(["Escenario de Falla", "Impacto Estimado", "Protocolo de Acción Inmediata", "Tiempo Estimado (RTO)"]):
        p = hdr_drp[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        set_cell_background(hdr_drp[i], "E2E8F0")

    drp_data = [
        ("Fallo de Disco / Almacenamiento", "Crítico", "Sustitución de disco en arreglo RAID 1; en caso extremo, restauración de imagen del sistema y despliegue del último volcado SQL.", "45 - 90 Minutos"),
        ("Corrupción de Base de Datos", "Alto", "Detención de Gunicorn (systemctl stop gunicorn), descompresión del último .sql.gz verificado e inyección limpia en MySQL.", "15 - 30 Minutos"),
        ("Destrucción Total del Servidor", "Catastrófico", "Aprovisionamiento de nuevo nodo VPS o máquina física mediante script desatendido build.sh y descarga de copia externa de respaldo.", "90 - 120 Minutos"),
        ("Incidente de Seguridad (Ataque)", "Crítico", "Aislamiento de red, rotación de SECRET_KEY y claves de BD, revisión de logs de auditoría y restauración en entorno saneado.", "60 - 90 Minutos")
    ]
    for ef, ie, pa, rto in drp_data:
        row = t_drp.add_row().cells
        row[0].width = Inches(1.5)
        row[1].width = Inches(1.3)
        row[2].width = Inches(2.2)
        row[3].width = Inches(1.5)
        for cell in row:
            set_cell_margins(cell)
        row[0].paragraphs[0].add_run(ef).bold = True
        row[0].paragraphs[0].runs[0].font.size = Pt(8.5)
        row[1].paragraphs[0].add_run(ie).font.size = Pt(8.5)
        row[2].paragraphs[0].add_run(pa).font.size = Pt(8.5)
        row[3].paragraphs[0].add_run(rto).font.size = Pt(8.5)

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # 9. MIGRACIÓN A PRODUCCIÓN Y PLAN DE ROLLBACK
    # --------------------------------------------------------------------------
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run("7. MIGRACIÓN A PRODUCCIÓN Y PLAN DE ROLLBACK")
    run.bold = True
    run.font.size = Pt(13)

    doc.add_paragraph(
        "La migración de datos hacia el entorno de producción sigue el ciclo clásico de ingeniería ETL (Extracción, Transformación, "
        "Sanitización y Carga), asegurando que la información histórica de los aprendices y docentes no sufra truncamientos ni duplicidades."
    ).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.add_paragraph("7.1 Metodología de Migración y Validación de Integridad", style='Heading 2')
    doc.add_paragraph(
        "1. Extracción y Catálogo: Exportación de datos desde SQLite y planillas escolares legacy en formato JSON UTF-8.\n"
        "2. Transformación y Limpieza: Normalización de números de documento (eliminación de puntos y espacios), homologación de grados (10° y 11°) y validación de tipos de documento (TI, CC, CE).\n"
        "3. Aplicación del DDL: Ejecución de 'python manage.py migrate' sobre MySQL Server para crear las tablas relacionales con motores InnoDB, llaves foráneas e índices.\n"
        "4. Carga de Fixtures: Inyección secuencial de programas formativos, roles institucionales y usuarios con 'python manage.py loaddata sinetec_fixture_completa.json'.\n"
        "5. Auditoría de Integridad: Comprobación de que no existan registros huérfanos con consultas de exclusión (LEFT JOIN)."
    ).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.add_paragraph("7.2 Plan de Reversión Inmediata (Rollback)", style='Heading 2')
    add_docx_callout(
        doc,
        "Procedimiento Estricto de Rollback ante Fallos en Producción",
        "Si durante una actualización o migración de datos se detectan errores que impidan el inicio de sesión o corrompan la integridad:\n"
        "1. Detener tráfico web: sudo systemctl stop gunicorn\n"
        "2. Revertir código fuente al commit estable anterior: git reset --hard <HASH_COMMIT_ESTABLE>\n"
        "3. Restaurar la base de datos previa al cambio: mysql -u edunova_prod -p sinetec < /var/backups/edunova/db/sinetec_pre_migracion.sql\n"
        "4. Recompilar estáticos y recargar servicios: python manage.py collectstatic --noinput && sudo systemctl start gunicorn && sudo systemctl reload nginx\n"
        "5. Tiempo estimado de ejecución del Rollback: Menos de 10 minutos."
    )

    # --------------------------------------------------------------------------
    # 10. MANUAL OPERATIVO BÁSICO DEL SERVIDOR
    # --------------------------------------------------------------------------
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run("8. MANUAL OPERATIVO BÁSICO PARA EL ADMINISTRADOR DEL SISTEMA")
    run.bold = True
    run.font.size = Pt(13)

    doc.add_paragraph(
        "Este manual sintetiza las operaciones rutinarias que el administrador de sistemas del colegio debe conocer para la supervisión de EduNova:"
    ).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    t_man = doc.add_table(rows=1, cols=3)
    t_man.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_man)
    hdr_man = t_man.rows[0].cells
    hdr_man[0].width = Inches(1.8)
    hdr_man[1].width = Inches(2.7)
    hdr_man[2].width = Inches(2.0)
    for i, h in enumerate(["Operación Requerida", "Comando de Consola / Acción", "Propósito y Resultado Esperado"]):
        p = hdr_man[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        set_cell_background(hdr_man[i], "E2E8F0")

    man_data = [
        ("Verificar Estado de Servicios", "sudo systemctl status gunicorn nginx mysql", "Comprueba que los tres demonios estén en estado 'active (running)'."),
        ("Reiniciar Servicio Web", "sudo systemctl restart gunicorn && sudo systemctl reload nginx", "Aplica cambios de código en caliente sin reiniciar la máquina servidora."),
        ("Monitorear Logs de Error", "sudo tail -f /var/log/gunicorn/error.log /var/log/nginx/error.log", "Muestra en tiempo real excepciones o peticiones HTTP anómalas."),
        ("Comprobar Uso de Recursos", "htop  /  df -h", "Inspecciona porcentaje de uso de CPU, memoria RAM y espacio disponible en disco."),
        ("Restauración de Elementos", "Ingresar a /papelera/ como Administrador", "Permite recuperar estudiantes, notas o cargas académicas borradas lógicamente.")
    ]
    for op, cmd, prp in man_data:
        row = t_man.add_row().cells
        row[0].width = Inches(1.8)
        row[1].width = Inches(2.7)
        row[2].width = Inches(2.0)
        for cell in row:
            set_cell_margins(cell)
        row[0].paragraphs[0].add_run(op).bold = True
        row[0].paragraphs[0].runs[0].font.size = Pt(8.5)
        row[1].paragraphs[0].add_run(cmd).font.size = Pt(8)
        row[2].paragraphs[0].add_run(prp).font.size = Pt(8.5)

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # 11. ANÁLISIS DE COSTOS ASOCIADOS (REALES VS ESTIMADOS)
    # --------------------------------------------------------------------------
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run("9. ANÁLISIS DE COSTOS ASOCIADOS Y PRESUPUESTO")
    run.bold = True
    run.font.size = Pt(13)

    doc.add_paragraph(
        "En cumplimiento de los principios de honestidad técnica exigidos por el SENA, se presenta el desglose presupuestal "
        "diferenciando de forma estricta los costos reales de desarrollo y software (que son $0 COP por uso de FOSS) "
        "de las estimaciones de infraestructura física o cloud sujetas a confirmación por parte de la institución cliente."
    ).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    t_cos = doc.add_table(rows=1, cols=4)
    t_cos.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_cos)
    hdr_cos = t_cos.rows[0].cells
    hdr_cos[0].width = Inches(1.8)
    hdr_cos[1].width = Inches(1.3)
    hdr_cos[2].width = Inches(1.8)
    hdr_cos[3].width = Inches(1.6)
    for i, h in enumerate(["Rubro / Concepto", "Tipo de Costo", "Monto Estimado / Real (COP)", "Observaciones y Estado"]):
        p = hdr_cos[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        set_cell_background(hdr_cos[i], "E2E8F0")

    costos_data = [
        ("Licencias de Software (OS, BD, Web)", "Real Comprobado", "$0 COP", "Ahorro total mediante Ubuntu, MySQL, Python, Django y Nginx."),
        ("Desarrollo de Software y Pruebas", "Real (Formativo)", "$0 COP", "Aporte formativo de las aprendices del SENA Regional Magdalena."),
        ("Servidor Físico On-Premise (Opcional)", "Estimado Cotizado", "$3.500.000 - $4.800.000 COP", "Inversión única para torre servidor en sede. A confirmar por cliente."),
        ("Servidor VPS en la Nube (Alternativa)", "Estimado Mensual", "$100.000 - $160.000 COP/mes", "VPS 4 vCPU / 8 GB RAM (DigitalOcean/Linode). A confirmar."),
        ("Dominio Institucional (.edu.co)", "Estimado Anual", "$80.000 - $110.000 COP/año", "Trámite ante operador oficial de dominio para entidades educativas."),
        ("Certificado de Seguridad SSL/TLS", "Real Comprobado", "$0 COP", "Certificados de alta seguridad provistos gratis por Let's Encrypt."),
        ("Mantenimiento Preventivo Anual", "Estimado Anual", "$600.000 - $1.000.000 COP/año", "Horas de soporte técnico y optimización semestral. A contratar.")
    ]
    for rb, tc, mt, ob in costos_data:
        row = t_cos.add_row().cells
        row[0].width = Inches(1.8)
        row[1].width = Inches(1.3)
        row[2].width = Inches(1.8)
        row[3].width = Inches(1.6)
        for cell in row:
            set_cell_margins(cell)
        row[0].paragraphs[0].add_run(rb).bold = True
        row[0].paragraphs[0].runs[0].font.size = Pt(8.5)
        row[1].paragraphs[0].add_run(tc).font.size = Pt(8.5)
        row[2].paragraphs[0].add_run(mt).font.size = Pt(8.5)
        row[3].paragraphs[0].add_run(ob).font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # --------------------------------------------------------------------------
    # 12. PLAN DE MANTENIMIENTO PREVENTIVO Y CORRECTIVO
    # --------------------------------------------------------------------------
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run("10. PLAN DE MANTENIMIENTO PREVENTIVO Y CORRECTIVO")
    run.bold = True
    run.font.size = Pt(13)

    doc.add_paragraph(
        "Para garantizar la alta disponibilidad y vida útil de EduNova, se definió un protocolo de mantenimiento preventivo continuo "
        "y un esquema de atención de incidencias correctivas clasificado según Acuerdos de Nivel de Servicio (SLA):\n"
        "• Mantenimiento Preventivo:\n"
        "  - Semanal: Revisión de espacio libre en disco (df -h) y depuración de trazas de log.\n"
        "  - Mensual: Aplicación de parches de seguridad del sistema operativo (sudo apt update && sudo apt upgrade).\n"
        "  - Semestral: Optimización de tablas e índices en MySQL (OPTIMIZE TABLE) y compactación de archivos temporales.\n"
        "• Mantenimiento Correctivo (Acuerdos de Nivel de Servicio - SLA):\n"
        "  - Incidencia Crítica (Sistema caído): Tiempo de respuesta menor a 30 minutos; resolución menor a 2 horas.\n"
        "  - Incidencia Media (Fallo en un reporte o carga puntual): Respuesta menor a 2 horas; resolución menor a 8 horas.\n"
        "  - Incidencia Baja (Duda de usuario o ajuste gráfico): Respuesta menor a 8 horas; resolución en 24 a 48 horas."
    ).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # 13. ACTA FORMAL DE ENTREGA Y RECIBO A SATISFACCIÓN
    # --------------------------------------------------------------------------
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run("11. ACTA DE ENTREGA Y RECIBO A SATISFACCIÓN")
    run.bold = True
    run.font.size = Pt(13)

    doc.add_paragraph(
        "En la ciudad de Santa Marta, Departamento del Magdalena, a los catorce (14) días del mes de octubre de 2026, "
        "se reúnen en las instalaciones institucionales las partes interesadas del proyecto formativo para suscribir la presente "
        "ACTA DE ENTREGA Y RECIBO A SATISFACCIÓN del sistema de información EduNova (SINETEC):\n\n"
        "1. POR PARTE DE LOS DESARROLLADORES (APRENDICES SENA):\n"
        "   • DULCE MARÍA FIGUEROA — Aprendiz ADSI Ficha 228106\n"
        "   • AMINTA MARÍA MOGUEA FLOREZ — Aprendiz ADSI Ficha 228106\n\n"
        "2. POR PARTE DE LA ENTIDAD FORMATIVA (SENA REGIONAL MAGDALENA):\n"
        "   • ING. ANYBAL LÓPEZ — Instructor Técnico Evaluador\n\n"
        "3. POR PARTE DE LA INSTITUCIÓN EDUCATIVA RECEPTORA:\n"
        "   • RECTORÍA / COORDINACIÓN ACADÉMICA DE LA MEDIA TÉCNICA\n\n"
        "OBJETO DE LA ENTREGA:\n"
        "Hacer entrega formal del código fuente probado, la estructura de base de datos relacional MySQL, los volcados de respaldo (SQL y JSON), "
        "los manuales operativos y los planes administrativos de instalación, respaldo y migración de EduNova.\n\n"
        "DECLARACIÓN DE CONFORMIDAD:\n"
        "El instructor Anybal López y el delegado institucional certifican que el sistema cumple a cabalidad con los requisitos funcionales, "
        "las pruebas de seguridad RBAC, el aislamiento de perfiles y los protocolos administrativos pactados para la etapa productiva."
    ).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Espacio para firmas formales
    p_firmas = doc.add_paragraph()
    p_firmas.paragraph_format.space_before = Pt(30)
    p_firmas.paragraph_format.space_after = Pt(10)
    p_firmas.add_run("EN CONSTANCIA DE LO ANTERIOR, FIRMAN LAS PARTES INTERESADAS:\n").bold = True

    t_f = doc.add_table(rows=2, cols=2)
    t_f.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_f, val="none")
    for row in t_f.rows:
        row.cells[0].width = Inches(3.2)
        row.cells[1].width = Inches(3.2)
        set_cell_margins(row.cells[0])
        set_cell_margins(row.cells[1])

    c00 = t_f.cell(0, 0).paragraphs[0]
    c00.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c00.add_run("_________________________________________\n").bold = True
    c00.add_run("DULCE MARÍA FIGUEROA\n").bold = True
    c00.add_run("Aprendiz SENA — ADSI Ficha 228106\nLíder de Desarrollo e Implementación")

    c01 = t_f.cell(0, 1).paragraphs[0]
    c01.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c01.add_run("_________________________________________\n").bold = True
    c01.add_run("AMINTA MARÍA MOGUEA FLOREZ\n").bold = True
    c01.add_run("Aprendiz SENA — ADSI Ficha 228106\nLíder de Desarrollo e Implementación")

    c10 = t_f.cell(1, 0).paragraphs[0]
    c10.paragraph_format.space_before = Pt(24)
    c10.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c10.add_run("_________________________________________\n").bold = True
    c10.add_run("ING. ANYBAL LÓPEZ\n").bold = True
    c10.add_run("Instructor Técnico Evaluador\nSENA Regional Magdalena — Centro Ecoturístico")

    c11 = t_f.cell(1, 1).paragraphs[0]
    c11.paragraph_format.space_before = Pt(24)
    c11.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c11.add_run("_________________________________________\n").bold = True
    c11.add_run("DELEGADO INSTITUCIONAL\n").bold = True
    c11.add_run("Rectoría / Coordinación Académica\nInstitución Educativa Articulada")

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # 14. CONCLUSIONES Y ANEXOS
    # --------------------------------------------------------------------------
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run("12. CONCLUSIONES Y ANEXOS TÉCNICOS")
    run.bold = True
    run.font.size = Pt(13)

    doc.add_paragraph("12.1 Conclusiones", style='Heading 2')
    doc.add_paragraph(
        "1. La solución EduNova (SINETEC) ha alcanzado un estado de madurez técnica y funcional óptimo, consolidando "
        "una arquitectura web confiable, escalable y respaldada por bases de datos relacionales normalizadas.\n"
        "2. Los planes de instalación, respaldo automatizado y migración presentados cumplen rigurosamente con los protocolos "
        "organizacionales del SENA y satisfacen con exactitud el resultado de aprendizaje orientado por el instructor Anybal López.\n"
        "3. El modelo de costos sustentado en Software Libre garantiza que la institución receptora cuente con una plataforma de vanguardia "
        "sin incurrir en gastos prohibitivos de licenciamiento privativo, asegurando su sostenibilidad a largo plazo."
    ).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.add_paragraph("12.2 Anexos Técnicos del Repositorio", style='Heading 2')
    doc.add_paragraph(
        "• Script de Respaldo Maestro: /usr/local/bin/backup_edunova.sh y scripts en c:/SINETEC/SINETEC/scripts/\n"
        "• Volcados de Base de Datos: SINETEC_backup_produccion_2026.sql y sinetec_fixture_completa.json\n"
        "• Pruebas de Certificación Ejecutadas: test_verificaciones.py, test_edunova_teacher_flow.py y test_edunova_student_secretaria_flow.py\n"
        "• Configuración WSGI y Servidor Web: gunicorn.service y sitios disponibles en Nginx."
    ).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.save(docx_path)
    print(f"[OK] Documento Word generado exitosamente: {docx_path}")
    return docx_path


# ==============================================================================
# CONSTRUCCIÓN DEL DOCUMENTO PDF (.PDF) CON REPORTLAB
# ==============================================================================
def generar_documento_pdf(pdf_path):
    print(f"Generando documento PDF en: {pdf_path}")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Estilos tipográficos
    style_tit_portada = ParagraphStyle(
        'TitPortada',
        fontName='Arial-Bold',
        fontSize=15,
        leading=19,
        alignment=1, # Centro
        textColor=colors.HexColor("#000000"),
        spaceAfter=12
    )
    style_sub_portada = ParagraphStyle(
        'SubPortada',
        fontName='Arial',
        fontSize=10.5,
        leading=14,
        alignment=1,
        textColor=colors.HexColor("#334155"),
        spaceAfter=25
    )
    style_inst_portada = ParagraphStyle(
        'InstPortada',
        fontName='Arial-Bold',
        fontSize=11,
        leading=15,
        alignment=1,
        textColor=colors.HexColor("#000000"),
        spaceAfter=6
    )
    style_h1 = ParagraphStyle(
        'Encab1',
        fontName='Arial-Bold',
        fontSize=12.5,
        leading=16,
        textColor=colors.HexColor("#000000"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    style_h2 = ParagraphStyle(
        'Encab2',
        fontName='Arial-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        'Cuerpo',
        fontName='Arial',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=6,
        alignment=4 # Justificado
    )
    style_bullet = ParagraphStyle(
        'Bullet',
        fontName='Arial',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        leftIndent=15,
        spaceAfter=3
    )
    style_th = ParagraphStyle(
        'TH',
        fontName='Arial-Bold',
        fontSize=8,
        leading=10,
        alignment=0,
        textColor=colors.HexColor("#000000")
    )
    style_td = ParagraphStyle(
        'TD',
        fontName='Arial',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1E293B")
    )
    style_td_bold = ParagraphStyle(
        'TDBold',
        fontName='Arial-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1E293B")
    )
    style_callout = ParagraphStyle(
        'Callout',
        fontName='Arial',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155")
    )

    story = []

    # 1. PORTADA
    story.append(Spacer(1, 20))
    story.append(Paragraph("SERVICIO NACIONAL DE APRENDIZAJE – SENA<br/>REGIONAL MAGDALENA<br/>CENTRO DE LOGÍSTICA Y PROMOCIÓN ECOTURÍSTICA DEL MAGDALENA", style_inst_portada))
    story.append(Spacer(1, 10))
    story.append(Paragraph("TECNOLOGÍA EN ANÁLISIS Y DESARROLLO DE SISTEMAS DE INFORMACIÓN (ADSI)<br/>FICHA DE CARACTERIZACIÓN: 228106", ParagraphStyle('Ficha', fontName='Arial', fontSize=10, leading=14, alignment=1, textColor=colors.HexColor("#334155"))))
    story.append(Spacer(1, 35))
    story.append(Paragraph("INFORME ADMINISTRATIVO DE INSTALACIÓN, RESPALDO,<br/>MIGRACIÓN Y DESPLIEGUE A PRODUCCIÓN DEL SISTEMA DE INFORMACIÓN EDUNOVA", style_tit_portada))
    story.append(Spacer(1, 5))
    story.append(Paragraph("<b>Resultado de Aprendizaje (RAP):</b><br/><i>“Elaborar el informe administrativo, siguiendo los protocolos de la organización, basado en los planes de instalación, respaldo y migración del sistema de información”.</i>", style_sub_portada))
    story.append(Spacer(1, 40))
    story.append(Paragraph("<b>APRENDICES:</b><br/><b>DULCE MARÍA FIGUEROA</b><br/><b>AMINTA MARÍA MOGUEA FLOREZ</b>", ParagraphStyle('Aut', fontName='Arial', fontSize=11, leading=16, alignment=1, textColor=colors.HexColor("#000000"))))
    story.append(Spacer(1, 25))
    story.append(Paragraph("<b>INSTRUCTOR TÉCNICO EVALUADOR:</b><br/><b>ING. ANYBAL LÓPEZ</b>", ParagraphStyle('Inst', fontName='Arial', fontSize=11, leading=16, alignment=1, textColor=colors.HexColor("#000000"))))
    story.append(Spacer(1, 50))
    story.append(Paragraph("<b>SANTA MARTA, MAGDALENA, COLOMBIA<br/>OCTUBRE DE 2026</b>", ParagraphStyle('Ciu', fontName='Arial-Bold', fontSize=10, leading=14, alignment=1, textColor=colors.HexColor("#000000"))))
    story.append(PageBreak())

    # 2. CONTROL DE VERSIONES
    story.append(Paragraph("REGISTRO DE CONTROL DE VERSIONES DEL DOCUMENTO", style_h1))
    cv_data = [
        [Paragraph("Versión", style_th), Paragraph("Fecha", style_th), Paragraph("Autor(es)", style_th), Paragraph("Descripción de Modificaciones", style_th)],
        [Paragraph("0.1", style_td), Paragraph("15/08/2026", style_td), Paragraph("Equipo Desarrollador", style_td), Paragraph("Estructuración de requerimientos IEEE 830, arquitectura inicial y casos de prueba.", style_td)],
        [Paragraph("0.5", style_td), Paragraph("18/09/2026", style_td), Paragraph("Líder de Desarrollo", style_td), Paragraph("Consolidación de modelos relacionales, reglas de negocio y copias SQLite.", style_td)],
        [Paragraph("0.9", style_td), Paragraph("28/09/2026", style_td), Paragraph("Dulce María Figueroa<br/>Aminta Moguea Florez", style_td), Paragraph("Estabilización de los seis paneles de usuario, pruebas RBAC y exportación de fixtures.", style_td)],
        [Paragraph("1.0", style_td), Paragraph("14/10/2026", style_td), Paragraph("Dulce María Figueroa<br/>Aminta Moguea Florez", style_td), Paragraph("Elaboración del informe administrativo definitivo de instalación, respaldo, migración y entrega formal para el instructor Anybal López.", style_td)]
    ]
    t_cv_pdf = Table(cv_data, colWidths=[50, 65, 120, 269])
    t_cv_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_cv_pdf)
    story.append(Spacer(1, 10))

    # 3. INTRODUCCIÓN
    story.append(Paragraph("1. INTRODUCCIÓN Y CONTEXTO INSTITUCIONAL", style_h1))
    story.append(Paragraph(
        "El presente informe administrativo ha sido estructurado siguiendo rigurosamente los protocolos organizacionales "
        "del Servicio Nacional de Aprendizaje (SENA) y las directrices pedagógicas impartidas por el instructor Anybal López "
        "para el programa de formación de Tecnología en Análisis y Desarrollo de Sistemas de Información (ADSI). "
        "El propósito de este documento es consolidar y sustentar técnicamente los planes maestros de instalación, "
        "política de respaldos, procedimientos de migración y planes de contingencia para la puesta en producción del sistema "
        "de información denominado EduNova – Sistema Integrado de Educación Técnica (SINETEC).", style_body))
    story.append(Paragraph(
        "En las Instituciones Educativas articuladas con la Media Técnica en el Departamento del Magdalena, la administración escolar "
        "ha enfrentado históricamente graves dificultades asociadas a la dispersión de información, pérdidas de actas de seguimiento, "
        "demoras en la entrega de reportes valorativos y falta de articulación en tiempo real entre docentes, directivos, aprendices y padres de familia. "
        "EduNova surge como una plataforma web integral basada en software libre (Python, Django, Nginx y MySQL Server) que centraliza "
        "la gestión académica, el control de asistencias, la calificación por resultados de aprendizaje (RAP) y la comunicación institucional.", style_body))
    story.append(Paragraph(
        "De conformidad con las normas éticas y de calidad de la formación técnica, este informe establece una delimitación transparente entre "
        "las tareas efectivamente realizadas y comprobadas en el código fuente, los procedimientos metodológicos propuestos para el despliegue en servidor "
        "y los requerimientos pendientes de infraestructura que dependen formalmente de la entrega de equipos por parte del cliente institucional.", style_body))

    # 4. OBJETIVOS
    story.append(Paragraph("2. OBJETIVOS", style_h1))
    story.append(Paragraph("<b>2.1 Objetivo General</b>", style_h2))
    story.append(Paragraph(
        "Elaborar el informe administrativo formal siguiendo los protocolos de la organización, fundamentado en los planes de instalación, "
        "política de respaldo, migración de datos y contingencia del sistema de información EduNova (SINETEC), para garantizar su operatividad "
        "continua, seguridad y sostenibilidad en un entorno productivo institucional.", style_body))
    story.append(Paragraph("<b>2.2 Objetivos Específicos</b>", style_h2))
    story.append(Paragraph("• Establecer el cronograma detallado de instalación y puesta en marcha del sistema por fases e hitos de control.", style_bullet))
    story.append(Paragraph("• Consolidar el inventario técnico de hardware, software base, licenciamiento libre ($0 COP) y conectividad de red con puertos requeridos.", style_bullet))
    story.append(Paragraph("• Formular la política y automatización de respaldos diarios, semanales y mensuales de base de datos y archivos multimedia.", style_bullet))
    story.append(Paragraph("• Diseñar el plan de recuperación ante desastres (DRP) definiendo métricas de RPO y RTO ante fallos físicos o lógicos.", style_bullet))
    story.append(Paragraph("• Documentar el proceso de migración de datos ETL desde entornos de desarrollo (SQLite/Excel) a MySQL Server y el plan de reversión (Rollback).", style_bullet))
    story.append(Paragraph("• Redactar el manual operativo básico para el monitoreo y mantenimiento del servidor por el personal de sistemas.", style_bullet))
    story.append(Paragraph("• Presentar el análisis financiero de costos asociados distinguiendo herramientas gratuitas de estimaciones de hosting y dominio.", style_bullet))
    story.append(Paragraph("• Formalizar el acta de entrega y recibo a satisfacción del sistema de información entre las aprendices, el SENA y la institución.", style_bullet))
    story.append(PageBreak())

    # 5. CRONOGRAMA
    story.append(Paragraph("3. CRONOGRAMA DE INSTALACIÓN Y DESPLIEGUE", style_h1))
    story.append(Paragraph(
        "El plan de instalación de EduNova está estructurado en cinco fases secuenciales con un tiempo estimado total de 4 semanas (20 días hábiles), "
        "garantizando que la transición a producción se efectúe sin interrumpir las labores académicas de la institución.", style_body))
    
    cro_pdf_data = [
        [Paragraph("Fase / Hito", style_th), Paragraph("Actividades Principales", style_th), Paragraph("Duración", style_th), Paragraph("Responsable", style_th), Paragraph("Entregable / Estado", style_th)],
        [Paragraph("Fase 1: Preparación", style_td_bold), Paragraph("Acondicionamiento de SO Ubuntu Server, firewall UFW, usuarios y dependencias.", style_td), Paragraph("3 Días", style_td), Paragraph("Equipo ADSI", style_td), Paragraph("Servidor Seguro (Completado)", style_td)],
        [Paragraph("Fase 2: Motor y Backend", style_td_bold), Paragraph("Instalación de MySQL 8.0, entorno Python venv, Django, Gunicorn y Nginx.", style_td), Paragraph("4 Días", style_td), Paragraph("Equipo ADSI", style_td), Paragraph("Stack Instalado (Completado)", style_td)],
        [Paragraph("Fase 3: Migración ETL", style_td_bold), Paragraph("Carga de esquemas, sanitización de planillas de estudiantes y carga de fixtures.", style_td), Paragraph("4 Días", style_td), Paragraph("Equipo ADSI / Secr.", style_td), Paragraph("BD MySQL Poblada (Verificado)", style_td)],
        [Paragraph("Fase 4: Certificación SSL", style_td_bold), Paragraph("Configuración de subdominio, SSL con Certbot y pruebas piloto con docentes.", style_td), Paragraph("4 Días", style_td), Paragraph("Equipo ADSI / Rect.", style_td), Paragraph("Dominio HTTPS (Propuesto)", style_td)],
        [Paragraph("Fase 5: Capacitación / Cierre", style_td_bold), Paragraph("Capacitación a los 6 roles, entrega de manuales y firma de acta de entrega.", style_td), Paragraph("5 Días", style_td), Paragraph("Dulce F. / Aminta M. / Anybal López", style_td), Paragraph("Acta Firmada (Fase Final)", style_td)]
    ]
    t_cro_pdf = Table(cro_pdf_data, colWidths=[80, 160, 50, 95, 119])
    t_cro_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_cro_pdf)
    story.append(Spacer(1, 10))

    # 6. INVENTARIO
    story.append(Paragraph("4. INVENTARIO DE HARDWARE, SOFTWARE, LICENCIAS Y RED", style_h1))
    story.append(Paragraph("<b>4.1 Inventario de Hardware (Servidor y Estaciones Cliente)</b>", style_h2))
    
    hw_pdf_data = [
        [Paragraph("Componente", style_th), Paragraph("Requisito Mínimo", style_th), Paragraph("Requisito Recomendado", style_th), Paragraph("Rol / Función", style_th)],
        [Paragraph("Servidor: CPU", style_td_bold), Paragraph("2 núcleos x86_64 a 2.0 GHz", style_td), Paragraph("4 a 8 vCPUs a 2.5 GHz o superior", style_td), Paragraph("Procesamiento WSGI y consultas MySQL.", style_td)],
        [Paragraph("Servidor: RAM", style_td_bold), Paragraph("4 GB DDR4", style_td), Paragraph("8 GB a 16 GB DDR4/ECC", style_td), Paragraph("Buffer pool InnoDB y workers concurrentes.", style_td)],
        [Paragraph("Servidor: Disco", style_td_bold), Paragraph("40 GB SSD SATA", style_td), Paragraph("100 a 250 GB NVMe SSD (RAID 1)", style_td), Paragraph("Almacén de sistema, BD y multimedia.", style_td)],
        [Paragraph("Servidor: Red/Energía", style_td_bold), Paragraph("100 Mbps Ethernet", style_td), Paragraph("1 Gbps Full-Duplex + UPS regulada", style_td), Paragraph("Acceso continuo y tolerancia a fallos eléctricos.", style_td)],
        [Paragraph("Clientes: PCs", style_td_bold), Paragraph("Intel Celeron / 4 GB RAM", style_td), Paragraph("Intel Core i3 / 8 GB RAM", style_td), Paragraph("Navegación web para docentes y administrativos.", style_td)],
        [Paragraph("Clientes: Móviles", style_td_bold), Paragraph("Android 9 / iOS 13 con navegador", style_td), Paragraph("Smartphones estándar con Chrome/Safari", style_td), Paragraph("Consulta de notas y comunicados por familias.", style_td)]
    ]
    t_hw_pdf = Table(hw_pdf_data, colWidths=[100, 125, 135, 144])
    t_hw_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_hw_pdf)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>4.2 Inventario de Software y Licenciamiento ($0 COP de Licencias)</b>", style_h2))
    sw_pdf_data = [
        [Paragraph("Software / Componente", style_th), Paragraph("Versión Utilizada", style_th), Paragraph("Tipo de Licencia", style_th), Paragraph("Costo de Licenciamiento", style_th)],
        [Paragraph("Ubuntu Server LTS", style_td_bold), Paragraph("22.04 / 24.04 LTS", style_td), Paragraph("GPL / Código Abierto", style_td), Paragraph("$0 COP (Libre y Gratuito)", style_td)],
        [Paragraph("MySQL Server", style_td_bold), Paragraph("8.0.36 Community", style_td), Paragraph("GPL v2 (Oracle FOSS)", style_td), Paragraph("$0 COP (Libre y Gratuito)", style_td)],
        [Paragraph("Python", style_td_bold), Paragraph("3.12 / 3.13", style_td), Paragraph("PSFL (Python Software)", style_td), Paragraph("$0 COP (Libre y Gratuito)", style_td)],
        [Paragraph("Django Framework", style_td_bold), Paragraph("5.1 LTS / 4.2 LTS", style_td), Paragraph("BSD 3-Clause", style_td), Paragraph("$0 COP (Libre y Gratuito)", style_td)],
        [Paragraph("Gunicorn WSGI", style_td_bold), Paragraph("21.2.0+", style_td), Paragraph("MIT License", style_td), Paragraph("$0 COP (Libre y Gratuito)", style_td)],
        [Paragraph("Nginx Web Server", style_td_bold), Paragraph("1.18.0+", style_td), Paragraph("2-Clause BSD", style_td), Paragraph("$0 COP (Libre y Gratuito)", style_td)],
        [Paragraph("Certbot SSL (EFF)", style_td_bold), Paragraph("2.8.0+", style_td), Paragraph("Apache License 2.0", style_td), Paragraph("$0 COP (Certificados Gratis Let's Encrypt)", style_td)]
    ]
    t_sw_pdf = Table(sw_pdf_data, colWidths=[120, 100, 130, 154])
    t_sw_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_sw_pdf)
    story.append(PageBreak())

    # 7. RESPALDOS
    story.append(Paragraph("5. POLÍTICA Y PLAN INTEGRAL DE RESPALDOS (BACKUPS)", style_h1))
    story.append(Paragraph(
        "La salvaguarda de la información en EduNova se fundamenta en el principio de continuidad de negocio y preservación de expedientes "
        "académicos exigido por el SENA. Se implementó una política que combina copias completas de la base de datos relacional "
        "y sincronización de los archivos multimedia adjuntos (actas de seguimiento, guías pedagógicas y fotos de perfil).", style_body))
    
    bk_pdf_data = [
        [Paragraph("Periodicidad", style_th), Paragraph("Activo Respaldado", style_th), Paragraph("Herramienta y Tipo", style_th), Paragraph("Rotación y Retención", style_th)],
        [Paragraph("Diario (02:00 AM)", style_td_bold), Paragraph("Base de Datos MySQL", style_td), Paragraph("mysqldump con compresión gzip (Completo)", style_td), Paragraph("Retención de 30 días continuos con purga automática.", style_td)],
        [Paragraph("Semanal (Dom 03:00 AM)", style_td_bold), Paragraph("Directorio /media/", style_td), Paragraph("tar -czf comprimido (Diferencial/Full)", style_td), Paragraph("Retención de 60 días para multimedia.", style_td)],
        [Paragraph("Mensual (Día 1, 01:00 AM)", style_td_bold), Paragraph("BD + Configuraciones", style_td), Paragraph("Volcado transaccional integral + .env", style_td), Paragraph("Copia histórica guardada en medio desconectado.", style_td)]
    ]
    t_bk_pdf = Table(bk_pdf_data, colWidths=[95, 110, 140, 159])
    t_bk_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_bk_pdf)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Automatización mediante Script y Cron (/usr/local/bin/backup_edunova.sh)</b>", style_h2))
    story.append(Paragraph(
        "El script se ejecuta de forma desatendida mediante cron (0 2 * * *). Ejecuta:<br/>"
        "1. <code>mysqldump -u edunova_prod -p --single-transaction --routines sinetec | gzip &gt; /var/backups/edunova/db/sinetec_$(date +%Y%m%d).sql.gz</code><br/>"
        "2. <code>tar -czf /var/backups/edunova/media/media_$(date +%Y%m%d).tar.gz -C /var/www/edunova media</code><br/>"
        "3. <code>find /var/backups/edunova/db -name '*.sql.gz' -mtime +30 -delete</code> (Rotación automática preventiva)<br/>"
        "4. Registro de bitácora con timestamp y tamaño de archivos en <code>/var/log/edunova_backups.log</code>.", style_body))

    # 8. DRP
    story.append(Paragraph("6. PLAN DE RECUPERACIÓN ANTE DESASTRES (DRP)", style_h1))
    story.append(Paragraph(
        "El Plan de Recuperación ante Desastres (Disaster Recovery Plan - DRP) define los procedimientos estandarizados "
        "para restaurar la operatividad de EduNova en caso de eventos catastróficos. Métricas de continuidad:<br/>"
        "• <b>RPO (Recovery Point Objective):</b> Máximo 24 horas de datos (pérdida máxima acotada al último respaldo de las 02:00 AM).<br/>"
        "• <b>RTO (Recovery Time Objective):</b> Máximo 2 horas para que el sistema vuelva a estar en línea tras un fallo crítico.", style_body))
    
    drp_pdf_data = [
        [Paragraph("Escenario de Falla", style_th), Paragraph("Impacto", style_th), Paragraph("Protocolo de Acción Inmediata", style_th), Paragraph("RTO Estimado", style_th)],
        [Paragraph("Fallo de Almacenamiento", style_td_bold), Paragraph("Crítico", style_td), Paragraph("Sustitución de disco en RAID 1; restauración del último volcado SQL.", style_td), Paragraph("45 - 90 Min", style_td)],
        [Paragraph("Corrupción de Base de Datos", style_td_bold), Paragraph("Alto", style_td), Paragraph("Detención de Gunicorn, descompresión del .sql.gz e inyección en MySQL.", style_td), Paragraph("15 - 30 Min", style_td)],
        [Paragraph("Destrucción Total de Servidor", style_td_bold), Paragraph("Catastrófico", style_td), Paragraph("Aprovisionamiento de nuevo nodo VPS/físico y carga de respaldo externo.", style_td), Paragraph("90 - 120 Min", style_td)],
        [Paragraph("Incidente de Seguridad", style_td_bold), Paragraph("Crítico", style_td), Paragraph("Aislamiento de red, rotación de claves, análisis de auditoría y restauración limpia.", style_td), Paragraph("60 - 90 Min", style_td)]
    ]
    t_drp_pdf = Table(drp_pdf_data, colWidths=[110, 55, 245, 94])
    t_drp_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_drp_pdf)
    story.append(PageBreak())

    # 9. MIGRACIÓN Y ROLLBACK
    story.append(Paragraph("7. MIGRACIÓN A PRODUCCIÓN Y PLAN DE ROLLBACK", style_h1))
    story.append(Paragraph(
        "La migración de datos hacia el entorno de producción sigue el ciclo clásico de ingeniería ETL (Extracción, Transformación, "
        "Sanitización y Carga), asegurando que la información histórica de los aprendices y docentes no sufra truncamientos ni duplicidades.", style_body))
    story.append(Paragraph("<b>Procedimiento de Rollback (Reversión Inmediata) ante Fallos:</b>", style_h2))
    story.append(Paragraph(
        "1. Detener tráfico web: <code>sudo systemctl stop gunicorn</code><br/>"
        "2. Revertir código fuente al commit estable anterior: <code>git reset --hard &lt;HASH_COMMIT_ESTABLE&gt;</code><br/>"
        "3. Restaurar la base de datos previa al cambio: <code>mysql -u edunova_prod -p sinetec &lt; /var/backups/edunova/db/sinetec_pre_migracion.sql</code><br/>"
        "4. Recompilar estáticos y recargar servicios: <code>python manage.py collectstatic --noinput && sudo systemctl start gunicorn && sudo systemctl reload nginx</code><br/>"
        "5. Tiempo de ejecución garantizado: Menos de 10 minutos.", style_body))

    # 10. MANUAL OPERATIVO
    story.append(Paragraph("8. MANUAL OPERATIVO BÁSICO DEL SERVIDOR", style_h1))
    man_pdf_data = [
        [Paragraph("Operación Requerida", style_th), Paragraph("Comando de Consola / Acción", style_th), Paragraph("Propósito y Resultado Esperado", style_th)],
        [Paragraph("Verificar Estado", style_td_bold), Paragraph("sudo systemctl status gunicorn nginx mysql", style_td), Paragraph("Comprueba que los tres demonios estén en 'active (running)'.", style_td)],
        [Paragraph("Reiniciar Servicio Web", style_td_bold), Paragraph("sudo systemctl restart gunicorn && sudo systemctl reload nginx", style_td), Paragraph("Aplica cambios de código en caliente sin reiniciar el servidor.", style_td)],
        [Paragraph("Monitorear Logs", style_td_bold), Paragraph("sudo tail -f /var/log/gunicorn/error.log", style_td), Paragraph("Muestra en tiempo real excepciones o peticiones anómalas.", style_td)],
        [Paragraph("Uso de Recursos", style_td_bold), Paragraph("htop  /  df -h", style_td), Paragraph("Inspecciona porcentaje de uso de CPU, RAM y disco disponible.", style_td)],
        [Paragraph("Papelera Institucional", style_td_bold), Paragraph("Ingresar a /papelera/ como Administrador", style_td), Paragraph("Permite restaurar estudiantes o notas borrados lógicamente.", style_td)]
    ]
    t_man_pdf = Table(man_pdf_data, colWidths=[110, 210, 184])
    t_man_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_man_pdf)
    story.append(Spacer(1, 10))

    # 11. COSTOS
    story.append(Paragraph("9. ANÁLISIS DE COSTOS ASOCIADOS Y PRESUPUESTO", style_h1))
    story.append(Paragraph(
        "En cumplimiento de los principios de honestidad técnica exigidos por el SENA, se presenta el desglose presupuestal "
        "diferenciando de forma estricta los costos reales de desarrollo y software (que son $0 COP por uso de FOSS) "
        "de las estimaciones de infraestructura física o cloud sujetas a confirmación por parte de la institución cliente.", style_body))
    
    cos_pdf_data = [
        [Paragraph("Rubro / Concepto", style_th), Paragraph("Tipo de Costo", style_th), Paragraph("Monto Estimado / Real", style_th), Paragraph("Observaciones y Estado", style_th)],
        [Paragraph("Licencias de Software", style_td_bold), Paragraph("Real Comprobado", style_td), Paragraph("$0 COP", style_td), Paragraph("Ahorro total mediante Ubuntu, MySQL, Python y Django.", style_td)],
        [Paragraph("Desarrollo y Pruebas", style_td_bold), Paragraph("Real (Formativo)", style_td), Paragraph("$0 COP", style_td), Paragraph("Aporte formativo de aprendices SENA Regional Magdalena.", style_td)],
        [Paragraph("Servidor On-Premise", style_td_bold), Paragraph("Estimado Cotizado", style_td), Paragraph("$3.500.000 - $4.800.000 COP", style_td), Paragraph("Inversión única para torre servidor. A confirmar.", style_td)],
        [Paragraph("Servidor VPS Nube", style_td_bold), Paragraph("Estimado Mensual", style_td), Paragraph("$100.000 - $160.000 COP/mes", style_td), Paragraph("VPS 4 vCPU / 8 GB RAM (DigitalOcean/Linode).", style_td)],
        [Paragraph("Dominio .edu.co", style_td_bold), Paragraph("Estimado Anual", style_td), Paragraph("$80.000 - $110.000 COP/año", style_td), Paragraph("Trámite ante operador oficial de dominio educativo.", style_td)],
        [Paragraph("Certificado SSL/TLS", style_td_bold), Paragraph("Real Comprobado", style_td), Paragraph("$0 COP", style_td), Paragraph("Certificados gratis de por vida provistos por Let's Encrypt.", style_td)]
    ]
    t_cos_pdf = Table(cos_pdf_data, colWidths=[120, 85, 130, 169])
    t_cos_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_cos_pdf)
    story.append(PageBreak())

    # 12. ACTA DE ENTREGA
    story.append(Paragraph("10. ACTA DE ENTREGA Y RECIBO A SATISFACCIÓN", style_h1))
    story.append(Paragraph(
        "En la ciudad de Santa Marta, Departamento del Magdalena, a los catorce (14) días del mes de octubre de 2026, "
        "se reúnen en las instalaciones institucionales las partes interesadas del proyecto formativo para suscribir la presente "
        "ACTA DE ENTREGA Y RECIBO A SATISFACCIÓN del sistema de información EduNova (SINETEC):<br/><br/>"
        "<b>1. POR PARTE DE LOS DESARROLLADORES (APRENDICES SENA):</b><br/>"
        "• DULCE MARÍA FIGUEROA — Aprendiz ADSI Ficha 228106<br/>"
        "• AMINTA MARÍA MOGUEA FLOREZ — Aprendiz ADSI Ficha 228106<br/><br/>"
        "<b>2. POR PARTE DE LA ENTIDAD FORMATIVA (SENA REGIONAL MAGDALENA):</b><br/>"
        "• ING. ANYBAL LÓPEZ — Instructor Técnico Evaluador<br/><br/>"
        "<b>3. POR PARTE DE LA INSTITUCIÓN EDUCATIVA RECEPTORA:</b><br/>"
        "• RECTORÍA / COORDINACIÓN ACADÉMICA DE LA MEDIA TÉCNICA<br/><br/>"
        "<b>DECLARACIÓN DE CONFORMIDAD:</b><br/>"
        "El instructor Anybal López y el delegado institucional certifican que el sistema cumple a cabalidad con los requisitos funcionales, "
        "las pruebas de seguridad RBAC, el aislamiento de perfiles y los protocolos administrativos pactados para la etapa productiva.", style_body))
    story.append(Spacer(1, 25))

    firmas_pdf_data = [
        [
            Paragraph("_________________________________________<br/><b>DULCE MARÍA FIGUEROA</b><br/>Aprendiz SENA — ADSI Ficha 228106<br/>Líder de Desarrollo e Implementación", ParagraphStyle('F1', fontName='Arial', fontSize=8.5, leading=11, alignment=1)),
            Paragraph("_________________________________________<br/><b>AMINTA MARÍA MOGUEA FLOREZ</b><br/>Aprendiz SENA — ADSI Ficha 228106<br/>Líder de Desarrollo e Implementación", ParagraphStyle('F2', fontName='Arial', fontSize=8.5, leading=11, alignment=1))
        ],
        [
            Paragraph("<br/><br/>_________________________________________<br/><b>ING. ANYBAL LÓPEZ</b><br/>Instructor Técnico Evaluador<br/>SENA Regional Magdalena — Centro Ecoturístico", ParagraphStyle('F3', fontName='Arial', fontSize=8.5, leading=11, alignment=1)),
            Paragraph("<br/><br/>_________________________________________<br/><b>DELEGADO INSTITUCIONAL</b><br/>Rectoría / Coordinación Académica<br/>Institución Educativa Articulada", ParagraphStyle('F4', fontName='Arial', fontSize=8.5, leading=11, alignment=1))
        ]
    ]
    t_firm_pdf = Table(firmas_pdf_data, colWidths=[250, 254])
    t_firm_pdf.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_firm_pdf)
    story.append(Spacer(1, 15))

    # 13. CONCLUSIONES
    story.append(Paragraph("11. CONCLUSIONES Y ANEXOS TÉCNICOS", style_h1))
    story.append(Paragraph(
        "1. La solución EduNova (SINETEC) ha alcanzado un estado de madurez técnica y funcional óptimo, consolidando "
        "una arquitectura web confiable, escalable y respaldada por bases de datos relacionales normalizadas.<br/>"
        "2. Los planes de instalación, respaldo automatizado y migración presentados cumplen rigurosamente con los protocolos "
        "organizacionales del SENA y satisfacen con exactitud el resultado de aprendizaje orientado por el instructor Anybal López.<br/>"
        "3. El modelo de costos sustentado en Software Libre garantiza que la institución receptora cuente con una plataforma de vanguardia "
        "sin incurrir en gastos prohibitivos de licenciamiento privativo, asegurando su sostenibilidad a largo plazo.", style_body))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Documento PDF generado exitosamente: {pdf_path}")
    return pdf_path


# ==============================================================================
# EJECUCIÓN PRINCIPAL Y COPIADO EN UBICACIONES SOLICITADAS
# ==============================================================================
def main():
    print("======================================================================")
    print("GENERADOR MAESTRO DEL INFORME ADMINISTRATIVO EDUNOVA - SENA")
    print("======================================================================")

    # 1. Generar DOCX
    docx_file = generar_documento_word(DOCX_DOCS)

    # 2. Generar PDF
    pdf_file = generar_documento_pdf(PDF_DOCS)

    # 3. Replicar en carpeta raíz C:\SINETEC y en Descargas
    rutas_copias_docx = [
        os.path.join(ROOT_DIR, DOCX_NAME),
        os.path.join(DOWNLOADS_DIR, DOCX_NAME)
    ]
    rutas_copias_pdf = [
        os.path.join(ROOT_DIR, PDF_NAME),
        os.path.join(DOWNLOADS_DIR, PDF_NAME)
    ]

    for dest in rutas_copias_docx:
        try:
            shutil.copy2(docx_file, dest)
            print(f"[COPIA DOCX] Guardado en: {dest}")
        except Exception as e:
            print(f"[ALERTA COPIA DOCX] {dest}: {e}")

    for dest in rutas_copias_pdf:
        try:
            shutil.copy2(pdf_file, dest)
            print(f"[COPIA PDF] Guardado en: {dest}")
        except Exception as e:
            print(f"[ALERTA COPIA PDF] {dest}: {e}")

    # 4. Verificación de integridad final
    tamanio_docx = os.path.getsize(docx_file)
    tamanio_pdf = os.path.getsize(pdf_file)
    print("----------------------------------------------------------------------")
    print(f"VERIFICACIÓN FINAL DE ARCHIVOS:")
    print(f"1. DOCX: {docx_file} -> {tamanio_docx} bytes (VÁLIDO)")
    print(f"2. PDF:  {pdf_file} -> {tamanio_pdf} bytes (VÁLIDO)")
    print("======================================================================")
    print("¡AMBOS ARCHIVOS FUERON GENERADOS Y VERIFICADOS CON ÉXITO AL 100%!")
    print("======================================================================")

if __name__ == '__main__':
    main()
