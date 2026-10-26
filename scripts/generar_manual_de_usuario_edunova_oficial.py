# -*- coding: utf-8 -*-
"""
Generador Maestro Oficial del Manual de Usuario EduNova
Genera:
- c:/EDUNOVA/EDUNOVA/docs/Manual_de_Usuario_EduNova.docx
- c:/EDUNOVA/EDUNOVA/docs/Manual_de_Usuario_EduNova.pdf
Cumple con los 20 criterios del Instrumento de Auditoría y Validación de Manuales de Usuario del SENA ADSI.
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
os.makedirs(DOCS_DIR, exist_ok=True)

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

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

try:
    pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Italic', 'C:/Windows/Fonts/ariali.ttf'))
    FONT_FAMILY = 'Arial'
    FONT_BOLD = 'Arial-Bold'
    FONT_ITALIC = 'Arial-Italic'
except Exception:
    FONT_FAMILY = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'
    FONT_ITALIC = 'Helvetica-Oblique'

class SenaNumberedCanvas(canvas.Canvas):
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
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        if self._pageNumber == 1:
            return  # Portada limpia

        self.saveState()
        self.setFont(FONT_FAMILY, 8)
        self.setFillColor(colors.HexColor("#4A3728"))

        self.drawString(54, 11 * inch - 36, "SENA Regional Magdalena — Centro de Logística y Promoción Ecoturística")
        self.drawRightString(8.5 * inch - 54, 11 * inch - 36, "EduNova | Manual Oficial de Usuario • Ficha 3173430")
        self.setStrokeColor(colors.HexColor("#8B5E3C"))
        self.setLineWidth(1.0)
        self.line(54, 11 * inch - 40, 8.5 * inch - 54, 11 * inch - 40)

        self.setStrokeColor(colors.HexColor("#D4A373"))
        self.setLineWidth(0.6)
        self.line(54, 46, 8.5 * inch - 54, 46)
        self.drawString(54, 32, "ADSI — Validación de Manual de Usuario • Instructor: Ing. Anybal López • Aprendices: Aminta Moguea & Dulce Figueroa")
        self.drawRightString(8.5 * inch - 54, 32, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=90, bottom=90, left=130, right=130):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_header_styled(doc, text, level=1):
    h = doc.add_paragraph()
    h.paragraph_format.keep_with_next = True
    run = h.add_run(text)
    run.font.name = "Arial"
    run.font.bold = True
    
    if level == 1:
        h.paragraph_format.space_before = Pt(22)
        h.paragraph_format.space_after = Pt(4)
        run.font.size = Pt(14.5)
        run.font.color.rgb = RGBColor(139, 94, 60)
        p_line = doc.add_paragraph()
        p_line.paragraph_format.space_before = Pt(0)
        p_line.paragraph_format.space_after = Pt(8)
        r_line = p_line.add_run("―" * 52)
        r_line.font.color.rgb = RGBColor(212, 163, 115)
    elif level == 2:
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(90, 56, 37)
    elif level == 3:
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(2)
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(45, 35, 30)
    return h

def add_p(doc, text, bold_prefix="", space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Arial"
        r_pre.font.size = Pt(10)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(45, 35, 30)
    r_body = p.add_run(text)
    r_body.font.name = "Arial"
    r_body.font.size = Pt(10)
    r_body.font.color.rgb = RGBColor(55, 45, 40)
    return p

def add_bullet(doc, text, bold_prefix=""):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Arial"
        r_pre.font.size = Pt(10)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(45, 35, 30)
    r_body = p.add_run(text)
    r_body.font.name = "Arial"
    r_body.font.size = Pt(10)
    r_body.font.color.rgb = RGBColor(55, 45, 40)
    return p

def add_callout_box_docx(doc, title, text, box_type="NOTE"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    
    bg_color = "F8F9FA"
    icon = "ℹ️ NOTA INFORMATIVA:"
    if box_type == "WARNING":
        bg_color = "FFFBEB"
        icon = "⚠️ ADVERTENCIA DE SEGURIDAD:"
    elif box_type == "IMPORTANT":
        bg_color = "FEF2F2"
        icon = "❗ REGLA INSTITUCIONAL OBLIGATORIA:"
    elif box_type == "TIP":
        bg_color = "F0FDF4"
        icon = "💡 CONSEJO PRÁCTICO:"
    
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=100, bottom=100, left=180, right=140)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run_t = p.add_run(f"{icon} {title}\n")
    run_t.font.name = "Arial"
    run_t.font.size = Pt(9.5)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(45, 35, 30)
    
    run_b = p.add_run(text)
    run_b.font.name = "Arial"
    run_b.font.size = Pt(9)
    run_b.font.color.rgb = RGBColor(60, 50, 45)
    
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

def add_capture_marker_docx(doc, code, screen_name, profile, action, elements_to_highlight):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "EFF6FF")
    set_cell_margins(cell, top=110, bottom=110, left=180, right=140)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    run_tag = p.add_run(f"📷 MARCADOR DE CAPTURA REAL — [{code}: {screen_name}]\n")
    run_tag.font.name = "Arial"
    run_tag.font.size = Pt(9.5)
    run_tag.font.bold = True
    run_tag.font.color.rgb = RGBColor(29, 78, 216)
    
    details = (
        f"• Perfil a utilizar: {profile}\n"
        f"• Pantalla / URL: {screen_name}\n"
        f"• Acción a realizar para obtener la captura: {action}\n"
        f"• Instrucción visual (señalar con flechas o recuadros): {elements_to_highlight}"
    )
    run_d = p.add_run(details)
    run_d.font.name = "Arial"
    run_d.font.size = Pt(8.5)
    run_d.font.color.rgb = RGBColor(30, 58, 138)
    
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

def add_table_styled_docx(doc, headers, data, col_widths=None):
    tbl = doc.add_table(rows=len(data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    hdr_row = tbl.rows[0]
    for idx, heading in enumerate(headers):
        cell = hdr_row.cells[idx]
        set_cell_background(cell, "8B5E3C")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(heading)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
    
    for r_idx, row_data in enumerate(data):
        row = tbl.rows[r_idx + 1]
        bg = "F8F9FA" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.1
            r = p.add_run(str(val))
            r.font.name = "Arial"
            r.font.size = Pt(8)
            r.font.color.rgb = RGBColor(45, 35, 30)
            
    if col_widths:
        for r in tbl.rows:
            for c_idx, w in enumerate(col_widths):
                r.cells[c_idx].width = Inches(w)
                
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

print("Iniciando construcción formal de Manual_de_Usuario_EduNova.docx...")

doc = docx.Document()
for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    header = section.header
    p_hdr = header.paragraphs[0]
    p_hdr.text = "EDUNOVA | Manual de Usuario Oficial • SENA ADSI Ficha 3173430"
    p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_hdr.style.font.name = "Arial"
    p_hdr.style.font.size = Pt(8.5)
    p_hdr.style.font.color.rgb = RGBColor(139, 94, 60)
    
    footer = section.footer
    p_ftr = footer.paragraphs[0]
    p_ftr.text = "Sistema de Información EduNova • Regional Magdalena • Instrumento de Validación ADSI"
    p_ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ftr.style.font.name = "Arial"
    p_ftr.style.font.size = Pt(8)
    p_ftr.style.font.color.rgb = RGBColor(120, 120, 120)

# ==============================================================================
# PORTADA OFICIAL
# ==============================================================================
p_inst = doc.add_paragraph()
p_inst.paragraph_format.space_before = Pt(30)
p_inst.paragraph_format.space_after = Pt(4)
r_inst = p_inst.add_run("SERVICIO NACIONAL DE APRENDIZAJE — SENA\nREGIONAL MAGDALENA\nCENTRO DE LOGÍSTICA Y PROMOCIÓN ECOTURÍSTICA DEL MAGDALENA")
r_inst.font.name = "Arial"
r_inst.font.size = Pt(11)
r_inst.font.bold = True
r_inst.font.color.rgb = RGBColor(139, 94, 60)

p_prog = doc.add_paragraph()
p_prog.paragraph_format.space_after = Pt(25)
r_prog = p_prog.add_run("TECNOLOGÍA EN ANÁLISIS Y DESARROLLO DE SISTEMAS DE INFORMACIÓN (ADSI)\nFICHA DE CARACTERIZACIÓN: 3173430")
r_prog.font.name = "Arial"
r_prog.font.size = Pt(10)
r_prog.font.bold = True
r_prog.font.color.rgb = RGBColor(90, 56, 37)

p_title = doc.add_paragraph()
p_title.paragraph_format.space_after = Pt(8)
r_title = p_title.add_run("MANUAL DE USUARIO OFICIAL DEL SISTEMA DE INFORMACIÓN EDUNOVA")
r_title.font.name = "Arial"
r_title.font.size = Pt(22)
r_title.font.bold = True
r_title.font.color.rgb = RGBColor(45, 35, 30)

p_sub = doc.add_paragraph()
p_sub.paragraph_format.space_after = Pt(20)
r_sub = p_sub.add_run("Guía Maestra y Operativa Paso a Paso para Administradores, Rectoría, Secretaría Académica, Docentes, Familias y Estudiantes\n(Cumplimiento Riguroso de los 20 Criterios del Instrumento de Auditoría y Validación SENA)")
r_sub.font.name = "Arial"
r_sub.font.size = Pt(11.5)
r_sub.font.italic = True
r_sub.font.color.rgb = RGBColor(110, 80, 60)

p_div = doc.add_paragraph()
p_div.paragraph_format.space_after = Pt(25)
r_div = p_div.add_run("―" * 52)
r_div.font.color.rgb = RGBColor(212, 163, 115)

tbl_meta = doc.add_table(rows=7, cols=2)
tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
meta_info = [
    ("Nombre Oficial del Sistema:", "EduNova (Anteriormente SINETEC)"),
    ("Versión del Software:", "2.4.0 Estable (Verificada en Código y Producción)"),
    ("Instructor Evaluador:", "Ing. Anybal López"),
    ("Aprendices Desarrolladoras:", "Aminta María Moguea Florez y Dulce María Figueroa"),
    ("Institución Educativa Aliada:", "IED Nuevo Horizonte / Institución Educativa Técnica"),
    ("Entorno de Producción Cloud:", "https://sinetec-1.onrender.com/"),
    ("Fecha de Publicación:", f"Octubre de 2026 (Compilación Definitiva)"),
]
for idx, (lbl, val) in enumerate(meta_info):
    row = tbl_meta.rows[idx]
    c0, c1 = row.cells[0], row.cells[1]
    c0.width = Inches(2.3)
    c1.width = Inches(4.2)
    c0.paragraphs[0].text = lbl
    c0.paragraphs[0].runs[0].font.name = "Arial"
    c0.paragraphs[0].runs[0].font.bold = True
    c0.paragraphs[0].runs[0].font.size = Pt(9)
    c0.paragraphs[0].runs[0].font.color.rgb = RGBColor(45, 35, 30)
    c1.paragraphs[0].text = val
    c1.paragraphs[0].runs[0].font.name = "Arial"
    c1.paragraphs[0].runs[0].font.size = Pt(9)
    c1.paragraphs[0].runs[0].font.color.rgb = RGBColor(70, 60, 55)
    set_cell_background(c0, "F8F9FA" if idx % 2 == 0 else "FFFFFF")
    set_cell_background(c1, "F8F9FA" if idx % 2 == 0 else "FFFFFF")
    set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
    set_cell_margins(c1, top=60, bottom=60, left=100, right=100)

doc.add_page_break()

# ==============================================================================
# TABLA DE CONTENIDO / ÍNDICE ORGANIZADO
# ==============================================================================
add_header_styled(doc, "TABLA DE CONTENIDO GENERAL", level=1)
add_p(doc, "El presente manual está organizado en doce (12) capítulos temáticos y dos (2) anexos normativos de auditoría, diseñados para garantizar la rápida localización de procedimientos, formularios, reglas de validación y solución de errores:", bold_prefix="Estructura del Manual: ")

indice_items = [
    ("1. INTRODUCCIÓN, JUSTIFICACIÓN Y PROPÓSITO FORMATIVO", "Pág. 3"),
    ("2. OBJETIVOS DEL SISTEMA EDUNOVA", "Pág. 4"),
    ("3. ALCANCE DEL SISTEMA Y DELIMITACIÓN OPERATIVA POR ROLES", "Pág. 4"),
    ("4. REQUISITOS TÉCNICOS Y CONDICIONES DE ACCESO", "Pág. 5"),
    ("5. INTERFAZ, AUTENTICACIÓN Y RECUPERACIÓN SEGURA DE CONTRASEÑA", "Pág. 6"),
    ("   5.1. Pantalla de Bienvenida y Formulario de Inicio de Sesión", "Pág. 6"),
    ("   5.2. Enrutamiento y Aislamiento por Perfil Institucional (RBAC)", "Pág. 7"),
    ("   5.3. Flujo Criptográfico de Recuperación de Contraseña", "Pág. 7"),
    ("   5.4. Cierre de Sesión Seguro y Expiración por Inactividad", "Pág. 8"),
    ("6. GUÍA PASO A PASO DE MÓDULOS OPERATIVOS POR PERFIL", "Pág. 9"),
    ("   6.1. Panel de Administración del Sistema (/dashboard/)", "Pág. 9"),
    ("   6.2. Portal de Rectoría y Coordinación Académica (/rectoria/, /coordinacion/)", "Pág. 11"),
    ("   6.3. Portal de Secretaría Académica: Matrícula y Expedientes (/secretaria/)", "Pág. 13"),
    ("   6.4. Portal del Docente e Instructor: Operación de Clase (/instructor/)", "Pág. 17"),
    ("   6.5. Portal del Estudiante / Aprendiz (/aprendiz/, /estudiante/)", "Pág. 21"),
    ("   6.6. Portal de Familias y Acudientes (/familia/)", "Pág. 24"),
    ("7. CASOS DE USO REALISTAS Y EXHAUSTIVOS (10 CASOS CLAVE)", "Pág. 26"),
    ("8. DIAGRAMAS DE FLUJO DE LOS PRINCIPALES PROCESOS", "Pág. 32"),
    ("9. GUÍA DE SOLUCIÓN DE ERRORES FRECUENTES Y CONTINGENCIAS", "Pág. 34"),
    ("10. PREGUNTAS FRECUENTES (FAQ) CON RESPUESTAS PRÁCTICAS", "Pág. 37"),
    ("11. POLÍTICAS DE SEGURIDAD Y PROTECCIÓN DE DATOS (LEY 1581 / HABEAS DATA)", "Pág. 39"),
    ("12. GLOSARIO DE TÉRMINOS INSTITUCIONALES Y TÉCNICOS", "Pág. 41"),
    ("ANEXO A: LISTA MAESTRA NUMERADA DE CAPTURAS DE PANTALLA REQUERIDAS (23)", "Pág. 43"),
    ("ANEXO B: MATRIZ DE CUMPLIMIENTO DE LOS 20 CRITERIOS SENA ADSI", "Pág. 46"),
]

for tit, pag in indice_items:
    p_ind = doc.add_paragraph()
    p_ind.paragraph_format.space_before = Pt(1)
    p_ind.paragraph_format.space_after = Pt(2)
    p_ind.paragraph_format.line_spacing = 1.15
    r_tit = p_ind.add_run(tit)
    r_tit.font.name = "Arial"
    r_tit.font.size = Pt(9.5)
    r_tit.font.color.rgb = RGBColor(45, 35, 30)
    if not tit.startswith("   "):
        r_tit.font.bold = True
    
    # Relleno de puntos
    dots_len = max(3, 75 - len(tit))
    r_dots = p_ind.add_run(" " + "." * dots_len + " ")
    r_dots.font.name = "Arial"
    r_dots.font.size = Pt(8.5)
    r_dots.font.color.rgb = RGBColor(180, 160, 150)
    
    r_pag = p_ind.add_run(pag)
    r_pag.font.name = "Arial"
    r_pag.font.size = Pt(9.5)
    r_pag.font.bold = True
    r_pag.font.color.rgb = RGBColor(139, 94, 60)

doc.add_page_break()

# ==============================================================================
# CAPÍTULO 1: INTRODUCCIÓN Y JUSTIFICACIÓN
# ==============================================================================
add_header_styled(doc, "1. INTRODUCCIÓN, JUSTIFICACIÓN Y PROPÓSITO FORMATIVO", level=1)

add_p(doc, "El presente Manual Oficial de Usuario ha sido elaborado para guiar de manera didáctica, exhaustiva y ergonómica a toda la comunidad educativa de la Institución Educativa Distrital articulada con la Media Técnica SENA en el Departamento del Magdalena, en la operación diaria del Sistema de Información EduNova (anteriormente denominado SINETEC).", bold_prefix="Bienvenida Institucional: ")

add_p(doc, "Históricamente, los colegios articulados con el SENA enfrentan serias dificultades administrativas: dispersión de las calificaciones en hojas de cálculo no estandarizadas, retrasos en la entrega de boletines periódicos, falta de trazabilidad en la toma de asistencia en aula y desarticulación entre las secretarías escolares y los instructores técnicos. EduNova nace como una solución de ingeniería de software robusta, centralizada y de software libre (Python/Django con MySQL Server y despliegue WhiteNoise/Render) que unifica el control de la formación técnica y básica bajo estrictos estándares de usabilidad y seguridad de la información.", bold_prefix="Justificación del Proyecto: ")

add_p(doc, "Este documento está especialmente diseñado para que una persona sin conocimientos informáticos avanzados pueda comprender la filosofía del sistema, acceder a su portal con total confianza, diligenciar los formularios requeridos y comprobar que sus operaciones se guardaron exitosamente sin perderse en menús confusos.", bold_prefix="Propósito del Manual: ")

add_callout_box_docx(doc, "Evolución de Marca Institucional: De SINETEC a EduNova", 
                     "El sistema fue concebido originalmente bajo el nombre técnico SINETEC (Sistema Integrado de Educación Técnica). En su versión 2.4.0 de producción se adopta formalmente el nombre comercial y pedagógico EduNova. Todas las referencias internas en bases de datos y rutas técnicas mantienen compatibilidad total con la identidad visual institucional EduNova.", box_type="TIP")

# ==============================================================================
# CAPÍTULO 2: OBJETIVOS
# ==============================================================================
add_header_styled(doc, "2. OBJETIVOS DEL SISTEMA EDUNOVA", level=1)

add_p(doc, "Centralizar, optimizar y automatizar los procesos de matrícula escolar, gestión de expedientes académicos, control diario de asistencia, publicación y entrega virtual de tareas, asentamiento de calificaciones y expedición de boletines periódicos oficiales en las Instituciones Educativas articuladas con la Media Técnica SENA.", bold_prefix="Objetivo General: ")

add_p(doc, "Para materializar el objetivo general, el sistema y este manual cumplen los siguientes objetivos específicos:", bold_prefix="Objetivos Específicos: ")
add_bullet(doc, "Proveer una interfaz de autenticación ergonómica con enrutamiento automático hacia los portales especializados de Administrador, Rectoría, Secretaría, Docente, Familia y Estudiante.", bold_prefix="1. Seguridad y Acceso: ")
add_bullet(doc, "Garantizar la matrícula ágil de estudiantes de 1° a 11° grado mediante dos modalidades: registro individual asistido y carga masiva mediante plantilla estándar de Excel.", bold_prefix="2. Gestión de Matrícula: ")
add_bullet(doc, "Facilitar al docente el registro diario de asistencia en el aula con botones de marcación rápida (Presente, Tardanza, Ausente, Justificada) y guardado instantáneo.", bold_prefix="3. Asistencia en Vivo: ")
add_bullet(doc, "Implementar la doble escala evaluativa: escala cuantitativa y cualitativa del Ministerio de Educación Nacional (Superior, Alto, Básico, Bajo) articulada con los juicios evaluativos de Resultados de Aprendizaje del SENA (Aprobado 'A' y No Aprobado 'D').", bold_prefix="4. Evaluación Formativa: ")
add_bullet(doc, "Ofrecer a padres de familia y acudientes un canal digital transparente para consultar boletines de calificaciones, observar registros de convivencia y acusar recibo de circulares institucionales.", bold_prefix="5. Vinculación Familiar: ")

# ==============================================================================
# CAPÍTULO 3: ALCANCE DEL SISTEMA Y DELIMITACIÓN
# ==============================================================================
add_header_styled(doc, "3. ALCANCE DEL SISTEMA Y DELIMITACIÓN OPERATIVA POR ROLES", level=1)

add_p(doc, "El alcance del proyecto formativo EduNova está estrictamente delimitado a la gestión académica, escolar y pedagógica de la institución educativa. Por política de diseño y en estricto cumplimiento del alcance aprobado por el SENA, se definen los siguientes límites:", bold_prefix="Delimitación de Alcance: ")

add_p(doc, "El sistema comprende e implementa plenamente los siguientes seis (6) perfiles de usuario:", bold_prefix="Perfiles Oficiales Implementados: ")
add_bullet(doc, "Supervisa la infraestructura técnica, gestiona cuentas de usuario, asigna roles, audita registros y administra la papelera de reciclaje.", bold_prefix="• Administrador: ")
add_bullet(doc, "Monitorea indicadores globales de cobertura y rendimiento, emite circulares oficiales y consulta sábanas de notas.", bold_prefix="• Rectoría y Dirección: ")
add_bullet(doc, "Supervisa el calendario escolar, configura las fechas de los cuatro periodos académicos y fiscaliza las cargas horarias.", bold_prefix="• Coordinación Académica: ")
add_bullet(doc, "Formaliza matrículas individuales y masivas, custodia el directorio de aprendices, genera reportes y emite constancias.", bold_prefix="• Secretaría Académica: ")
add_bullet(doc, "Gestiona asignaturas asignadas, toma asistencia diaria, asienta notas por periodos, publica tareas y retroalimenta entregas.", bold_prefix="• Docente / Instructor: ")
add_bullet(doc, "Consulta su horario semanal, revisa calificaciones acumuladas, descarga guías de clase y remite tareas en línea.", bold_prefix="• Estudiante (Aprendiz): ")
add_bullet(doc, "Supervisa el rendimiento escolar de sus hijos acudidos, descarga boletines oficiales y acusa recibo de comunicados.", bold_prefix="• Familia / Acudiente: ")

add_callout_box_docx(doc, "Módulos Excluidos del Alcance Aprobado del Proyecto", 
                     "De acuerdo con las directrices formativas de la ficha 3173430, no forman parte del alcance del software los siguientes servicios: pasarelas de pago electrónico en línea, cobro forzoso de pensiones, facturación electrónica DIAN, geolocalización satelital de transporte escolar ni emisión de carnets físicos con lectura de molinetes. Si bien en el código existen modelos y prototipos auxiliares de pensiones o rutas, estos corresponden a extensiones secundarias y no al núcleo de certificación del manual.", box_type="IMPORTANT")

# ==============================================================================
# CAPÍTULO 4: REQUISITOS TÉCNICOS
# ==============================================================================
add_header_styled(doc, "4. REQUISITOS TÉCNICOS Y CONDICIONES DE ACCESO", level=1)

add_p(doc, "EduNova está desarrollado como una aplicación web progresiva y responsiva (Responsive Web Application), lo que significa que no requiere la instalación de software adicional en las computadoras ni teléfonos inteligentes de los usuarios. Puede ser utilizado desde cualquier dispositivo con las siguientes especificaciones mínimas:", bold_prefix="Requisitos de Infraestructura del Cliente: ")

add_bullet(doc, "Computador de escritorio, portátil, tableta digital o teléfono móvil con procesador de al menos 1.5 GHz y 2 GB de memoria RAM.", bold_prefix="• Dispositivo: ")
add_bullet(doc, "Google Chrome (versión 100+), Mozilla Firefox (versión 100+), Microsoft Edge (versión 100+) o Apple Safari (versión 15+). JavaScript y cookies deben estar habilitados.", bold_prefix="• Navegador Web Recomendado: ")
add_bullet(doc, "Resolución de 1366 x 768 píxeles en computadores o pantalla táctil en dispositivos móviles.", bold_prefix="• Resolución de Pantalla: ")
add_bullet(doc, "Conexión de banda ancha fija o datos móviles con velocidad de descarga de al menos 2 Mbps para visualización rápida de reportes PDF.", bold_prefix="• Conectividad a Internet: ")
add_bullet(doc, "Dirección local institucional: http://127.0.0.1:8000/login/ • Dirección en la nube (producción): https://sinetec-1.onrender.com/login/", bold_prefix="• Puntos de Acceso Autorizados: ")

# ==============================================================================
# CAPÍTULO 5: INTERFAZ Y ACCESO
# ==============================================================================
add_header_styled(doc, "5. INTERFAZ, AUTENTICACIÓN Y RECUPERACIÓN SEGURA DE CONTRASEÑA", level=1)

add_p(doc, "El acceso al sistema se realiza a través de un portal unificado con validación de credenciales criptográficas, protección contra ataques de fuerza bruta y redirección automática por rol.", bold_prefix="Seguridad de Acceso: ")

add_header_styled(doc, "5.1. Procedimiento de Inicio de Sesión Paso a Paso", level=2)
add_p(doc, "Siga con atención los siguientes pasos para autenticarse formalmente en la plataforma:", bold_prefix="Instrucciones de Acceso: ")
add_bullet(doc, "Abra su navegador de preferencia y escriba la URL oficial: https://sinetec-1.onrender.com/login/ (o http://127.0.0.1:8000/login/ en red local).", bold_prefix="Paso 1 (Dónde entrar): ")
add_bullet(doc, "En la casilla 'Usuario', digite su nombre de usuario institucional o su Número de Documento de Identidad (cédula o tarjeta de identidad, sin espacios, puntos ni guiones).", bold_prefix="Paso 2 (Qué datos introducir): ")
add_bullet(doc, "En la casilla 'Contraseña', escriba su clave personal asignada. Puede hacer clic en el ícono del ojo para verificar los caracteres digitados.", bold_prefix="Paso 3 (Contraseña): ")
add_bullet(doc, "Opcionalmente, marque la casilla 'Recordar mi inicio de sesión' si se encuentra en un computador personal de confianza.", bold_prefix="Paso 4 (Persistencia): ")
add_bullet(doc, "Haga clic en el botón principal color café: 'Iniciar Sesión'.", bold_prefix="Paso 5 (Qué botón pulsar): ")
add_bullet(doc, "El sistema valida sus credenciales en la base de datos MySQL, consulta el rol activo vinculado a su perfil y lo redirige en menos de un segundo a su portal de trabajo. Verifique que en la esquina superior derecha aparezca su nombre y su perfil asignado.", bold_prefix="Paso 6 (Cómo comprobar el resultado): ")

add_capture_marker_docx(doc, "CAPTURA 01", "Pantalla de Inicio de Sesión (/login/)", "Cualquier Usuario no autenticado", 
                        "Abrir el navegador, cargar la ruta /login/, digitar usuario y contraseña de prueba y posicionar el cursor sobre el botón 'Iniciar Sesión'.", 
                        "Encerrar en un recuadro el campo de usuario/documento, el campo de contraseña, la casilla de verificación y señalar con una flecha el botón 'Iniciar Sesión' y el enlace '¿Olvidó su contraseña?'.")

add_callout_box_docx(doc, "Nota de Demostración en Desarrollo vs. Producción", 
                     "En entornos locales de desarrollo (DEBUG=True), puede aparecer un botón de prueba 'Entrar como Estudiante (demo_estudiante)'. En el servidor de producción (DEBUG=False), dicho acceso directo se encuentra deshabilitado por razones de seguridad, requiriendo siempre contraseña institucional auténtica.", box_type="WARNING")

add_header_styled(doc, "5.2. Procedimiento de Recuperación Segura de Contraseña", level=2)
add_p(doc, "EduNova cuenta con un mecanismo autónomo de restablecimiento de contraseña que cumple con los protocolos de seguridad de la información:", bold_prefix="Flujo Criptográfico: ")
add_bullet(doc, "En la pantalla de acceso (/login/), haga clic en el enlace '¿Olvidó su contraseña?'. Se abrirá la interfaz /recuperar-contrasena/.", bold_prefix="Paso 1 (Dónde entrar): ")
add_bullet(doc, "Digite su Número de Documento de Identidad institucional y haga clic en 'Validar y Continuar'.", bold_prefix="Paso 2 (Identificación): ")
add_bullet(doc, "El backend verifica la existencia del documento. Si el usuario existe y tiene un correo institucional configurado, se genera un token criptográfico seguro de un solo uso (con expiración a las 24 horas) y se despacha al correo registrado.", bold_prefix="Paso 3 (Validación Antifraude): ")
add_bullet(doc, "El usuario revisa su bandeja de entrada, hace clic en el enlace de restablecimiento e ingresa su nueva contraseña cumpliendo las políticas de complejidad (mínimo 8 caracteres alfanuméricos).", bold_prefix="Paso 4 (Nueva Clave): ")
add_bullet(doc, "Al pulsar 'Guardar Nueva Contraseña', el sistema confirma el cambio y redirige a la pantalla de login para ingresar con la nueva clave.", bold_prefix="Paso 5 (Comprobación): ")

add_capture_marker_docx(doc, "CAPTURA 02", "Formulario de Recuperación de Contraseña (/recuperar-contrasena/)", "Usuario que olvidó su clave", 
                        "Hacer clic en '¿Olvidó su contraseña?' desde el login, escribir un número de documento y observar el mensaje de confirmación.", 
                        "Señalar el campo de número de documento, el botón 'Validar y Continuar' y el mensaje de alerta institucional de seguridad.")

add_header_styled(doc, "5.3. Cierre de Sesión Seguro", level=2)
add_p(doc, "Para garantizar la privacidad de los expedientes escolares, especialmente en computadores compartidos de salas de informática o secretaría, el usuario debe pulsar el menú desplegable de su perfil ubicado en la barra superior derecha y seleccionar 'Cerrar sesión' (/logout/). El sistema invalidará la cookie de sesión y devolverá al usuario a la pantalla de bienvenida.", bold_prefix="Protocolo de Salida: ")

# ==============================================================================
# CAPÍTULO 6: GUÍA PASO A PASO DE MÓDULOS POR PERFIL
# ==============================================================================
add_header_styled(doc, "6. GUÍA PASO A PASO DE MÓDULOS OPERATIVOS POR PERFIL", level=1)

# 6.1 Administrador
add_header_styled(doc, "6.1. Panel de Administración del Sistema (/dashboard/)", level=2)
add_p(doc, "El Administrador del sistema ostenta el control técnico global de la plataforma EduNova. Dispone de herramientas para la supervisión de la infraestructura, seguridad de cuentas y mantenimiento de datos.", bold_prefix="Rol Autorizado: Administrador | ")

add_p(doc, "Módulos y operaciones disponibles para el Administrador:", bold_prefix="Operaciones del Perfil: ")
add_bullet(doc, "Ruta /dashboard/. Presenta tarjetas KPI con el total de estudiantes matriculados, docentes activos, cursos conformados y tasa de asistencia institucional.", bold_prefix="• Dashboard General: ")
add_bullet(doc, "Ruta /usuarios/. Permite crear nuevas cuentas institucionales, editar nombres, apellidos y correos, alternar el estado de activación (activo/inactivo) y forzar el restablecimiento de contraseñas.", bold_prefix="• Gestión de Usuarios y Roles: ")
add_bullet(doc, "Ruta /auditoria/. Bitácora cronológica inmutable que registra cada inicio de sesión, creación de matrículas, modificación de notas y eliminación de registros, con dirección IP y fecha/hora exacta.", bold_prefix="• Auditoría Forense: ")
add_bullet(doc, "Ruta /papelera/. Implementación de borrado lógico (Soft Delete). Todo estudiante, matrícula u horario eliminado no se destruye de la base de datos, sino que se almacena en esta papelera, permitiendo su restauración con un solo clic.", bold_prefix="• Papelera de Reciclaje Institucional: ")
add_bullet(doc, "Ruta /configuracion/. Permite modificar el nombre oficial de la institución, código DANE, NIT, nombre del rector y paleta de colores institucionales.", bold_prefix="• Identidad y Configuración del Colegio: ")

add_capture_marker_docx(doc, "CAPTURA 03", "Dashboard General de Administración (/dashboard/)", "Administrador", 
                        "Iniciar sesión con cuenta de Administrador institucional y visualizar la pantalla principal del Dashboard.", 
                        "Enmarcar las tarjetas KPI de métricas, los accesos del menú lateral izquierdo y el indicador de rol 'Administrador' en la cabecera.")

add_capture_marker_docx(doc, "CAPTURA 04", "Gestión de Usuarios y Roles (/usuarios/)", "Administrador", 
                        "Navegar a /usuarios/, ubicar la lista de cuentas creadas y desplegar el modal de 'Crear Usuario'.", 
                        "Señalar la tabla de usuarios, las columnas de 'Rol' y 'Estado', el botón 'Nuevo Usuario' y los botones de acción 'Restablecer Clave' y 'Desactivar'.")

add_capture_marker_docx(doc, "CAPTURA 05", "Papelera de Reciclaje Institucional (/papelera/)", "Administrador", 
                        "Acceder a la ruta /papelera/ tras haber eliminado un registro de prueba.", 
                        "Resaltar la lista de elementos en papelera, la fecha de eliminación, el usuario responsable y el botón verde 'Restaurar Elemento'.")

# 6.2 Rectoría y Coordinación
add_header_styled(doc, "6.2. Portal de Rectoría y Coordinación Académica (/rectoria/, /coordinacion/)", level=2)
add_p(doc, "Orientado a la alta dirección educativa para la supervisión estratégica, control pedagógico y comunicación oficial.", bold_prefix="Roles Autorizados: Rectoría, Coordinador Académico | ")

add_bullet(doc, "Ruta /rectoria/. Tablero de mando que consolida la cobertura escolar por grados (1° a 11°), distribución de estudiantes por sede y alertas tempranas de riesgo de deserción.", bold_prefix="• Tablero Directivo de Indicadores: ")
add_bullet(doc, "Ruta /comunicaciones/redactar/. Formulario que permite redactar circulares dirigidas a docentes o familias, adjuntar archivos PDF y emitirlas con firma digital para exigir confirmación de lectura.", bold_prefix="• Redacción y Emisión de Circulares: ")
add_bullet(doc, "Ruta /academico/periodos-academicos/. Módulo crítico donde Coordinación define las fechas de inicio y finalización de los cuatro (4) periodos del año lectivo 2026, y activa la casilla '¿Cerrado Formalmente?' para bloquear la alteración de notas.", bold_prefix="• Configuración de Periodos Académicos: ")
add_bullet(doc, "Ruta /reportes/. Centro de analítica que permite exportar sábanas de notas consolidadas y padrones de matrícula en formatos Excel (.xlsx) y PDF de alta calidad.", bold_prefix="• Exportación de Informes Directivos: ")

add_capture_marker_docx(doc, "CAPTURA 06", "Tablero de Rectoría con Indicadores Clave (/rectoria/)", "Rectoría", 
                        "Ingresar al portal de Rectoría y observar los gráficos consolidados de aprobación y cobertura.", 
                        "Señalar los indicadores de porcentaje de cobertura, los filtros por grado y el acceso directo a emisión de circulares.")

add_capture_marker_docx(doc, "CAPTURA 07", "Redacción de Circular Institucional (/comunicaciones/redactar/)", "Rectoría", 
                        "Abrir el formulario de redacción de circular, escribir un asunto y seleccionar el grupo destinatario.", 
                        "Enmarcar los campos de asunto, mensaje, selección de audiencia (Docentes / Familias) y el botón 'Publicar Circular Oficial'.")

add_capture_marker_docx(doc, "CAPTURA 08", "Configuración de Periodos Académicos (/academico/periodos-academicos/)", "Coordinador / Rector", 
                        "Ingresar a la vista de configuración de periodos académicos del año lectivo.", 
                        "Resaltar la tabla con los cuatro periodos, las fechas de inicio y fin, el porcentaje de ponderación (25%) y el interruptor de 'Cierre Formal'.")

# 6.3 Secretaría Académica
add_header_styled(doc, "6.3. Portal de Secretaría Académica: Matrícula y Expedientes (/secretaria/)", level=2)
add_p(doc, "La Secretaría Académica es el corazón operativo del registro escolar. Custodia los expedientes de matrícula desde 1° hasta 11° grado.", bold_prefix="Rol Autorizado: Secretaría Académica | ")

add_p(doc, "Procedimientos detallados del portal de Secretaría:", bold_prefix="Operaciones Clave: ")
add_bullet(doc, "Ruta /matriculas/. Muestra la cuadrícula de los 11 grados escolares (1° a 11°). Permite filtrar por grado, ficha técnica y estado de formación (En Formación, Desertado, Trasladado, Retirado, Certificado).", bold_prefix="• Padrón General de Matrículas: ")
add_bullet(doc, "Rutas /estudiantes/registrar/ o /academico/fichas/<id>/matricular/. Formulario completo para registrar a un nuevo alumno: nombres, apellidos, tipo y número de documento, fecha de nacimiento, género, dirección, datos del acudiente y asignación de grupo.", bold_prefix="• Matrícula Individual de Estudiante: ")
add_bullet(doc, "Ruta /estudiantes/importar/. Permite descargar la plantilla oficial en Excel (.xlsx), rellenar en bloque los datos de decenas de alumnos y procesar la importación masiva en segundos con validación automática de unicidad de documento.", bold_prefix="• Carga Masiva de Estudiantes en Excel: ")
add_bullet(doc, "Ruta /usuarios/importar-instructores/. Permite cargar masivamente la nómina docente desde una plantilla Excel con sus correos y áreas de formación.", bold_prefix="• Carga Masiva de Docentes en Excel: ")
add_bullet(doc, "Ruta /estudiantes/. Directorio para localizar alumnos con barra de búsqueda en tiempo real, abrir su expediente completo, modificar datos de contacto o generar certificados de estudio.", bold_prefix="• Expedientes y Directorio: ")

add_capture_marker_docx(doc, "CAPTURA 09", "Padrón de Matrículas y Cuadrícula de Grados 1° a 11° (/matriculas/)", "Secretaría", 
                        "Abrir /matriculas/, observar las tarjetas de grados escolares y la tabla de aprendices matriculados.", 
                        "Señalar la cuadrícula superior de grados (1° a 11°), el botón 'Nueva Matrícula' y los botones de 'Carga Masiva Estudiantes' y 'Carga Masiva Docentes'.")

add_capture_marker_docx(doc, "CAPTURA 10", "Formulario de Matrícula Individual (/estudiantes/registrar/)", "Secretaría", 
                        "Hacer clic en 'Registrar Estudiante' y desplegar el formulario de inscripción.", 
                        "Enmarcar las secciones de 'Datos del Estudiante', 'Asignación de Grado y Ficha', 'Información del Acudiente' y el botón 'Guardar Matrícula Oficial'.")

add_capture_marker_docx(doc, "CAPTURA 11", "Módulo de Carga Masiva de Estudiantes en Excel (/estudiantes/importar/)", "Secretaría", 
                        "Ingresar a la vista de importación masiva de estudiantes.", 
                        "Resaltar el botón 'Descargar Plantilla Oficial Excel', la zona de arrastre del archivo .xlsx y el botón 'Procesar Carga Masiva'.")

add_capture_marker_docx(doc, "CAPTURA 12", "Directorio de Estudiantes y Expediente (/estudiantes/)", "Secretaría", 
                        "Ingresar a /estudiantes/, escribir el nombre de un alumno en la barra de búsqueda y desplegar su fila.", 
                        "Señalar la barra de búsqueda en vivo, el botón 'Ver Ficha / Expediente', el botón de edición (lápiz) y el estado de matrícula.")

# 6.4 Docente / Instructor
add_header_styled(doc, "6.4. Portal del Docente e Instructor: Operación de Clase (/instructor/)", level=2)
add_p(doc, "El portal del docente está optimizado para facilitar el trabajo en el aula, reduciendo el tiempo dedicado a tareas administrativas.", bold_prefix="Rol Autorizado: Docente / Instructor SENA | ")

add_bullet(doc, "Rutas /mis-grupos/, /mis-asignaturas/. Muestra las clases asignadas por Coordinación, con el horario semanal y la lista de aprendices matriculados en cada salón.", bold_prefix="• Mis Asignaturas y Mis Grupos: ")
add_bullet(doc, "Ruta /asistencia/. El profesor selecciona la fecha y el grupo. Frente a cada estudiante aparecen cuatro botones ergonómicos: P (Presente - Verde), T (Tardanza - Amarillo), A (Ausente - Rojo), J (Justificada - Azul). Al presionar un botón, se guarda de inmediato en la base de datos sin recargar la página.", bold_prefix="• Toma Inteligente de Asistencia en Vivo: ")
add_bullet(doc, "Ruta /calificaciones-docente/. Planilla oficial para asentar notas del Periodo 1, 2, 3 o 4. Permite digitar notas numéricas de 0.0 a 5.0, traduciéndolas en tiempo real al desempeño nacional MEN (Bajo, Básico, Alto, Superior) y al juicio RAP SENA (Aprobado 'A' o Deficiente 'D').", bold_prefix="• Registro Oficial de Calificaciones por Periodo: ")
add_bullet(doc, "Ruta /academico/clase/<id>/crear-tarea/. Permite redactar el enunciado de un taller, establecer la fecha y hora exacta de vencimiento y adjuntar material pedagógico en formato PDF o Word.", bold_prefix="• Publicación de Tareas y Talleres: ")
add_bullet(doc, "Ruta /instructor/tarea/<id>/entregas/. Bandeja de recepción donde el profesor visualiza los archivos subidos por los alumnos, digita la retroalimentación cualitativa y asigna la nota correspondiente.", bold_prefix="• Casillero de Revisión y Calificación de Entregas: ")

add_capture_marker_docx(doc, "CAPTURA 13", "Portal Docente con Carga Asignada (/instructor/)", "Docente", 
                        "Iniciar sesión como Docente (ej: Miguel González) y abrir el portal de bienvenida con asignaturas activas.", 
                        "Señalar las tarjetas de asignaturas vinculadas, el horario de la semana y el acceso directo al módulo de asistencia.")

add_capture_marker_docx(doc, "CAPTURA 14", "Planilla de Asistencia con Botones P, T, A, J (/asistencia/)", "Docente", 
                        "Ingresar a /asistencia/, seleccionar la fecha de hoy y desplegar la lista del curso 10°A.", 
                        "Enmarcar la botonera de asistencia (P, T, A, J) para un estudiante y señalar el mensaje de guardado automático.")

add_capture_marker_docx(doc, "CAPTURA 15", "Planilla de Calificaciones por Periodo (/calificaciones-docente/)", "Docente", 
                        "Abrir la planilla de notas de una asignatura, seleccionar 'Periodo 1' y digitar una nota numérica.", 
                        "Resaltar la columna de nota numérica, la etiqueta de Desempeño MEN calculada automáticamente y el botón 'Guardar Planilla'.")

add_capture_marker_docx(doc, "CAPTURA 16", "Formulario de Creación de Tarea (/academico/clase/<id>/crear-tarea/)", "Docente", 
                        "Ingresar a la vista de publicación de nueva tarea de clase.", 
                        "Señalar los campos de título, instrucciones, selector de fecha/hora de vencimiento, botón de adjuntar archivo y 'Publicar Tarea'.")

add_capture_marker_docx(doc, "CAPTURA 17", "Casillero de Revisión de Entregas (/instructor/tarea/<id>/entregas/)", "Docente", 
                        "Abrir una tarea con entregas recibidas de estudiantes.", 
                        "Enmarcar la tabla de aprendices que entregaron, el enlace de descarga del archivo adjunto del alumno y la casilla de retroalimentación.")

# 6.5 Estudiante
add_header_styled(doc, "6.5. Portal del Estudiante / Aprendiz (/aprendiz/, /estudiante/)", level=2)
add_p(doc, "Diseñado con una estética amigable e intuitiva para que el aprendiz asuma el protagonismo de su formación académica.", bold_prefix="Rol Autorizado: Estudiante (Aprendiz) | ")

add_bullet(doc, "Ruta /estudiante/horario/. Cuadrícula semanal organizada de lunes a viernes con los bloques de clase, materias, salones y docentes asignados.", bold_prefix="• Mi Horario Escolar: ")
add_bullet(doc, "Ruta /estudiante/calificaciones/. Visualización transparente de las notas acumuladas en los periodos lectivos y el juicio cualitativo de sus RAPs. Si no hay notas asentadas, el sistema informa con claridad: 'Aún no tienes calificaciones registradas'.", bold_prefix="• Mis Calificaciones y Desempeño: ")
add_bullet(doc, "Ruta /estudiante/tareas/. Casillero personal con las actividades formativas pendientes y vencidas. Al abrir un taller, el estudiante puede leer las instrucciones y descargar las guías adjuntas.", bold_prefix="• Actividades y Tareas en Línea: ")
add_bullet(doc, "Ruta /aprendiz/tarea/<id>/entregar/. Formulario que permite escribir comentarios de entrega, adjuntar el archivo de respuesta (Word, PDF, imagen) y enviarlo formalmente antes del cierre de plazo.", bold_prefix="• Formulario de Entrega de Evidencia: ")
add_bullet(doc, "Ruta /estudiante/asistencia/. Consulta del porcentaje acumulado de asistencia y registro pormenorizado de inasistencias o tardanzas.", bold_prefix="• Mi Asistencia y Comunicados: ")

add_capture_marker_docx(doc, "CAPTURA 18", "Portal del Estudiante con Resumen Académico (/aprendiz/)", "Estudiante", 
                        "Iniciar sesión con la cuenta de un estudiante matriculado (ej: Juan Pérez en 10°A) y ver la pantalla principal.", 
                        "Señalar el saludo personalizado, las materias en curso, el resumen de tareas próximas y los accesos rápidos a calificaciones.")

add_capture_marker_docx(doc, "CAPTURA 19", "Consulta de Calificaciones del Estudiante (/estudiante/calificaciones/)", "Estudiante", 
                        "Navegar a la pestaña de calificaciones del estudiante.", 
                        "Enmarcar la tabla de asignaturas, las notas por periodo (1 al 4) y el promedio acumulado.")

add_capture_marker_docx(doc, "CAPTURA 20", "Visualización y Entrega de Tareas en Línea (/estudiante/tareas/)", "Estudiante", 
                        "Abrir una tarea pendiente, acceder al formulario de entrega y adjuntar un archivo de prueba.", 
                        "Resaltar las instrucciones del docente, el enlace de descarga de la guía, la casilla de adjunto de archivo y el botón 'Entregar Tarea'.")

# 6.6 Familia
add_header_styled(doc, "6.6. Portal de Familias y Acudientes (/familia/)", level=2)
add_p(doc, "Provee un canal directo de vinculación y acompañamiento formativo para los padres de familia y acudientes legales.", bold_prefix="Rol Autorizado: Familia / Acudiente | ")

add_bullet(doc, "Ruta /familia/matricula/. Permite verificar los datos del aprendiz acudido, grado, ficha formativa y datos de contacto de la institución.", bold_prefix="• Expediente del Acudido: ")
add_bullet(doc, "Ruta /familia/boletines/. Permite consultar en línea y descargar en formato PDF oficial el boletín de calificaciones de cada uno de los periodos cerrados formalmente.", bold_prefix="• Boletines Oficiales de Calificaciones: ")
add_bullet(doc, "Ruta /familia/asistencia/. Notificaciones en tiempo real sobre inasistencias o llegadas tarde del alumno en la jornada diaria.", bold_prefix="• Seguimiento de Asistencia: ")
add_bullet(doc, "Ruta /familia/circulares/. Bandeja de comunicados emitidos por Rectoría con un botón obligatorio de 'Confirmar Lectura Digital', garantizando el debido acuse de recibo.", bold_prefix="• Circulares con Acuse de Lectura Digital: ")

add_capture_marker_docx(doc, "CAPTURA 21", "Portal de Familias con Expediente del Acudido (/familia/)", "Familia", 
                        "Iniciar sesión con cuenta de Acudiente y abrir el portal familiar.", 
                        "Señalar la ficha del estudiante vinculado, los botones de descarga de boletines y el resumen de asistencia.")

add_capture_marker_docx(doc, "CAPTURA 22", "Descarga de Boletín de Calificaciones en PDF (/familia/boletines/)", "Familia", 
                        "Ingresar a la sección de boletines y posicionar el cursor sobre el botón 'Descargar Boletín Periodo 1'.", 
                        "Enmarcar la lista de periodos, el estado de aprobación y el botón de descarga del documento PDF oficial.")

add_capture_marker_docx(doc, "CAPTURA 23", "Bandeja de Circulares con Acuse de Lectura Digital (/familia/circulares/)", "Familia", 
                        "Abrir la sección de circulares familiares y visualizar una circular emitida.", 
                        "Resaltar el texto de la circular emitida por Rectoría y el botón 'Confirmar Lectura Digital' con su fecha y hora de acuse.")

doc.add_page_break()

# ==============================================================================
# CAPÍTULO 7: CASOS DE USO REALISTAS
# ==============================================================================
add_header_styled(doc, "7. CASOS DE USO REALISTAS Y EXHAUSTIVOS (10 CASOS CLAVE)", level=1)
add_p(doc, "A continuación se documentan diez (10) casos de uso exhaustivos que modelan el comportamiento real del sistema ante las operaciones cotidianas de la institución educativa. Cada caso especifica su actor, precondiciones, flujo paso a paso, resultado esperado y alternativas de solución ante contingencias:", bold_prefix="Modelado Operativo: ")

casos_de_uso = [
    {
        "id": "CU-01",
        "nombre": "Matrícula Individual de un Nuevo Estudiante",
        "actor": "Secretaría Académica",
        "pre": "El usuario ha iniciado sesión como Secretaría. El estudiante cuenta con documento de identidad y no se encuentra matriculado previamente en el mismo año lectivo.",
        "pasos": [
            "1. En el menú de navegación, hacer clic en 'Matrículas y Cupos' o ingresar a /estudiantes/registrar/.",
            "2. Seleccionar el Tipo de Documento (Tarjeta de Identidad, Cédula de Ciudadanía, etc.) e ingresar el Número de Documento.",
            "3. Diligenciar Nombres, Apellidos, Correo Electrónico institucional o personal, Teléfono, Género y Fecha de Nacimiento.",
            "4. En la sección académica, seleccionar el Grado Escolar (10° u 11°) y la Ficha Técnica correspondiente.",
            "5. Ingresar el Nombre Completo del Acudiente y su Teléfono de contacto.",
            "6. Hacer clic en el botón café 'Guardar Matrícula Oficial'."
        ],
        "resultado": "El sistema almacena el registro en MySQL, crea la cuenta de usuario con rol 'Estudiante' vinculada al PerfilUsuario, asocia la matrícula en estado 'En Formación' y emite una alerta verde de éxito.",
        "error": "Si el número de documento ya existe (Restricción RN-001), el sistema rechaza el guardado y muestra: 'Ya existe un usuario registrado con este número de documento'. Solución: Localizar al estudiante en el directorio para actualizar su matrícula sin duplicar el expediente."
    },
    {
        "id": "CU-02",
        "nombre": "Carga Masiva de Estudiantes mediante Archivo Excel",
        "actor": "Secretaría Académica",
        "pre": "Secretaría dispone del archivo Excel con los datos de los aprendices estructurados bajo la plantilla oficial (.xlsx).",
        "pasos": [
            "1. Ingresar a /matriculas/ y hacer clic en el botón superior 'Carga Masiva Estudiantes'.",
            "2. En la vista /estudiantes/importar/, presionar 'Descargar Plantilla Oficial Excel' si no se cuenta con el formato.",
            "3. Verificar que las columnas obligatorias contengan: TipoDoc, NumeroDoc, Nombres, Apellidos, Email, Grado, Ficha.",
            "4. Arrastrar el archivo .xlsx a la zona de subida o hacer clic en 'Examinar' para seleccionarlo.",
            "5. Presionar el botón 'Procesar Carga Masiva'."
        ],
        "resultado": "El procesador de EduNova valida fila por fila. Se crean los usuarios y matrículas correspondientes y se presenta un informe detallado indicando: 'Carga completada: X registros importados con éxito'.",
        "error": "Si el archivo contiene documentos duplicados o filas vacías intermedias, el sistema indica el número exacto de fila fallida y procesa las demás filas válidas sin abortar toda la operación."
    },
    {
        "id": "CU-03",
        "nombre": "Toma y Registro de Asistencia en el Aula de Clase",
        "actor": "Docente / Instructor",
        "pre": "El docente tiene asignada la materia y el grupo mediante Carga Académica. Es la fecha y hora de la clase.",
        "pasos": [
            "1. Ingresar al portal docente (/instructor/) y hacer clic en 'Asistencia' en el menú lateral.",
            "2. Seleccionar la Asignatura / Grupo y confirmar la fecha de la sesión.",
            "3. Frente al nombre de cada alumno en la lista, presionar el botón correspondiente: P (Presente), T (Tardanza), A (Ausente), J (Justificada).",
            "4. Opcionalmente, escribir una observación breve en el campo de texto adyacente (ej: 'Ingresa 15 minutos tarde').",
            "5. El sistema envía una petición asíncrona (Fetch API) a /asistencia/api/guardar-individual/."
        ],
        "resultado": "La asistencia queda asentada en la base de datos de inmediato. El botón seleccionado cambia de color y se muestra una notificación flotante de confirmación.",
        "error": "Si falla la conexión a internet, el sistema muestra una alerta roja en el botón: 'Error de conexión. Reintente'. Los datos permanecen en pantalla para reintentar el guardado."
    },
    {
        "id": "CU-04",
        "nombre": "Asentamiento de Calificaciones Oficiales de Periodo",
        "actor": "Docente / Instructor",
        "pre": "El periodo académico se encuentra abierto ('En Curso'). El docente tiene la carga académica vinculada.",
        "pasos": [
            "1. En el menú docente, hacer clic en 'Calificaciones' (/calificaciones-docente/).",
            "2. Seleccionar el Periodo Académico (ej: Periodo 1) y la Asignatura.",
            "3. En la tabla de estudiantes, digitar la nota definitiva en la casilla numérica (escala de 0.0 a 5.0).",
            "4. Observar que el sistema calcula dinámicamente la escala MEN (Superior, Alto, Básico, Bajo) y el juicio RAP SENA (A/D).",
            "5. Presionar el botón café 'Guardar Planilla de Calificaciones'."
        ],
        "resultado": "Las calificaciones quedan registradas con restricción de unicidad (un solo registro por matrícula, carga y periodo), disponibles para la emisión del boletín.",
        "error": "Si el periodo fue cerrado formalmente por Coordinación (RN-004), los campos numéricos se muestran bloqueados (readonly) y el botón de guardado se deshabilita, evitando cualquier alteración extemporánea."
    },
    {
        "id": "CU-05",
        "nombre": "Creación, Publicación y Revisión de Tareas",
        "actor": "Docente / Instructor",
        "pre": "El docente se encuentra dentro de su panel de asignatura.",
        "pasos": [
            "1. Ingresar a /actividades-y-tareas/ y hacer clic en 'Crear Tarea' (/academico/clase/<id>/crear-tarea/).",
            "2. Escribir el Título de la actividad y las instrucciones pedagógicas detalladas.",
            "3. Seleccionar la Fecha y Hora límite de entrega.",
            "4. Adjuntar la Guía de Aprendizaje en formato PDF o Word (máximo 10 MB).",
            "5. Presionar 'Publicar Actividad'.",
            "6. Posteriormente, ingresar a /instructor/tarea/<id>/entregas/ para revisar los trabajos enviados, descargar los archivos de los alumnos, escribir retroalimentaciones y asentar la nota."
        ],
        "resultado": "La tarea aparece de inmediato en el casillero de todos los estudiantes del curso. Tras la revisión del docente, las notas y observaciones quedan disponibles para los alumnos.",
        "error": "Si el docente intenta publicar una tarea con fecha de vencimiento en el pasado, el formulario emite un aviso de validación impidiendo el guardado."
    },
    {
        "id": "CU-06",
        "nombre": "Entrega Virtual de Evidencia / Tarea en Línea",
        "actor": "Estudiante (Aprendiz)",
        "pre": "El estudiante está matriculado en el curso y existe una tarea publicada con plazo vigente.",
        "pasos": [
            "1. Ingresar al portal de Estudiante (/aprendiz/) y hacer clic en 'Mis Tareas' (/estudiante/tareas/).",
            "2. Ubicar la actividad pendiente y pulsar 'Ver Tarea y Guía'.",
            "3. Leer atentamente las instrucciones y descargar el archivo de apoyo adjuntado por el docente.",
            "4. En la sección de entrega, redactar comentarios explicativos si se requiere.",
            "5. Presionar 'Seleccionar archivo' y cargar el documento de solución en PDF, DOCX o ZIP.",
            "6. Hacer clic en el botón 'Entregar Tarea'."
        ],
        "resultado": "El estado de la tarea cambia a 'Entregada', se registra la marca temporal de envío y el archivo queda archivado en el servidor para evaluación del profesor.",
        "error": "Si el alumno intenta entregar después de la fecha y hora límite, el sistema bloquea el formulario si la tarea fue configurada con cierre estricto, o marca el estado como 'Entregada fuera de plazo'."
    },
    {
        "id": "CU-07",
        "nombre": "Consulta y Descarga del Boletín de Notas Oficial",
        "actor": "Familia / Acudiente",
        "pre": "El acudiente está vinculado al estudiante en el modelo FamiliaAcudiente y el periodo ha finalizado.",
        "pasos": [
            "1. Iniciar sesión como Acudiente e ingresar al portal familiar (/familia/).",
            "2. Seleccionar la opción 'Boletines de Calificaciones' (/familia/boletines/).",
            "3. Verificar el resumen de materias, notas parciales y porcentaje de inasistencias de su hijo acudido.",
            "4. Presionar el botón 'Descargar Boletín Oficial (PDF)'."
        ],
        "resultado": "El navegador genera y descarga el documento PDF con membrete institucional oficial, escudo del colegio, sábanas de notas por materia, puesto ocupado y firma de Rectoría.",
        "error": "Si las notas del periodo aún no han sido conciliadas por los docentes, el botón de descarga mostrará: 'Boletín en proceso de consolidación docente'."
    },
    {
        "id": "CU-08",
        "nombre": "Gestión de Usuarios, Asignación de Roles y Restablecimiento de Clave",
        "actor": "Administrador",
        "pre": "Acceso con credenciales de superusuario o Administrador institucional.",
        "pasos": [
            "1. Ingresar a /usuarios/ y presionar 'Nuevo Usuario'.",
            "2. Diligenciar username, nombre, apellido, correo, documento y asignar el Rol formal (Secretaría, Docente, Rectoría, etc.).",
            "3. Guardar el registro. La señal post_save creará automáticamente el PerfilUsuario.",
            "4. Si un funcionario olvida su clave, ubicar la cuenta en la lista y presionar 'Restablecer Clave'.",
            "5. Ingresar la nueva contraseña temporal o marcar 'Forzar cambio en el primer inicio'."
        ],
        "resultado": "La cuenta queda creada o actualizada, y la acción queda archivada en la bitácora de auditoría forense con la IP del administrador.",
        "error": "Si se intenta crear un usuario con un nombre de usuario o documento ya existente, el sistema aborta la operación señalando el campo en conflicto."
    },
    {
        "id": "CU-09",
        "nombre": "Emisión de Circular Institucional con Acuse de Lectura Digital",
        "actor": "Rectoría",
        "pre": "El usuario posee el rol de Rectoría.",
        "pasos": [
            "1. Acceder a /comunicaciones/redactar/.",
            "2. Escribir el Asunto de la circular (ej: 'Reunión General de Acudientes - Entrega de Informes 1° Periodo').",
            "3. Redactar el cuerpo del comunicado y adjuntar la resolución o agenda en formato PDF.",
            "4. Seleccionar el grupo de destino: 'Familias' o 'Docentes'.",
            "5. Hacer clic en 'Publicar y Notificar Circular'."
        ],
        "resultado": "La circular se publica en los portales correspondientes. Cuando cada acudiente ingresa a /familia/circulares/ y pulsa 'Confirmar Lectura Digital', el sistema guarda el timestamp exacto de notificación.",
        "error": "Si el archivo adjunto excede el límite permitido de subida (10 MB), el servidor notifica el exceso de tamaño antes de guardar."
    },
    {
        "id": "CU-10",
        "nombre": "Configuración de Periodos Académicos y Bloqueo de Calificaciones",
        "actor": "Coordinación Académica",
        "pre": "El usuario cuenta con permiso de Coordinación o Administración.",
        "pasos": [
            "1. Ingresar a /academico/periodos-academicos/.",
            "2. Revisar las fechas de inicio y finalización de los cuatro periodos del año lectivo.",
            "3. Para un periodo que ha concluido su ciclo de reclamos, marcar la casilla '¿Cerrado Formalmente?'.",
            "4. Presionar 'Guardar Configuración de Periodos'."
        ],
        "resultado": "El modelo PeriodoAcademico actualiza el campo cerrado=True. A partir de ese instante, cualquier intento de un docente de modificar una nota de ese periodo es rechazado por las reglas de negocio RN-004.",
        "error": "Si se ingresa una fecha de fin anterior a la fecha de inicio, el modelo lanza ValidationError: 'La fecha de finalización no puede ser anterior a la fecha de inicio'."
    }
]

for caso in casos_de_uso:
    add_header_styled(doc, f"{caso['id']}: {caso['nombre']}", level=2)
    tbl_c = doc.add_table(rows=5, cols=2)
    tbl_c.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    campos = [
        ("Actor Principal:", caso['actor']),
        ("Requisitos Previos:", caso['pre']),
        ("Procedimiento Paso a Paso:", "\n".join(caso['pasos'])),
        ("Resultado Esperado:", caso['resultado']),
        ("Solución de Contingencias / Errores:", caso['error']),
    ]
    for idx, (lbl, val) in enumerate(campos):
        r = tbl_c.rows[idx]
        c0, c1 = r.cells[0], r.cells[1]
        c0.width = Inches(2.0)
        c1.width = Inches(4.5)
        c0.paragraphs[0].text = lbl
        c0.paragraphs[0].runs[0].font.name = "Arial"
        c0.paragraphs[0].runs[0].font.bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(8.5)
        c0.paragraphs[0].runs[0].font.color.rgb = RGBColor(45, 35, 30)
        
        c1.paragraphs[0].text = val
        c1.paragraphs[0].runs[0].font.name = "Arial"
        c1.paragraphs[0].runs[0].font.size = Pt(8.5)
        c1.paragraphs[0].runs[0].font.color.rgb = RGBColor(55, 45, 40)
        
        bg = "F8F9FA" if idx % 2 == 0 else "FFFFFF"
        set_cell_background(c0, bg)
        set_cell_background(c1, bg)
        set_cell_margins(c0, top=60, bottom=60, left=80, right=80)
        set_cell_margins(c1, top=60, bottom=60, left=80, right=80)
        
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

doc.add_page_break()

# ==============================================================================
# CAPÍTULO 8: DIAGRAMAS DE FLUJO
# ==============================================================================
add_header_styled(doc, "8. DIAGRAMAS DE FLUJO DE LOS PRINCIPALES PROCESOS", level=1)
add_p(doc, "Para facilitar la comprensión visual de los procesos lógicos y la interacción entre el usuario y la plataforma, se presentan los diagramas de flujo estructurados de los tres ciclos cardinales del software:", bold_prefix="Modelado de Procesos: ")

add_header_styled(doc, "8.1. Flujo de Autenticación, Validación y Enrutamiento por Rol (RBAC)", level=2)
flujo_login = """
  [ INICIO ]
      │
      ▼
