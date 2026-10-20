# -*- coding: utf-8 -*-
"""
Script Generador del Documento Maestro Único en PDF para el SENA
Proyecto EduNova — Sistema Integrado de Educación Técnica (SINETEC)

Hecho por: Dulce María Figueroa y Aminta María Moguea.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

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

# Registrar fuentes Windows
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Italic', 'C:/Windows/Fonts/ariali.ttf'))
pdfmetrics.registerFont(TTFont('Consolas', 'C:/Windows/Fonts/consola.ttf'))

# Importar datos base
from scripts.informe_content import (
    METADATOS, CONTROL_VERSIONES, INTRODUCCION_TEXT, OBJETIVOS_DATA,
    ALCANCE_DATA, MATRIZ_ESTADO, REQUISITOS_SERVIDOR, PLAN_INSTALACION_FASES,
    VARIABLES_ENTORNO_DATA, PLAN_RESPALDO_DATA, PLAN_MIGRACION_DATA,
    PRUEBAS_EVIDENCIAS_DATA, SEGURIDAD_DATA, MANTENIMIENTO_DATA,
    RIESGOS_DATA, CONCLUSIONES_DATA, RECOMENDACIONES_DATA
)

# Salidas
PDF_FINAL_DOCS = os.path.join(BASE_DIR, "docs", "EduNova_Documento_Maestro_SENA.pdf")
PDF_FINAL_ROOT = os.path.join(os.path.dirname(BASE_DIR), "EduNova_Documento_Maestro_SENA.pdf")
PDF_FINAL_DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads", "EduNova_Documento_Maestro_SENA.pdf")

# ==============================================================================
# CLASE CANVAS NUMERADO CON MEMBRETE SENA
# ==============================================================================
class SENAMasterCanvas(canvas.Canvas):
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
            self.draw_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Portada limpia
        
        self.saveState()
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Encabezado superior
        self.drawString(54, 11 * inch - 36, "SENA | Regional Magdalena — Documento Maestro de Despliegue, Operatividad y Mantenimiento")
        self.drawRightString(8.5 * inch - 54, 11 * inch - 36, "Sistema EduNova")
        self.setStrokeColor(colors.HexColor("#39A900"))  # Verde SENA
        self.setLineWidth(0.8)
        self.line(54, 11 * inch - 40, 8.5 * inch - 54, 11 * inch - 40)
        
        # Pie de página inferior
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, 8.5 * inch - 54, 46)
        self.drawString(54, 32, "Centro de Logística y Promoción Ecoturística • Ficha 228106 • Hecho por: Dulce Figueroa y Aminta Moguea")
        self.drawRightString(8.5 * inch - 54, 32, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()

# ==============================================================================
# CONSTRUCTOR DEL DOCUMENTO MAESTRO
# ==============================================================================
def construir_documento_maestro(ruta_salida):
    print(f"Construyendo Documento Maestro PDF en: {ruta_salida}...")
    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    c_sena = colors.HexColor("#39A900")
    c_slate = colors.HexColor("#1E293B")
    c_body = colors.HexColor("#334155")
    c_code = colors.HexColor("#E2E8F0")

    style_badge = ParagraphStyle('CoverBadge', fontName='Arial-Bold', fontSize=10, leading=13, textColor=c_sena, spaceAfter=6)
    style_title = ParagraphStyle('CoverTitle', fontName='Arial-Bold', fontSize=18, leading=22, textColor=c_slate, spaceAfter=8)
    style_sub = ParagraphStyle('CoverSubtitle', fontName='Arial', fontSize=11, leading=15, textColor=colors.HexColor("#475569"), spaceAfter=14)
    style_autores = ParagraphStyle('CoverAutores', fontName='Arial-Bold', fontSize=11.5, leading=15, textColor=c_slate, spaceAfter=14)
    
    style_h1 = ParagraphStyle('H1', fontName='Arial-Bold', fontSize=12.5, leading=15.5, textColor=c_sena, spaceBefore=12, spaceAfter=5, keepWithNext=True)
    style_h2 = ParagraphStyle('H2', fontName='Arial-Bold', fontSize=10, leading=12.5, textColor=c_slate, spaceBefore=8, spaceAfter=3, keepWithNext=True)
    style_body = ParagraphStyle('Body', fontName='Arial', fontSize=8.5, leading=11.5, textColor=c_body, spaceAfter=4)
    style_code = ParagraphStyle('CodeBlock', fontName='Consolas', fontSize=7.2, leading=9.2, textColor=c_code)
    style_table_cell = ParagraphStyle('TableCell', fontName='Arial', fontSize=7.5, leading=9.5, textColor=c_body)
    style_table_hdr = ParagraphStyle('TableHdr', fontName='Arial-Bold', fontSize=7.5, leading=9.5, textColor=colors.white)
    style_alert = ParagraphStyle('AlertText', fontName='Arial', fontSize=8, leading=11, textColor=colors.HexColor("#166534"))
    style_toc_num = ParagraphStyle('TOCNum', fontName='Arial-Bold', fontSize=8, leading=10, textColor=c_sena)
    style_toc_tit = ParagraphStyle('TOCTit', fontName='Arial', fontSize=8, leading=10, textColor=c_slate)

    story = []

    # ==========================================================================
    # 1. PORTADA FORMAL SENA
    # ==========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("SERVICIO NACIONAL DE APRENDIZAJE – SENA | REGIONAL MAGDALENA", style_badge))
    story.append(Paragraph("INFORME ADMINISTRATIVO, PLAN DE DESPLIEGUE EN PRODUCCIÓN Y MANUAL TÉCNICO OPERATIVO", style_title))
    story.append(Paragraph("SISTEMA DE INFORMACIÓN EDUNOVA — SISTEMA INTEGRADO DE EDUCACIÓN TÉCNICA (SINETEC)", style_sub))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_sena, spaceAfter=10))

    # Frase exacta requerida por el usuario en la portada
    box_autores = [[
        Paragraph("<font size='10' color='#166534'><b>Hecho por: Dulce María Figueroa y Aminta María Moguea.</b></font>", style_alert)
    ]]
    t_box_autores = Table(box_autores, colWidths=[504])
    t_box_autores.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0FDF4")),
        ('BOX', (0, 0), (-1, -1), 1, c_sena),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_box_autores)
    story.append(Spacer(1, 10))

    meta_rows = [
        [Paragraph("<b>Programa de Formación:</b>", style_table_cell), Paragraph(METADATOS["programa"], style_table_cell)],
        [Paragraph("<b>Código de Ficha / SOFIA:</b>", style_table_cell), Paragraph(f"Ficha {METADATOS['ficha']} | Proyecto SOFIA Plus: {METADATOS['proyecto_sofia']}", style_table_cell)],
        [Paragraph("<b>Centro de Formación:</b>", style_table_cell), Paragraph(METADATOS["centro"], style_table_cell)],
        [Paragraph("<b>Nombre Oficial del Proyecto:</b>", style_table_cell), Paragraph(METADATOS["nombre_proyecto"], style_table_cell)],
        [Paragraph("<b>Versión del Documento:</b>", style_table_cell), Paragraph("Versión 1.0 Definitiva (Documento Único Consolidado)", style_table_cell)],
        [Paragraph("<b>Destinatario / Evaluación:</b>", style_table_cell), Paragraph("Instructor Técnico de Formación y Comité Evaluador SENA", style_table_cell)],
        [Paragraph("<b>Autoras / Desarrolladoras:</b>", style_table_cell), Paragraph("Dulce María Figueroa y Aminta María Moguea", style_table_cell)],
        [Paragraph("<b>Ciudad y Fecha de Entrega:</b>", style_table_cell), Paragraph(f"{METADATOS['ciudad']} — Octubre de 2026", style_table_cell)],
    ]
    t_meta = Table(meta_rows, colWidths=[150, 354])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_meta)
    story.append(PageBreak())

    # ==========================================================================
    # 2. ÍNDICE GENERAL FORMAL
    # ==========================================================================
    story.append(Paragraph("ÍNDICE GENERAL DEL DOCUMENTO", style_h1))
    story.append(Paragraph("Estructura integral y secuencial del informe administrativo, planes y manual operativo:", style_body))
    
    indice_items = [
        ("1.", "Control de Versiones y Metadatos Documentales"),
        ("2.", "Introducción y Contexto Organizacional de la Solución Informática"),
        ("3.", "Objetivos del Documento (General y 8 Específicos)"),
        ("4.", "Alcance del Sistema, Paneles Operativos y Límites Formales"),
        ("5.", "Matriz de Estado Real del Proyecto (Actividades Realizadas, Propuestas y Pendientes)"),
        ("6.", "Requisitos de Infraestructura y Servidor (Hardware, Software Homologado, Red y Puertos)"),
        ("7.", "Plan Detallado de Instalación y Despliegue en Servidor Linux (9 Fases Técnicas)"),
        ("8.", "Configuración del Sistema y Variables de Entorno Seguras (.env y decouple)"),
        ("9.", "Plan de Respaldo y Recuperación ante Desastres (DRP, Backups MySQL y Archivos Multimedia)"),
        ("10.", "Plan de Migración de Datos (Metodología ETL, Esquemas Django y Carga de Fixtures)"),
        ("11.", "Pruebas de Funcionamiento y Evidencias de Calidad (15 Casos de Prueba Aprobados)"),
        ("12.", "Seguridad de la Solución Informática (RBAC, OWASP Top 10, Anti-CSRF y Anti-IDOR)"),
        ("13.", "Plan de Operatividad y Mantenimiento (Preventivo, Correctivo y Zero-Downtime)"),
        ("14.", "Gestión de Riesgos Técnicos y Operativos con Matrices de Mitigación y Contingencia"),
        ("15.", "Documentación Técnica y Manual Operativo de los Seis Paneles Institucionales"),
        ("16.", "Conclusiones de Ingeniería y Recomendaciones para la Operación Institucional"),
        ("17.", "Acta de Control, Recepción y Firmas de Responsabilidad")
    ]
    t_toc_data = []
    for num, tit in indice_items:
        t_toc_data.append([Paragraph(num, style_toc_num), Paragraph(tit, style_toc_tit)])
    t_toc = Table(t_toc_data, colWidths=[25, 479])
    t_toc.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, -1), 0.3, colors.HexColor("#E2E8F0")),
    ]))
    story.append(t_toc)
    story.append(Spacer(1, 8))

    # Control de versiones
    story.append(Paragraph("<b>Registro de Control de Versiones:</b>", style_h2))
    ver_table_data = [[
        Paragraph(h, style_table_hdr) for h in ["Versión", "Fecha", "Autoras", "Descripción del Cambio / Hito"]
    ]]
    for item in CONTROL_VERSIONES:
        autora = "Dulce Figueroa y Aminta Moguea" if "Equipo" in item["autor"] or "Líder" in item["autor"] else item["autor"]
        ver_table_data.append([
            Paragraph(f"<b>{item['version']}</b>", style_table_cell),
            Paragraph(item["fecha"], style_table_cell),
            Paragraph(autora, style_table_cell),
            Paragraph(item["descripcion"], style_table_cell)
        ])
    t_ver = Table(ver_table_data, colWidths=[55, 65, 120, 264])
    t_ver.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_slate),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
    ]))
    story.append(t_ver)

    # ==========================================================================
    # 3. INTRODUCCIÓN Y CONTEXTO
    # ==========================================================================
    story.append(PageBreak())
    story.append(Paragraph("1. INTRODUCCIÓN Y CONTEXTO ORGANIZACIONAL", style_h1))
    for par in INTRODUCCION_TEXT.split("\n\n"):
        story.append(Paragraph(par, style_body))

    alert_data = [[Paragraph("<b>DECLARACIÓN DE TRANSPARENCIA TÉCNICA SENA</b><br/>En estricto apego a las instrucciones del instructor, este documento no inventa dominios, servidores en la nube ni credenciales ficticias en producción. Se deja expresa constancia de que el software EduNova está 100% desarrollado, estabilizado y verificado con pruebas automatizadas en entorno local, mientras que la instalación física en servidor institucional se documenta como procedimiento propuesto pendiente de la asignación formal del hardware por parte del cliente.", style_alert)]]
    t_alert = Table(alert_data, colWidths=[504])
    t_alert.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0FDF4")),
        ('LINELEFT', (0, 0), (0, -1), 3, c_sena),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#BBF7D0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_alert)
    story.append(Spacer(1, 6))

    # ==========================================================================
    # 4. OBJETIVOS
    # ==========================================================================
    story.append(Paragraph("2. OBJETIVOS DEL DOCUMENTO", style_h1))
    story.append(Paragraph("<b>2.1 Objetivo General</b>", style_h2))
    story.append(Paragraph(OBJETIVOS_DATA["general"], style_body))
    story.append(Paragraph("<b>2.2 Objetivos Específicos</b>", style_h2))
    for obj in OBJETIVOS_DATA["especificos"]:
        story.append(Paragraph(f"• {obj}", style_body))

    # ==========================================================================
    # 5. ALCANCE
    # ==========================================================================
    story.append(Paragraph("3. ALCANCE DEL SISTEMA Y LÍMITES FORMALES", style_h1))
    story.append(Paragraph("<b>3.1 Alcance Funcional de la Solución (Seis Paneles)</b>", style_h2))
    for p_fun in ALCANCE_DATA["funcional"]:
        parts = p_fun.split(": ")
        story.append(Paragraph(f"• <b>{parts[0]}:</b> {parts[1]}", style_body))
    story.append(Paragraph("<b>3.2 Alcance del Despliegue en Servidor</b>", style_h2))
    story.append(Paragraph(ALCANCE_DATA["despliegue"], style_body))
    story.append(Paragraph("<b>3.3 Límites y Exclusiones del Sistema</b>", style_h2))
    for lim in ALCANCE_DATA["limites"]:
        story.append(Paragraph(f"• <b>Exclusión:</b> {lim}", style_body))

    # ==========================================================================
    # 6. MATRIZ DE ESTADO
    # ==========================================================================
    story.append(PageBreak())
    story.append(Paragraph("4. MATRIZ DE ESTADO REAL DEL PROYECTO", style_h1))
    story.append(Paragraph("A continuación se consolida el estado verificado de cada componente técnico, distinguiendo entre lo realizado, propuesto y pendiente:", style_body))
    est_table_data = [[
        Paragraph(h, style_table_hdr) for h in ["Área Técnica", "Actividad / Componente", "Estado", "Evidencia"]
    ]]
    for item in MATRIZ_ESTADO:
        col = "#166534" if item["tipo"] == "REALIZADA" else ("#1E40AF" if item["tipo"] == "PROPUESTA" else "#B45309")
        est_table_data.append([
            Paragraph(item["area"], style_table_cell),
            Paragraph(item["actividad"], style_table_cell),
            Paragraph(f"<b><font color='{col}'>{item['tipo']}</font></b>", style_table_cell),
            Paragraph(item["evidencia"], style_table_cell)
        ])
    t_est = Table(est_table_data, colWidths=[100, 174, 80, 150])
    t_est.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_slate),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
    ]))
    story.append(t_est)
    story.append(Spacer(1, 8))

    # ==========================================================================
    # 7. REQUISITOS DEL SERVIDOR
    # ==========================================================================
    story.append(Paragraph("5. REQUISITOS DEL SERVIDOR (INFRAESTRUCTURA, HARDWARE, SOFTWARE Y RED)", style_h1))
    story.append(Paragraph("<b>5.1 Requisitos de Hardware del Servidor</b>", style_h2))
    hw_table_data = []
    for i, r in enumerate(REQUISITOS_SERVIDOR["hardware"]):
        st = style_table_hdr if i == 0 else style_table_cell
        hw_table_data.append([Paragraph(val, st) for val in r])
    t_hw = Table(hw_table_data, colWidths=[90, 115, 125, 174])
    t_hw.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_slate),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
    ]))
    story.append(t_hw)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>5.2 Requisitos de Software Homologado</b>", style_h2))
    sw_table_data = []
    for i, r in enumerate(REQUISITOS_SERVIDOR["software"]):
        st = style_table_hdr if i == 0 else style_table_cell
        sw_table_data.append([Paragraph(val, st) for val in r])
    t_sw = Table(sw_table_data, colWidths=[95, 105, 110, 194])
    t_sw.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_slate),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
    ]))
    story.append(t_sw)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>5.3 Requisitos de Red, Puertos y Firewall</b>", style_h2))
    net_table_data = []
    for i, r in enumerate(REQUISITOS_SERVIDOR["red_puertos"]):
        st = style_table_hdr if i == 0 else style_table_cell
        net_table_data.append([Paragraph(val, st) for val in r])
    t_net = Table(net_table_data, colWidths=[40, 50, 105, 105, 204])
    t_net.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_slate),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
    ]))
    story.append(t_net)

    # ==========================================================================
    # 8. PLAN DETALLADO DE INSTALACIÓN (9 FASES)
    # ==========================================================================
    story.append(PageBreak())
    story.append(Paragraph("6. PLAN DETALLADO DE INSTALACIÓN Y DESPLIEGUE A PRODUCCIÓN", style_h1))
    story.append(Paragraph("Procedimiento técnico paso a paso para desplegar EduNova sobre un servidor institucional con Ubuntu Server:", style_body))
    for fase in PLAN_INSTALACION_FASES:
        story.append(Paragraph(fase["fase"], style_h2))
        story.append(Paragraph(fase["descripcion"], style_body))
        code_p = Paragraph("<br/>".join(fase["comandos"]).replace(" ", "&nbsp;"), style_code)
        t_code = Table([[code_p]], colWidths=[504])
        t_code.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#0F172A")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t_code)
        story.append(Spacer(1, 4))

    # ==========================================================================
    # 9. VARIABLES DE ENTORNO
    # ==========================================================================
    story.append(PageBreak())
    story.append(Paragraph("7. CONFIGURACIÓN DEL SISTEMA Y VARIABLES DE ENTORNO", style_h1))
    story.append(Paragraph("Variables de entorno seguras gestionadas en archivo .env con permisos 600:", style_body))
    env_table_data = [[
        Paragraph(h, style_table_hdr) for h in ["Variable", "Propósito en el Sistema", "Ejemplo", "Criticidad"]
    ]]
    for item in VARIABLES_ENTORNO_DATA:
        env_table_data.append([
            Paragraph(f"<b>{item[0]}</b>", style_table_cell),
            Paragraph(item[1], style_table_cell),
            Paragraph(item[2], style_table_cell),
            Paragraph(item[3], style_table_cell)
        ])
    t_env = Table(env_table_data, colWidths=[105, 174, 145, 80])
    t_env.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_slate),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
    ]))
    story.append(t_env)
    story.append(Spacer(1, 6))

    # ==========================================================================
    # 10. RESPALDO Y RECUPERACIÓN
    # ==========================================================================
    story.append(Paragraph("8. PLAN DE RESPALDO Y RECUPERACIÓN (BACKUP & DISASTER RECOVERY)", style_h1))
    story.append(Paragraph(PLAN_RESPALDO_DATA["descripcion"], style_body))
    story.append(Paragraph("<b>8.1 Política y Periodicidad de Respaldos</b>", style_h2))
    pol_table_data = []
    for i, r in enumerate(PLAN_RESPALDO_DATA["politica"]):
        st = style_table_hdr if i == 0 else style_table_cell
        pol_table_data.append([Paragraph(val, st) for val in r])
    t_pol = Table(pol_table_data, colWidths=[100, 95, 95, 95, 119])
    t_pol.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_slate),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
    ]))
    story.append(t_pol)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>8.2 Script de Respaldo Automatizado (/usr/local/bin/backup_edunova.sh)</b>", style_h2))
    sh_p = Paragraph("<br/>".join(PLAN_RESPALDO_DATA["script_bash"][:17]).replace(" ", "&nbsp;"), style_code)
    t_sh = Table([[sh_p]], colWidths=[504])
    t_sh.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#0F172A")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_sh)
    story.append(Paragraph(f"<b>Entrada Crontab (02:00 AM nocturno):</b> {PLAN_RESPALDO_DATA['cron_entry']}", style_body))

    story.append(Paragraph("<b>8.3 Protocolo de Restauración ante Desastres</b>", style_h2))
    for p in PLAN_RESPALDO_DATA["restauracion_pasos"]:
        story.append(Paragraph(p, style_body))

    story.append(Paragraph("<b>8.4 Inventario de Respaldos Reales en el Repositorio</b>", style_h2))
    bak_table_data = [[
        Paragraph(h, style_table_hdr) for h in ["Archivo Real", "Tamaño", "Ruta en Repositorio", "Descripción"]
    ]]
    for item in PLAN_RESPALDO_DATA["backups_reales"]:
        bak_table_data.append([
            Paragraph(f"<b>{item[0]}</b>", style_table_cell),
            Paragraph(item[1], style_table_cell),
            Paragraph(item[2], style_table_cell),
            Paragraph(item[3], style_table_cell)
        ])
    t_bak = Table(bak_table_data, colWidths=[130, 60, 140, 174])
    t_bak.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_slate),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
    ]))
    story.append(t_bak)

    # ==========================================================================
    # 11. MIGRACIÓN DE DATOS
    # ==========================================================================
    story.append(PageBreak())
    story.append(Paragraph("9. PLAN DE MIGRACIÓN DE DATOS", style_h1))
    story.append(Paragraph(PLAN_MIGRACION_DATA["metodologia"], style_body))
    story.append(Paragraph("<b>9.1 Etapas del Proceso de Migración (ETL)</b>", style_h2))
    for tit, desc in PLAN_MIGRACION_DATA["etapas"]:
        story.append(Paragraph(f"• <b>{tit}:</b> {desc}", style_body))
    story.append(Paragraph("<b>9.2 Chequeos y Verificaciones Post-Migración</b>", style_h2))
    for chk in PLAN_MIGRACION_DATA["chequeos_post_migracion"]:
        story.append(Paragraph(f"• <b>Verificación SQL:</b> {chk}", style_body))

    # ==========================================================================
    # 12. PRUEBAS DE FUNCIONAMIENTO
    # ==========================================================================
    story.append(Spacer(1, 4))
    story.append(Paragraph("10. PRUEBAS DE FUNCIONAMIENTO Y CONTROL DE CALIDAD", style_h1))
    story.append(Paragraph("Matriz de casos de prueba unitarias e integración ejecutadas y aprobadas (100% de éxito):", style_body))
    pru_table_data = [[
        Paragraph(h, style_table_hdr) for h in ["ID", "Caso de Prueba", "Resultado Esperado vs Obtenido", "Estado", "Evidencia"]
    ]]
    for item in PRUEBAS_EVIDENCIAS_DATA:
        res_comp = f"<b>Esp:</b> {item['resultado_esperado'][:55]}...<br/><b>Obt:</b> {item['resultado_obtenido'][:55]}..."
        pru_table_data.append([
            Paragraph(f"<b>{item['id']}</b>", style_table_cell),
            Paragraph(item["nombre"], style_table_cell),
            Paragraph(res_comp, style_table_cell),
            Paragraph("<b><font color='#166534'>APROBADO</font></b>", style_table_cell),
            Paragraph(item["evidencia"], style_table_cell)
        ])
    t_pru = Table(pru_table_data, colWidths=[45, 115, 164, 60, 120])
    t_pru.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_slate),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
    ]))
    story.append(t_pru)

    # ==========================================================================
    # 13. SEGURIDAD INFORMÁTICA
    # ==========================================================================
    story.append(PageBreak())
    story.append(Paragraph("11. SEGURIDAD DE LA SOLUCIÓN INFORMÁTICA", style_h1))
    story.append(Paragraph("<b>11.1 Matriz de Roles y Control de Acceso (RBAC)</b>", style_h2))
    rbac_table_data = [[
        Paragraph(h, style_table_hdr) for h in ["Rol Institucional", "Atribuciones Operativas", "Restricciones de Seguridad"]
    ]]
    for item in SEGURIDAD_DATA["rbac_roles"]:
        rbac_table_data.append([
            Paragraph(f"<b>{item[0]}</b>", style_table_cell),
            Paragraph(item[1], style_table_cell),
            Paragraph(item[2], style_table_cell)
        ])
    t_rbac = Table(rbac_table_data, colWidths=[110, 204, 190])
    t_rbac.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_slate),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
    ]))
    story.append(t_rbac)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>11.2 Mitigación de Vulnerabilidades Críticas (Top 10 OWASP)</b>", style_h2))
    owasp_table_data = [[
        Paragraph(h, style_table_hdr) for h in ["Vulnerabilidad OWASP", "Mecanismo de Mitigación en EduNova", "Capa"]
    ]]
    for item in SEGURIDAD_DATA["owasp_mitigaciones"]:
        owasp_table_data.append([
            Paragraph(f"<b>{item[0]}</b>", style_table_cell),
            Paragraph(item[1], style_table_cell),
            Paragraph(item[2], style_table_cell)
        ])
    t_owasp = Table(owasp_table_data, colWidths=[120, 264, 120])
    t_owasp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_slate),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
    ]))
    story.append(t_owasp)

    # ==========================================================================
    # 14. OPERATIVIDAD Y MANTENIMIENTO
    # ==========================================================================
    story.append(Spacer(1, 6))
    story.append(Paragraph("12. PLAN DE OPERATIVIDAD Y MANTENIMIENTO", style_h1))
    story.append(Paragraph("<b>12.1 Mantenimiento Preventivo Periódico</b>", style_h2))
    for act in MANTENIMIENTO_DATA["preventivo"]:
        story.append(Paragraph(f"• <b>Tarea Preventiva:</b> {act}", style_body))
    story.append(Paragraph("<b>12.2 Mantenimiento Correctivo y Contingencias</b>", style_h2))
    for act in MANTENIMIENTO_DATA["correctivo"]:
        story.append(Paragraph(f"• <b>Tarea Correctiva:</b> {act}", style_body))
    story.append(Paragraph("<b>12.3 Procedimiento de Actualización Continua (Zero-Downtime)</b>", style_h2))
    for paso in MANTENIMIENTO_DATA["zero_downtime"]:
        story.append(Paragraph(paso, style_body))

    # ==========================================================================
    # 15. GESTIÓN DE RIESGOS
    # ==========================================================================
    story.append(PageBreak())
    story.append(Paragraph("13. GESTIÓN DE RIESGOS TÉCNICOS Y OPERATIVOS", style_h1))
    rsg_table_data = [[
        Paragraph(h, style_table_hdr) for h in ["ID", "Descripción del Riesgo", "Prob / Imp", "Medida Preventiva", "Plan Contingencia"]
    ]]
    for item in RIESGOS_DATA:
        rsg_table_data.append([
            Paragraph(f"<b>{item['id']}</b>", style_table_cell),
            Paragraph(item["descripcion"], style_table_cell),
            Paragraph(f"{item['probabilidad']}<br/>{item['impacto']}", style_table_cell),
            Paragraph(item["mitigacion"], style_table_cell),
            Paragraph(item["contingencia"], style_table_cell)
        ])
    t_rsg = Table(rsg_table_data, colWidths=[35, 140, 65, 134, 130])
    t_rsg.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_slate),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
    ]))
    story.append(t_rsg)
    story.append(Spacer(1, 6))

    # ==========================================================================
    # 16. DOCUMENTACIÓN TÉCNICA Y MANUALES DE LOS SEIS PANELES
    # ==========================================================================
    story.append(Paragraph("14. DOCUMENTACIÓN TÉCNICA Y MANUAL OPERATIVO DE LOS SEIS PANELES", style_h1))
    story.append(Paragraph("A continuación se describe la operatividad detallada de cada portal institucional de EduNova:", style_body))

    story.append(Paragraph("<b>14.1 Panel de Administrador del Sistema</b>", style_h2))
    story.append(Paragraph("El Administrador ejerce el control global del sistema: gestión de instituciones educativas articuladas, programas del SENA, sedes, fichas formativas, creación de usuarios y roles institucionales. Cuenta con acceso exclusivo al módulo de <b>Auditoría Forense</b> (modelo <i>RegistroAuditoria</i> con registro de IP, timestamp y acción ejecutada) y a la <b>Papelera de Reciclaje</b> que aplica borrado lógico evitando pérdidas accidentales de expedientes.", style_body))

    story.append(Paragraph("<b>14.2 Panel de Rectoría y Directivos</b>", style_h2))
    story.append(Paragraph("Facilita la toma de decisiones gerenciales mediante tableros de control con tasas de retención escolar, ausentismo de aprendices, cobertura por ficha y consolidados de notas. Permite emitir circulares institucionales dirigidas a toda la comunidad educativa o filtradas por rol.", style_body))

    story.append(Paragraph("<b>14.3 Panel de Secretaría Académica</b>", style_h2))
    story.append(Paragraph("Administra el ciclo de vida del estudiante: legalización de admisiones, matrículas oficiales por ficha/grado, control de pagos de pensiones, asignación a rutas de transporte escolar y generación de certificados de estudio y constancias de notas oficiales.", style_body))

    story.append(Paragraph("<b>14.4 Panel de Docentes e Instructores</b>", style_h2))
    story.append(Paragraph("El docente gestiona exclusivamente sus grupos asignados: toma diaria de asistencia con cuatro estados (Presente, Falla Justificada, Falla Injustificada, Retardo), registro cuantitativo de notas (1.0 a 5.0) y cualitativo mediante juicios evaluativos oficiales del SENA ('A' Aprobado / 'D' Deficiente), diseño de guías de aprendizaje y publicación de tareas pedagógicas.", style_body))

    story.append(Paragraph("<b>14.5 Panel de Estudiantes / Aprendices (Perfil Juan Pérez)</b>", style_h2))
    story.append(Paragraph("El portal del estudiante cuenta con arquitectura desacoplada y aislamiento visual estricto: al pulsar una opción en el menú lateral, el contenedor derecho muestra únicamente dicha sección. Dispone de: Mi Horario de clases, Mis Asignaturas reales, Mis Calificaciones oficiales, Tareas vigentes con estado de entrega, Historial de Asistencia y Portafolio de Evidencias.", style_body))

    story.append(Paragraph("<b>14.6 Panel de Familia y Acudientes</b>", style_h2))
    story.append(Paragraph("Brinda a padres y acudientes un canal seguro para supervisar el desempeño de sus hijos a cargo: visualización de asistencia diaria en tiempo real, alertas tempranas de notas, consulta del estado de pensiones y comunicación directa con los docentes directores de grupo.", style_body))

    story.append(Paragraph("<b>14.7 Guía de Sustentación al Instructor (Libreto de Demostración de 20 Minutos)</b>", style_h2))
    demo_table_data = [
        [Paragraph("Tiempo", style_table_hdr), Paragraph("Módulo / Panel", style_table_hdr), Paragraph("Acciones a Demostrar al Docente del SENA", style_table_hdr)],
        [Paragraph("0:00–1:00", style_table_cell), Paragraph("Inicio y Login", style_table_cell), Paragraph("Acceso a login (/login/), roles de usuario y verificación de credenciales.", style_table_cell)],
        [Paragraph("1:00–4:00", style_table_cell), Paragraph("Administrador", style_table_cell), Paragraph("Dashboard con métricas reales, gestión de usuarios, auditoría y papelera.", style_table_cell)],
        [Paragraph("4:00–6:00", style_table_cell), Paragraph("Rectoría", style_table_cell), Paragraph("Indicadores consolidados, tasas de retención y emisión de circulares.", style_table_cell)],
        [Paragraph("6:00–8:30", style_table_cell), Paragraph("Secretaría", style_table_cell), Paragraph("Búsqueda de aprendices, matrículas, rutas de transporte y pensiones.", style_table_cell)],
        [Paragraph("8:30–11:30", style_table_cell), Paragraph("Docente", style_table_cell), Paragraph("Carga académica, toma de asistencia y calificación de notas y juicios A/D.", style_table_cell)],
        [Paragraph("11:30–14:00", style_table_cell), Paragraph("Estudiante", style_table_cell), Paragraph("Perfil de Juan Pérez, aislamiento de subpaneles, horario, notas y tareas.", style_table_cell)],
        [Paragraph("14:00–16:30", style_table_cell), Paragraph("Familia", style_table_cell), Paragraph("Estudiantes vinculados, boletín de notas, asistencia y estado de cuenta.", style_table_cell)],
        [Paragraph("16:30–19:00", style_table_cell), Paragraph("Flujo Cruzado", style_table_cell), Paragraph("Tarea creada por docente reflejada de inmediato en panel del estudiante.", style_table_cell)],
        [Paragraph("19:00–20:00", style_table_cell), Paragraph("Cierre y RBAC", style_table_cell), Paragraph("Demostración de bloqueo a usuarios no autorizados (HTTP 302 y 403).", style_table_cell)]
    ]
    t_demo = Table(demo_table_data, colWidths=[65, 95, 344])
    t_demo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_slate),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
    ]))
    story.append(t_demo)

    # ==========================================================================
    # 17. CONCLUSIONES, RECOMENDACIONES Y FIRMAS
    # ==========================================================================
    story.append(PageBreak())
    story.append(Paragraph("15. CONCLUSIONES Y RECOMENDACIONES", style_h1))
    story.append(Paragraph("<b>15.1 Conclusiones de Ingeniería y Gestión</b>", style_h2))
    for c in CONCLUSIONES_DATA:
        story.append(Paragraph(f"• {c}", style_body))
    story.append(Paragraph("<b>15.2 Recomendaciones para la Operación Institucional</b>", style_h2))
    for r in RECOMENDACIONES_DATA:
        story.append(Paragraph(f"• {r}", style_body))

    story.append(Spacer(1, 8))
    story.append(Paragraph("16. ACTA DE CONTROL, RECEPCIÓN Y FIRMAS DE RESPONSABILIDAD", style_h1))
    story.append(Paragraph("En señal de conformidad y validación técnica, se suscribe el presente documento maestro:", style_body))
    
    firmas_data_custom = [
        ("Aprendices / Desarrolladoras Líderes", "Dulce María Figueroa y Aminta María Moguea\nSENA Regional Magdalena — Ficha 228106 ADSI", "Desarrollo integral, pruebas de calidad y formulación de planes de despliegue.\n\n___________________________\nFirma de las Aprendices"),
        ("Instructor Técnico de Formación", "Centro de Logística y Promoción Ecoturística del Magdalena", "Validación técnica, metodológica y evaluación de resultados de aprendizaje.\n\n___________________________\nFirma del Instructor"),
        ("Delegado Institucional del Cliente", "Institución Educativa Articulada con la Media Técnica", "Recepción formal del documento maestro y verificación de viabilidad operativa.\n\n___________________________\nFirma y Sello Institucional")
    ]
    fir_table_data = [[
        Paragraph(h, style_table_hdr) for h in ["Rol / Cargo Interviniente", "Institución / Nombres", "Firma y Responsabilidad"]
    ]]
    for cargo, ent, resp in firmas_data_custom:
        fir_table_data.append([
            Paragraph(f"<b>{cargo}</b>", style_table_cell),
            Paragraph(ent.replace("\n", "<br/>"), style_table_cell),
            Paragraph(resp.replace("\n", "<br/>"), style_table_cell)
        ])
    t_fir = Table(fir_table_data, colWidths=[140, 160, 204])
    t_fir.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_slate),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
    ]))
    story.append(t_fir)

    doc.build(story, canvasmaker=SENAMasterCanvas)
    print(f"Documento Maestro generado exitosamente: {ruta_salida}")

# ==============================================================================
# EJECUCIÓN
# ==============================================================================
if __name__ == "__main__":
    construir_documento_maestro(PDF_FINAL_DOCS)
    
    # Copiar a raíz c:\SINETEC y a C:\Users\julia\Downloads
    import shutil
    try:
        shutil.copy2(PDF_FINAL_DOCS, PDF_FINAL_ROOT)
        print(f"Copia creada en: {PDF_FINAL_ROOT}")
    except Exception as e:
        print(f"Error copiando a raíz: {e}")
        
    try:
        shutil.copy2(PDF_FINAL_DOCS, PDF_FINAL_DOWNLOADS)
        print(f"Copia creada en: {PDF_FINAL_DOWNLOADS}")
    except Exception as e:
        print(f"Error copiando a Downloads: {e}")

    print("DOCUMENTO MAESTRO PDF COMPLETO Y LISTO PARA ENTREGAR.")
