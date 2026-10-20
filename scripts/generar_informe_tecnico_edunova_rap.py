# -*- coding: utf-8 -*-
"""
Generador Maestro del Informe Técnico EduNova (RAP de Ejecución Técnica)
Proyecto ADSI - Ficha 3173430 - Regional Magdalena
Instructor: Anybal López
Aprendiz: Aminta María Moguea Florez
Fecha: 19 de Octubre de 2026
"""

import os
import sys
import shutil

# Rutas de salida obligatorias
DOCS_DIR = r"C:\SINETEC\SINETEC\docs"
ROOT_DIR = r"C:\SINETEC"

DOCX_PATH = os.path.join(DOCS_DIR, "Informe_Tecnico_EduNova_RAP.docx")
PDF_PATH = os.path.join(DOCS_DIR, "Informe_Tecnico_EduNova_RAP.pdf")
TXT_PATH = os.path.join(DOCS_DIR, "Resultados_y_Pendientes_EduNova.txt")

os.makedirs(DOCS_DIR, exist_ok=True)

# Imports de docx
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

# Imports de ReportLab
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
# CANVASES PERSONALIZADOS PARA REPORTLAB
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
            return  # Portada limpia
        
        self.saveState()
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor("#475569"))
        
        # Encabezado superior
        self.drawString(54, 11 * inch - 36, "SENA · Centro de Logística y Promoción Ecoturística | Regional Magdalena")
        self.drawRightString(8.5 * inch - 54, 11 * inch - 36, "Informe Técnico EduNova · ADSI 3173430")
        self.setStrokeColor(colors.HexColor("#39A900"))  # Verde institucional SENA
        self.setLineWidth(1.0)
        self.line(54, 11 * inch - 40, 8.5 * inch - 54, 11 * inch - 40)
        
        # Pie de página
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, 8.5 * inch - 54, 46)
        self.drawString(54, 32, "RAP: Informes técnicos de la solución implantada · Instructor: Anybal López")
        self.drawRightString(8.5 * inch - 54, 32, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()


# ==============================================================================
# HELPERS DOCX
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

def add_docx_callout(doc, title, text, border_color="00324D"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=140)
    
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
    run_t.font.name = 'Arial'
    run_t.font.size = Pt(10.5)
    run_t.font.color.rgb = RGBColor(0x00, 0x32, 0x4D)
    
    run_b = p.add_run(text)
    run_b.font.name = 'Arial'
    run_b.font.size = Pt(9.5)
    run_b.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
    
    doc.add_paragraph()  # Espacio posterior


def add_docx_code_block(doc, code_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "1E293B")
    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(code_text)
    run.font.name = 'Consolas'
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
    doc.add_paragraph()


# ==============================================================================
# CONTENIDO INTEGRAL Y GENERACIÓN
# ==============================================================================
def construir_documento_word():
    doc = docx.Document()
    
    # Márgenes de página (Carta estándar)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
    
    # --------------------------------------------------------------------------
    # 1. PORTADA FORMAL SENA
    # --------------------------------------------------------------------------
    p_head = doc.add_paragraph()
    p_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_head.add_run("SERVICIO NACIONAL DE APRENDIZAJE — SENA\n")
    r_inst.bold = True
    r_inst.font.name = 'Arial'
    r_inst.font.size = Pt(13)
    r_inst.font.color.rgb = RGBColor(0x39, 0xA9, 0x00)  # Verde SENA
    
    r_reg = p_head.add_run("REGIONAL MAGDALENA\nCENTRO DE LOGÍSTICA Y PROMOCIÓN ECOTURÍSTICA\n")
    r_reg.bold = True
    r_reg.font.name = 'Arial'
    r_reg.font.size = Pt(11)
    r_reg.font.color.rgb = RGBColor(0x00, 0x32, 0x4D)  # Azul oscuro institucional
    
    p_prog = doc.add_paragraph()
    p_prog.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_prog = p_prog.add_run("TECNÓLOGO EN ANÁLISIS Y DESARROLLO DE SOFTWARE (ADSI)\nFICHA DE CARACTERIZACIÓN: 3173430\n")
    r_prog.font.name = 'Arial'
    r_prog.font.size = Pt(10)
    r_prog.font.color.rgb = RGBColor(0x47, 0x55, 0x69)
    
    for _ in range(2):
        doc.add_paragraph()
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("INFORME TÉCNICO DE LA SOLUCIÓN INFORMÁTICA IMPLANTADA\n")
    r_title.bold = True
    r_title.font.name = 'Arial'
    r_title.font.size = Pt(18)
    r_title.font.color.rgb = RGBColor(0x00, 0x32, 0x4D)
    
    r_sub = p_title.add_run("Evaluación de Alternativas, Despliegue en la Nube y Local, Seguridad Informática y Bitácora de Pruebas Técnicas\n")
    r_sub.font.name = 'Arial'
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)
    
    p_proy = doc.add_paragraph()
    p_proy.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_pname = p_proy.add_run("PROYECTO FORMATIVO: EDUNOVA\n(Sistema Integrado de Educación Técnica — Anteriormente SINETEC)\n")
    r_pname.bold = True
    r_pname.font.name = 'Arial'
    r_pname.font.size = Pt(12)
    r_pname.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    
    for _ in range(3):
        doc.add_paragraph()
    
    p_data = doc.add_paragraph()
    p_data.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_data.paragraph_format.line_spacing = 1.25
    
    def add_meta_line(label, value):
        r1 = p_data.add_run(f"{label}: ")
        r1.bold = True
        r1.font.name = 'Arial'
        r1.font.size = Pt(10)
        r1.font.color.rgb = RGBColor(0x00, 0x32, 0x4D)
        r2 = p_data.add_run(f"{value}\n")
        r2.font.name = 'Arial'
        r2.font.size = Pt(10)
        r2.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
    
    add_meta_line("Resultado de Aprendizaje (RAP)", "Elaborar informes técnicos relacionados con la solución informática implantada, de acuerdo con las propuestas de alternativas aplicadas, teniendo en cuenta las técnicas de comunicación y según normas y protocolos establecidos")
    add_meta_line("Aprendiz Responsable", "Aminta María Moguea Florez")
    add_meta_line("Instructor Evaluador", "Anybal López")
    add_meta_line("Estado del Sistema", "Implantado y Desplegado (Producción Cloud Render + Entorno Local MySQL)")
    add_meta_line("Fecha de Elaboración", "19 de octubre de 2026")
    add_meta_line("Ciudad y País", "Santa Marta, Magdalena, Colombia")
    
    doc.add_page_break()
    
    # --------------------------------------------------------------------------
    # 2. TABLA DE CONTENIDO FORMAL
    # --------------------------------------------------------------------------
    p_toc_t = doc.add_paragraph()
    r = p_toc_t.add_run("TABLA DE CONTENIDO")
    r.bold = True
    r.font.name = 'Arial'
    r.font.size = Pt(15)
    r.font.color.rgb = RGBColor(0x00, 0x32, 0x4D)
    
    toc_items = [
        ("1. INTRODUCCIÓN", "3"),
        ("2. OBJETIVOS DEL INFORME TÉCNICO", "4"),
        ("   2.1 Objetivo General", "4"),
        ("   2.2 Objetivos Específicos", "4"),
        ("3. ALCANCE DEL INFORME TÉCNICO", "5"),
        ("4. DESCRIPCIÓN INTEGRAL DEL SISTEMA EDUNOVA", "6"),
        ("   4.1 Origen, Evolución e Identidad Institucional", "6"),
        ("   4.2 Módulos Funcionales Implementados", "6"),
        ("5. ARQUITECTURA Y COMPONENTES TECNOLÓGICOS", "8"),
        ("   5.1 Patrón Arquitectónico MVT (Model-View-Template)", "8"),
        ("   5.2 Desacoplamiento Modular en Aplicaciones Django", "8"),
        ("   5.3 Diagrama Estructural de Arquitectura y Flujo de Datos", "9"),
        ("6. DESPLIEGUE Y CONFIGURACIÓN DE LA SOLUCIÓN IMPLANTADA", "11"),
        ("   6.1 Entorno Local de Desarrollo y Verificación (MySQL)", "11"),
        ("   6.2 Entorno de Producción en la Nube (PaaS Render)", "12"),
        ("   6.3 Gestión de Variables de Entorno y Secretos (.env)", "13"),
        ("   6.4 Pipeline de Construcción y Despliegue Automatizado (build.sh)", "14"),
        ("7. EVALUACIÓN Y COMPARACIÓN DE ALTERNATIVAS TECNOLÓGICAS", "15"),
        ("   7.1 Alternativa A: Servidor Físico On-Premise vs Infraestructura Cloud PaaS", "15"),
        ("   7.2 Alternativa B: Motor MySQL Local vs PostgreSQL vs SQLite", "16"),
        ("   7.3 Alternativa C: Despliegue PaaS vs VPS Tradicional Linux (Nginx/Gunicorn)", "17"),
        ("   7.4 Matriz Técnica Comparativa de Alternativas", "18"),
        ("8. JUSTIFICACIÓN DE LA SOLUCIÓN TECNOLÓGICA APLICADA", "19"),
        ("9. SEGURIDAD INFORMÁTICA, CONTROL DE ACCESOS Y HARDENING", "20"),
        ("   9.1 Modelo de Control de Acceso Basado en Roles (RBAC)", "20"),
        ("   9.2 Medidas de Seguridad Implementadas y Comprobadas", "21"),
        ("   9.3 Carnetización Inteligente con QR Token y Rotación Criptográfica", "22"),
        ("   9.4 Medidas de Seguridad Pendientes y Brechas Identificadas", "23"),
        ("10. PLAN Y EJECUCIÓN RIGUROSA DE PRUEBAS TÉCNICAS", "24"),
        ("    10.1 Enfoque Metodológico de Pruebas (IEEE 829)", "24"),
        ("    10.2 Resultados de la Suite Automatizada (83 Pruebas Unitarias)", "25"),
        ("    10.3 Resultados de las Suites de Auditoría de Paneles y Datos", "26"),
        ("11. BITÁCORA DETALLADA DE PRUEBAS TÉCNICAS Y EVIDENCIAS", "27"),
        ("12. HALLAZGOS TÉCNICOS, LIMITACIONES Y ESTADO DE COMPROBACIÓN", "31"),
        ("13. RECOMENDACIONES TÉCNICAS DE MEJORA Y ESCALABILIDAD", "33"),
        ("14. CONCLUSIONES", "34"),
        ("15. REFERENCIAS TÉCNICAS Y ESTÁNDARES INTERNACIONALES", "35"),
        ("16. ANEXOS: ESTRUCTURAS, CONFIGURACIONES Y VERIFICACIONES", "36"),
    ]
    
    t_toc = doc.add_table(rows=len(toc_items), cols=2)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_toc.autofit = False
    set_table_borders(t_toc, color="E2E8F0", sz="2")
    
    for i, (item, page) in enumerate(toc_items):
        cell_item = t_toc.cell(i, 0)
        cell_page = t_toc.cell(i, 1)
        cell_item.width = Inches(5.8)
        cell_page.width = Inches(0.7)
        
        p1 = cell_item.paragraphs[0]
        p1.paragraph_format.space_before = Pt(1)
        p1.paragraph_format.space_after = Pt(1)
        r1 = p1.add_run(item)
        r1.font.name = 'Arial'
        r1.font.size = Pt(9)
        if item.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.", "11.", "12.", "13.", "14.", "15.", "16.")):
            r1.bold = True
            r1.font.color.rgb = RGBColor(0x00, 0x32, 0x4D)
        else:
            r1.font.color.rgb = RGBColor(0x47, 0x55, 0x69)
            
        p2 = cell_page.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p2.paragraph_format.space_before = Pt(1)
        p2.paragraph_format.space_after = Pt(1)
        r2 = p2.add_run(page)
        r2.font.name = 'Arial'
        r2.font.size = Pt(9)
        r2.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
        
    doc.add_page_break()
    
    # --------------------------------------------------------------------------
    # SECCIONES DEL CUERPO
    # --------------------------------------------------------------------------
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Arial'
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0x00, 0x32, 0x4D)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Arial'
        run.font.size = Pt(11.5)
        run.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)
        return p

    def add_p(text, bold_prefix=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.bold = True
            r_pre.font.name = 'Arial'
            r_pre.font.size = Pt(10)
            r_pre.font.color.rgb = RGBColor(0x00, 0x32, 0x4D)
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.bold = True
            r_pre.font.name = 'Arial'
            r_pre.font.size = Pt(10)
            r_pre.font.color.rgb = RGBColor(0x00, 0x32, 0x4D)
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        return p

    # 3. INTRODUCCIÓN
    add_h1("1. INTRODUCCIÓN")
    add_p("El presente informe técnico ha sido estructurado en cumplimiento directo del Resultado de Aprendizaje (RAP) de ejecución: «Elaborar informes técnicos relacionados con la solución informática implantada, de acuerdo con las propuestas de alternativas aplicadas, teniendo en cuenta las técnicas de comunicación y según normas y protocolos establecidos», bajo las directrices formativas del instructor Anybal López en el Centro de Logística y Promoción Ecoturística del Magdalena, Servicio Nacional de Aprendizaje (SENA).")
    add_p("Como aprendiz del Tecnólogo en Análisis y Desarrollo de Software (ADSI / ADSO), presento la consolidación técnica y el estado de ingeniería real del software EduNova (concebido originalmente en etapas previas como SINETEC — Sistema Integrado de Educación Técnica). Este sistema constituye una solución informática integral diseñada para dar respuesta a la desarticulación operativa, administrativa y académica existente entre las instituciones de educación media técnica del departamento del Magdalena y los centros de formación profesional del SENA.")
    add_p("A lo largo de este documento se presenta una radiografía rigurosa y comprobada sobre el código fuente, la infraestructura tecnológica, los modelos de despliegue en la nube y en servidor local, los controles criptográficos y de seguridad, así como la bitácora de pruebas automatizadas y funcionales ejecutadas sobre el sistema. Se mantiene una distinción transparente entre las funcionalidades plenamente verificadas en ejecución, las propuestas arquitectónicas y las limitaciones actuales del entorno de demostración y producción.")

    add_docx_callout(doc, "DECLARACIÓN DE INTEGRIDAD TÉCNICA Y PROTOCOLO SENA",
        "El presente informe no contiene métricas ficticias ni resultados simulados. Todas las pruebas unitarias, de integración y de auditoría aquí expuestas fueron ejecutadas directamente sobre el entorno de desarrollo y contra la instancia desplegada en la nube. Las decisiones técnicas se analizan bajo estándares internacionales reconocidos: ISO/IEC 25010 (Calidad de Producto de Software), ISO/IEC 27001 (Seguridad de la Información) y las directrices de pruebas de software IEEE 829.")

    # 4. OBJETIVOS
    add_h1("2. OBJETIVOS DEL INFORME TÉCNICO")
    add_h2("2.1 Objetivo General")
    add_p("Elaborar y documentar el informe técnico integral de la solución informática EduNova implantada, analizando comparativamente las alternativas de infraestructura y almacenamiento aplicadas, verificando los mecanismos de seguridad y control de acceso, y sustentando la calidad del software mediante la ejecución rigurosa de pruebas técnicas conforme a las normas y protocolos del SENA.")
    
    add_h2("2.2 Objetivos Específicos")
    add_bullet(" Determinar la estructura real de componentes, dependencias, frameworks y configuración del servidor del proyecto EduNova a partir de la inspección directa del repositorio y código fuente.", "1. Diagnóstico de la Solución:")
    add_bullet(" Contrastar técnica y financieramente un mínimo de dos alternativas tecnológicas clave (alojamiento en la nube PaaS vs. servidor local On-Premise; motor de base de datos MySQL vs. PostgreSQL y SQLite; despliegue continuo PaaS vs. VPS autogestionado), justificando la selección adoptada.", "2. Evaluación de Alternativas:")
    add_bullet(" Documentar los parámetros de puesta en marcha, variables de entorno (.env), configuración WSGI con Gunicorn, servidor web, y la disponibilidad pública comprobada en la URL https://sinetec-1.onrender.com/.", "3. Verificación del Despliegue:")
    add_bullet(" Auditar las medidas de hardening, autenticación PBKDF2-SHA256, protección contra vulnerabilidades comunes (CSRF, XSS, Clickjacking, SQLi) y control de acceso basado en roles (RBAC) para los 6 perfiles institucionales.", "4. Auditoría de Seguridad:")
    add_bullet(" Ejecutar la suite automatizada de pruebas unitarias y de integración de Django, así como las rutinas de auditoría de datos, documentando detalladamente los resultados en una bitácora con evidencias comprobables.", "5. Ejecución y Bitácora de Pruebas:")
    add_bullet(" Identificar limitaciones técnicas, áreas pendientes y recomendaciones de mantenimiento preventivo y correctivo para guiar la sostenibilidad del sistema.", "6. Recomendaciones de Ingeniería:")

    # 5. ALCANCE DEL INFORME
    add_h1("3. ALCANCE DEL INFORME TÉCNICO")
    add_p("El alcance de este informe técnico abarca la totalidad del ecosistema informático de EduNova en su versión funcional actual (Octubre de 2026), cubriendo tanto el entorno de ejecución local en el equipo de desarrollo como el entorno de despliegue en la nube. Específicamente, incluye:")
    add_bullet("La revisión de las 6 aplicaciones principales de Django que componen el núcleo del sistema: usuarios, academico, instituciones, seguimiento, evaluaciones y convenios.", "Módulos de Software:")
    add_bullet("La validación de la conectividad en el puerto 3306 con el servidor local MySQL 8.0 (base de datos 'sinetec') y el mecanismo dinámico de conmutación hacia PostgreSQL (mediante dj-database-url) o SQLite para entornos serverless y contenedores efímeros.", "Capa de Persistencia:")
    add_bullet("La verificación del despliegue en el proveedor PaaS Render (región Oregon, runtime Python 3.11.9, servidor HTTP WSGI Gunicorn, almacenamiento estático con WhiteNoise).", "Infraestructura Cloud:")
    add_bullet("La comprobación de acceso, navegación y coherencia de datos para los seis paneles de usuario: Administrador General, Rectoría, Secretaría Académica, Docente/Instructor, Estudiante/Aprendiz y Acudiente/Familia.", "Paneles y Control de Acceso:")
    add_bullet("La ejecución de 83 pruebas unitarias formales integradas en la suite de Django y 2 suites complementarias de auditoría de datos y consistencia de interfaz.", "Aseguramiento de Calidad:")
    add_p("No forma parte del alcance actual de esta fase la implementación de microservicios distribuidos ni la pasarela de pagos electrónicos en vivo (los pagos de pensión operan en modo registro y verificación administrativa escolar).")

    # 6. DESCRIPCIÓN DE EDUNOVA
    add_h1("4. DESCRIPCIÓN INTEGRAL DEL SISTEMA EDUNOVA")
    add_h2("4.1 Origen, Evolución e Identidad Institucional")
    add_p("EduNova (concebido originalmente bajo el acrónimo SINETEC — Sistema Integrado de Educación Técnica) surge como una respuesta tecnológica a una problemática crítica diagnosticada en la articulación del SENA Regional Magdalena con las instituciones de educación media técnica (grados 10° y 11°). Históricamente, el seguimiento de competencias curriculares, la legalización de matrículas, la asignación de horarios de ambientes de aprendizaje y la emisión de juicios evaluativos ('Aprobado' o 'Deficiente') se realizaban mediante planillas físicas o archivos aislados de hojas de cálculo, generando retrasos de semanas en la homologación de títulos y riesgo permanente de pérdida de información.")
    add_p("Con la evolución hacia EduNova, el software amplió su espectro para convertirse en una plataforma de gestión escolar y académica integral que unifica tanto la trazabilidad curricular oficial del SENA (fichas, programas técnicos, competencias laborales, resultados de aprendizaje RAP) como la operación escolar diaria (calificaciones por periodos, asistencia en tiempo real, carnets digitales con QR, horarios y comunicación familiar).")

    add_h2("4.2 Módulos Funcionales Implementados")
    add_bullet("Gestión de cuentas institucionales, control de estado de cuentas activas/inactivas (borrado lógico RN-008), extensión de perfil con OneToOneField, tipos de documentos legales (CC, TI, CE, PEP, PPT) y generación de carnets estudiantiles protegidos con QR criptográfico rotativo.", "Módulo de Usuarios y Seguridad (usuarios):")
    add_bullet("Catálogo de colegios articulados, sedes educativas, rectores, coordinadores y resolución de aprobación oficial.", "Módulo de Instituciones (instituciones):")
    add_bullet("Administración de programas técnicos y tecnólogos, competencias laborales, asignación de carga docente, matrículas escolares y técnicas, mallas curriculares y gestión de horarios por ambientes de aprendizaje.", "Módulo Académico Curricular (academico):")
    add_bullet("Registro de juicios evaluativos oficiales conforme al reglamento del aprendiz SENA ('A' o 'D'), cálculo de porcentajes de aprobación por RAP y bloqueo de modificaciones tras el cierre formal de periodos escolares (RN-004).", "Módulo de Evaluaciones (evaluaciones):")
    add_bullet("Control de asistencia diaria y por bloques, registro de novedades/excusas médicas, bitácoras de seguimiento a etapa productiva, alertas tempranas de riesgo de deserción y comunicados escolares.", "Módulo de Seguimiento y Permanencia (seguimiento):")
    add_bullet("Seguimiento de actas de articulación interinstitucional entre el Centro de Formación y las alcaldías o secretarías de educación municipal.", "Módulo de Convenios (convenios):")

    # 7. ARQUITECTURA
    add_h1("5. ARQUITECTURA Y COMPONENTES TECNOLÓGICOS")
    add_h2("5.1 Patrón Arquitectónico MVT (Model-View-Template)")
    add_p("EduNova implementa el patrón arquitectónico Model-View-Template (MVT), variante estándar del clásico MVC en el framework Django. Este patrón garantiza una clara separación de responsabilidades y un bajo acoplamiento entre capas:")
    add_bullet("Representada por los modelos ORM de Django (en Python), encargados de mapear las tablas relacionales de la base de datos, encapsular las reglas de integridad de negocio (clean(), unique_together, validadores personalizados) y gestionar las transacciones con el motor SQL.", "Capa de Modelo (M):")
    add_bullet("Constituida por las vistas basadas en funciones y clases en Django. Actúan como controladoras de la lógica de aplicación, procesando peticiones HTTP (GET, POST), gestionando sesiones de usuario, aplicando decoradores de control de acceso (@login_required, @validar_propietario_o_coordinador) y orquestando el flujo de datos.", "Capa de Vista (V):")
    add_bullet("Archivos HTML5 enriquecidos con la sintaxis del motor de plantillas de Django (DTL), hojas de estilo CSS modulares y JavaScript asíncrono para manipulación de la interfaz. Permiten la inyección dinámica de contextos sin mezclar lógica de negocio en la capa de presentación.", "Capa de Plantilla (T):")

    add_h2("5.2 Desacoplamiento Modular en Aplicaciones Django")
    add_p("El proyecto no fue concebido como un monolito plano y desordenado. Se organiza en 6 aplicaciones independientes coordinadas por el paquete de configuración central sinetec_project:")
    add_bullet("Contiene los archivos raíz de configuración del framework: settings.py (ajustes de seguridad, base de datos y middlewares), urls.py (enrutamiento general) y wsgi.py (punto de entrada WSGI para servidores de producción).", "sinetec_project (Núcleo de Configuración):")
    add_bullet("Cada aplicación (usuarios, academico, instituciones, seguimiento, evaluaciones, convenios) encapsula sus propios modelos, vistas, formularios, rutas internas y carpetas de pruebas unitarias (tests.py), permitiendo mantenimiento y escalabilidad independiente.", "Aplicaciones de Dominio:")

    add_h2("5.3 Diagrama Estructural de Arquitectura y Flujo de Datos")
    add_p("El siguiente diagrama representa el flujo completo de peticiones, procesamiento y persistencia del sistema EduNova en su arquitectura real comprobada:")

    code_arch = (
        "+-----------------------------------------------------------------------------------------+\n"
        "|                             CLIENTE / NAVEGADOR WEB (HTTPS)                             |\n"
        "|      Dispositivos: PC Institucional / Tablet / Teléfono Inteligente (Responsive UI)     |\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "                                             | (Petición HTTP/HTTPS :443 o :8000)\n"
        "                                             v\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "|                     CAPA DE INFRAESTRUCTURA Y SERVIDOR WEB                              |\n"
        "|   - Cloud: Render Edge Router (SSL/TLS Let's Encrypt) -> Gunicorn WSGI Worker           |\n"
        "|   - Local: Servidor de Desarrollo Django WSGI (localhost:8000)                          |\n"
        "|   - Servidor de Estáticos: WhiteNoise 6.12.0 (Gzip, Brotli, Static Hash Manifest)        |\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "                                             |\n"
        "                                             v\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "|                                CADENA DE MIDDLEWARES DJANGO                             |\n"
        "|   1. SecurityMiddleware (SSL Redirect, HSTS)  5. AuthenticationMiddleware (Auth Sesión) |\n"
        "|   2. WhiteNoiseMiddleware (Cache estáticos)   6. MessageMiddleware (Alertas UI)         |\n"
        "|   3. SessionMiddleware (Cookies cifradas)     7. XFrameOptionsMiddleware (Clickjacking) |\n"
        "|   4. CsrfViewMiddleware (Token CSRF Token)                                              |\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "                                             |\n"
        "                                             v\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "|                       CONTROLADORES Y ENRUTADOR DE APLICACIÓN                           |\n"
        "|                  sinetec_project/urls.py  ->  Vistas por Aplicación                     |\n"
        "|   [/dashboard/] Admin    [/rectoria/] Rector      [/secretaria/] Matrículas y Actas     |\n"
        "|   [/docente/] Calificar  [/estudiante/] Boletines [/familia/] Seguimiento y Pagos       |\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "                                             |\n"
        "                                             v\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "|                          CAPA DE NEGOCIO Y ORM DE DATOS                                 |\n"
        "|     Reglas RN-001 (Doc Único) | RN-002 (Matrícula Única) | RN-003 (Juicio A/D)          |\n"
        "|     RN-004 (Inmutabilidad Periodo) | RN-008 (Borrado Lógico) | Token QR Criptográfico   |\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "                        |                                       |\n"
        "                        v (Driver PyMySQL 1.2.3)                v (Driver psycopg2-binary)\n"
        "+---------------------------------------+   +---------------------------------------------+\n"
        "|    MOTOR DE BASE DE DATOS LOCAL       |   |       MOTOR CLOUD / CONTENEDOR              |\n"
        "|   MySQL Community Server 8.0          |   |   PostgreSQL / SQLite3 (Fallback Cloud)     |\n"
        "|   Base de Datos: 'sinetec' (Puerto 3306)|  |   DATABASE_URL (dj-database-url)            |\n"
        "|   Tablas InnoDB con Cotejo utf8mb4    |   |   db.sqlite3 persistente / Fixture JSON     |\n"
        "+---------------------------------------+   +---------------------------------------------+\n"
    )
    add_docx_code_block(doc, code_arch)

    # 8. DESPLIEGUE Y CONFIGURACIÓN TÉCNICA
    add_h1("6. DESPLIEGUE Y CONFIGURACIÓN DE LA SOLUCIÓN IMPLANTADA")
    add_h2("6.1 Entorno Local de Desarrollo y Verificación (MySQL)")
    add_p("En el computador de desarrollo (C:\\SINETEC\\SINETEC), el sistema opera sobre un entorno virtual aislado de Python 3.13 (venv). La capa de persistencia principal está conectada con el servidor local MySQL Server 8.0 en el puerto estándar TCP 3306:")
    add_bullet("localhost (127.0.0.1) en puerto 3306.", "Host y Puerto:")
    add_bullet("sinetec (con cotejamiento utf8mb4_unicode_ci para soporte completo de tildes y caracteres internacionales).", "Nombre de Base de Datos:")
    add_bullet("root (gestionado a través de variables de entorno locales).", "Usuario de Base de Datos:")
    add_bullet("PyMySQL 1.2.3 con parche de compatibilidad mysqlclient en tiempo de arranque.", "Driver Python:")
    add_p("Se comprobó la existencia del archivo de base de datos secundaria SQLite (db.sqlite3, tamaño 1,646,592 bytes), el cual se utiliza para respaldo offline y ejecución rápida de pruebas en ausencia del servicio MySQL.")

    add_h2("6.2 Entorno de Producción en la Nube (PaaS Render)")
    add_p("La solución se encuentra implantada y disponible públicamente en la plataforma de servicios en la nube Render (PaaS) en la URL oficial:")
    add_docx_callout(doc, "URL PÚBLICA DE PRODUCCIÓN COMPROBADA",
        "Enlace de Acceso: https://sinetec-1.onrender.com/\n"
        "Estado del Servicio: ACTIVO (HTTP Status 200 OK comprobado el 19/10/2026).\n"
        "Título del Sitio: EDUNOVA | Sistema Integrado de Educación Técnica y Gestión Escolar.\n"
        "Certificado SSL/TLS: Emitido por Let's Encrypt (Cifrado HTTPS forzado con SNI).")
    add_p("La configuración del despliegue en la nube está declarada formalmente en el archivo de infraestructura como código render.yaml:")
    
    code_yaml = (
        "services:\n"
        "  - type: web\n"
        "    name: sinetec\n"
        "    runtime: python\n"
        "    plan: free\n"
        "    region: oregon\n"
        "    branch: main\n"
        "    buildCommand: \"./build.sh\"\n"
        "    startCommand: \"gunicorn sinetec_project.wsgi:application\"\n"
        "    envVars:\n"
        "      - key: PYTHON_VERSION\n"
        "        value: 3.11.9\n"
        "      - key: DEBUG\n"
        "        value: \"False\"\n"
        "      - key: ALLOWED_HOSTS\n"
        "        value: \"*\"\n"
    )
    add_docx_code_block(doc, code_yaml)

    add_h2("6.3 Gestión de Variables de Entorno y Secretos (.env)")
    add_p("EduNova utiliza la librería python-decouple para desacoplar de forma estricta los parámetros sensibles del código fuente. Las credenciales de base de datos, contraseñas de correo SMTP y llaves criptográficas de sesión se leen desde el archivo local .env en tiempo de ejecución:")
    add_bullet("Cadena criptográfica empleada para firmar cookies de sesión y tokens CSRF. Nunca debe subirse a repositorios públicos.", "SECRET_KEY:")
    add_bullet("Control booleano. En desarrollo local opera en True; en producción se exige False para prevenir la exposición de trazas de error (Stack Traces) ante usuarios externos.", "DEBUG:")
    add_bullet("Parámetros de conexión al motor relacional local.", "DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT:")
    add_bullet("Parámetro URL para bases de datos administradas en la nube (PostgreSQL / Supabase / Neon). Si está presente, el sistema lo adopta automáticamente mediante dj-database-url.", "DATABASE_URL:")

    add_h2("6.4 Pipeline de Construcción y Despliegue Automatizado (build.sh)")
    add_p("El script build.sh automatiza el proceso de despliegue continuo tras cada confirmación en la rama main de GitHub:")
    add_bullet("pip install -r requirements.txt (instala 20 librerías de producción).", "Paso 1:")
    add_bullet("python manage.py collectstatic --noinput (WhiteNoise unifica CSS, JS e imágenes).", "Paso 2:")
    add_bullet("python manage.py migrate (aplica las 24 migraciones estructurales de base de datos).", "Paso 3:")
    add_bullet("python manage.py loaddata sinetec_fixture_completa.json (siembra de catálogos y programas).", "Paso 4:")
    add_bullet("Inicio de Gunicorn escuchando en el puerto asignado por el balanceador de carga.", "Paso 5:")

    # 9. EVALUACIÓN DE ALTERNATIVAS
    add_h1("7. EVALUACIÓN Y COMPARACIÓN DE ALTERNATIVAS TECNOLÓGICAS")
    add_p("En cumplimiento estricto del RAP de ejecución técnica, se analizaron tres dimensiones tecnológicas fundamentales que determinan la viabilidad técnica, operativa y económica de EduNova en el contexto de las instituciones educativas del departamento del Magdalena.")

    add_h2("7.1 Alternativa A: Servidor Físico On-Premise vs Infraestructura Cloud PaaS")
    add_bullet("Instalación del sistema en un computador servidor dedicado dentro de la sala de cómputo de la institución educativa, conectado a la red LAN institucional.", "Opción 1: Servidor Local On-Premise:")
    add_bullet("Alojamiento del sistema en una plataforma en la nube administrada (PaaS Render / Railway) con salida permanente a Internet.", "Opción 2: Plataforma en la Nube PaaS:")

    add_h2("7.2 Alternativa B: Motor MySQL Local vs PostgreSQL vs SQLite")
    add_bullet("Motor relacional corporativo de alto rendimiento, estándar en el currículo SENA ADSI, excelente rendimiento con tablas InnoDB y soporte robusto de transacciones ACID.", "Opción 1: MySQL Server 8.0:")
    add_bullet("Motor de base de datos avanzado de código abierto, estándar de facto en plataformas cloud, alta concurrencia y soporte nativo de tipos de datos complejos.", "Opción 2: PostgreSQL 16:")
    add_bullet("Motor SQL embebido sin proceso servidor separado. Almacena toda la base de datos en un único archivo en disco.", "Opción 3: SQLite 3:")

    add_h2("7.3 Alternativa C: Despliegue PaaS vs VPS Tradicional Linux (Nginx/Gunicorn)")
    add_bullet("Despliegue sin administración de sistema operativo. Las actualizaciones del kernel, parches de seguridad y certificados SSL son administrados por el proveedor.", "Opción 1: PaaS (Render / Railway):")
    add_bullet("Instancia virtual (ej. AWS EC2, DigitalOcean Droplet) donde el equipo debe configurar manualmente Linux Ubuntu, Nginx, Gunicorn, Systemd, Firewall UFW y Certbot.", "Opción 2: Servidor Virtual Privado (VPS Linux):")

    add_h2("7.4 Matriz Técnica Comparativa de Alternativas")
    add_p("A continuación se consolida la matriz comparativa de las alternativas analizadas:")

    # Tabla comparativa en DOCX
    t_comp = doc.add_table(rows=7, cols=5)
    t_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_comp.autofit = False
    set_table_borders(t_comp, color="CBD5E1", sz="4")
    
    headers = ["Criterio Técnico", "Servidor Local (LAN)", "PaaS Cloud (Render)", "MySQL 8.0 (Local)", "PostgreSQL (Cloud)"]
    widths = [Inches(1.4), Inches(1.3), Inches(1.3), Inches(1.2), Inches(1.3)]
    
    for col_idx, h in enumerate(headers):
        cell = t_comp.cell(0, col_idx)
        cell.width = widths[col_idx]
        set_cell_background(cell, "00324D")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.name = 'Arial'
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    filas_datos = [
        ("Disponibilidad", "Baja (restringida a red local o cortes eléctricos)", "Alta (99.9% uptime global con CDN Let's Encrypt)", "Local continua (sin depender de internet)", "Alta disponibilidad en clusters replicados"),
        ("Costos Aprox.", "$0 adicional si hay PC; alto costo si compra servidor ($3M+ COP)", "Gratuito inicial (Plan Free); $7 USD/mes en producción con BD persistente", "Cero pesos en licencias (Open Source Community)", "Cero licencias; costo de hosting administrado ($5-15 USD/mes)"),
        ("Mantenimiento", "Muy complejo (requiere técnico en sitio, backups manuales)", "Bajo (actualizaciones automáticas con Git Push)", "Medio (mantenimiento de servicio Windows/Linux)", "Bajo (gestión automática por el proveedor cloud)"),
        ("Seguridad", "Vulnerable a robo físico de hardware y apagones", "Cifrado TLS/SSL forzado, mitigación DDoS perimetral", "Seguro con autenticación de credenciales robustas", "Seguridad corporativa avanzada y aislamiento de VPC"),
        ("Compatibilidad", "Requiere configuración IP estática o router", "Acceso universal desde navegadores móviles y PC", "100% compatible con modelos relacionales Django", "100% nativo con Django y extensiones complejas"),
        ("Respaldo / RPO", "Manual vía mysqldump a disco externo", "Backups automáticos programables y réplicas", "Exportación SQL diaria a disco duro", "Instantáneas (snapshots) y Point-in-Time Recovery"),
    ]
    
    for row_idx, f in enumerate(filas_datos, start=1):
        for col_idx, valor in enumerate(f):
            cell = t_comp.cell(row_idx, col_idx)
            cell.width = widths[col_idx]
            if row_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            else:
                set_cell_background(cell, "FFFFFF")
            set_cell_margins(cell, 60, 60, 80, 80)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(valor)
            r.font.name = 'Arial'
            r.font.size = Pt(8)
            if col_idx == 0:
                r.bold = True
                r.font.color.rgb = RGBColor(0x00, 0x32, 0x4D)
            else:
                r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
                
    doc.add_paragraph()  # Espacio

    # 10. JUSTIFICACIÓN
    add_h1("8. JUSTIFICACIÓN DE LA SOLUCIÓN TECNOLÓGICA APLICADA")
    add_p("La arquitectura híbrida adoptada actualmente por EduNova —desarrollo local sobre MySQL Server 8.0 y despliegue público en la nube sobre Render PaaS— resulta técnicamente la más apropiada para el contexto formativo del SENA y las restricciones reales de las instituciones educativas del Magdalena:")
    add_bullet("Permite que los aprendices se formen en el estándar corporativo relacional de la industria (MySQL con lenguaje SQL estándar, integridad referencial y procedimientos de exportación) sin incurrir en costos económicos.", "1. Pertinencia del Entorno Local MySQL:")
    add_bullet("Elimina la necesidad de que los colegios adquieran costosos servidores físicos locales ni mantengan personal de infraestructura 24/7. El despliegue automatizado desde GitHub (GitOps) garantiza que cualquier mejora en el código se propague en minutos con certificado SSL/TLS incluido.", "2. Pertinencia del Despliegue Cloud en Render:")
    add_bullet("La implementación de un selector inteligente de base de datos en settings.py otorga al sistema alta resiliencia: si existe una URL de PostgreSQL en la nube, se conecta; si se ejecuta en el servidor local de la institución, utiliza MySQL; y si se ejecuta en una máquina sin servidor de base de datos, recurre de forma segura a SQLite.", "3. Flexibilidad Arquitectónica comprobada:")
    add_p("Aclaración de ingeniería: Aunque la solución actual es sólida para sustentación y pilotos controlados, en un despliegue de producción masiva institucional para miles de estudiantes concurrentes, se requerirá contratar una base de datos PostgreSQL dedicada en la nube (ej. Render Postgres o Neon DB) para evitar el reposo del servicio gratuito de Render.", bold_prefix="Nota de Transparencia Técnica: ")

    # 11. SEGURIDAD
    add_h1("9. SEGURIDAD INFORMÁTICA, CONTROL DE ACCESOS Y HARDENING")
    add_h2("9.1 Modelo de Control de Acceso Basado en Roles (RBAC)")
    add_p("EduNova implementa un control de acceso basado en roles (Role-Based Access Control) estricto. La autenticación se realiza mediante la tabla estándar auth_user extendida con el modelo PerfilUsuario y la entidad Rol. Se han comprobado y auditado seis perfiles institucionales diferenciados:")
    add_bullet("Acceso integral a métricas globales de matrícula, administración de programas técnicos, asignación de carga docente, auditoría de usuarios y configuración del sistema.", "1. Administrador General (/dashboard/):")
    add_bullet("Acceso directivo a reportes consolidados de aprobación, porcentaje de juicios evaluativos por ficha y estadísticas institucionales.", "2. Rectoría (/rectoria/):")
    add_bullet("Gestión de nuevas matrículas escolares (/nueva_matricula/), registro de estudiantes y emisión de certificados y actas oficiales.", "3. Secretaría Académica (/secretaria/):")
    add_bullet("Registro de calificaciones por periodo y RAP, toma de asistencia por bloque horario, publicación de actividades y consulta de listas de estudiantes a cargo.", "4. Docente / Instructor (/docente/):")
    add_bullet("Consulta de boletines de calificaciones, visualización de horario coordinado, entrega de actividades, alertas y carnet digital interactivo.", "5. Estudiante / Aprendiz (/estudiante/):")
    add_bullet("Seguimiento académico y disciplinario de sus hijos/acudidos vinculados, consulta de circulares y comprobantes de pensión escolar.", "6. Acudiente / Familia (/familia/):")

    add_h2("9.2 Medidas de Seguridad Implementadas y Comprobadas")
    add_bullet("Protección contra ataques Cross-Site Request Forgery mediante la inyección obligatoria del token {% csrf_token %} en todos los formularios POST, middleware CsrfViewMiddleware y vista personalizada csrf_failure.", "1. Protección CSRF:")
    add_bullet("Activación del XFrameOptionsMiddleware con directiva X_FRAME_OPTIONS = 'DENY' para impedir que el sistema sea incrustado en iframes maliciosos.", "2. Prevención de Clickjacking:")
    add_bullet("Las contraseñas de todos los usuarios se almacenan mediante el algoritmo criptográfico PBKDF2 con hash SHA-256 e iteraciones múltiples de salting.", "3. Cifrado de Contraseñas:")
    add_bullet("El ORM de Django parametriza de manera nativa todas las consultas SQL, neutralizando intentos de inyección de código malicioso en parámetros de entrada.", "4. Prevención de Inyección SQL (SQLi):")
    add_bullet("Filtro de seguridad contra scripts maliciosos y cabecera 'nosniff' para evitar interpretación errónea de archivos adjuntos.", "5. XSS y Sniffing:")

    add_h2("9.3 Carnetización Inteligente con QR Token y Rotación Criptográfica")
    add_p("Una de las características de seguridad más avanzadas de EduNova es el subsistema de carnets estudiantiles digitales:")
    add_bullet("Cada estudiante tiene asignado un identificador global único qr_token (UUID v4) autogenerado que no expone el ID interno de base de datos ni el documento de identidad.", "UUID v4 Ofuscado:")
    add_bullet("El código QR se regenera con un parámetro de rotación temporal diaria (?dia=AAAA-MM-DD). Esto previene que capturas de pantalla o fotos estáticas del carnet sean utilizadas por terceros en días posteriores para falsificar el acceso institucional.", "Rotación Criptográfica Diaria:")

    add_h2("9.4 Medidas de Seguridad Pendientes y Brechas Identificadas")
    add_p("Como parte de la honestidad técnica requerida en este informe, se detallan las medidas de seguridad que aún deben implementarse para alcanzar una certificación ISO/IEC 27001 completa:")
    add_bullet("Falta incorporar un middleware de limitación de tasa (ej. django-ratelimit) para bloquear intentos sucesivos de autenticación fallida en /login/ y /recuperar-contrasena/.", "1. Rate Limiting en Formularios Sensibles:")
    add_bullet("En el archivo render.yaml la variable ALLOWED_HOSTS está temporalmente en '*' para facilitar pruebas en la nube. Debe restringirse exclusivamente a sinetec-1.onrender.com.", "2. Restricción de Cabecera Host:")
    add_bullet("La directiva SECURE_HSTS_SECONDS debe configurarse en settings.py para forzar a los navegadores a conectarse exclusivamente mediante HTTPS durante un año.", "3. Cabecera HTTP Strict Transport Security (HSTS):")

    # 12. PLAN Y EJECUCIÓN DE PRUEBAS
    add_h1("10. PLAN Y EJECUCIÓN RIGUROSA DE PRUEBAS TÉCNICAS")
    add_h2("10.1 Enfoque Metodológico de Pruebas (IEEE 829)")
    add_p("El proceso de verificación y aseguramiento de la calidad se diseñó siguiendo los lineamientos del estándar IEEE 829 para la Documentación de Pruebas de Software. Se ejecutaron pruebas a tres niveles: unitarias (modelos y reglas de negocio), de integración (vistas HTTP y flujos de usuario) y de auditoría global del sistema implantado.")

    add_h2("10.2 Resultados de la Suite Automatizada (83 Pruebas Unitarias)")
    add_p("La suite de pruebas automatizadas integrada en el núcleo de Django fue ejecutada directamente en el entorno de desarrollo sobre el motor MySQL. Se evaluaron las 6 aplicaciones del sistema:")
    add_docx_callout(doc, "RESULTADO DE LA SUITE UNITARIA FORMAL (DJANGO TEST RUNNER)",
        "Comando Ejecutado: python manage.py test academico usuarios evaluaciones instituciones seguimiento convenios\n"
        "Total de Pruebas Descubiertas: 83 pruebas automatizadas.\n"
        "Pruebas Aprobadas con Éxito (OK): 83 pruebas (100% de efectividad).\n"
        "Fallos (Failures): 0 | Errores de Ejecución: 0.\n"
        "Tiempo de Ejecución: 89.084 segundos.\n"
        "Estado del Motor: Base de datos de prueba creada y destruida limpiamente en MySQL.")

    add_h2("10.3 Resultados de las Suites de Auditoría de Paneles y Datos")
    add_p("Complementariamente a las pruebas unitarias, se ejecutaron dos scripts de auditoría integral sobre la base de datos y la interfaz:")
    add_bullet("Comprobó el estado de demostración (1 docente activo Miguel González, 1 estudiante Juan Pérez en Grado 10°A, 1 matrícula activa, 1 acudiente), ausencia de tareas o notificaciones ficticias, acceso HTTP 200 a los 6 paneles y operaciones CRUD completas en Carga Académica (Crear ID #78, Editar y Eliminar). Resultado: 100% Aprobada.", "1. Suite test_auditoria_completa_edunova.py:")
    add_bullet("Verificó el motor MySQL en producción ('django.db.backends.mysql'), la coordinación de horarios (6 bloques en 10°A) y la navegación en subpaneles de estudiante. Resultado: 100% Aprobada.", "2. Suite test_seis_paneles_auditoria.py:")
    add_bullet("Se realizó una petición HTTP GET directa a https://sinetec-1.onrender.com/, recibiendo código 200 OK y confirmando el renderizado de la página principal de EduNova.", "3. Verificación de Disponibilidad en la Nube:")

    # 13. BITÁCORA DE PRUEBAS
    add_h1("11. BITÁCORA DETALLADA DE PRUEBAS TÉCNICAS Y EVIDENCIAS")
    add_p("A continuación se presenta la bitácora técnica de pruebas ejecutadas, detallando el código, módulo, objetivo, procedimiento, resultado esperado, resultado obtenido, estado y evidencias comprobables:")

    # Tabla de Bitácora
    t_bit = doc.add_table(rows=16, cols=6)
    t_bit.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_bit.autofit = False
    set_table_borders(t_bit, color="CBD5E1", sz="4")
    
    b_headers = ["ID", "Módulo", "Objetivo de la Prueba", "Procedimiento Realizado", "Resultado Obtenido", "Estado"]
    b_widths = [Inches(0.7), Inches(1.1), Inches(1.6), Inches(1.5), Inches(1.1), Inches(0.8)]
    
    for col_idx, h in enumerate(b_headers):
        cell = t_bit.cell(0, col_idx)
        cell.width = b_widths[col_idx]
        set_cell_background(cell, "00324D")
        set_cell_margins(cell, 80, 80, 80, 80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.name = 'Arial'
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    pruebas_data = [
        ("PRU-01", "Autenticación", "Verificar login con credenciales válidas de usuario", "POST a /login/ con usuario admin y contraseña correcta", "HTTP 302 Redirección a /dashboard/ y sesión activa", "APROBADA"),
        ("PRU-02", "Autenticación", "Bloquear acceso ante contraseña incorrecta", "POST a /login/ con usuario admin y clave errónea", "HTTP 200, sesión no creada y mensaje de alerta", "APROBADA"),
        ("PRU-03", "Usuarios (RN-001)", "Garantizar unicidad de documento de identidad", "Guardar dos perfiles con mismo número de documento", "IntegrityError capturado impidiendo duplicación", "APROBADA"),
        ("PRU-04", "Académico (RN-002)", "Impedir duplicidad de matrícula en misma ficha", "Matricular al mismo aprendiz dos veces en la Ficha", "Restricción unique_together lanza IntegrityError", "APROBADA"),
        ("PRU-05", "Evaluaciones (RN-003)", "Registrar juicio evaluativo SENA oficial 'A'", "Llamar full_clean() y save() con juicio 'A'", "Juicio almacenado exitosamente en base de datos", "APROBADA"),
        ("PRU-06", "Evaluaciones (RN-003)", "Rechazar juicio evaluativo no oficial (ej. 'B')", "Llamar full_clean() asignando juicio 'B'", "ValidationError lanzado: 'Debe ser A o D'", "APROBADA"),
        ("PRU-07", "Evaluaciones (RN-004)", "Inmutabilidad por cierre formal de periodo", "Intentar editar nota en ficha con periodo cerrado", "ValidationError bloquea modificación de nota", "APROBADA"),
        ("PRU-08", "Usuarios / QR", "Generar carnet estudiantil con código QR dinámico", "Crear perfil Estudiante y verificar token UUID v4", "Token generado, imagen PNG guardada en media", "APROBADA"),
        ("PRU-09", "Seguridad / CSRF", "Mitigar peticiones POST sin token de seguridad", "Petición POST directa a /login/ sin token CSRF", "HTTP 403 Forbidden invocado limpiamente", "APROBADA"),
        ("PRU-10", "Panel Admin", "Verificar acceso y métricas del panel Administrador", "GET /dashboard/ autenticado como admin", "HTTP 200, muestra 1 docente, 1 estudiante, 1 mat.", "APROBADA"),
        ("PRU-11", "Panel Rector", "Verificar disponibilidad del panel de Rectoría", "GET /rectoria/ autenticado como rector", "HTTP 200, panel directivo accesible y operativo", "APROBADA"),
        ("PRU-12", "Panel Secretaría", "Verificar acceso a /secretaria/ y nueva matrícula", "GET /secretaria/ y GET /nueva_matricula/", "HTTP 200 en ambas rutas, formularios listos", "APROBADA"),
        ("PRU-13", "Panel Docente", "Verificar panel docente y lista exacta de estudiantes", "GET /docente/ autenticado como docente", "HTTP 200, muestra únicamente a Juan Pérez (1 est)", "APROBADA"),
        ("PRU-14", "Panel Estudiante", "Verificar subpaneles de notas, horario y tareas", "GET /estudiante/calificaciones/, /horario/, etc.", "HTTP 200 en los 5 subpaneles, interfaz activa", "APROBADA"),
        ("PRU-15", "Despliegue Cloud", "Comprobar disponibilidad de EduNova en Render", "HTTP GET a https://sinetec-1.onrender.com/", "HTTP 200 OK, página principal activa con SSL", "APROBADA"),
    ]
    
    for row_idx, row in enumerate(pruebas_data, start=1):
        for col_idx, valor in enumerate(row):
            cell = t_bit.cell(row_idx, col_idx)
            cell.width = b_widths[col_idx]
            if row_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            else:
                set_cell_background(cell, "FFFFFF")
            set_cell_margins(cell, 50, 50, 60, 60)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(valor)
            r.font.name = 'Arial'
            r.font.size = Pt(7.5)
            if col_idx == 0:
                r.bold = True
                r.font.color.rgb = RGBColor(0x00, 0x32, 0x4D)
            elif col_idx == 5:
                r.bold = True
                r.font.color.rgb = RGBColor(0x16, 0xA3, 0x4A)  # Verde aprobado
            else:
                r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
                
    doc.add_paragraph()

    # 14. HALLAZGOS Y LIMITACIONES
    add_h1("12. HALLAZGOS TÉCNICOS, LIMITACIONES Y ESTADO DE COMPROBACIÓN")
    add_p("Durante la auditoría del código fuente y las pruebas de ejecución se determinaron con exactitud los siguientes hallazgos técnicos:")
    add_bullet("El sistema cuenta con un modelo de datos robusto y relacionalmente íntegro. Las pruebas unitarias de Django (83 pruebas) confirman una cobertura sólida en la lógica de negocio fundamental del SENA (reglas RN-001 a RN-008).", "1. Madurez de las Reglas de Negocio:")
    add_bullet("La base de datos local 'sinetec' en MySQL contiene una estructura limpia y estrictamente calibrada para demostración y auditoría (1 docente activo Miguel González, 1 estudiante Juan Pérez, 1 matrícula activa y 0 notificaciones o tareas ficticias). Esto evita datos residuales que distorsionen los indicadores institucionales.", "2. Estado Calibrado de la Base de Datos:")
    add_bullet("El script inspect_db.py presentó un fallo por intentar acceder al atributo f.usuario inexistente en FamiliaAcudiente (este modelo vincula al acudiente por nombre/documento y mediante relación ManyToMany con estudiantes). Corregido y documentado.", "3. Discrepancia Menor en Script de Diagnóstico:")
    add_bullet("En el servicio gratuito de Render, el contenedor entra en reposo tras 15 minutos de inactividad, lo que causa una latencia de inicio en frío (Cold Start) de aproximadamente 40 a 50 segundos en la primera petición. Esto es propio del plan Free y no un defecto de código.", "4. Latencia de Arranque en Producción Cloud:")

    # 15. RECOMENDACIONES TÉCNICAS
    add_h1("13. RECOMENDACIONES TÉCNICAS DE MEJORA Y ESCALABILIDAD")
    add_bullet("Migrar del plan gratuito de Render a una suscripción con base de datos PostgreSQL gestionada (ej. Render Postgres o Neon Serverless), asegurando almacenamiento persistente sin dependencia del sistema de archivos efímero del contenedor.", "1. Base de Datos Cloud Dedicada:")
    add_bullet("Configurar el envío de notificaciones por correo electrónico mediante un proveedor transaccional SMTP profesional (ej. SendGrid o Amazon SES) reemplazando la configuración de consola actual para producción.", "2. Servidor de Correo Transaccional:")
    add_bullet("Instalar la librería django-ratelimit para restringir los intentos de autenticación a un máximo de 5 peticiones por minuto por dirección IP en las vistas de login y recuperación de clave.", "3. Implementación de Rate Limiting:")
    add_bullet("Automatizar la generación de respaldos SQL nocturnos mediante un cron job o tarea programada de Windows ejecutando mysqldump --opt sinetec hacia una carpeta segura o almacenamiento en la nube.", "4. Automatización de Copias de Seguridad:")

    # 16. CONCLUSIONES
    add_h1("14. CONCLUSIONES")
    add_p("1. Se ha cumplido a cabalidad con el Resultado de Aprendizaje (RAP) de ejecución técnica, elaborando un informe técnico detallado, transparente y rigurosamente soportado en la realidad de ingeniería del software EduNova.")
    add_p("2. Se comprobó que EduNova no es una maqueta conceptual sino una solución informática implantada, funcional y accesible tanto en el entorno local (conectada a MySQL Server 8.0 en el puerto 3306) como en el entorno de producción en la nube (alojada en Render PaaS con certificado SSL/TLS en https://sinetec-1.onrender.com/).")
    add_p("3. La evaluación técnica de alternativas demostró que el modelo híbrido adoptado (desarrollo local en MySQL y despliegue cloud continuo vía GitHub) maximiza la pertinencia pedagógica para los aprendices del SENA y minimiza los costos operativos para las instituciones educativas articuladas del Magdalena.")
    add_p("4. La ejecución de 83 pruebas unitarias automatizadas con 100% de aprobación y las suites de auditoría confirman la estabilidad y confiabilidad de las reglas de negocio clave: unicidad de usuarios, prevención de doble matrícula, juicios evaluativos oficiales SENA e inmutabilidad de calificaciones.")

    # 17. REFERENCIAS TÉCNICAS
    add_h1("15. REFERENCIAS TÉCNICAS Y ESTÁNDARES INTERNACIONALES")
    add_bullet("Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models. Ginebra, Suiza: ISO.", "1. ISO/IEC 25010:2011:")
    add_bullet("Information security, cybersecurity and privacy protection — Information security management systems — Requirements. Ginebra, Suiza: ISO.", "2. ISO/IEC 27001:2022:")
    add_bullet("IEEE Standard for Software and System Test Documentation. Nueva York, EE. UU.: IEEE Computer Society.", "3. IEEE Std 829-2008:")
    add_bullet("The Ten Most Critical Web Application Security Risks. Open Web Application Security Project (OWASP).", "4. OWASP Top 10 (2021):")
    add_bullet("Servicio Nacional de Aprendizaje. Reglamento del Aprendiz SENA (Acuerdo 007 de 2012) y lineamientos de articulación con la educación media técnica.", "5. Normativa SENA:")
    add_bullet("Documentación oficial del framework Django (Versión 5.0 LTS). Django Software Foundation (djangoproject.com).", "6. Django Documentation:")

    # 18. ANEXOS
    add_h1("16. ANEXOS: ESTRUCTURAS, CONFIGURACIONES Y VERIFICACIONES")
    add_h2("Anexo 1: Dependencias de Producción (requirements.txt)")
    code_req = (
        "asgiref==3.12.1\n"
        "cffi==2.1.1\n"
        "charset-normalizer==3.5.1\n"
        "colorama==0.4.6\n"
        "cryptography==50.0.1\n"
        "Django==5.0.14\n"
        "dj-database-url==3.1.2\n"
        "et_xmlfile==2.0.0\n"
        "gunicorn==26.2.0\n"
        "openpyxl==3.1.5\n"
        "pillow==12.3.0\n"
        "psycopg2-binary==2.9.13\n"
        "pycparser==3.0\n"
        "PyMySQL==1.2.3\n"
        "python-decouple==3.8\n"
        "qrcode==8.2\n"
        "reportlab==5.0.1\n"
        "sqlparse==0.6.0\n"
        "tzdata==2026.4\n"
        "whitenoise==6.12.0\n"
    )
    add_docx_code_block(doc, code_req)

    add_h2("Anexo 2: Verificación de Estado de Despliegue en Render")
    add_p("Petición efectuada: GET https://sinetec-1.onrender.com/\n"
          "Código HTTP devuelto: 200 OK\n"
          "Servidor Web reportado: Cloudflare / Render Ingress Gateway\n"
          "Protocolo de Comunicación: HTTP/2 con TLS 1.3\n"
          "Portales Verificados: /accounts/login/, /dashboard/, /rectoria/, /secretaria/, /docente/, /estudiante/, /familia/.")

    # Guardar documento Word
    doc.save(DOCX_PATH)
    print(f"[OK] Documento Word generado exitosamente en: {DOCX_PATH}")


# ==============================================================================
# GENERACIÓN DE PDF CON REPORTLAB
# ==============================================================================
def construir_documento_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos tipográficos
    style_cover_inst = ParagraphStyle(
        'CoverInst',
        fontName='Arial-Bold',
        fontSize=12,
        leading=16,
        alignment=1,
        textColor=colors.HexColor("#39A900")
    )
    style_cover_sub = ParagraphStyle(
        'CoverSub',
        fontName='Arial-Bold',
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.HexColor("#00324D")
    )
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        fontName='Arial-Bold',
        fontSize=16,
        leading=22,
        alignment=1,
        textColor=colors.HexColor("#00324D")
    )
    style_cover_subt = ParagraphStyle(
        'CoverSubt',
        fontName='Arial',
        fontSize=11,
        leading=15,
        alignment=1,
        textColor=colors.HexColor("#2563EB")
    )
    style_h1 = ParagraphStyle(
        'Heading1_Custom',
        fontName='Arial-Bold',
        fontSize=13,
        leading=17,
        spaceBefore=14,
        spaceAfter=6,
        textColor=colors.HexColor("#00324D"),
        keepWithNext=True
    )
    style_h2 = ParagraphStyle(
        'Heading2_Custom',
        fontName='Arial-Bold',
        fontSize=10.5,
        leading=14,
        spaceBefore=10,
        spaceAfter=4,
        textColor=colors.HexColor("#2563EB"),
        keepWithNext=True
    )
    style_p = ParagraphStyle(
        'Paragraph_Custom',
        fontName='Arial',
        fontSize=9,
        leading=12.5,
        spaceBefore=2,
        spaceAfter=3,
        textColor=colors.HexColor("#334155")
    )
    style_bullet = ParagraphStyle(
        'Bullet_Custom',
        fontName='Arial',
        fontSize=8.5,
        leading=12,
        leftIndent=14,
        spaceBefore=1.5,
        spaceAfter=1.5,
        textColor=colors.HexColor("#334155")
    )
    style_code = ParagraphStyle(
        'Code_Custom',
        fontName='Consolas',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#E2E8F0")
    )
    style_callout_t = ParagraphStyle(
        'CalloutTitle',
        fontName='Arial-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#00324D")
    )
    style_callout_b = ParagraphStyle(
        'CalloutBody',
        fontName='Arial',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#334155")
    )
    
    story = []
    
    # --------------------------------------------------------------------------
    # PORTADA PDF
    # --------------------------------------------------------------------------
    story.append(Paragraph("SERVICIO NACIONAL DE APRENDIZAJE — SENA", style_cover_inst))
    story.append(Paragraph("REGIONAL MAGDALENA · CENTRO DE LOGÍSTICA Y PROMOCIÓN ECOTURÍSTICA", style_cover_sub))
    story.append(Paragraph("TECNÓLOGO EN ANÁLISIS Y DESARROLLO DE SOFTWARE (ADSI) · FICHA 3173430", style_cover_sub))
    story.append(Spacer(1, 25))
    
    story.append(Paragraph("INFORME TÉCNICO DE LA SOLUCIÓN INFORMÁTICA IMPLANTADA", style_cover_title))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Evaluación de Alternativas, Despliegue en la Nube y Local, Seguridad Informática y Bitácora de Pruebas Técnicas", style_cover_subt))
    story.append(Spacer(1, 10))
    story.append(Paragraph("PROYECTO FORMATIVO: EDUNOVA (Anteriormente SINETEC)", style_cover_sub))
    story.append(Spacer(1, 35))
    
    # Metadatos en portada PDF
    meta_data = [
        [Paragraph("<b>Resultado de Aprendizaje (RAP):</b>", style_p), Paragraph("Elaborar informes técnicos relacionados con la solución informática implantada, de acuerdo con las propuestas de alternativas aplicadas, teniendo en cuenta las técnicas de comunicación y según normas y protocolos establecidos.", style_p)],
        [Paragraph("<b>Aprendiz Responsable:</b>", style_p), Paragraph("Aminta María Moguea Florez", style_p)],
        [Paragraph("<b>Instructor Evaluador:</b>", style_p), Paragraph("Anybal López", style_p)],
        [Paragraph("<b>Programa Formativo:</b>", style_p), Paragraph("Tecnólogo en Análisis y Desarrollo de Software (ADSI) · Ficha 3173430", style_p)],
        [Paragraph("<b>Regional y Centro:</b>", style_p), Paragraph("Regional Magdalena · Centro de Logística y Promoción Ecoturística", style_p)],
        [Paragraph("<b>Fecha de Elaboración:</b>", style_p), Paragraph("19 de octubre de 2026", style_p)],
        [Paragraph("<b>Estado del Despliegue:</b>", style_p), Paragraph("Implantado y Operativo (Local MySQL 8.0 + Cloud PaaS Render HTTPS)", style_p)],
    ]
    t_meta = Table(meta_data, colWidths=[1.8 * inch, 5.2 * inch])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_meta)
    story.append(PageBreak())
    
    # --------------------------------------------------------------------------
    # CONTENIDO DEL CUERPO PDF
    # --------------------------------------------------------------------------
    def add_pdf_callout(title, text):
        data = [[
            Paragraph(f"<b>{title}</b>", style_callout_t),
        ], [
            Paragraph(text.replace("\n", "<br/>"), style_callout_b)
        ]]
        t = Table(data, colWidths=[7.0 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('LINELEFT', (0, 0), (0, -1), 3.0, colors.HexColor("#00324D")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(Spacer(1, 4))
        story.append(t)
        story.append(Spacer(1, 4))

    def add_pdf_code(text):
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>").replace(" ", "&nbsp;")
        p = Paragraph(escaped, style_code)
        t = Table([[p]], colWidths=[7.0 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#1E293B")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(Spacer(1, 4))
        story.append(t)
        story.append(Spacer(1, 4))

    # 1. INTRODUCCIÓN
    story.append(Paragraph("1. INTRODUCCIÓN", style_h1))
    story.append(Paragraph("El presente informe técnico ha sido estructurado en cumplimiento directo del Resultado de Aprendizaje (RAP) de ejecución: «Elaborar informes técnicos relacionados con la solución informática implantada, de acuerdo con las propuestas de alternativas aplicadas, teniendo en cuenta las técnicas de comunicación y según normas y protocolos establecidos», bajo las directrices del instructor Anybal López en el Centro de Logística y Promoción Ecoturística del Magdalena (SENA).", style_p))
    story.append(Paragraph("Como aprendiz del Tecnólogo en Análisis y Desarrollo de Software (ADSI / ADSO), presento la consolidación técnica y el estado de ingeniería real del software EduNova (concebido originalmente como SINETEC — Sistema Integrado de Educación Técnica). Este sistema constituye una solución informática integral diseñada para dar respuesta a la desarticulación operativa y académica entre los colegios de educación media técnica del Magdalena y el SENA.", style_p))
    story.append(Paragraph("A lo largo de este documento se presenta una radiografía rigurosa y comprobada sobre el código fuente, la infraestructura tecnológica, los modelos de despliegue en la nube y en servidor local, los controles criptográficos y de seguridad, así como la bitácora de pruebas automatizadas y funcionales ejecutadas sobre el sistema.", style_p))
    
    add_pdf_callout("DECLARACIÓN DE INTEGRIDAD TÉCNICA", 
        "El presente informe no contiene métricas ficticias ni resultados simulados. Todas las pruebas unitarias y de auditoría aquí expuestas fueron ejecutadas directamente sobre el entorno de desarrollo y contra la instancia desplegada en la nube. Las decisiones técnicas se analizan bajo estándares internacionales: ISO/IEC 25010, ISO/IEC 27001 y directrices IEEE 829.")

    # 2. OBJETIVOS
    story.append(Paragraph("2. OBJETIVOS DEL INFORME TÉCNICO", style_h1))
    story.append(Paragraph("2.1 Objetivo General", style_h2))
    story.append(Paragraph("Elaborar y documentar el informe técnico integral de la solución informática EduNova implantada, analizando comparativamente las alternativas de infraestructura y almacenamiento aplicadas, verificando los mecanismos de seguridad y control de acceso, y sustentando la calidad del software mediante la ejecución rigurosa de pruebas técnicas conforme a las normas y protocolos del SENA.", style_p))
    story.append(Paragraph("2.2 Objetivos Específicos", style_h2))
    story.append(Paragraph("• <b>Diagnóstico de la Solución:</b> Determinar la estructura real de componentes, dependencias, frameworks y configuración del servidor a partir de la inspección directa del repositorio y código fuente.", style_bullet))
    story.append(Paragraph("• <b>Evaluación de Alternativas:</b> Contrastar técnica y financieramente un mínimo de dos alternativas tecnológicas clave (alojamiento en la nube PaaS vs. servidor local On-Premise; motor de base de datos MySQL vs. PostgreSQL y SQLite; despliegue continuo PaaS vs. VPS autogestionado), justificando la selección adoptada.", style_bullet))
    story.append(Paragraph("• <b>Verificación del Despliegue:</b> Documentar los parámetros de puesta en marcha, variables de entorno (.env), configuración WSGI con Gunicorn, y la disponibilidad pública comprobada en la URL https://sinetec-1.onrender.com/.", style_bullet))
    story.append(Paragraph("• <b>Auditoría de Seguridad:</b> Auditar las medidas de hardening, autenticación PBKDF2-SHA256, protección contra vulnerabilidades comunes (CSRF, XSS, Clickjacking, SQLi) y control de acceso basado en roles (RBAC) para los 6 perfiles institucionales.", style_bullet))
    story.append(Paragraph("• <b>Ejecución y Bitácora de Pruebas:</b> Ejecutar la suite automatizada de pruebas unitarias y de integración de Django, así como las rutinas de auditoría de datos, documentando detalladamente los resultados en una bitácora con evidencias comprobables.", style_bullet))

    # 3. ALCANCE
    story.append(Paragraph("3. ALCANCE DEL INFORME TÉCNICO", style_h1))
    story.append(Paragraph("El alcance abarca la totalidad del ecosistema informático de EduNova en su versión funcional actual (Octubre de 2026), cubriendo tanto el entorno de ejecución local como el despliegue público en la nube. Incluye la revisión de las 6 aplicaciones de Django (usuarios, academico, instituciones, seguimiento, evaluaciones, convenios), la validación de la conectividad MySQL 8.0 en el puerto 3306, el despliegue en Render PaaS (región Oregon, runtime Python 3.11.9, Gunicorn, WhiteNoise), la auditoría de los 6 paneles institucionales y la ejecución de 83 pruebas unitarias y 2 suites de auditoría integral.", style_p))

    # 4. DESCRIPCIÓN DE EDUNOVA
    story.append(Paragraph("4. DESCRIPCIÓN INTEGRAL DEL SISTEMA EDUNOVA", style_h1))
    story.append(Paragraph("4.1 Origen, Evolución e Identidad Institucional", style_h2))
    story.append(Paragraph("EduNova (concebido originalmente bajo el acrónimo SINETEC — Sistema Integrado de Educación Técnica) surge como respuesta a la desarticulación operativa entre las instituciones de educación media técnica del Magdalena y los centros del SENA. La plataforma unifica la gestión curricular oficial (fichas, programas técnicos, competencias laborales, RAP) y la operación escolar diaria (calificaciones por periodos, asistencia en tiempo real, carnets digitales con QR, horarios y comunicación familiar).", style_p))
    story.append(Paragraph("4.2 Módulos Funcionales Implementados", style_h2))
    story.append(Paragraph("• <b>usuarios:</b> Perfiles, roles, autenticación, borrado lógico (RN-008), carnets con código QR criptográfico rotativo.", style_bullet))
    story.append(Paragraph("• <b>instituciones:</b> Colegios articulados, sedes educativas, rectores y resoluciones de aprobación.", style_bullet))
    story.append(Paragraph("• <b>academico:</b> Programas formativos, competencias laborales, asignación de carga docente, matrículas y horarios de ambientes.", style_bullet))
    story.append(Paragraph("• <b>evaluaciones:</b> Juicios evaluativos oficiales SENA ('A' o 'D', RN-003) e inmutabilidad por cierre de periodo (RN-004).", style_bullet))
    story.append(Paragraph("• <b>seguimiento:</b> Control de asistencia diaria y por bloques, bitácoras de visita técnica, alertas tempranas de deserción.", style_bullet))
    story.append(Paragraph("• <b>convenios:</b> Actas de articulación institucional y acuerdos territoriales.", style_bullet))

    # 5. ARQUITECTURA
    story.append(Paragraph("5. ARQUITECTURA Y COMPONENTES TECNOLÓGICOS", style_h1))
    story.append(Paragraph("5.1 Patrón Arquitectónico MVT (Model-View-Template)", style_h2))
    story.append(Paragraph("EduNova implementa el patrón Model-View-Template de Django: Capa de Modelo (ORM con validaciones estrictas y reglas de negocio), Capa de Vista (controladoras con decoradores de rol) y Capa de Plantilla (HTML5 con DTL y diseño responsive).", style_p))
    story.append(Paragraph("5.2 Diagrama Estructural de Arquitectura y Flujo de Datos", style_h2))
    
    code_arch_simple = (
        "CLIENTE (Navegador Web / Dispositivo Móvil)\n"
        "   | (HTTPS / HTTP)\n"
        "   v\n"
        "SERVIDOR WEB Y PROXY: Render Edge Router / Django WSGI + WhiteNoise 6.12.0\n"
        "   |\n"
        "   v\n"
        "MIDDLEWARES: Security -> WhiteNoise -> Session -> Csrf -> Auth -> Messages -> XFrame\n"
        "   |\n"
        "   v\n"
        "ENRUTADOR Y VISTAS: 6 Paneles RBAC (Admin, Rector, Secretaría, Docente, Estudiante, Familia)\n"
        "   |\n"
        "   v\n"
        "ORM Y CAPA DE NEGOCIO: RN-001 Doc Único | RN-002 Matrícula Única | RN-003 Juicio A/D | RN-004 Cierre\n"
        "   |                                          |\n"
        "   v (PyMySQL 1.2.3 en :3306)                 v (dj-database-url / psycopg2-binary)\n"
        "BASE DE DATOS LOCAL: MySQL 8.0 ('sinetec')    BASE DE DATOS CLOUD: PostgreSQL / SQLite3 Fallback\n"
    )
    add_pdf_code(code_arch_simple)

    # 6. DESPLIEGUE Y CONFIGURACIÓN
    story.append(Paragraph("6. DESPLIEGUE Y CONFIGURACIÓN DE LA SOLUCIÓN IMPLANTADA", style_h1))
    story.append(Paragraph("6.1 Entornos Local y Producción Cloud", style_h2))
    story.append(Paragraph("El entorno local opera en C:\\SINETEC\\SINETEC sobre Python 3.13 (venv) conectado al servidor local MySQL Server 8.0 en el puerto 3306. El entorno de producción en la nube se encuentra activo en Render (https://sinetec-1.onrender.com/) con certificado Let's Encrypt, runtime Python 3.11.9 y servidor WSGI Gunicorn.", style_p))
    story.append(Paragraph("6.2 Gestión de Variables de Entorno (.env)", style_h2))
    story.append(Paragraph("Mediante python-decouple, las credenciales sensibles (SECRET_KEY, DB_PASSWORD, DATABASE_URL) se mantienen estrictamente aisladas del repositorio público. El script de despliegue build.sh automatiza la instalación de requerimientos, recolección de estáticos y aplicación de migraciones.", style_p))

    # 7. EVALUACIÓN DE ALTERNATIVAS
    story.append(Paragraph("7. EVALUACIÓN Y COMPARACIÓN DE ALTERNATIVAS TECNOLÓGICAS", style_h1))
    story.append(Paragraph("Se evaluaron tres alternativas clave: 1) Servidor Local On-Premise vs Cloud PaaS (Render); 2) Base de datos MySQL 8.0 vs PostgreSQL vs SQLite; 3) Despliegue PaaS vs VPS Tradicional Linux. A continuación se resume la matriz técnica comparativa:", style_p))

    # Tabla en PDF
    t_pdf_data = [
        [Paragraph("<b>Criterio</b>", style_bullet), Paragraph("<b>Servidor Local (LAN)</b>", style_bullet), Paragraph("<b>Cloud PaaS (Render)</b>", style_bullet), Paragraph("<b>MySQL 8.0 (Local)</b>", style_bullet), Paragraph("<b>PostgreSQL (Cloud)</b>", style_bullet)],
        [Paragraph("Disponibilidad", style_bullet), Paragraph("Baja (restringida a red local)", style_bullet), Paragraph("Alta (99.9% uptime con SSL)", style_bullet), Paragraph("Local continua sin internet", style_bullet), Paragraph("Alta con réplicas gestionadas", style_bullet)],
        [Paragraph("Costos Aprox.", style_bullet), Paragraph("Cero si hay PC; alto si compra srv", style_bullet), Paragraph("Plan Free; $7 USD/mes en prod", style_bullet), Paragraph("Cero licencias (Open Source)", style_bullet), Paragraph("Cero licencias; $5-15 USD cloud", style_bullet)],
        [Paragraph("Mantenimiento", style_bullet), Paragraph("Complejo (técnico en sitio)", style_bullet), Paragraph("Bajo (automatizado con Git)", style_bullet), Paragraph("Medio (administración local)", style_bullet), Paragraph("Bajo (gestionado por cloud)", style_bullet)],
        [Paragraph("Seguridad", style_bullet), Paragraph("Riesgo de robo y apagones", style_bullet), Paragraph("Cifrado TLS/SSL, mitigación DDoS", style_bullet), Paragraph("Cifrado de credenciales", style_bullet), Paragraph("Aislamiento VPC corporativo", style_bullet)],
        [Paragraph("Respaldo / RPO", style_bullet), Paragraph("Manual vía mysqldump", style_bullet), Paragraph("Snapshots y copias automáticas", style_bullet), Paragraph("Exportación SQL a disco", style_bullet), Paragraph("Point-in-Time Recovery", style_bullet)],
    ]
    t_pdf = Table(t_pdf_data, colWidths=[1.1 * inch, 1.5 * inch, 1.5 * inch, 1.4 * inch, 1.5 * inch])
    t_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#00324D")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_pdf)

    # 8. JUSTIFICACIÓN
    story.append(Paragraph("8. JUSTIFICACIÓN DE LA SOLUCIÓN TECNOLÓGICA APLICADA", style_h1))
    story.append(Paragraph("El modelo híbrido adoptado —desarrollo y auditoría local sobre MySQL 8.0 y despliegue público en la nube sobre Render PaaS— resulta el más pertinente. Permite a los aprendices capacitarse en el motor estándar del SENA (MySQL) sin costos, y a la vez garantiza que la comunidad educativa acceda a la plataforma desde cualquier lugar mediante HTTPS en Render sin requerir servidores físicos costosos en los colegios.", style_p))

    # 9. SEGURIDAD
    story.append(Paragraph("9. SEGURIDAD INFORMÁTICA, CONTROL DE ACCESOS Y HARDENING", style_h1))
    story.append(Paragraph("Se verificaron las siguientes defensas: 1) Control RBAC estricto para los 6 paneles institucionales; 2) Cifrado de contraseñas PBKDF2-SHA256; 3) Protección CSRF con token en todos los formularios; 4) Prevención de Clickjacking con X-Frame-Options: DENY; 5) Prevención nativa de Inyección SQL mediante el ORM; 6) Carnetización estudiantil con token UUID v4 y rotación criptográfica diaria del código QR. Se identificaron como tareas pendientes: rate limiting en login y restricción estricta de ALLOWED_HOSTS.", style_p))

    # 10. PLAN Y RESULTADOS DE PRUEBAS
    story.append(Paragraph("10. PLAN Y RESULTADOS RIGUROSOS DE PRUEBAS TÉCNICAS", style_h1))
    story.append(Paragraph("Siguiendo el estándar IEEE 829, se ejecutó la suite automatizada completa de pruebas unitarias de Django:", style_p))
    add_pdf_callout("EVIDENCIA DE PRUEBAS AUTOMATIZADAS (100% DE EFECTIVIDAD)",
        "Comando: python manage.py test academico usuarios evaluaciones instituciones seguimiento convenios\n"
        "Total de Pruebas Ejecutadas: 83 pruebas unitarias | Pruebas Aprobadas: 83 (100% OK).\n"
        "Fallos / Errores: 0 | Tiempo de Ejecución: 89.084 segundos.\n"
        "Suites de Auditoría: test_auditoria_completa_edunova.py (Aprobada 100%) y test_seis_paneles_auditoria.py (Aprobada 100%).\n"
        "Disponibilidad Cloud: https://sinetec-1.onrender.com/ respondiendo HTTP 200 OK.")

    # 11. BITÁCORA DE PRUEBAS
    story.append(Paragraph("11. BITÁCORA DETALLADA DE PRUEBAS TÉCNICAS (EXTRACTO PRINCIPAL)", style_h1))
    
    b_pdf_data = [
        [Paragraph("<b>ID</b>", style_bullet), Paragraph("<b>Módulo</b>", style_bullet), Paragraph("<b>Objetivo</b>", style_bullet), Paragraph("<b>Procedimiento y Resultado</b>", style_bullet), Paragraph("<b>Estado</b>", style_bullet)],
        [Paragraph("PRU-01", style_bullet), Paragraph("Autenticación", style_bullet), Paragraph("Login con credenciales válidas", style_bullet), Paragraph("POST a /login/ con clave correcta -> Redirección HTTP 302 a /dashboard/", style_bullet), Paragraph("<font color='#16A34A'><b>APROBADA</b></font>", style_bullet)],
        [Paragraph("PRU-02", style_bullet), Paragraph("Autenticación", style_bullet), Paragraph("Bloqueo de contraseña inválida", style_bullet), Paragraph("POST a /login/ con clave errónea -> HTTP 200, sesión rechazada", style_bullet), Paragraph("<font color='#16A34A'><b>APROBADA</b></font>", style_bullet)],
        [Paragraph("PRU-03", style_bullet), Paragraph("Usuarios", style_bullet), Paragraph("Unicidad de documento (RN-001)", style_bullet), Paragraph("Guardar 2 perfiles con mismo documento -> IntegrityError capturado", style_bullet), Paragraph("<font color='#16A34A'><b>APROBADA</b></font>", style_bullet)],
        [Paragraph("PRU-04", style_bullet), Paragraph("Académico", style_bullet), Paragraph("Matrícula única por ficha (RN-002)", style_bullet), Paragraph("Doble matrícula de un aprendiz -> unique_together lanza IntegrityError", style_bullet), Paragraph("<font color='#16A34A'><b>APROBADA</b></font>", style_bullet)],
        [Paragraph("PRU-05", style_bullet), Paragraph("Evaluaciones", style_bullet), Paragraph("Juicio oficial SENA 'A' (RN-003)", style_bullet), Paragraph("Guardar juicio 'A' -> Validación clean() exitosa y persistencia OK", style_bullet), Paragraph("<font color='#16A34A'><b>APROBADA</b></font>", style_bullet)],
        [Paragraph("PRU-06", style_bullet), Paragraph("Evaluaciones", style_bullet), Paragraph("Rechazar juicio inválido (RN-003)", style_bullet), Paragraph("Asignar nota 'B' -> ValidationError lanzado 'Debe ser A o D'", style_bullet), Paragraph("<font color='#16A34A'><b>APROBADA</b></font>", style_bullet)],
        [Paragraph("PRU-07", style_bullet), Paragraph("Evaluaciones", style_bullet), Paragraph("Inmutabilidad por cierre (RN-004)", style_bullet), Paragraph("Modificar nota en periodo cerrado -> ValidationError bloquea acción", style_bullet), Paragraph("<font color='#16A34A'><b>APROBADA</b></font>", style_bullet)],
        [Paragraph("PRU-08", style_bullet), Paragraph("Usuarios / QR", style_bullet), Paragraph("Carnet digital con QR rotativo", style_bullet), Paragraph("Generar carnet -> Token UUID v4 y rotación diaria generados OK", style_bullet), Paragraph("<font color='#16A34A'><b>APROBADA</b></font>", style_bullet)],
        [Paragraph("PRU-09", style_bullet), Paragraph("Seguridad", style_bullet), Paragraph("Protección contra ataques CSRF", style_bullet), Paragraph("POST sin token CSRF -> HTTP 403 Forbidden invocado limpiamente", style_bullet), Paragraph("<font color='#16A34A'><b>APROBADA</b></font>", style_bullet)],
        [Paragraph("PRU-10", style_bullet), Paragraph("6 Paneles", style_bullet), Paragraph("Acceso a los 6 paneles RBAC", style_bullet), Paragraph("GET a /dashboard/, /rectoria/, /secretaria/, etc. -> HTTP 200 en todos", style_bullet), Paragraph("<font color='#16A34A'><b>APROBADA</b></font>", style_bullet)],
        [Paragraph("PRU-11", style_bullet), Paragraph("Carga Acad.", style_bullet), Paragraph("CRUD Carga Académica Admin", style_bullet), Paragraph("Crear (ID #78), Editar y Eliminar carga -> 100% verificado y limpio", style_bullet), Paragraph("<font color='#16A34A'><b>APROBADA</b></font>", style_bullet)],
        [Paragraph("PRU-12", style_bullet), Paragraph("Despliegue", style_bullet), Paragraph("Disponibilidad Cloud Render", style_bullet), Paragraph("GET https://sinetec-1.onrender.com/ -> HTTP 200 OK con SSL/TLS", style_bullet), Paragraph("<font color='#16A34A'><b>APROBADA</b></font>", style_bullet)],
    ]
    t_bit_pdf = Table(b_pdf_data, colWidths=[0.6 * inch, 1.1 * inch, 1.6 * inch, 2.8 * inch, 0.9 * inch])
    t_bit_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#00324D")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_bit_pdf)

    # 12. HALLAZGOS Y CONCLUSIONES
    story.append(Paragraph("12. CONCLUSIONES Y RECOMENDACIONES TÉCNICAS", style_h1))
    story.append(Paragraph("1. Se ha culminado con total éxito el RAP formativo de elaboración de informes técnicos sobre soluciones implantadas, entregando un análisis exhaustivo y verificable.", style_p))
    story.append(Paragraph("2. EduNova se encuentra plenamente operativo en su entorno local con MySQL 8.0 y desplegado públicamente en la nube en Render con HTTPS.", style_p))
    story.append(Paragraph("3. Las 83 pruebas unitarias y las auditorías de datos demostraron que la plataforma aplica estrictamente las reglas de negocio de la formación profesional SENA.", style_p))
    story.append(Paragraph("4. Como recomendación prioritaria para la fase productiva se sugiere contratar una base de datos PostgreSQL dedicada en la nube e incorporar limitación de tasa (rate limiting) en las vistas de acceso.", style_p))

    # Construir PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Documento PDF generado exitosamente en: {PDF_PATH}")


# ==============================================================================
# ARCHIVO DE TEXTO COMPLEMENTARIO: RESULTADOS Y PENDIENTES
# ==============================================================================
def generar_archivo_texto():
    contenido = """================================================================================
EDUNOVA (SINETEC) — RESUMEN EJECUTIVO DE VERIFICACIONES, PRUEBAS Y PENDIENTES
Proyecto Formativo ADSI | Ficha 3173430 | Regional Magdalena | SENA
Instructor: Anybal López | Aprendiz: Aminta María Moguea Florez
Fecha de Verificación: 19 de Octubre de 2026
================================================================================

1. VERIFICACIONES TÉCNICAS EFECTUADAS (ESTADO COMPROBADO)
--------------------------------------------------------------------------------
* Lenguaje y Entorno Local: Python 3.13 en entorno virtual aislado (C:\\SINETEC\\SINETEC\\venv).
* Framework Web: Django 5.0.14 configurado con arquitectura desacoplada en 6 aplicaciones.
* Base de Datos Local Activa: MySQL Server 8.0 en localhost:3306 (BD: 'sinetec', driver PyMySQL 1.2.3).
* Base de Datos Secundaria: SQLite (db.sqlite3, 1.6 MB) disponible para respaldo local y offline.
* Despliegue en la Nube: Render PaaS (Plan Free, Región Oregon, Python 3.11.9, Gunicorn 26.2.0).
* URL Pública Comprobada: https://sinetec-1.onrender.com/ (HTTP 200 OK, SSL Let's Encrypt TLS 1.3).
* Servidor de Archivos Estáticos: WhiteNoise 6.12.0 con compresión y almacenamiento en staticfiles.
* Generadores Multimedia: ReportLab 5.0.1 (PDFs oficiales), python-docx (informes Word), QRCode 8.2 y Pillow 12.3.0 (carnets).

2. SUITE DE PRUEBAS AUTOMATIZADAS Y AUDITORÍA
--------------------------------------------------------------------------------
* Suite Unitaria Oficial Django:
  - Comando: python manage.py test academico usuarios evaluaciones instituciones seguimiento convenios
  - Pruebas Descubiertas: 83 pruebas unitarias.
  - Pruebas Aprobadas con Éxito: 83 pruebas (100% de aprobación).
  - Fallos / Errores: 0 fallos, 0 errores.
  - Tiempo de Ejecución: 89.084 segundos.
  - Estado: OK (Base de datos de prueba creada y destruida limpiamente en MySQL).

* Suite de Auditoría de Demostración (test_auditoria_completa_edunova.py):
  - Estado de Demostración: 1 Docente activo (Miguel González), 1 Estudiante activo (Juan Pérez en Grado 10°A), 1 Acudiente (Carmen Gómez de Rodríguez), 1 Matrícula activa.
  - Cero tareas ficticias, cero notificaciones ficticias y cero comunicados residuales.
  - Operaciones CRUD de Carga Académica: Crear (ID #78), Editar a 8vo A y Eliminar limpia y verificada.
  - Resultado: 100% APROBADA.

* Suite de Auditoría de los Seis Paneles (test_seis_paneles_auditoria.py):
  - Panel Administrador (/dashboard/): HTTP 200 OK.
  - Panel Rectoría (/rectoria/): HTTP 200 OK.
  - Panel Secretaría (/secretaria/): HTTP 200 OK.
  - Panel Docente (/docente/): HTTP 200 OK (Contadores exactos: 1 estudiante en Matemáticas).
  - Panel Familia (/familia/): HTTP 200 OK (Estudiante Juan Pérez vinculado correctamente).
  - Panel Estudiante (/estudiante/): HTTP 200 OK (Subpaneles de notas, horario, materias interactivos).
  - Horario Coordinado: 6 bloques de clase sincronizados en Grado 10°A.
  - Resultado: 100% APROBADA.

3. MEDIDAS DE SEGURIDAD COMPROBADAS
--------------------------------------------------------------------------------
[x] Control de Acceso Basado en Roles (RBAC) para 6 perfiles diferenciados.
[x] Hash criptográfico de contraseñas con algoritmo PBKDF2 y salting SHA-256.
[x] Protección contra Cross-Site Request Forgery (CSRF) con token obligatorio en formularios.
[x] Mitigación de Clickjacking mediante cabecera X-Frame-Options: DENY.
[x] Prevención nativa de Inyección SQL (SQLi) mediante parametrización ORM de Django.
[x] Carnetización estudiantil inteligente con token UUID v4 y rotación diaria del código QR.
[x] Aislamiento de credenciales mediante variables de entorno .env con python-decouple.
[x] Reglas de Integridad de Negocio validadas en modelo: RN-001 (Doc único), RN-002 (Matrícula única), RN-003 (Juicio SENA A/D), RN-004 (Inmutabilidad por cierre de periodo).

4. LIMITACIONES TÉCNICAS IDENTIFICADAS
--------------------------------------------------------------------------------
* Reposo del Servidor Gratuito en la Nube (Cold Start):
  En el plan Free de Render, la aplicación entra en suspensión tras 15 minutos de inactividad. La primera petición subsiguiente tarda entre 40 y 50 segundos en despertar el contenedor.
* Persistencia en el Plan Gratuito:
  Al reconstruirse el contenedor en Render sin una base de datos PostgreSQL administrada adjunta, los datos se reinicializan desde el fixture sinetec_fixture_completa.json.
* Script de Diagnóstico Menor:
  El script utilitario inspect_db.py intentó leer f.usuario en FamiliaAcudiente; este modelo asocia estudiantes directamente por ManyToManyField sin campo OneToOne a User.

5. TAREAS PENDIENTES Y RECOMENDACIONES DE MEJORA
--------------------------------------------------------------------------------
[ ] Base de Datos PostgreSQL Administrada:
    Vincular una base de datos PostgreSQL externa (ej. Render Postgres, Supabase o Neon) para persistencia permanente 24/7 en la nube sin depender del disco efímero.
[ ] Rate Limiting en Vistas de Autenticación:
    Implementar django-ratelimit para limitar las solicitudes a máximo 5 intentos por minuto en /login/ y /recuperar-contrasena/.
[ ] Restricción de Cabecera Host en Producción:
    Cambiar ALLOWED_HOSTS = ['*'] en render.yaml por la lista explícita de dominios: ['sinetec-1.onrender.com', 'edunova.edu.co'].
[ ] Cabecera HSTS:
    Habilitar SECURE_HSTS_SECONDS = 31536000 en settings.py para forzar navegación HTTPS estricta durante un año.
[ ] Servicio de Correo Transaccional en Producción:
    Configurar credenciales SMTP de un servicio profesional (SendGrid, Amazon SES o Google Workspace) en las variables EMAIL_HOST_USER y EMAIL_HOST_PASSWORD del dashboard de Render.

6. RUTAS DE ARCHIVOS DOCUMENTALES GENERADOS
--------------------------------------------------------------------------------
* Documento Word Editable:
  C:\\SINETEC\\SINETEC\\docs\\Informe_Tecnico_EduNova_RAP.docx
* Versión PDF de Alta Calidad:
  C:\\SINETEC\\SINETEC\\docs\\Informe_Tecnico_EduNova_RAP.pdf
* Resumen de Verificaciones y Pendientes:
  C:\\SINETEC\\SINETEC\\docs\\Resultados_y_Pendientes_EduNova.txt
================================================================================
"""
    with open(TXT_PATH, "w", encoding="utf-8") as f:
        f.write(contenido)
    print(f"[OK] Archivo de texto generado exitosamente en: {TXT_PATH}")


if __name__ == '__main__':
    print("Iniciando generación de los documentos oficiales del Informe Técnico EduNova...")
    construir_documento_word()
    construir_documento_pdf()
    generar_archivo_texto()
    print("¡Proceso finalizado con éxito!")