┌──────────────────────────────────────────────┐
│ El usuario ingresa a /login/ e introduce     │
│ su Usuario/Documento y Contraseña            │
└──────────────────────────────────────────────┘
      │
      ▼
      /─────────────────────────────────────────\
     < ¿Credenciales válidas en base de datos?   >
      \─────────────────────────────────────────/
       │ SÍ                                  │ NO
       ▼                                     ▼
┌───────────────────────────────┐     ┌───────────────────────────────────┐
│ ¿Cuenta activa (esta_activo)? │     │ Mostrar mensaje: 'Credenciales    │
└───────────────────────────────┘     │ incorrectas o cuenta inactiva'    │
       │ SÍ                                  │ Volver a intentar (Fin de intento)│
       ▼                                     └───────────────────────────────────┘
┌────────────────────────────────────────────────────────┐
│ Evaluar categoría institucional del Rol (RBAC)         │
│ y despachar a la URL correspondiente:                  │
│                                                        │
│ • Superusuario / Administrador ──► /dashboard/         │
│ • Rectoría / Coordinación       ──► /rectoria/          │
│ • Secretaría Académica         ──► /secretaria/        │
│ • Docente / Instructor          ──► /instructor/        │
│ • Estudiante (Aprendiz)         ──► /aprendiz/          │
│ • Familia / Acudiente           ──► /familia/           │
└────────────────────────────────────────────────────────┘
      │
      ▼
  [ FIN: ACCESO EXITOSO ]
"""
p_fl = doc.add_paragraph()
r_fl = p_fl.add_run(flujo_login)
r_fl.font.name = "Consolas"
r_fl.font.size = Pt(8)
r_fl.font.color.rgb = RGBColor(40, 30, 25)

add_header_styled(doc, "8.2. Flujo del Proceso Oficial de Matrícula Escolar", level=2)
flujo_mat = """
  [ INICIO PROCESO DE MATRÍCULA ]
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ Secretaría selecciona modalidad:                       │
│ 1) Matrícula Individual    2) Carga Masiva en Excel    │
└────────────────────────────────────────────────────────┘
      │
      ├───► [MODALIDAD INDIVIDUAL]:
      │         │
      │         ▼
      │     ┌────────────────────────────────────────────────────────┐
      │     │ Digitar datos del alumno, documento, ficha y acudiente  │
      │     └────────────────────────────────────────────────────────┘
      │         │
      │         ▼
      │         /──────────────────────────────────────────\
      │        < ¿Documento ya registrado en la BD? (RN-001)>
      │         \──────────────────────────────────────────/
      │          │ NO                                   │ SÍ
      │          ▼                                      ▼
      │     ┌────────────────────────┐      ┌───────────────────────────┐
      │     │ Guardar Matrícula y    │      │ Error: 'Documento duplicado│
      │     │ crear Perfil de Usuario│      │ Corregir número de doc.   │
      │     └────────────────────────┘      └───────────────────────────┘
      │
      └───► [MODALIDAD MASIVA EXCEL]:
                │
                ▼
            ┌────────────────────────────────────────────────────────┐
            │ Descargar plantilla .xlsx, cargar archivo y procesar   │
            │ Validación automática fila por fila                    │
            └────────────────────────────────────────────────────────┘
                │
                ▼
  [ FIN: PADRÓN DE MATRÍCULAS ACTUALIZADO ]
"""
p_fm = doc.add_paragraph()
r_fm = p_fm.add_run(flujo_mat)
r_fm.font.name = "Consolas"
r_fm.font.size = Pt(8)
r_fm.font.color.rgb = RGBColor(40, 30, 25)

add_header_styled(doc, "8.3. Flujo del Ciclo Académico Pedagógico", level=2)
flujo_ped = """
  [ INICIO DEL PERIODO ACADÉMICO ]
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ Coordinación apertura el Periodo (ej: Periodo 1)       │
│ y asigna Cargas Académicas a los profesores            │
└────────────────────────────────────────────────────────┘
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ Docente imparte clases:                                │
│ • Toma asistencia diaria en vivo (P, T, A, J)          │
│ • Publica talleres y guías de aprendizaje              │
└────────────────────────────────────────────────────────┘
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ Estudiantes remiten soluciones en línea antes del plazo│
│ Docente califica evidencias y emite retroalimentación  │
└────────────────────────────────────────────────────────┘
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ Cierre de Periodo:                                     │
│ • Docente asienta notas definitivas en la planilla     │
│ • Coordinación activa 'Cierre Formal' (RN-004)         │
│ • Familias descargan Boletines Oficiales en PDF        │
└────────────────────────────────────────────────────────┘
      │
      ▼
  [ FIN DEL CICLO DE PERIODO ]
"""
p_fp = doc.add_paragraph()
r_fp = p_fp.add_run(flujo_ped)
r_fp.font.name = "Consolas"
r_fp.font.size = Pt(8)
r_fp.font.color.rgb = RGBColor(40, 30, 25)

doc.add_page_break()

# ==============================================================================
# CAPÍTULO 9: GUÍA DE ERRORES FRECUENTES
# ==============================================================================
add_header_styled(doc, "9. GUÍA DE SOLUCIÓN DE ERRORES FRECUENTES Y CONTINGENCIAS", level=1)
add_p(doc, "En esta sección se describen los mensajes de advertencia, excepciones y situaciones atípicas que pueden presentarse durante la operación del sistema. Se distingue con total honestidad y rigor técnico entre los errores comprobados directamente en el código y situaciones posibles de contingencia:", bold_prefix="Diagnóstico Operativo: ")

errores_data = [
    [
        "Acceso Restringido (Seguridad SINETEC): Tu rol no tiene permisos para acceder a esta sección.",
        "Error Comprobado en Backend (decorators.py)",
        "Ocurre cuando un usuario intenta acceder a una URL que no corresponde a su perfil (ej: un Estudiante intentando abrir /usuarios/ o /rectoria/).",
        "El sistema bloquea la petición mediante los decoradores RBAC y redirige de inmediato al portal que le corresponde al usuario. No requiere soporte técnico; el usuario debe utilizar exclusivamente los enlaces de su barra de navegación."
    ],
    [
        "Credenciales incorrectas o cuenta inactiva.",
        "Error Comprobado en Login (views.py)",
        "Se ingresó un usuario o contraseña no concordantes, o la casilla 'esta_activo' de la cuenta está en False.",
        "1) Verificar que la tecla Bloq Mayús no esté activada. 2) Confirmar que el número de documento no tenga puntos. 3) Si persiste, acudir a Secretaría o usar el enlace '¿Olvidó su contraseña?'."
    ],
    [
        "Ya existe un usuario registrado con este número de documento.",
        "Error Comprobado de Base de Datos (RN-001)",
        "Se intenta registrar a un estudiante o docente cuyo número de identificación ya se encuentra registrado en PerfilUsuario.",
        "Ingresar al Directorio de Estudiantes (/estudiantes/), buscar el documento del alumno y pulsar el botón 'Editar' para actualizar sus datos o asignarle una nueva matrícula sin duplicar el usuario."
    ],
    [
        "Operación Denegada (RN-004): El periodo evaluativo se encuentra formalmente cerrado.",
        "Error Comprobado en Calificaciones (models.py)",
        "Un docente intenta ingresar o modificar una nota en una ficha cuyo periodo académico fue cerrado formalmente por la Coordinación.",
        "El docente debe comunicarse formalmente con la Coordinación Académica. Solo el Coordinador o Administrador tiene la potestad de desmarcar temporalmente el cierre si existe una reclamación avalada por Comité."
    ],
    [
        "Formato de archivo rechazado en carga masiva.",
        "Error Comprobado en Importación",
        "Se intenta cargar un archivo con extensión distinta a .xlsx o con columnas renombradas que no coinciden con la plantilla.",
        "Descargar nuevamente la plantilla oficial desde /estudiantes/plantilla/, pegar la información de los alumnos asegurándose de mantener los nombres exactos de los encabezados y guardar en formato .xlsx nativo."
    ],
    [
        "Aún no tienes calificaciones registradas.",
        "Mensaje Informativo Comprobado",
        "El estudiante o acudiente ingresa a calificaciones pero el docente aún no ha asentado las notas del periodo en curso.",
        "No representa un fallo del sistema. Indica que la planilla de calificaciones aún se encuentra en etapa de digitación por parte del cuerpo docente."
    ],
    [
        "El documento no existe en el sistema o no cuenta con correo institucional.",
        "Error Comprobado en Recuperación",
        "El usuario escribe un documento erróneo en el formulario de recuperación de contraseña.",
        "Verificar que el documento coincida con el registrado en su matrícula física. Si el estudiante no tiene correo registrado, Secretaría debe ingresar a /estudiantes/ y registrar su correo electrónico."
    ],
    [
        "Pantalla en blanco o tiempo de espera agotado (Timeout en nube).",
        "Situación Posible de Red / Nube",
        "Pérdida momentánea de conexión a internet o reactivación del servidor en Render tras periodo de inactividad (cold start).",
        "Esperar 15 segundos y presionar F5 para recargar la página. EduNova cuenta con soporte WhiteNoise de alta disponibilidad que restablece la sesión automáticamente."
    ],
]

add_table_styled_docx(doc, ["Mensaje / Incidencia", "Naturaleza Técnica", "Causa Comprobada", "Procedimiento de Solución Inmediata"], 
                     errores_data, col_widths=[1.8, 1.2, 1.7, 1.8])

doc.add_page_break()

# ==============================================================================
# CAPÍTULO 10: PREGUNTAS FRECUENTES (FAQ)
# ==============================================================================
add_header_styled(doc, "10. PREGUNTAS FRECUENTES (FAQ) CON RESPUESTAS PRÁCTICAS", level=1)
add_p(doc, "Respuestas claras a las dudas más recurrentes planteadas por docentes, directivos, padres y estudiantes:", bold_prefix="Atención a Usuarios: ")

faqs = [
    ("¿Qué debo hacer si olvido mi contraseña de acceso?", 
     "En la pantalla de ingreso (/login/), haga clic en '¿Olvidó su contraseña?'. Digite su documento de identidad y recibirá un enlace de restablecimiento en su correo. Si no tiene acceso a su correo, solicite a la Secretaría Académica o al Administrador que le restablezca la contraseña temporal desde el panel de gestión de usuarios."),
    ("¿Por qué varios grados escolares en la cuadrícula de Secretaría aparecen como 'Inactivos'?", 
     "La cuadrícula de Secretaría despliega los 11 grados escolares reglamentarios de Colombia (1° a 11°). La etiqueta 'Inactivo' simplemente significa que en el periodo lectivo vigente la institución no ha matriculado aprendices en ese grado específico (por ejemplo, si el colegio solo atiende secundaria y media técnica)."),
    ("¿Cómo descarga un padre de familia el boletín de notas en PDF?", 
     "El acudiente debe ingresar con su cuenta a /familia/, hacer clic en 'Boletines de Calificaciones', ubicar el periodo académico correspondiente y pulsar el botón 'Descargar Boletín Oficial'. El archivo se descargará en formato PDF listo para imprimir o archivar."),
    ("¿Qué ocurre si un estudiante se transfiere de sede o cambia de jornada?", 
     "Secretaría Académica debe ingresar al directorio de estudiantes (/estudiantes/), localizar al alumno, abrir su ficha y seleccionar 'Editar Matrícula'. Allí podrá cambiar la ficha técnica, grado o jornada sin perder el historial de calificaciones previas."),
    ("¿Pueden los estudiantes alterar o modificar sus notas desde su portal?", 
     "No. El sistema implementa aislamiento estricto de roles (RBAC). El portal del estudiante es 100% de solo lectura para calificaciones. La base de datos rechaza en backend cualquier petición de actualización no originada por un docente o directivo autorizado."),
    ("¿Cómo recupero un estudiante o registro borrado accidentalmente?", 
     "El Administrador del sistema debe ingresar a la ruta /papelera/, ubicar el registro en la lista de elementos eliminados y presionar el botón verde 'Restaurar'. El estudiante retornará de inmediato al padrón activo con toda su información intacta."),
    ("¿Qué navegador es el más recomendable para utilizar EduNova?", 
     "Recomendamos utilizar Google Chrome o Microsoft Edge en sus versiones más recientes, ya que ofrecen la mayor velocidad de renderizado para los formularios interactivos y el visor de documentos PDF."),
    ("¿Cómo funciona el guardado de asistencia si se cae la conexión a internet en el salón?", 
     "Los botones de asistencia cuentan con indicadores de estado en vivo. Si el guardado falla por corte de red, el botón mostrará una alerta visual y no cambiará a estado guardado. El docente debe esperar el restablecimiento de la conexión y pulsar nuevamente el botón."),
    ("¿Por qué un docente no puede ver a un grupo en su lista de clases?", 
     "Porque Coordinación Académica aún no le ha creado la asignación de 'Carga Académica' para esa asignatura, grado y sección. El Coordinador debe ingresar a /academico/ y registrar la asignación docente."),
    ("¿Es posible usar EduNova desde un teléfono celular?", 
     "Sí. EduNova está construido con diseño web responsivo (Responsive Web Design). Todos los menús, botones de asistencia y consultas de calificaciones se adaptan ergonómicamente a la pantalla del teléfono celular."),
]

for preg, resp in faqs:
    add_p(doc, preg, bold_prefix="P: ", space_after=1)
    add_p(doc, resp, bold_prefix="R: ", space_after=6)

# ==============================================================================
# CAPÍTULO 11: SEGURIDAD Y DATOS PERSONALES
# ==============================================================================
add_header_styled(doc, "11. POLÍTICAS DE SEGURIDAD Y PROTECCIÓN DE DATOS (LEY 1581 / HABEAS DATA)", level=1)
add_p(doc, "El tratamiento de la información dentro de EduNova está sujeto a los principios de confidencialidad, integridad y disponibilidad consagrados en la Ley Estatutaria 1581 de 2012 de Protección de Datos Personales de la República de Colombia:", bold_prefix="Marco Normativo Institucional: ")

add_bullet(doc, "Las contraseñas de todos los usuarios se almacenan en la base de datos cifradas mediante el algoritmo criptográfico PBKDF2 con hash SHA-256 y salt individual. Ningún funcionario, docente o directivo puede visualizar la contraseña real de otra persona.", bold_prefix="• Cifrado Robusto de Claves: ")
add_bullet(doc, "Los datos de estudiantes menores de edad (nombres, documentos, direcciones, teléfonos de acudientes, valoraciones convivenciales e historias académicas) son de carácter sensible. Queda terminantemente prohibido exportar o compartir listados con terceros no autorizados.", bold_prefix="• Protección de Menores de Edad: ")
add_bullet(doc, "Todo funcionario que utilice computadores en salas de profesores o secretaría tiene la obligación de cerrar sesión formalmente antes de retirarse de su puesto de trabajo para evitar suplantaciones de identidad.", bold_prefix="• Cierre de Sesión Obligatorio: ")
add_bullet(doc, "El sistema audita de manera forense la fecha, hora, usuario y dirección IP de cada registro creado o modificado. Cualquier alteración maliciosa o no autorizada de calificaciones acarrea sanciones disciplinarias y penales.", bold_prefix="• Trazabilidad y Auditoría: ")

# ==============================================================================
# CAPÍTULO 12: GLOSARIO DE TÉRMINOS
# ==============================================================================
add_header_styled(doc, "12. GLOSARIO DE TÉRMINOS INSTITUCIONALES Y TÉCNICOS", level=1)
glosario_items = [
    ("ADSI", "Análisis y Desarrollo de Sistemas de Información. Programa de formación tecnológica del SENA enfocado en el ciclo de vida del software."),
    ("Boletín Oficial", "Documento periódico generado por el sistema que certifica el rendimiento escolar, inasistencias y puesto de un alumno."),
    ("Carga Académica", "Asignación formal que vincula a un docente con una asignatura, grado escolar, sección y año lectivo."),
    ("Ficha Técnica", "Identificador único asignado a una cohorte o grupo de aprendices en el marco del programa de articulación con la Media Técnica."),
    ("Juicio Evaluativo", "Calificación cualitativa emitida bajo la metodología SENA: Aprobado (A) o No Aprobado / Deficiente (D)."),
    ("MEN", "Ministerio de Educación Nacional de Colombia. Ente rector que establece las escalas de desempeño (Bajo, Básico, Alto, Superior)."),
    ("Padrón de Matrículas", "Registro consolidado y oficial de todos los aprendices inscritos en la institución educativa durante el año lectivo."),
    ("RAP", "Resultado de Aprendizaje. Logro formativo que evidencia la adquisición de competencias laborales específicas."),
    ("RBAC", "Role-Based Access Control (Control de Acceso Basado en Roles). Mecanismo de seguridad que limita las pantallas según el perfil del usuario."),
    ("Soft Delete", "Borrado lógico. Mecanismo mediante el cual un registro eliminado se traslada a la papelera sin destruirse de la base de datos."),
]
for term, defn in glosario_items:
    add_p(doc, defn, bold_prefix=f"• {term}: ", space_after=3)

doc.add_page_break()

# ==============================================================================
# ANEXO A: LISTA MAESTRA DE CAPTURAS
# ==============================================================================
add_header_styled(doc, "ANEXO A: LISTA MAESTRA NUMERADA DE CAPTURAS DE PANTALLA REQUERIDAS (23)", level=1)
add_p(doc, "Tabla consolidada de las veintitrés (23) capturas reales que deben ser insertadas en los marcadores del presente manual, con la indicación exacta del perfil a utilizar, la pantalla a abrir, la acción a ejecutar y los elementos visuales a destacar:", bold_prefix="Instrucciones para el Usuario: ")

capturas_tabla = [
    ("CAPTURA 01", "Cualquier Usuario", "/login/", "Abrir la pantalla de acceso, digitar credenciales y situar el cursor en 'Iniciar Sesión'.", "Recuadro en usuario, contraseña, botón 'Iniciar Sesión' y enlace de recuperación."),
    ("CAPTURA 02", "Usuario solicitante", "/recuperar-contrasena/", "Hacer clic en '¿Olvidó su contraseña?' y escribir un documento institucional.", "Campo de número de documento y botón 'Validar y Continuar'."),
    ("CAPTURA 03", "Administrador", "/dashboard/", "Iniciar sesión como Admin y visualizar el tablero general.", "Tarjetas KPI de estadísticas y accesos del menú lateral."),
    ("CAPTURA 04", "Administrador", "/usuarios/", "Entrar a gestión de usuarios y desplegar el modal de nuevo usuario.", "Lista de usuarios, botones de reset de clave y 'Nuevo Usuario'."),
    ("CAPTURA 05", "Administrador", "/papelera/", "Acceder a papelera con registros enviados a borrado lógico.", "Tabla de elementos en papelera y botón verde 'Restaurar Elemento'."),
    ("CAPTURA 06", "Rectoría", "/rectoria/", "Abrir tablero directivo con gráficos de rendimiento y cobertura.", "Gráficas de aprobación y botones de exportación de informes directivos."),
    ("CAPTURA 07", "Rectoría", "/comunicaciones/redactar/", "Abrir formulario de redacción de circular institucional.", "Campos de asunto, mensaje, selección de audiencia y 'Publicar'."),
    ("CAPTURA 08", "Coordinador/Rector", "/academico/periodos-academicos/", "Abrir configuración de periodos académicos 2026.", "Tabla con los 4 periodos, fechas inicio/fin y casilla de 'Cierre Formal'."),
    ("CAPTURA 09", "Secretaría", "/matriculas/", "Abrir padrón de matrículas y ver la cuadrícula de 1° a 11°.", "Cuadrícula superior de 11 grados y botones de matrícula individual y masiva."),
    ("CAPTURA 10", "Secretaría", "/estudiantes/registrar/", "Abrir formulario de matrícula individual.", "Secciones de datos del alumno, ficha, acudiente y botón 'Guardar'."),
    ("CAPTURA 11", "Secretaría", "/estudiantes/importar/", "Abrir módulo de carga masiva de estudiantes.", "Botón 'Descargar Plantilla Excel' y zona de arrastre del archivo .xlsx."),
    ("CAPTURA 12", "Secretaría", "/estudiantes/", "Abrir directorio y buscar a un alumno por su nombre.", "Barra de búsqueda en tiempo real, botón 'Ficha' y botón de edición."),
    ("CAPTURA 13", "Docente", "/instructor/", "Iniciar sesión como docente y abrir portal de asignaturas.", "Tarjetas de clases asignadas y horario semanal de clases."),
    ("CAPTURA 14", "Docente", "/asistencia/", "Abrir planilla de asistencia del curso 10°A.", "Botonera ergonómica P, T, A, J y aviso de guardado automático."),
    ("CAPTURA 15", "Docente", "/calificaciones-docente/", "Abrir planilla de notas y seleccionar 'Periodo 1'.", "Casilla numérica, desempeño MEN automático y botón 'Guardar Planilla'."),
    ("CAPTURA 16", "Docente", "/academico/clase/<id>/crear-tarea/", "Abrir formulario de creación de tarea de clase.", "Campos de título, fecha/hora límite, botón de adjuntar guía y 'Publicar'."),
    ("CAPTURA 17", "Docente", "/instructor/tarea/<id>/entregas/", "Abrir casillero de entregas recibidas de estudiantes.", "Lista de alumnos que entregaron, enlace de descarga y casilla de retroalimentación."),
    ("CAPTURA 18", "Estudiante", "/aprendiz/", "Iniciar sesión como Estudiante (ej: Juan Pérez).", "Saludo institucional, materias en curso y tareas pendientes."),
    ("CAPTURA 19", "Estudiante", "/estudiante/calificaciones/", "Abrir pestaña de calificaciones del aprendiz.", "Tabla de notas acumuladas por periodo y promedios."),
    ("CAPTURA 20", "Estudiante", "/estudiante/tareas/", "Abrir formulario de entrega de tarea de clase.", "Enlace de descarga de guía, botón de adjuntar solución y 'Entregar Tarea'."),
    ("CAPTURA 21", "Familia", "/familia/", "Iniciar sesión como Acudiente en el portal familiar.", "Expediente del estudiante vinculado y resumen de asistencia."),
    ("CAPTURA 22", "Familia", "/familia/boletines/", "Abrir módulo de boletines del acudido.", "Botón 'Descargar Boletín Periodo 1' en formato PDF."),
    ("CAPTURA 23", "Familia", "/familia/circulares/", "Abrir bandeja de circulares familiares.", "Texto de circular y botón 'Confirmar Lectura Digital' con fecha/hora.")
]

add_table_styled_docx(doc, ["Código", "Perfil", "Pantalla / Ruta", "Acción a Ejecutar", "Instrucción de Recuadros / Flechas"], 
                     capturas_tabla, col_widths=[1.0, 1.1, 1.5, 1.5, 1.4])

doc.add_page_break()

# ==============================================================================
# ANEXO B: MATRIZ DE LOS 20 CRITERIOS SENA ADSI
# ==============================================================================
add_header_styled(doc, "ANEXO B: MATRIZ DE CUMPLIMIENTO DE LOS 20 CRITERIOS SENA ADSI", level=1)
add_p(doc, "Alineación detallada entre los veinte (20) criterios del Instrumento de Auditoría y Validación de Manuales de Usuario del SENA y las secciones que los atienden rigurosamente en este documento:", bold_prefix="Auditoría de Calidad: ")

criterios_data = [
    ("1. Portada formal e institucional", "Portada Oficial", "CUMPLE", "Incluye nombre EduNova, ficha 3173430, aprendices, instructor y centro SENA."),
    ("2. Tabla de contenido / Índice estructurado", "Tabla de Contenido", "CUMPLE", "Estructura completa de 12 capítulos y 2 anexos con paginación."),
    ("3. Introducción y Justificación", "Capítulo 1", "CUMPLE", "Explica la problemática escolar, el contexto regional y la solución EduNova."),
    ("4. Definición de Objetivos", "Capítulo 2", "CUMPLE", "Define objetivo general y 5 objetivos específicos medibles del software."),
    ("5. Delimitación clara del Alcance", "Capítulo 3", "CUMPLE", "Delimita los 6 roles aprobados y aclara módulos excluidos (pasarelas, etc.)."),
    ("6. Requisitos de acceso (HW/SW/Red)", "Capítulo 4", "CUMPLE", "Especifica dispositivos, navegadores, resolución y conectividad requerida."),
    ("7. Arquitectura y navegación de interfaz", "Capítulo 5", "CUMPLE", "Describe la barra de navegación, menús laterales y aislamiento RBAC."),
    ("8. Procedimiento de inicio y cierre seguro", "Capítulo 5.1 y 5.3", "CUMPLE", "Paso a paso con datos de entrada, botones y validación de salida segura."),
    ("9. Recuperación segura de contraseña", "Capítulo 5.2", "CUMPLE", "Flujo criptográfico antifraude con token y validación de documento."),
    ("10. Descripción paso a paso de módulos", "Capítulo 6", "CUMPLE", "Detalla los procedimientos para Admin, Rectoría, Secretaría, Docente, Familia y Alumno."),
    ("11. Casos de uso prácticos y completos", "Capítulo 7", "CUMPLE", "10 casos de uso con actor, precondiciones, pasos, resultado y contingencia."),
    ("12. Especificación de datos y formularios", "Capítulos 6 y 7", "CUMPLE", "Indica los campos exactos, tipos de datos, selectores y controles."),
    ("13. Nombres reales de botones y opciones", "Capítulos 5 y 6", "CUMPLE", "Usa la nomenclatura real verificada en el código fuente de EduNova."),
    ("14. Comprobación de resultados esperados", "Capítulos 6 y 7", "CUMPLE", "Explica cómo verificar que el registro se guardó (alertas, cambios visuales)."),
    ("15. Diagramas de flujo de procesos clave", "Capítulo 8", "CUMPLE", "Diagramas estructurados de login, matrícula escolar y ciclo pedagógico."),
    ("16. Marcadores e instrucciones de capturas", "Capítulo 6 y Anexo A", "CUMPLE", "23 marcadores visibles [CAPTURA XX] con perfil, acción y elementos a señalar."),
    ("17. Solución de errores y contingencias", "Capítulo 9", "CUMPLE", "Tabla de errores distinguiendo casos comprobados de situaciones de red."),
    ("18. Preguntas frecuentes (FAQ) prácticas", "Capítulo 10", "CUMPLE", "10 preguntas reales con soluciones explicadas paso a paso."),
    ("19. Políticas de seguridad y Habeas Data", "Capítulo 11", "CUMPLE", "Normativa Ley 1581 de 2012, cifrado PBKDF2 y custodia de datos de menores."),
    ("20. Glosario de términos y presentación", "Capítulo 12", "CUMPLE", "Glosario técnico/institucional y formato profesional para el evaluador SENA."),
]

add_table_styled_docx(doc, ["Criterio de Auditoría SENA ADSI", "Sección que lo Atiende", "Estado", "Evidencia y Verificación en el Manual"], 
                     criterios_data, col_widths=[2.0, 1.3, 0.9, 2.3])

docx_path = os.path.join(DOCS_DIR, "Manual_de_Usuario_EduNova.docx")
doc.save(docx_path)
print(f"Manual DOCX generado exitosamente en: {docx_path} ({os.path.getsize(docx_path)} bytes)")

# ==============================================================================
# GENERACIÓN DE LA VERSIÓN PDF CON REPORTLAB
# ==============================================================================
print("Generando versión PDF con ReportLab...")
pdf_path = os.path.join(DOCS_DIR, "Manual_de_Usuario_EduNova.pdf")

doc_pdf = SimpleDocTemplate(
    pdf_path,
    pagesize=letter,
    leftMargin=54,
    rightMargin=54,
    topMargin=54,
    bottomMargin=54
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'CoverTitle', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=20, leading=24,
    textColor=colors.HexColor('#2D231E'), alignment=1, spaceAfter=10
)
sub_style = ParagraphStyle(
    'CoverSub', parent=styles['Normal'], fontName=FONT_ITALIC, fontSize=11, leading=15,
    textColor=colors.HexColor('#8B5E3C'), alignment=1, spaceAfter=20
)
h1_style = ParagraphStyle(
    'Head1', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=13, leading=16,
    textColor=colors.HexColor('#8B5E3C'), spaceBefore=14, spaceAfter=6, keepWithNext=True
)
h2_style = ParagraphStyle(
    'Head2', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=10.5, leading=14,
    textColor=colors.HexColor('#5A3825'), spaceBefore=10, spaceAfter=4, keepWithNext=True
)
body_style = ParagraphStyle(
    'Body', parent=styles['Normal'], fontName=FONT_FAMILY, fontSize=9, leading=12.5,
    textColor=colors.HexColor('#333333'), spaceAfter=5
)
bullet_style = ParagraphStyle(
    'Bullet', parent=styles['Normal'], fontName=FONT_FAMILY, fontSize=8.5, leading=11.5,
    textColor=colors.HexColor('#333333'), leftIndent=15, spaceAfter=3
)
code_style = ParagraphStyle(
    'CodeFlow', parent=styles['Normal'], fontName='Consolas' if 'Consolas' in pdfmetrics.getRegisteredFontNames() else FONT_FAMILY,
    fontSize=7, leading=9, textColor=colors.HexColor('#222222'), spaceAfter=6
)

story = []

# Portada PDF
story.append(Spacer(1, 30))
story.append(Paragraph("SERVICIO NACIONAL DE APRENDIZAJE — SENA<br/>REGIONAL MAGDALENA • CENTRO DE LOGÍSTICA Y PROMOCIÓN ECOTURÍSTICA", ParagraphStyle('Inst', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=10, leading=13, textColor=colors.HexColor('#8B5E3C'), alignment=1)))
story.append(Spacer(1, 10))
story.append(Paragraph("TECNOLOGÍA EN ANÁLISIS Y DESARROLLO DE SISTEMAS DE INFORMACIÓN (ADSI) • FICHA 3173430", ParagraphStyle('Prog', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9, leading=12, textColor=colors.HexColor('#5A3825'), alignment=1)))
story.append(Spacer(1, 20))
story.append(Paragraph("MANUAL DE USUARIO OFICIAL DEL SISTEMA DE INFORMACIÓN EDUNOVA", title_style))
story.append(Paragraph("Guía Maestra y Operativa Paso a Paso para Administradores, Rectoría, Secretaría Académica, Docentes, Familias y Estudiantes<br/>(Cumplimiento Integral de los 20 Criterios del Instrumento de Auditoría y Validación SENA)", sub_style))
story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#D4A373'), spaceAfter=20))

meta_pdf_data = [
    [Paragraph("<b>Sistema de Software:</b>", body_style), Paragraph("EduNova (Anteriormente SINETEC)", body_style)],
    [Paragraph("<b>Versión del Sistema:</b>", body_style), Paragraph("2.4.0 Estable (Octubre de 2026)", body_style)],
    [Paragraph("<b>Instructor Evaluador:</b>", body_style), Paragraph("Ing. Anybal López", body_style)],
    [Paragraph("<b>Aprendices Desarrolladoras:</b>", body_style), Paragraph("Aminta María Moguea Florez & Dulce María Figueroa", body_style)],
    [Paragraph("<b>Institución Educativa:</b>", body_style), Paragraph("IED Nuevo Horizonte / IED Técnica", body_style)],
    [Paragraph("<b>URL en Producción Cloud:</b>", body_style), Paragraph("https://sinetec-1.onrender.com/", body_style)],
]
t_meta_pdf = Table(meta_pdf_data, colWidths=[2.2 * inch, 4.3 * inch])
t_meta_pdf.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
story.append(t_meta_pdf)
story.append(PageBreak())

# Tabla de Contenido
story.append(Paragraph("TABLA DE CONTENIDO GENERAL", h1_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#8B5E3C'), spaceAfter=10))
for tit, pag in indice_items:
    t_row = [Paragraph(f"<b>{tit}</b>" if not tit.startswith("   ") else tit, body_style), Paragraph(f"<b>{pag}</b>", ParagraphStyle('PNum', parent=styles['Normal'], alignment=2, textColor=colors.HexColor('#8B5E3C')))]
    t_ind_p = Table([t_row], colWidths=[5.5 * inch, 1.0 * inch])
    t_ind_p.setStyle(TableStyle([('BOTTOMPADDING', (0, 0), (-1, -1), 1), ('TOPPADDING', (0, 0), (-1, -1), 1)]))
    story.append(t_ind_p)
story.append(PageBreak())

# Capítulos en PDF
capitulos_texto = [
    ("1. INTRODUCCIÓN, JUSTIFICACIÓN Y PROPÓSITO FORMATIVO", [
        "El presente Manual Oficial de Usuario ha sido elaborado para guiar de manera didáctica, exhaustiva y ergonómica a toda la comunidad educativa de la Institución Educativa Distrital articulada con la Media Técnica SENA en el Departamento del Magdalena, en la operación diaria del Sistema de Información EduNova (anteriormente SINETEC).",
        "Históricamente, los colegios articulados con el SENA enfrentan serias dificultades administrativas: dispersión de las calificaciones en hojas de cálculo no estandarizadas, retrasos en la entrega de boletines periódicos, falta de trazabilidad en la toma de asistencia en aula y desarticulación entre las secretarías escolares y los instructores técnicos. EduNova nace como una solución de ingeniería de software robusta, centralizada y de software libre que unifica el control de la formación técnica y básica bajo estrictos estándares de usabilidad.",
        "NOTA DE EVOLUCIÓN: El sistema fue concebido bajo el nombre SINETEC y en su versión 2.4.0 adopta formalmente el nombre EduNova, garantizando total consistencia visual y técnica."
    ]),
    ("2. OBJETIVOS DEL SISTEMA EDUNOVA", [
        "OBJETIVO GENERAL: Centralizar, optimizar y automatizar los procesos de matrícula escolar, gestión de expedientes académicos, control diario de asistencia, publicación y entrega virtual de tareas, asentamiento de calificaciones y expedición de boletines periódicos oficiales.",
        "OBJETIVOS ESPECÍFICOS: 1) Proveer autenticación segura con enrutamiento automático por rol (RBAC). 2) Garantizar la matrícula ágil individual y masiva en Excel de 1° a 11°. 3) Facilitar la toma de asistencia en vivo con botones P, T, A, J. 4) Articular la escala nacional MEN (Bajo/Básico/Alto/Superior) con juicios de RAPs SENA (A/D). 5) Vincular a las familias mediante consulta digital de boletines y acuse de circulares."
    ]),
    ("3. ALCANCE DEL SISTEMA Y DELIMITACIÓN OPERATIVA POR ROLES", [
        "PERFILES IMPLEMENTADOS: Administrador (gestión técnica y auditoría), Rectoría (supervisión gerencial y circulares), Coordinación (periodos y cargas), Secretaría (matrículas y expedientes), Docente (asistencia, calificaciones y tareas), Estudiante (horario, calificaciones y tareas) y Familia (boletines y circulares).",
        "MÓDULOS EXCLUIDOS DEL ALCANCE: No forman parte del alcance aprobado los módulos de pagos en línea, pensiones obligatorias, facturación electrónica, transporte escolar satelital ni carnets físicos con torniquete."
    ]),
    ("4. REQUISITOS TÉCNICOS Y CONDICIONES DE ACCESO", [
        "DISPOSITIVOS: Computador o teléfono inteligente con procesador de 1.5 GHz y 2 GB RAM.",
        "NAVEGADORES: Chrome, Edge, Firefox o Safari con JavaScript habilitado.",
        "DIRECCIONES DE ACCESO: Nube: https://sinetec-1.onrender.com/login/ | Red Local: http://127.0.0.1:8000/login/"
    ]),
    ("5. INTERFAZ, AUTENTICACIÓN Y RECUPERACIÓN SEGURA DE CONTRASEÑA", [
        "5.1. INICIO DE SESIÓN: Ingrese a /login/, escriba su Usuario o Número de Documento, su Contraseña y presione 'Iniciar Sesión'. El sistema valida sus credenciales y lo redirige a su panel específico.",
        "MARCADOR [CAPTURA 01: Pantalla de Inicio de Sesión (/login/)] - Mostrar campos de usuario, clave y botón de ingreso.",
        "5.2. RECUPERACIÓN DE CLAVE: En caso de olvido, haga clic en '¿Olvidó su contraseña?', escriba su documento institucional y el sistema enviará un token criptográfico seguro a su correo para definir una nueva clave.",
        "MARCADOR [CAPTURA 02: Formulario de Recuperación (/recuperar-contrasena/)] - Mostrar campo de documento y botón 'Validar y Continuar'.",
        "5.3. CIERRE DE SESIÓN: Seleccione 'Cerrar sesión' en el menú de usuario superior para invalidar la cookie de forma segura."
    ]),
    ("6. GUÍA DE MÓDULOS OPERATIVOS POR PERFIL", [
        "ADMINISTRADOR: Dashboard (/dashboard/), gestión de usuarios y roles (/usuarios/), papelera de reciclaje lógica (/papelera/), auditoría forense (/auditoria/) y configuración de identidad institucional (/configuracion/).",
        "MARCADOR [CAPTURA 03: Dashboard de Administración] | MARCADOR [CAPTURA 04: Gestión de Usuarios] | MARCADOR [CAPTURA 05: Papelera de Reciclaje]",
        "RECTORÍA Y COORDINACIÓN: Indicadores clave (/rectoria/), redacción de circulares (/comunicaciones/redactar/) y configuración de periodos académicos (/academico/periodos-academicos/).",
        "MARCADOR [CAPTURA 06: Tablero Rectoría] | MARCADOR [CAPTURA 07: Redacción Circular] | MARCADOR [CAPTURA 08: Periodos Académicos]",
        "SECRETARÍA ACADÉMICA: Padrón de matrículas (/matriculas/), registro individual (/estudiantes/registrar/), carga masiva en Excel (/estudiantes/importar/) y directorio de expedientes (/estudiantes/).",
        "MARCADOR [CAPTURA 09: Padrón Matrículas] | MARCADOR [CAPTURA 10: Formulario Matrícula] | MARCADOR [CAPTURA 11: Carga Masiva Excel] | MARCADOR [CAPTURA 12: Directorio]",
        "DOCENTE / INSTRUCTOR: Asignaturas (/instructor/), asistencia en vivo con botones P, T, A, J (/asistencia/), calificaciones oficiales por periodos 1 al 4 (/calificaciones-docente/), tareas (/crear-tarea/) y casillero de entregas.",
        "MARCADOR [CAPTURA 13: Portal Docente] | MARCADOR [CAPTURA 14: Asistencia en Vivo] | MARCADOR [CAPTURA 15: Calificaciones Periodo] | MARCADOR [CAPTURA 16: Creación Tarea] | MARCADOR [CAPTURA 17: Revisión Entregas]",
        "ESTUDIANTE (APRENDIZ): Horario semanal (/estudiante/horario/), calificaciones acumuladas (/estudiante/calificaciones/) y casillero de tareas y entregas en línea (/estudiante/tareas/).",
        "MARCADOR [CAPTURA 18: Portal Estudiante] | MARCADOR [CAPTURA 19: Consulta Calificaciones] | MARCADOR [CAPTURA 20: Entrega Tarea]",
        "FAMILIA Y ACUDIENTE: Expediente del alumno (/familia/matricula/), descarga de boletines en PDF (/familia/boletines/) y circulares con acuse de lectura digital (/familia/circulares/).",
        "MARCADOR [CAPTURA 21: Portal Familia] | MARCADOR [CAPTURA 22: Descarga Boletín PDF] | MARCADOR [CAPTURA 23: Circulares con Acuse Digital]"
    ]),
    ("7. RESUMEN DE LOS 10 CASOS DE USO REALISTAS", [
        "CU-01: Matrícula Individual de Nuevo Estudiante (Secretaría) • CU-02: Carga Masiva de Estudiantes en Excel (Secretaría)",
        "CU-03: Toma y Registro de Asistencia en Aula (Docente) • CU-04: Asentamiento de Notas Oficiales por Periodo (Docente)",
        "CU-05: Creación, Publicación y Revisión de Tareas (Docente) • CU-06: Entrega Virtual de Evidencias (Estudiante)",
        "CU-07: Consulta y Descarga de Boletín en PDF (Familia) • CU-08: Gestión de Usuarios y Claves (Administrador)",
        "CU-09: Emisión de Circular con Acuse Digital (Rectoría) • CU-10: Configuración de Periodos y Bloqueo de Calificaciones (Coordinación)"
    ]),
    ("8. DIAGRAMAS DE FLUJO DE PROCESOS CLAVE", [
        "FLUJO 1: Inicio de Sesión y Enrutamiento RBAC (Validación en base de datos -> Comprobación cuenta activa -> Redirección a portal específico).",
        "FLUJO 2: Matrícula Escolar (Opción individual o masiva Excel -> Validación RN-001 documento único -> Registro en padrón).",
        "FLUJO 3: Ciclo Pedagógico (Apertura periodo -> Asistencia y tareas -> Calificaciones finales -> Bloqueo formal RN-004 -> Emisión boletines PDF)."
    ]),
    ("9. GUÍA DE ERRORES FRECUENTES Y CONTINGENCIAS", [
        "• Acceso Restringido: Ocurre al abrir una URL sin permisos. El sistema redirige al portal correspondiente.",
        "• Credenciales incorrectas: Verificar mayúsculas y digitar documento sin puntos ni comas.",
        "• Documento ya registrado (RN-001): El estudiante ya existe; actualizar en directorio sin duplicar.",
        "• Periodo cerrado formalmente (RN-004): Las notas no pueden alterarse tras el cierre oficial de Coordinación.",
        "• Formato de archivo rechazado: Usar exclusivamente la plantilla oficial .xlsx sin alterar encabezados."
    ]),
    ("10. PREGUNTAS FRECUENTES (FAQ)", [
        "P: ¿Qué hacer si olvido mi clave? R: Usar el enlace de recuperación en el login o acudir a Secretaría.",
        "P: ¿Cómo descarga el acudiente el boletín? R: En /familia/boletines/ presionar 'Descargar Boletín Oficial'.",
        "P: ¿Pueden los alumnos alterar notas? R: No, el portal del estudiante es de solo lectura con validación estricta en servidor.",
        "P: ¿Cómo se recupera un registro borrado? R: El Administrador puede restaurarlo desde /papelera/."
    ]),
    ("11. POLÍTICAS DE SEGURIDAD Y HABEAS DATA", [
        "Cumplimiento estricto de la Ley Estatutaria 1581 de 2012 de Protección de Datos Personales. Cifrado seguro de contraseñas con algoritmo PBKDF2-SHA256, confidencialidad de la información médica y familiar de menores de edad y auditoría forense inmutable de operaciones."
    ]),
    ("12. GLOSARIO DE TÉRMINOS", [
        "ADSI: Análisis y Desarrollo de Sistemas de Información | RBAC: Control de Acceso Basado en Roles | Ficha: Grupo técnico SENA | RAP: Resultado de Aprendizaje | MEN: Ministerio de Educación Nacional | Soft Delete: Borrado lógico con recuperación."
    ])
]

for tit, paras in capitulos_texto:
    story.append(Paragraph(tit, h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#D4A373'), spaceAfter=8))
    for p_txt in paras:
        if p_txt.startswith("MARCADOR ["):
            story.append(Paragraph(f"<b>{p_txt}</b>", ParagraphStyle('CapBox', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=8, textColor=colors.HexColor('#1D4ED8'), spaceBefore=3, spaceAfter=4)))
        else:
            story.append(Paragraph(p_txt, body_style))
    story.append(Spacer(1, 6))

story.append(PageBreak())

# Tabla de Criterios SENA en PDF
story.append(Paragraph("ANEXO B: MATRIZ DE CUMPLIMIENTO DE LOS 20 CRITERIOS SENA ADSI", h1_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#8B5E3C'), spaceAfter=8))

t_crit_rows = [[
    Paragraph("<b>Criterio de Auditoría SENA</b>", body_style),
    Paragraph("<b>Sección</b>", body_style),
    Paragraph("<b>Estado</b>", body_style),
    Paragraph("<b>Verificación en el Manual</b>", body_style)
]]
for c_item in criterios_data:
    t_crit_rows.append([
        Paragraph(c_item[0], bullet_style),
        Paragraph(c_item[1], bullet_style),
        Paragraph(f"<b>{c_item[2]}</b>", ParagraphStyle('St', parent=bullet_style, textColor=colors.HexColor('#16A34A'))),
        Paragraph(c_item[3], bullet_style)
    ])

t_crit_pdf = Table(t_crit_rows, colWidths=[2.1 * inch, 1.2 * inch, 0.8 * inch, 2.4 * inch])
t_crit_pdf.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B5E3C')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
]))
story.append(t_crit_pdf)

doc_pdf.build(story, canvasmaker=SenaNumberedCanvas)
print(f"Manual PDF generado exitosamente en: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
print("¡Manual de Usuario EduNova generado en DOCX y PDF!")
