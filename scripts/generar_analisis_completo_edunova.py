# -*- coding: utf-8 -*-
"""
Generador Maestro del Documento de Análisis Exhaustivo de EduNova para ChatGPT / Auditoría SENA
Salidas:
- C:/Users/julia/Downloads/Analisis_Completo_Funciones_EduNova.docx
- C:/EDUNOVA/EDUNOVA/docs/Analisis_Completo_Funciones_EduNova.docx
- C:/EDUNOVA/EDUNOVA/Analisis_Completo_Funciones_EduNova.docx
"""

import os
import sys
import shutil

sys.stdout.reconfigure(encoding='utf-8')

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
DOWNLOADS_DIR = os.path.join(os.environ.get('USERPROFILE', 'C:\\Users\\julia'), 'Downloads')
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Colors
C_PRIMARY = RGBColor(11, 37, 69)      # #0B2545 Deep Navy
C_SECONDARY = RGBColor(19, 64, 116)   # #134074 Indigo Navy
C_ACCENT = RGBColor(0, 102, 204)      # #0066CC Blue Accent
C_TEXT = RGBColor(30, 41, 59)         # #1E293B Slate Dark Text
C_MUTED = RGBColor(100, 116, 139)     # #64748B Muted Slate
C_SUCCESS = RGBColor(22, 101, 52)     # #166534 Green Dark
C_DANGER = RGBColor(153, 27, 27)      # #991B1B Red Dark

HEX_PRIMARY = "0B2545"
HEX_SECONDARY = "134074"
HEX_ACCENT = "0066CC"
HEX_LIGHT_BG = "F8FAFC"
HEX_CALLOUT_BG = "EEF4F8"
HEX_BORDER = "CBD5E1"
HEX_DANGER_BG = "FEF2F2"
HEX_DANGER_BORDER = "EF4444"
HEX_SUCCESS_BG = "F0FDF4"
HEX_SUCCESS_BORDER = "22C55E"

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>'))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, hex_color="CBD5E1"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="{hex_color}"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="{hex_color}"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{hex_color}"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_header(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    run = h.runs[0]
    run.font.name = "Arial"
    if level == 1:
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = C_PRIMARY
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(6)
    elif level == 2:
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = C_SECONDARY
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
    elif level == 3:
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = C_ACCENT
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(2)
    return h

def add_p(doc, text, bold_prefix=None, italic=False, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = "Arial"
        r_pre.font.size = Pt(10)
        r_pre.font.color.rgb = C_PRIMARY
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(10)
    r.font.italic = italic
    r.font.color.rgb = C_TEXT
    return p

def add_callout(doc, text, title="NOTA IMPORTANTE", border_hex=HEX_ACCENT, bg_hex=HEX_CALLOUT_BG):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="36" w:space="0" w:color="{border_hex}"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run_t = p.add_run(f"[{title}] ")
    run_t.bold = True
    run_t.font.name = "Arial"
    run_t.font.size = Pt(10)
    run_t.font.color.rgb = C_PRIMARY
    
    run_txt = p.add_run(text)
    run_txt.font.name = "Arial"
    run_txt.font.size = Pt(9.5)
    run_txt.font.color.rgb = C_TEXT
    
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(4)

def add_kv_table(doc, data_dict, col_widths=[2.2, 4.3]):
    tbl = doc.add_table(rows=len(data_dict), cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, HEX_BORDER)
    for idx, (k, v) in enumerate(data_dict.items()):
        row = tbl.rows[idx]
        cell_k, cell_v = row.cells[0], row.cells[1]
        
        cell_k.width = Inches(col_widths[0])
        cell_v.width = Inches(col_widths[1])
        
        set_cell_margins(cell_k, top=60, bottom=60, left=100, right=100)
        set_cell_margins(cell_v, top=60, bottom=60, left=100, right=100)
        
        if idx % 2 == 0:
            set_cell_background(cell_k, HEX_LIGHT_BG)
            set_cell_background(cell_v, HEX_LIGHT_BG)
            
        pk = cell_k.paragraphs[0]
        pk.paragraph_format.space_before = Pt(0)
        pk.paragraph_format.space_after = Pt(0)
        rk = pk.add_run(k)
        rk.bold = True
        rk.font.name = "Arial"
        rk.font.size = Pt(9.5)
        rk.font.color.rgb = C_PRIMARY
        
        pv = cell_v.paragraphs[0]
        pv.paragraph_format.space_before = Pt(0)
        pv.paragraph_format.space_after = Pt(0)
        rv = pv.add_run(str(v))
        rv.font.name = "Arial"
        rv.font.size = Pt(9.5)
        rv.font.color.rgb = C_TEXT
        
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(6)

def add_functional_spec(doc, title, module_info, steps_data):
    """
    Agrega una ficha exhaustiva de función con toda la estructura requerida:
    - Nombre exacto y localización
    - Propósito y perfil autorizado
    - Botón de activación
    - Campos y formulario
    - Botón de confirmación / guardado
    - Respuesta visual del sistema
    - Comprobación de éxito
    - Ruta de retorno
    - Manejo de excepciones y errores
    """
    add_header(doc, title, level=3)
    add_kv_table(doc, module_info)
    
    for section_name, section_desc in steps_data:
        add_p(doc, section_desc, bold_prefix=f"{section_name}: ", space_after=4)

print("Inicializando documento docx exhaustivo...")
doc = docx.Document()

# Configuración de márgenes
for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False

# ==========================================
# PORTADA Y PRESENTACIÓN TÉCNICA
# ==========================================
p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_before = Pt(36)
p_title.paragraph_format.space_after = Pt(6)
r_title = p_title.add_run("EDUNOVA — PLATAFORMA INTEGRAL DE GESTIÓN ACADÉMICA Y ESCOLAR")
r_title.bold = True
r_title.font.name = "Arial"
r_title.font.size = Pt(22)
r_title.font.color.rgb = C_PRIMARY

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_before = Pt(0)
p_sub.paragraph_format.space_after = Pt(24)
r_sub = p_sub.add_run("DOCUMENTO BASE DE ANÁLISIS INTEGRAL DEL SISTEMA REAL\nEspecificación Funcional Exhaustiva, Rutas, Vistas, Formularios, Botones y Recorridos Operativos para la Redacción del Manual de Usuario Definitivo (SENA ADSI)")
r_sub.font.name = "Arial"
r_sub.font.size = Pt(12)
r_sub.font.color.rgb = C_SECONDARY

add_callout(doc, 
    "DIRECTRIZ E INSTRUCCIÓN MAESTRA PARA CHATGPT:\n"
    "Este documento contiene la radiografía funcional completa, comprobada y verificada del código fuente de EduNova (Django 4.2 / PostgreSQL). "
    "Todas las rutas, nombres de botones, campos de formularios, mensajes flash del sistema, decoradores de permisos (RBAC) y flujos descritos "
    "corresponden exactamente a la implementación física del software. "
    "ChatGPT debe utilizar este documento como FUENTE ÚNICA Y VERÍDICA para elaborar el Manual de Usuario académico y operativo, "
    "absteniéndose de asumir o inventar funciones inexistentes. Cumple estrictamente con los 20 criterios de auditoría SENA ADSI.",
    title="PROPÓSITO DEL DOCUMENTO Y GUÍA PARA CHATGPT", border_hex=HEX_ACCENT, bg_hex=HEX_CALLOUT_BG)

doc.add_page_break()

# ==========================================
# SECCIÓN 1: ARQUITECTURA GENERAL Y SEGURIDAD
# ==========================================
add_header(doc, "1. ARQUITECTURA GENERAL, ROLES Y MECANISMOS DE SEGURIDAD (RBAC)", level=1)

add_p(doc, "El sistema EduNova (desarrollado sobre Django 4.2, Python 3.10+, PostgreSQL y Bootstrap 5) implementa un modelo de control de acceso basado en roles (RBAC) estrictamente tipificado en el modelo CustomUser bajo el atributo 'rol'. Los accesos no dependen de simples menús cosméticos, sino de decoradores de vista y validaciones a nivel de base de datos.", bold_prefix="Fundamento de Control de Acceso: ")

add_header(doc, "1.1 Matriz Oficial de Perfiles de Usuario", level=2)
roles_table_data = {
    "1. Administrador (ADMIN)": "Superusuario con control global de la plataforma, gestión de cuentas de usuario, asignación de roles, configuración institucional de marca, monitoreo forense y papelera de reciclaje.",
    "2. Rectoría (RECTOR)": "Gestión estratégica y directiva. Configuración y cierre estricto de periodos académicos, redacción de circulares institucionales oficiales y emisión de reportes gerenciales.",
    "3. Secretaría (SECRETARIA)": "Operación del libro maestro de matrículas, inscripción y registro individual de aprendices, importación masiva vía Excel, gestión de fichas académicas y directorio docente.",
    "4. Docente (DOCENTE)": "Control de aula. Toma de asistencia diaria (P/T/A/J), registro de calificaciones en doble escala (MEN 0.0-5.0 y SENA RAP A/D), gestión de temas y tareas con revisión de evidencias.",
    "5. Familia (FAMILIA)": "Portal de acompañamiento acudiente. Consulta del expediente de matrícula, visualización de boletines periódicos, descarga de PDF, seguimiento de asistencia y acuse de circulares.",
    "6. Estudiante (APRENDIZ)": "Portal del aprendiz. Consulta interactiva de horario semanal, calificaciones registradas, aula virtual para envío de tareas y evidencias, e historial personal de asistencias."
}
add_kv_table(doc, roles_table_data, col_widths=[2.2, 4.3])

add_header(doc, "1.2 Mecanismos de Protección y Decoradores de Código", level=2)
add_p(doc, "La seguridad en EduNova se gobierna centralmente desde 'usuarios/decorators.py'. Las vistas críticas están decoradas con funciones que interceptan la solicitud antes de ejecutar cualquier lógica de negocio:")
add_p(doc, "- @requerir_roles(['ADMIN', 'RECTOR', ...]): Valida si el usuario autenticado posee uno de los roles permitidos en la tupla.")
add_p(doc, "- @solo_admin: Exclusivo para el superusuario. Restringe vistas como creación de usuarios, papelera de reciclaje y auditoría.")
add_p(doc, "- @solo_rectoria_o_admin: Permite acceso a configuración de periodos académicos y circulares directivas.")
add_p(doc, "- @solo_secretaria: Permite acceso al flujo de matrícula, importaciones y modificación de expedientes de estudiantes.")
add_p(doc, "- @solo_docente: Reserva el acceso a calificaciones, asistencia docente y gestión de tareas.")
add_p(doc, "- @solo_aprendiz: Protege el portal de estudiantes y la entrega de evidencias.")
add_p(doc, "- @bloquear_estudiantes: Decorador preventivo que impide que un usuario de rol APRENDIZ ingrese a vistas operativas o directivas.")

add_callout(doc,
    "RESPUESTA EXACTA ANTE ACCESO NO AUTORIZADO:\n"
    "Cuando un usuario intenta acceder a una URL para la cual no posee privilegios, el sistema ejecuta la función 'manejar_acceso_denegado':\n"
    "1. Genera un mensaje de alerta flash tipo ERROR: 'Acceso Restringido (Seguridad SINETEC): Tu rol de usuario no tiene permisos para acceder a esta sección.'\n"
    "2. Ejecuta una redirección HTTP inmediata mediante 'obtener_url_redireccion_por_rol(user)', devolviendo al usuario a su panel correspondiente (ej. un docente es devuelto a /docente/, un estudiante a /aprendiz/, un acudiente a /familia/).\n"
    "3. Si el usuario no ha iniciado sesión, es redirigido a /login/?next=/url_solicitada/.",
    title="RESPUESTA OFICIAL DE SEGURIDAD ANTE INTENTOS NO AUTORIZADOS", border_hex=HEX_DANGER_BORDER, bg_hex=HEX_DANGER_BG)

add_header(doc, "1.3 Delimitación de Funcionalidades: Implementadas vs. No Requeridas", level=2)
add_p(doc, "Para la acreditación académica SENA ADSI, EduNova se enfoca en la gestión curricular, evaluativa, asistencial y de control escolar. Es fundamental aclarar el estado del código para no inducir a error al evaluador:")
add_p(doc, "• Módulos 100% Implementados y Funcionales: Autenticación, Auditoría, Papelera, Usuarios, Matrículas, Cargas Masivas Excel, Grados y Fichas, Calificaciones MEN/RAP, Asistencia Diaria P/T/A/J, Circulares con Acuse, Aulas de Tareas con Subida de Archivos, Boletines PDF y Horarios.")
add_p(doc, "• Módulos Auxiliares / Prototípicos no Requeridos: En el modelo existen prototipos para pensiones bancarias ('PagoPension') y rutas de transporte escolar ('TransporteRuta'). Estos no forman parte del alcance de la acreditación académica y no deben documentarse como servicios operativos terminados, sino como extensiones secundarias.")

doc.add_page_break()

# ==========================================
# SECCIÓN 2: PROCEDIMIENTOS TRANSVERSALES
# ==========================================
add_header(doc, "2. PROCEDIMIENTOS GLOBALES TRANSVERSALES", level=1)

# Iniciar Sesión
add_functional_spec(doc, "2.1 Inicio de Sesión Seguro (Login)", {
    "Ruta URL Oficial": "/login/",
    "Vista Django": "usuarios.views.custom_login_view",
    "Plantilla HTML": "usuarios/login.html",
    "Roles Autorizados": "Público general autenticable (ADMIN, RECTOR, SECRETARIA, DOCENTE, FAMILIA, APRENDIZ)"
}, [
    ("Dónde se encuentra", "Página de inicio de la plataforma EduNova accesible desde cualquier navegador web moderno."),
    ("Para qué sirve", "Validar la identidad del usuario en la base de datos PostgreSQL y establecer una sesión cifrada HTTP."),
    ("Qué botón debe seleccionar", "Botón azul centrado etiquetado como [ Ingresar al Sistema ] o [ Iniciar Sesión ]."),
    ("Qué información debe escribir", "Campo 'Usuario o Correo': Número de documento de identidad (ej. 1098765432) o nombre de usuario registrado. Campo 'Contraseña': Clave secreta alfanumérica."),
    ("Cómo completar el formulario", "1. Digitar el identificador. 2. Digitar la contraseña en el campo enmascarado. 3. Opcionalmente marcar 'Recordar sesión'."),
    ("Botón de confirmación", "Pulsar el botón principal [ Ingresar al Sistema ] (o presionar la tecla Enter)."),
    ("Respuesta del sistema", "Si las credenciales son válidas, el sistema redirige automáticamente al Dashboard asignado según el rol. Si son incorrectas, muestra alerta roja: 'Usuario o contraseña incorrectos. Por favor intente nuevamente.'"),
    ("Comprobación de éxito", "El navegador carga la interfaz del panel correspondiente y en la esquina superior derecha se observa el nombre completo del usuario y su insignia de rol."),
    ("Ruta de retorno", "En caso de equivocación, el formulario permanece visible con los campos limpios para reintentar."),
    ("Qué hacer en caso de error", "Si el usuario olvidó su clave, debe pulsar el enlace inferior [ ¿Olvidaste tu contraseña? ] para iniciar el flujo de restablecimiento.")
])

# Cerrar Sesión
add_functional_spec(doc, "2.2 Cierre de Sesión Seguro (Logout)", {
    "Ruta URL Oficial": "/logout/",
    "Vista Django": "usuarios.views.custom_logout_view",
    "Plantilla HTML": "Redirección a login.html con mensaje flash",
    "Roles Autorizados": "Cualquier usuario autenticado en el sistema"
}, [
    ("Dónde se encuentra", "Menú desplegable de perfil en la esquina superior derecha de la barra de navegación (Navbar)."),
    ("Para qué sirve", "Destruir la cookie de sesión activa en el servidor y evitar accesos no autorizados en terminales compartidos."),
    ("Qué botón debe seleccionar", "1. Hacer clic en el avatar/nombre de usuario. 2. En el menú desplegable, seleccionar la opción con ícono rojo [ Cerrar Sesión ]."),
    ("Qué información debe escribir", "Ninguna. La acción es inmediata e invalida la sesión de Django."),
    ("Respuesta del sistema", "Redirección inmediata a /login/ y despliegue del mensaje flash verde informativo: 'Has cerrado sesión exitosamente.'"),
    ("Comprobación de éxito", "La barra de navegación desaparece y se visualiza nuevamente el formulario de ingreso."),
    ("Ruta de retorno", "El usuario queda en la pantalla de bienvenida /login/.")
])

# Recuperar Contraseña
add_functional_spec(doc, "2.3 Recuperación de Contraseña", {
    "Ruta URL Oficial": "/recuperar-contrasena/ y /confirmar-recuperacion/<uidb64>/<token>/",
    "Vista Django": "usuarios.views.recuperar_contrasena",
    "Plantilla HTML": "usuarios/recuperar_contrasena.html",
    "Roles Autorizados": "Público con cuenta activa registrada en el sistema"
}, [
    ("Dónde se encuentra", "Enlace situado debajo del botón de ingreso en /login/."),
    ("Para qué sirve", "Permitir a un usuario que olvidó su clave generar un enlace seguro para restablecerla."),
    ("Qué botón debe seleccionar", "Enlace de texto [ ¿Olvidaste tu contraseña? ]."),
    ("Qué información debe escribir", "Campo 'Correo Electrónico Institucional': Correo previamente asociado a su cuenta de usuario."),
    ("Cómo completar el formulario", "Ingresar el correo exacto (ej. docente@edunova.edu.co) y hacer clic en [ Enviar Instrucciones ]."),
    ("Respuesta del sistema", "Alerta informativa verde: 'Si el correo ingresado coincide con un usuario registrado, se ha enviado un enlace de recuperación.'"),
    ("Paso en el correo", "El usuario abre el correo, hace clic en el enlace seguro y es dirigido a /confirmar-recuperacion/. Allí digita su nueva clave (mínimo 8 caracteres) y confirmación."),
    ("Comprobación de éxito", "Mensaje flash: 'Tu contraseña ha sido actualizada exitosamente. Ahora puedes iniciar sesión.' Redirección automática a /login/.")
])

# Perfil
add_functional_spec(doc, "2.4 Consulta y Actualización de Perfil de Usuario", {
    "Ruta URL Oficial": "/perfil/",
    "Vista Django": "usuarios.views.perfil_usuario",
    "Plantilla HTML": "usuarios/perfil.html",
    "Roles Autorizados": "Todos los roles autenticados"
}, [
    ("Dónde se encuentra", "Barra superior de navegación -> Clic en el nombre de usuario -> [ Mi Perfil ]."),
    ("Para qué sirve", "Consultar los datos personales registrados, actualizar número de teléfono/celular, cargar foto de avatar y cambiar voluntariamente la contraseña."),
    ("Qué botón debe seleccionar", "Botón [ Editar Perfil ] o [ Cambiar Contraseña ]."),
    ("Qué información debe escribir", "Campos editables: Teléfono, Dirección, Fotografía (archivo JPG o PNG). Campos protegidos (solo lectura): Rol, Documento de Identidad y Nombres."),
    ("Botón de confirmación", "Hacer clic en el botón [ Guardar Cambios ]."),
    ("Respuesta del sistema", "Mensaje flash verde: 'Perfil actualizado correctamente.'"),
    ("Comprobación de éxito", "La nueva foto o número telefónico se actualiza en pantalla."),
    ("Ruta de retorno", "Hacer clic en el logo superior de EduNova o en [ Volver al Dashboard ].")
])

doc.add_page_break()

# ==========================================
# SECCIÓN 3: PANEL ADMINISTRADOR
# ==========================================
add_header(doc, "3. PANEL 1: ADMINISTRADOR DEL SISTEMA (ADMIN)", level=1)
add_p(doc, "El Administrador tiene el control absoluto de la configuración tecnológica de EduNova. Accede a través de la URL '/dashboard/' y gestiona las identidades, la seguridad y la auditoría forense.", bold_prefix="Alcance del Perfil: ")

# Dashboard
add_functional_spec(doc, "3.1 Dashboard de Administración", {
    "Ruta URL Oficial": "/dashboard/",
    "Vista Django": "usuarios.views.dashboard",
    "Plantilla HTML": "usuarios/dashboard_admin.html",
    "Roles Autorizados": "Exclusivo ADMIN"
}, [
    ("Dónde se encuentra", "Página principal de aterrizaje tras iniciar sesión con rol Administrador."),
    ("Para qué sirve", "Visualizar métricas globales: Total de Usuarios, Estudiantes Matriculados, Docentes Activos, Fichas Abiertas y acceso a widgets rápidos."),
    ("Acciones disponibles", "Hacer clic en las tarjetas métricas para saltar directamente a la lista de usuarios, matrículas o reportes."),
    ("Ruta de retorno", "Siempre accesible mediante el enlace [ Dashboard ] en el menú lateral izquierdo.")
])

# Gestión de Usuarios
add_functional_spec(doc, "3.2 Gestión Integral de Cuentas de Usuario", {
    "Ruta URL Oficial": "/usuarios/",
    "Vista Django": "usuarios.views.gestion_usuarios",
    "Plantilla HTML": "usuarios/gestion_usuarios.html",
    "Roles Autorizados": "ADMIN"
}, [
    ("Dónde se encuentra", "Menú lateral izquierdo -> Sección [ Administración ] -> Opción [ Gestión de Usuarios ]."),
    ("Para qué sirve", "Crear nuevos usuarios, editar datos existentes, asignar roles institucionales, resetear contraseñas y desactivar o reactivar cuentas."),
    ("Qué botón debe seleccionar", "Para crear: botón superior verde [ + Nuevo Usuario ] (/usuarios/nuevo/). Para filtrar: caja de búsqueda con botón [ Buscar ]."),
    ("Campos del formulario de creación", "1. Tipo de Documento (CC, TI, CE). 2. Número de Documento. 3. Nombre de Usuario (username). 4. Primer Nombre. 5. Apellidos. 6. Correo Electrónico. 7. Rol Institucional (ADMIN, RECTOR, SECRETARIA, DOCENTE, FAMILIA, APRENDIZ). 8. Contraseña inicial. 9. Casilla 'Usuario Activo'."),
    ("Botón de confirmación", "Pulsar el botón azul [ Guardar Usuario ]."),
    ("Respuesta del sistema", "Mensaje flash verde: 'Usuario <username> creado exitosamente con el rol <ROL>.' Redirección a la tabla de usuarios."),
    ("Acciones sobre usuarios existentes", "• Botón [ Editar ]: Modificar datos básicos y rol.\n• Botón [ Reset Clave ]: Asigna una clave temporal y notifica al usuario.\n• Botón [ Bloquear/Activar ] (toggle): Desactiva inmediatamente el acceso sin borrar el registro.\n• Botón [ Eliminar ]: Envía al usuario a la Papelera de Reciclaje (soft-delete)."),
    ("Comprobación de éxito", "El usuario aparece en la tabla general con su badge de rol correspondiente."),
    ("Manejo de errores", "Si el número de documento o el username ya existen, el sistema alerta en rojo: 'Ya existe un usuario con este documento o nombre de usuario.'")
])

# Papelera de Reciclaje
add_functional_spec(doc, "3.3 Papelera de Reciclaje y Borrado Lógico", {
    "Ruta URL Oficial": "/papelera/",
    "Vista Django": "usuarios.views.papelera_reciclaje",
    "Plantilla HTML": "usuarios/papelera.html",
    "Roles Autorizados": "ADMIN"
}, [
    ("Dónde se encuentra", "Menú lateral izquierdo -> [ Configuración y Seguridad ] -> [ Papelera de Reciclaje ]."),
    ("Para qué sirve", "Garantizar la trazabilidad y recuperación ante borrados accidentales de usuarios, materias o fichas mediante borrado lógico (is_active=False)."),
    ("Acciones disponibles", "1. Botón [ Restaurar ] (/papelera/<id>/restaurar/): Devuelve el registro a su estado activo original con mensaje flash: 'Registro restaurado satisfactoriamente.'\n2. Botón rojo [ Vaciar Papelera ] (/papelera/vaciar/): Eliminación física irreversible (requiere confirmación modal)."),
    ("Comprobación de éxito", "El elemento desaparece de la papelera y vuelve a listarse en su módulo de origen.")
])

# Auditoría Forense
add_functional_spec(doc, "3.4 Pista de Auditoría Forense", {
    "Ruta URL Oficial": "/auditoria/",
    "Vista Django": "usuarios.views.auditoria_lista",
    "Plantilla HTML": "usuarios/auditoria.html",
    "Roles Autorizados": "ADMIN"
}, [
    ("Dónde se encuentra", "Menú lateral izquierdo -> [ Seguridad ] -> [ Auditoría del Sistema ]."),
    ("Para qué sirve", "Inspeccionar el registro cronológico inmutable de todas las operaciones críticas realizadas en la plataforma."),
    ("Información documentada", "Tabla con: Fecha y Hora exacta, Usuario responsable, Rol, Dirección IP, Acción realizada (LOGIN, CREACION, MODIFICACION, ELIMINACION) y Detalle en formato JSON."),
    ("Filtros de búsqueda", "Selector de fecha inicio/fin, selector de usuario y campo de texto para filtrar por acción.")
])

# Configuración de Marca
add_functional_spec(doc, "3.5 Configuración General y Marca Institucional", {
    "Ruta URL Oficial": "/configuracion/ y /configuracion/colores/guardar/",
    "Vista Django": "usuarios.views.configuracion_sistema",
    "Plantilla HTML": "usuarios/configuracion.html",
    "Roles Autorizados": "ADMIN"
}, [
    ("Dónde se encuentra", "Menú lateral -> [ Configuración ] -> [ Configuración General ]."),
    ("Para qué sirve", "Personalizar el nombre de la institución educativa, lema, cargar el escudo/logotipo oficial y configurar la paleta de colores CSS dinámica."),
    ("Botón de confirmación", "Botón [ Guardar Configuración ]. Respuesta: 'Ajustes institucionales guardados correctamente.'")
])

doc.add_page_break()

# ==========================================
# SECCIÓN 4: PANEL RECTORÍA Y COORDINACIÓN
# ==========================================
add_header(doc, "4. PANEL 2: RECTORÍA Y COORDINACIÓN ACADÉMICA", level=1)
add_p(doc, "El perfil Rectoría lidera la supervisión académica e institucional. Sus facultades principales se orientan a la gobernanza de los periodos académicos, la comunicación directiva y la toma de decisiones basada en reportes consolidados.", bold_prefix="Alcance del Perfil: ")

# Dashboard Rectoría
add_functional_spec(doc, "4.1 Dashboard Directivo de Rectoría", {
    "Ruta URL Oficial": "/rectoria/ (o /coordinacion/)",
    "Vista Django": "usuarios.views.rectoria_dashboard",
    "Plantilla HTML": "usuarios/rectoria_dashboard.html",
    "Roles Autorizados": "RECTOR, COORDINADOR, ADMIN"
}, [
    ("Dónde se encuentra", "Página inicial al autenticarse como Rector o Coordinador."),
    ("Para qué sirve", "Presentar el tablero de mando con indicadores de rendimiento escolar: porcentaje global de aprobación, tasas de inasistencia por grado, balance de matrícula activa y circulares en curso.")
])

# Periodos Académicos
add_functional_spec(doc, "4.2 Gestión de Periodos Académicos y Bloqueo de Modificaciones", {
    "Ruta URL Oficial": "/academico/periodos-academicos/",
    "Vista Django": "academico.views.configurar_periodos_academicos",
    "Plantilla HTML": "academico/periodos_academicos.html",
    "Roles Autorizados": "RECTOR, ADMIN"
}, [
    ("Dónde se encuentra", "Menú lateral -> [ Gestión Académica ] -> [ Periodos Académicos ]."),
    ("Para qué sirve", "Definir los periodos lectivos anuales (Periodo 1 a Periodo 4), fijar fechas de inicio y culminación, y aplicar el BLOQUEO RECTORAL DE CALIFICACIONES."),
    ("Formulario y Campos", "• Nombre del Periodo (ej. Primer Periodo 2026).\n• Fecha de Apertura.\n• Fecha de Cierre.\n• Porcentaje Ponderado (ej. 25%).\n• Estado: 'Abierto' / 'Cerrado'."),
    ("Acción Crítica de Bloqueo (RN-004)", "El Rector selecciona el periodo y pulsa el botón rojo [ Cerrar Periodo Académico ]. El sistema marca 'cerrado = True'."),
    ("Respuesta y Regla de Negocio RN-004", "Mensaje flash: 'El Periodo Académico ha sido cerrado. A partir de este momento ningún docente podrá alterar notas de este periodo.' Si un docente intenta modificar calificaciones en un periodo cerrado, el sistema rechaza la solicitud mostrando: 'El periodo académico seleccionado se encuentra cerrado para modificaciones.'"),
    ("Comprobación de éxito", "El estado del periodo cambia a badge rojo [ CERRADO / BLOQUEADO ]."),
    ("Ruta de retorno", "Enlace superior [ Volver al Panel de Rectoría ].")
])

# Comunicaciones y Circulares
add_functional_spec(doc, "4.3 Comunicaciones Institucionales y Circulares Oficiales", {
    "Ruta URL Oficial": "/comunicaciones/ y /comunicaciones/redactar/",
    "Vista Django": "usuarios.views.mensajeria / redactar_circular",
    "Plantilla HTML": "usuarios/mensajeria.html y usuarios/redactar_circular.html",
    "Roles Autorizados": "RECTOR, COORDINADOR, ADMIN"
}, [
    ("Dónde se encuentra", "Menú superior o lateral -> [ Comunicaciones ] -> [ Redactar Circular ]."),
    ("Para qué sirve", "Emitir directivas oficiales y boletines informativos dirigidos a estamentos específicos (Docentes, Familias, Estudiantes o Toda la Comunidad)."),
    ("Campos del formulario", "• Título de la Circular (Asunto).\n• Audiencia Objetivo (Selector múltiple: Docentes, Familias, Estudiantes).\n• Nivel de Prioridad: Normal, Alta, Urgente.\n• Cuerpo del Comunicado (Editor de texto).\n• Adjuntar Documento Oficial (PDF opcional)."),
    ("Botón de confirmación", "Pulsar el botón azul [ Publicar y Difundir Circular ]."),
    ("Respuesta del sistema", "Mensaje flash verde: 'Circular oficial publicada exitosamente. Notificación despachada a los destinatarios.'"),
    ("Monitoreo de Acuses de Recibo", "En /comunicaciones/, Rectoría puede hacer clic en [ Ver Acuses ] y consultar la lista de familias y docentes que ya abrieron y confirmaron la lectura del documento.")
])

# Centro de Reportes
add_functional_spec(doc, "4.4 Centro de Reportes Estadísticos y Exportación", {
    "Ruta URL Oficial": "/reportes/ (Exportar: /reportes/exportar/excel/ y /reportes/exportar/pdf/)",
    "Vista Django": "academico.views.centro_reportes",
    "Plantilla HTML": "academico/centro_reportes.html",
    "Roles Autorizados": "RECTOR, COORDINADOR, SECRETARIA, ADMIN"
}, [
    ("Dónde se encuentra", "Menú lateral -> [ Reportes y Estadísticas ]."),
    ("Para qué sirve", "Generar consolidados de matrícula, sábanas de notas, reportes de estudiantes en riesgo de reprobación y actas finales."),
    ("Botones de acción", "• Botón verde [ Exportar Consolidado a Excel ]: Descarga inmediata de archivo .xlsx estructurado.\n• Botón rojo [ Generar Libro de Calificaciones en PDF ]: Descarga del consolidado formateado."),
    ("Respuesta del sistema", "Descarga de archivo binario directamente en el navegador del usuario.")
])

doc.add_page_break()

# ==========================================
# SECCIÓN 5: PANEL SECRETARÍA ACADÉMICA
# ==========================================
add_header(doc, "5. PANEL 3: SECRETARÍA ACADÉMICA", level=1)
add_p(doc, "La Secretaría Académica es el motor operativo del registro estudiantil. Administra el Libro Maestro de Matrículas, procesa altas individuales, ejecuta cargas masivas y gestiona los expedientes de estudiantes y docentes.", bold_prefix="Alcance del Perfil: ")

# Libro Maestro de Matrículas
add_functional_spec(doc, "5.1 Libro Maestro de Matrículas", {
    "Ruta URL Oficial": "/matriculas/",
    "Vista Django": "academico.views.matriculas_lista",
    "Plantilla HTML": "academico/matriculas_lista.html",
    "Roles Autorizados": "SECRETARIA, ADMIN, RECTOR"
}, [
    ("Dónde se encuentra", "Menú lateral izquierdo -> [ Secretaría ] -> [ Libro de Matrículas ]."),
    ("Para qué sirve", "Consultar el estado de matrícula de todos los grados escolares (1° a 11° y niveles técnicos), con recuentos de cupos disponibles y matriculados."),
    ("Filtros", "Pestañas interactivas por Grado y selector de Vigencia Académica activa.")
])

# Matrícula Individual
add_functional_spec(doc, "5.2 Registro y Matrícula Individual de Estudiante", {
    "Ruta URL Oficial": "/estudiantes/registrar/ y /academico/fichas/<id>/matricular/",
    "Vista Django": "academico.views.registrar_aprendiz",
    "Plantilla HTML": "academico/registrar_aprendiz.html",
    "Roles Autorizados": "SECRETARIA, ADMIN"
}, [
    ("Dónde se encuentra", "En /matriculas/ o /estudiantes/ -> Botón azul [ + Nueva Matrícula ]."),
    ("Para qué sirve", "Vincular a un nuevo estudiante al sistema, asignarle su acudiente de familia y matricularlo en un grupo/ficha específico."),
    ("Campos del formulario", "1. Datos del Estudiante: Tipo y Número de Documento, Nombres, Apellidos, Fecha de Nacimiento, Género, Dirección, Teléfono, Correo.\n2. Datos del Acudiente: Documento, Nombre del Padre/Madre/Tutor, Teléfono y Correo de contacto familiar.\n3. Asignación Académica: Grado a cursar y Grupo/Ficha asignado (ej. Grado 9° - Grupo A)."),
    ("Botón de confirmación", "Hacer clic en el botón verde [ Formalizar Matrícula ]."),
    ("Respuesta del sistema", "Mensaje flash verde: 'Estudiante <Nombres> matriculado exitosamente. Código de Matrícula: MAT-2026-XXXX. Se ha creado la cuenta de acceso para el estudiante y su acudiente.'"),
    ("Comprobación de éxito", "El estudiante aparece inmediatamente en la lista de matriculados del grado correspondiente."),
    ("Manejo de errores", "Si el documento ya está matriculado en la misma vigencia, el sistema bloquea con: 'El estudiante con documento X ya se encuentra matriculado en la vigencia actual.'")
])

# Importación Masiva Excel
add_functional_spec(doc, "5.3 Carga Masiva de Estudiantes vía Archivo Excel", {
    "Ruta URL Oficial": "/estudiantes/importar/ (Plantilla: /estudiantes/plantilla/)",
    "Vista Django": "academico.views.importar_estudiantes_masivo",
    "Plantilla HTML": "academico/importar_estudiantes.html",
    "Roles Autorizados": "SECRETARIA, ADMIN"
}, [
    ("Dónde se encuentra", "Menú [ Estudiantes ] -> Botón superior [ Importación Masiva Excel ]."),
    ("Para qué sirve", "Cargar listas completas de aprendices en segundos sin digitación manual individual."),
    ("Paso 1: Descargar plantilla", "Hacer clic en el botón azul [ Descargar Plantilla Oficial .XLSX ]."),
    ("ESTRUCTURA EXACTA DE COLUMNAS ACEPTADAS", "El archivo Excel (.xlsx) debe contener obligatoriamente los siguientes encabezados en la Fila 1:\n"
     "• 'tipo_documento': Valores válidos: TI, CC, CE, PEP.\n"
     "• 'numero_documento': Numérico único sin puntos ni comas.\n"
     "• 'first_name': Nombres del estudiante.\n"
     "• 'last_name': Apellidos del estudiante.\n"
     "• 'email': Correo electrónico único.\n"
     "• 'grado': Número del grado (ej. 10).\n"
     "• 'seccion': Letra del grupo (ej. A, B o C)."),
    ("Paso 2: Subir archivo", "Pulsar el botón [ Seleccionar Archivo ] -> Elegir el .xlsx en el computador -> Pulsar el botón verde [ Procesar Carga Masiva ]."),
    ("Respuesta del sistema", "Alerta informativa con desglose: 'Proceso finalizado. Registros creados exitosamente: 35. Errores detectados: 0.' Si hay errores de formato, el sistema lista las filas exactas donde falló la validación."),
    ("Comprobación de éxito", "Los nuevos estudiantes se visualizan de inmediato en /estudiantes/.")
])

# Directorio y Expediente
add_functional_spec(doc, "5.4 Directorio de Estudiantes y Expediente Individual", {
    "Ruta URL Oficial": "/estudiantes/ y /estudiantes/<id>/",
    "Vista Django": "academico.views.estudiantes_lista / detalle_estudiante",
    "Plantilla HTML": "academico/estudiantes_lista.html y academico/detalle_estudiante.html",
    "Roles Autorizados": "SECRETARIA, RECTOR, COORDINADOR, ADMIN"
}, [
    ("Dónde se encuentra", "Menú lateral -> [ Estudiantes ] -> [ Directorio General ]."),
    ("Para qué sirve", "Consultar el historial completo del estudiante, datos familiares, ficha médica, registro de matrículas previas y estado actual (Activo, Retirado, Graduado)."),
    ("Acciones disponibles", "• [ Ver Ficha ]: Abre el expediente completo.\n• [ Editar ]: Modificar datos de contacto o dirección (/estudiantes/<id>/editar/).\n• [ Cambiar Estado ]: Registrar retiro o traslado del alumno (/estudiantes/<id>/cambiar-estado/).")
])

# Gestión de Docentes
add_functional_spec(doc, "5.5 Directorio y Carga Académica de Docentes", {
    "Ruta URL Oficial": "/docentes/gestion/ (Nuevo: /docentes/gestion/nuevo/)",
    "Vista Django": "usuarios.views_docentes.docentes_lista",
    "Plantilla HTML": "usuarios/docentes_lista.html",
    "Roles Autorizados": "SECRETARIA, RECTOR, ADMIN"
}, [
    ("Dónde se encuentra", "Menú lateral -> [ Gestión de Personal ] -> [ Planta Docente ]."),
    ("Para qué sirve", "Registrar nuevos docentes, asignar su carga académica (qué asignaturas dictará y en cuáles grupos) o realizar importación masiva (/usuarios/importar-instructores/).")
])

doc.add_page_break()

# ==========================================
# SECCIÓN 6: PANEL DOCENTE
# ==========================================
add_header(doc, "6. PANEL 4: DOCENTE / INSTRUCTOR", level=1)
add_p(doc, "El Panel Docente concentra la actividad pedagógica diaria: control de asistencia, evaluación numérica y cualitativa de competencias, asignación de tareas virtuales y retroalimentación de evidencias.", bold_prefix="Alcance del Perfil: ")

# Dashboard Docente
add_functional_spec(doc, "6.1 Dashboard del Docente", {
    "Ruta URL Oficial": "/instructor/ (o /docente/)",
    "Vista Django": "usuarios.views.instructor_dashboard",
    "Plantilla HTML": "usuarios/instructor_dashboard.html",
    "Roles Autorizados": "DOCENTE, ADMIN"
}, [
    ("Dónde se encuentra", "Pantalla de aterrizaje inmediata tras autenticarse con credenciales de Docente."),
    ("Para qué sirve", "Presentar las asignaturas a cargo del profesor en el día, accesos rápidos a asistencia, resumen de tareas pendientes de revisión y calendario.")
])

# Asistencia
add_functional_spec(doc, "6.2 Registro Diario de Asistencia Escolar", {
    "Ruta URL Oficial": "/asistencia/ (API: /asistencia/api/guardar-individual/)",
    "Vista Django": "seguimiento.views.asistencia_docente_view",
    "Plantilla HTML": "seguimiento/asistencia_docente.html",
    "Roles Autorizados": "DOCENTE, ADMIN"
}, [
    ("Dónde se encuentra", "Menú principal docente -> [ Control de Asistencia ]."),
    ("Para qué sirve", "Registrar de forma ágil la presencia o ausencia de los estudiantes en cada sesión de clase."),
    ("Paso 1: Filtros de clase", "Seleccionar: 1. Asignatura. 2. Grupo/Ficha. 3. Fecha (por defecto la fecha actual). Clic en [ Cargar Lista de Clase ]."),
    ("Paso 2: Pulsadores de estado P/T/A/J", "Para cada estudiante de la lista, el docente dispone de 4 botones circulares de color:\n"
     "• [ P ] Verde: PRESENTE (Asistió puntualmente).\n"
     "• [ T ] Amarillo: TARDANZA (Llegó con retraso justificado o no).\n"
     "• [ A ] Rojo: AUSENTE (Falta injustificada).\n"
     "• [ J ] Azul: JUSTIFICADA (Falta con soporte médico o institucional)."),
    ("Mecanismo de Guardado", "El sistema guarda automáticamente en tiempo real vía llamada asíncrona AJAX al pulsar cada letra, o bien el docente puede pulsar el botón inferior verde [ Guardar Asistencia de la Sesión ]."),
    ("Respuesta del sistema", "Aparece un indicador verde 'Guardado' junto a cada fila. Notificación flash: 'Asistencia registrada exitosamente para la fecha seleccionada.'"),
    ("Comprobación de éxito", "Los botones seleccionados permanecen marcados y resaltados con su color correspondiente.")
])

# Calificaciones Doble Escala
add_functional_spec(doc, "6.3 Registro de Calificaciones en Doble Escala (MEN y SENA RAP)", {
    "Ruta URL Oficial": "/calificaciones-docente/ y /panel-calificaciones/",
    "Vista Django": "evaluaciones.views.calificaciones_docente_view / panel_calificaciones",
    "Plantilla HTML": "evaluaciones/calificaciones_docente.html",
    "Roles Autorizados": "DOCENTE, ADMIN"
}, [
    ("Dónde se encuentra", "Menú principal docente -> [ Calificaciones ]."),
    ("Para qué sirve", "Asignar notas parciales, definitivas y juicios evaluativos bajo la normatividad colombiana y el modelo SENA."),
    ("Paso 1: Selección", "Seleccionar Asignatura, Grupo y Periodo Académico (Periodo 1 a 4). Clic en [ Cargar Planilla ]."),
    ("Paso 2: Doble Escala Integrada", "• Escala Numérica Nacional MEN (0.0 a 5.0): El docente digita valores decimales (ej. 4.2). El sistema calcula equivalencias automáticas:\n"
     "   - Superior: 4.6 a 5.0\n"
     "   - Alto: 4.0 a 4.5\n"
     "   - Básico: 3.0 a 3.9\n"
     "   - Bajo: 1.0 a 2.9 (Reprobatorio)\n"
     "• Escala Cualitativa Técnica SENA RAP: Pulsador de Juicio Evaluativo:\n"
     "   - [ A ]: APROBADO (Logró el Resultado de Aprendizaje).\n"
     "   - [ D ]: DEFICIENTE / POR MEJORAR (No alcanzó la competencia)."),
    ("Validación Crítica (RN-004)", "Si el periodo fue cerrado por Rectoría, los campos se tornan de solo lectura. Si se fuerza el envío, el sistema responde: 'El periodo académico seleccionado se encuentra cerrado para modificaciones.'"),
    ("Botón de confirmación", "Botón azul inferior [ Guardar Calificaciones ]."),
    ("Respuesta del sistema", "Alerta verde: 'Planilla de calificaciones actualizada satisfactoriamente.'")
])

# Temas y Tareas
add_functional_spec(doc, "6.4 Creación y Publicación de Temas y Tareas", {
    "Ruta URL Oficial": "/actividades-y-tareas/ y /academico/clase/<id>/crear-tarea/",
    "Vista Django": "academico.views_clase.temas_actividades_view / crear_tarea",
    "Plantilla HTML": "academico/temas_actividades.html",
    "Roles Autorizados": "DOCENTE, ADMIN"
}, [
    ("Dónde se encuentra", "Menú docente -> [ Actividades y Tareas ]."),
    ("Para qué sirve", "Estructurar las guías de aprendizaje y crear asignaciones virtuales con fecha de entrega para los estudiantes."),
    ("Formulario de creación de tarea", "• Título de la Actividad (ej. Taller de Algoritmos).\n• Descripción e Instrucciones detalladas.\n• Fecha y Hora límite de entrega.\n• Porcentaje sobre la nota del periodo (ej. 15%).\n• Archivo adjunto: Guía o material de apoyo en PDF/DOCX.\n• Estado de Publicación: Casilla 'Publicar inmediatamente'."),
    ("Botón de confirmación", "Pulsar el botón verde [ Publicar Actividad ]."),
    ("Respuesta del sistema", "Mensaje flash: 'Actividad publicada exitosamente. Visible para todos los estudiantes matriculados.'"),
    ("Opción de Despublicar", "En la lista de tareas, el docente puede pulsar el botón [ Ocultar / Despublicar ] para editar la guía antes de que sea vista.")
])

# Revisión de Entregas
add_functional_spec(doc, "6.5 Revisión y Retroalimentación de Evidencias de Estudiantes", {
    "Ruta URL Oficial": "/instructor/tarea/<id>/entregas/",
    "Vista Django": "academico.views_clase.revisar_entregas_tarea",
    "Plantilla HTML": "academico/revisar_entregas.html",
    "Roles Autorizados": "DOCENTE, ADMIN"
}, [
    ("Dónde se encuentra", "En /actividades-y-tareas/ -> Hacer clic en la tarea -> Botón [ Ver Entregas ]."),
    ("Para qué sirve", "Descargar las evidencias enviadas por los aprendices, calificar su desempeño y redactar observaciones pedagógicas."),
    ("Acciones en pantalla", "1. Hacer clic en [ Descargar Evidencia ] para abrir el PDF o Word enviado por el estudiante.\n2. En la casilla de nota, ingresar la calificación (0.0 a 5.0) y el estado RAP (A/D).\n3. Digitar el texto de retroalimentación en la caja de comentarios.\n4. Pulsar el botón [ Guardar Calificación y Enviar Retroalimentación ]."),
    ("Respuesta del sistema", "La fila del estudiante cambia a estado verde [ CALIFICADO ] y la nota queda registrada en el expediente.")
])

# Horario Docente
add_functional_spec(doc, "6.6 Consulta de Horario Escolar Docente", {
    "Ruta URL Oficial": "/horario-escolar/",
    "Vista Django": "academico.views.horario_docente_view",
    "Plantilla HTML": "academico/horario_docente.html",
    "Roles Autorizados": "DOCENTE, ADMIN"
}, [
    ("Dónde se encuentra", "Menú lateral docente -> [ Mi Horario Escolar ]."),
    ("Para qué sirve", "Visualizar la cuadrícula horaria semanal (Lunes a Viernes) con los bloques de clase, salón físico y grupo asignado.")
])

doc.add_page_break()

# ==========================================
# SECCIÓN 7: PANEL FAMILIA
# ==========================================
add_header(doc, "7. PANEL 5: FAMILIA / ACUDIENTE", level=1)
add_p(doc, "El Portal de la Familia está concebido para la corresponsabilidad formativa. Permite a padres de familia y acudientes legales realizar un acompañamiento permanente sin intermediarios y desde cualquier dispositivo.", bold_prefix="Alcance del Perfil: ")

# Portal Familiar
add_functional_spec(doc, "7.1 Portal de Inicio de la Familia", {
    "Ruta URL Oficial": "/familia/",
    "Vista Django": "usuarios.views_familia.familia_portal",
    "Plantilla HTML": "usuarios/familia_portal.html",
    "Roles Autorizados": "FAMILIA, ADMIN"
}, [
    ("Dónde se encuentra", "Página inicial al ingresar con cuenta de Acudiente."),
    ("Para qué sirve", "Presentar el resumen integral de los estudiantes a cargo. Si el acudiente tiene más de un hijo en el colegio, dispone de un selector desplegable superior [ Seleccionar Acudido ] para alternar entre sus expedientes.")
])

# Ficha de Matrícula Familiar
add_functional_spec(doc, "7.2 Consulta de Ficha de Matrícula", {
    "Ruta URL Oficial": "/familia/matricula/",
    "Vista Django": "usuarios.views_familia.familia_matricula",
    "Plantilla HTML": "usuarios/familia_matricula.html",
    "Roles Autorizados": "FAMILIA, ADMIN"
}, [
    ("Dónde se encuentra", "Menú del acudiente -> [ Matrícula y Expediente ]."),
    ("Para qué sirve", "Verificar la validez de la matrícula institucional, grado asignado, director de grupo y datos registrados en la secretaría.")
])

# Boletines PDF
add_functional_spec(doc, "7.3 Consulta de Calificaciones y Descarga de Boletín en PDF", {
    "Ruta URL Oficial": "/familia/boletines/ (PDF: /estudiantes/<id>/boletin-pdf/)",
    "Vista Django": "usuarios.views_familia.familia_boletines / boletin_pdf_view",
    "Plantilla HTML": "usuarios/familia_boletines.html",
    "Roles Autorizados": "FAMILIA, ADMIN"
}, [
    ("Dónde se encuentra", "Menú del acudiente -> [ Boletines y Notas ]."),
    ("Para qué sirve", "Revisar las notas parciales por materia y descargar el Boletín de Calificaciones Oficial en formato PDF."),
    ("Acciones del usuario", "1. Seleccionar el periodo académico (ej. Periodo 1).\n2. El sistema muestra la tabla con materias, docentes, nota cuantitativa, desempeño cualitativo (Superior, Alto, Básico, Bajo) y fallas acumuladas.\n3. Pulsar el botón rojo [ Descargar Boletín Oficial en PDF ]."),
    ("Respuesta del sistema", "Generación y descarga automática del documento PDF oficial con el escudo institucional, firmas y código de autenticidad.")
])

# Monitoreo de Asistencia
add_functional_spec(doc, "7.4 Monitoreo de Asistencia Escolar", {
    "Ruta URL Oficial": "/familia/asistencia/",
    "Vista Django": "usuarios.views_familia.familia_asistencia",
    "Plantilla HTML": "usuarios/familia_asistencia.html",
    "Roles Autorizados": "FAMILIA, ADMIN"
}, [
    ("Dónde se encuentra", "Menú del acudiente -> [ Control de Asistencia ]."),
    ("Para qué sirve", "Consultar el historial detallado de inasistencias y retardos del estudiante con fecha, asignatura y motivo."),
    ("Comprobación de éxito", "Tabla visual con badges de color: Verde (Presente), Rojo (Falta Injustificada), Azul (Falta Justificada).")
])

# Circulares con Acuse
add_functional_spec(doc, "7.5 Circulares Institucionales y Acuse de Recibo Digital", {
    "Ruta URL Oficial": "/familia/circulares/",
    "Vista Django": "usuarios.views_familia.familia_circulares",
    "Plantilla HTML": "usuarios/familia_circulares.html",
    "Roles Autorizados": "FAMILIA, ADMIN"
}, [
    ("Dónde se encuentra", "Menú del acudiente -> [ Circulares y Comunicados ]."),
    ("Para qué sirve", "Leer los comunicados oficiales emitidos por Rectoría y Docentes, y certificar formalmente su notificación."),
    ("Acción de Acuse de Recibo", "Al abrir una circular no leída, aparece un botón azul prominente: [ Confirmar Lectura y Acuse de Recibo ]."),
    ("Respuesta del sistema", "Al pulsar el botón, el sistema guarda la marca de tiempo (timestamp) de lectura y muestra el badge verde: 'Lectura Confirmada el DD/MM/AAAA a las HH:MM'. Rectoría ve reflejado este acuse en tiempo real.")
])

doc.add_page_break()

# ==========================================
# SECCIÓN 8: PANEL ESTUDIANTE (APRENDIZ)
# ==========================================
add_header(doc, "8. PANEL 6: ESTUDIANTE (APRENDIZ)", level=1)
add_p(doc, "El Portal del Aprendiz es el espacio virtual del estudiante para gestionar su itinerario de aprendizaje: consulta de horarios, seguimiento de notas, descarga de guías y envío digital de evidencias evaluativas.", bold_prefix="Alcance del Perfil: ")

# Dashboard Aprendiz
add_functional_spec(doc, "8.1 Dashboard del Estudiante", {
    "Ruta URL Oficial": "/aprendiz/ (o /estudiante/)",
    "Vista Django": "usuarios.views.aprendiz_dashboard",
    "Plantilla HTML": "usuarios/aprendiz_dashboard.html",
    "Roles Autorizados": "APRENDIZ, ADMIN"
}, [
    ("Dónde se encuentra", "Página principal al iniciar sesión con cuenta de Aprendiz/Estudiante."),
    ("Para qué sirve", "Tablero personal con alertas de tareas próximas a vencer, resumen de últimas notas publicadas y avisos institucionales.")
])

# Horario Estudiante
add_functional_spec(doc, "8.2 Consulta de Horario Escolar", {
    "Ruta URL Oficial": "/estudiante/horario/",
    "Vista Django": "academico.views.horario_estudiante_view",
    "Plantilla HTML": "academico/horario_estudiante.html",
    "Roles Autorizados": "APRENDIZ, ADMIN"
}, [
    ("Dónde se encuentra", "Menú del estudiante -> [ Mi Horario ]."),
    ("Para qué sirve", "Revisar los horarios de cada día de la semana, salones y nombres de los profesores de cada asignatura.")
])

# Calificaciones Estudiante
add_functional_spec(doc, "8.3 Consulta de Calificaciones y Desempeño", {
    "Ruta URL Oficial": "/estudiante/calificaciones/",
    "Vista Django": "evaluaciones.views.calificaciones_estudiante_view",
    "Plantilla HTML": "evaluaciones/calificaciones_estudiante.html",
    "Roles Autorizados": "APRENDIZ, ADMIN"
}, [
    ("Dónde se encuentra", "Menú del estudiante -> [ Mis Calificaciones ]."),
    ("Para qué sirve", "Supervisar las notas obtenidas en cada materia por periodo lectivo."),
    ("Visualización", "Tarjetas por materia que exhiben la nota numérica actual y el estado: Verde = Aprobado, Rojo = En Riesgo."),
    ("Manejo de estado vacío", "Si el docente aún no ha registrado notas, el sistema muestra el mensaje cordial: 'Aún no tienes calificaciones registradas en este periodo académico.'")
])

# Aula Virtual y Entrega de Tareas
add_functional_spec(doc, "8.4 Aula Virtual: Tareas y Entrega Digital de Evidencias", {
    "Ruta URL Oficial": "/estudiante/tareas/ y /aprendiz/tarea/<id>/entregar/",
    "Vista Django": "academico.views_clase.estudiante_tareas / entregar_tarea",
    "Plantilla HTML": "academico/estudiante_tareas.html y academico/entregar_tarea.html",
    "Roles Autorizados": "APRENDIZ, ADMIN"
}, [
    ("Dónde se encuentra", "Menú del estudiante -> [ Mis Tareas y Guías ]."),
    ("Para qué sirve", "Consultar instrucciones de las tareas publicadas por los profesores y subir los archivos de respuesta."),
    ("Paso 1: Selección de tarea", "En la lista filtrable (Pendientes, Entregadas, Calificadas), hacer clic en la tarea deseada."),
    ("Paso 2: Descarga de material", "Pulsar [ Descargar Material Adjunto ] si el profesor adjuntó guía o taller."),
    ("Paso 3: Formulario de Entrega", "• Pulsar el botón [ Seleccionar Archivo ] y buscar en el computador el archivo de evidencia (formatos admitidos: PDF, DOCX, ZIP, JPG, PNG; tamaño máximo 15 MB).\n• En la caja de texto 'Comentarios de entrega', escribir un mensaje para el docente (opcional)."),
    ("Paso 4: Envío", "Pulsar el botón verde [ Enviar Tarea para Calificación ]."),
    ("Respuesta del sistema", "Alerta verde: 'Tu tarea ha sido enviada exitosamente. El profesor ha recibido tu evidencia.' La tarea pasa inmediatamente a la pestaña [ ENTREGADA ]."),
    ("Validación de Entrega Extemporánea", "Si el estudiante intenta enviar después de la fecha y hora límite fijada por el docente, el sistema desactiva el botón y muestra: 'El plazo de entrega para esta actividad ha vencido. Contacta a tu docente.'"),
    ("Ruta de retorno", "Enlace superior [ Volver a la Lista de Tareas ].")
])

# Asistencia Estudiante
add_functional_spec(doc, "8.5 Historial de Asistencia Personal", {
    "Ruta URL Oficial": "/estudiante/asistencia/",
    "Vista Django": "seguimiento.views.asistencia_estudiante_view",
    "Plantilla HTML": "seguimiento/asistencia_estudiante.html",
    "Roles Autorizados": "APRENDIZ, ADMIN"
}, [
    ("Dónde se encuentra", "Menú del estudiante -> [ Mi Asistencia ]."),
    ("Para qué sirve", "Verificar el porcentaje de asistencia acumulado por materia y revisar fechas de fallas para tramitar justificaciones ante secretaría o coordinación.")
])

# Comunicados
add_functional_spec(doc, "8.6 Comunicados Institucionales para Estudiantes", {
    "Ruta URL Oficial": "/estudiante/comunicados/",
    "Vista Django": "usuarios.views.estudiante_comunicados",
    "Plantilla HTML": "usuarios/estudiante_comunicados.html",
    "Roles Autorizados": "APRENDIZ, ADMIN"
}, [
    ("Dónde se encuentra", "Menú del estudiante -> [ Avisos y Circulares ]."),
    ("Para qué sirve", "Leer las noticias, citaciones y anuncios emitidos por la rectoría o cuerpo docente dirigidos al estudiantado.")
])

doc.add_page_break()

# ==========================================
# SECCIÓN 9: SOLUCIÓN DE PROBLEMAS Y FAQ
# ==========================================
add_header(doc, "9. GUÍA DE RESOLUCIÓN DE INCIDENCIAS, ERRORES COMUNES Y FAQ", level=1)

faq_data = [
    ("1. Olvido de credenciales de acceso",
     "Síntoma: El usuario no puede ingresar a /login/ y el sistema muestra 'Usuario o contraseña incorrectos'.\n"
     "Solución paso a paso: 1. Hacer clic en [ ¿Olvidaste tu contraseña? ]. 2. Ingresar el correo institucional registrado. 3. Abrir el enlace enviado al buzón. 4. Si el usuario no tiene correo registrado o no le llega el mensaje, debe acudir a Secretaría o Administrador para que aplique el botón [ Reset Clave ] desde el panel de Gestión de Usuarios."),
    
    ("2. Error de 'Acceso Restringido (Seguridad SINETEC)'",
     "Síntoma: Al intentar abrir una URL, aparece una alerta roja de acceso denegado y se regresa al dashboard.\n"
     "Causa y Solución: El usuario está intentando acceder a una función reservada para otro rol (ej. un estudiante intentando ver /calificaciones-docente/ o un docente intentando ver /usuarios/). El usuario debe operar exclusivamente dentro de las opciones visibles en su menú lateral."),
    
    ("3. El docente no puede modificar calificaciones (Periodo Cerrado)",
     "Síntoma: Las casillas de notas aparecen bloqueadas en gris y al enviar se muestra 'El periodo académico seleccionado se encuentra cerrado para modificaciones.'\n"
     "Causa y Solución: La Rectoría ejecutó el cierre administrativo del periodo lectivo (Regla RN-004). Si se requiere una corrección extemporánea de notas, el Rector debe ingresar a /academico/periodos-academicos/ y habilitar temporalmente el periodo para la modificación."),
    
    ("4. Error al subir archivo Excel de Estudiantes",
     "Síntoma: La carga masiva falla o devuelve 'Error en fila X: formato inválido'.\n"
     "Solución paso a paso: 1. Asegurarse de utilizar la plantilla oficial descargada desde el botón [ Descargar Plantilla Oficial .XLSX ]. 2. Verificar que los nombres de columna estén en minúsculas y sin tildes: tipo_documento, numero_documento, first_name, last_name, email, grado, seccion. 3. Comprobar que no haya documentos duplicados ni correos vacíos."),
    
    ("5. El estudiante no puede adjuntar su tarea",
     "Síntoma: El botón [ Enviar Tarea para Calificación ] aparece inactivo o muestra 'Plazo vencido'.\n"
     "Causa y Solución: 1. Comprobar la fecha y hora límite estipulada por el docente; si ya venció, el sistema no permite entregas tardías automáticas. 2. Verificar que el archivo pese menos de 15 MB y tenga formato permitido (.pdf, .docx, .zip, .jpg, .png)."),
    
    ("6. Sesión cerrada por inactividad o pérdida de navegación",
     "Síntoma: Al hacer clic en [ Guardar ], el sistema redirige al formulario de Login.\n"
     "Causa y Solución: La sesión de Django expiró por seguridad tras tiempo prolongado de inactividad. El usuario debe ingresar nuevamente sus credenciales. Para evitar pérdida de notas extensas, se recomienda guardar periódicamente utilizando los botones de guardado parcial.")
]

for q, a in faq_data:
    add_header(doc, q, level=2)
    add_p(doc, a, space_after=6)

doc.add_page_break()

# ==========================================
# SECCIÓN 10: MATRIZ TÉCNICA DE AUDITORÍA
# ==========================================
add_header(doc, "10. MATRIZ TÉCNICA DE VERIFICACIÓN Y AUDITORÍA DE CÓDIGO", level=1)
add_p(doc, "Esta tabla consolida la trazabilidad técnica de todos los módulos analizados, contrastando la URL, la vista de controlador Django, el modelo de datos principal, la plantilla de presentación y el permiso de seguridad asociado:", bold_prefix="Trazabilidad Arquitectónica: ")

matrix_rows = [
    ("Autenticación", "/login/", "usuarios.views.custom_login_view", "CustomUser", "login.html", "Público"),
    ("Dashboard Admin", "/dashboard/", "usuarios.views.dashboard", "CustomUser, Institucion", "dashboard_admin.html", "@solo_admin"),
    ("Gestión Usuarios", "/usuarios/", "usuarios.views.gestion_usuarios", "CustomUser", "gestion_usuarios.html", "@solo_admin"),
    ("Papelera Reciclaje", "/papelera/", "usuarios.views.papelera_reciclaje", "SoftDeleteModel", "papelera.html", "@solo_admin"),
    ("Pista Auditoría", "/auditoria/", "usuarios.views.auditoria_lista", "RegistroAuditoria", "auditoria.html", "@solo_admin"),
    ("Periodos Académicos", "/academico/periodos-academicos/", "configurar_periodos_academicos", "PeriodoAcademico", "periodos_academicos.html", "@solo_rectoria_o_admin"),
    ("Circulares Oficiales", "/comunicaciones/", "usuarios.views.mensajeria", "Comunicado, Acuse", "mensajeria.html", "RECTOR, COORD, ADMIN"),
    ("Libro Matrículas", "/matriculas/", "academico.views.matriculas_lista", "Matricula, Grado", "matriculas_lista.html", "SECRETARIA, ADMIN"),
    ("Registro Estudiante", "/estudiantes/registrar/", "registrar_aprendiz", "Estudiante, Familia", "registrar_aprendiz.html", "SECRETARIA, ADMIN"),
    ("Importación Masiva", "/estudiantes/importar/", "importar_estudiantes_masivo", "Estudiante, CustomUser", "importar_estudiantes.html", "SECRETARIA, ADMIN"),
    ("Control Asistencia", "/asistencia/", "asistencia_docente_view", "Asistencia, SesionClase", "asistencia_docente.html", "@solo_docente"),
    ("Calificaciones MEN/RAP", "/calificaciones-docente/", "calificaciones_docente_view", "Calificacion, JuicioRAP", "calificaciones_docente.html", "@solo_docente"),
    ("Tareas y Guías", "/actividades-y-tareas/", "temas_actividades_view", "Tema, Tarea, Evidencia", "temas_actividades.html", "@solo_docente"),
    ("Portal Familiar", "/familia/", "usuarios.views_familia.familia_portal", "FamiliaEstudiante", "familia_portal.html", "FAMILIA"),
    ("Boletines PDF", "/familia/boletines/", "familia_boletines / boletin_pdf", "BoletinPeriodico", "familia_boletines.html", "FAMILIA, SECRETARIA"),
    ("Portal Aprendiz", "/aprendiz/", "usuarios.views.aprendiz_dashboard", "Estudiante, Ficha", "aprendiz_dashboard.html", "@solo_aprendiz"),
    ("Entrega Tareas", "/estudiante/tareas/", "estudiante_tareas / entregar_tarea", "EntregaTarea, Archivo", "estudiante_tareas.html", "@solo_aprendiz")
]

tbl_m = doc.add_table(rows=len(matrix_rows)+1, cols=6)
tbl_m.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_m, HEX_BORDER)

headers_m = ["Módulo", "Ruta URL", "Vista Django", "Modelo", "Plantilla", "Permiso"]
hdr_cells = tbl_m.rows[0].cells
for idx, h_txt in enumerate(headers_m):
    hdr_cells[idx].text = h_txt
    set_cell_background(hdr_cells[idx], HEX_PRIMARY)
    set_cell_margins(hdr_cells[idx], top=80, bottom=80, left=80, right=80)
    p = hdr_cells[idx].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p.runs:
        run.font.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        run.font.size = Pt(8.5)
        run.font.name = "Arial"

for row_idx, r_data in enumerate(matrix_rows):
    row_cells = tbl_m.rows[row_idx + 1].cells
    for col_idx, col_text in enumerate(r_data):
        row_cells[col_idx].text = col_text
        set_cell_margins(row_cells[col_idx], top=50, bottom=50, left=60, right=60)
        if row_idx % 2 == 0:
            set_cell_background(row_cells[col_idx], HEX_LIGHT_BG)
        p = row_cells[col_idx].paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        for run in p.runs:
            run.font.name = "Arial"
            run.font.size = Pt(8.0)
            run.font.color.rgb = C_TEXT

# Guardar documento
DOCX_NAME = "Analisis_Completo_Funciones_EduNova.docx"
target_downloads = os.path.join(DOWNLOADS_DIR, DOCX_NAME)
target_docs = os.path.join(DOCS_DIR, DOCX_NAME)
target_root = os.path.join(BASE_DIR, DOCX_NAME)

print(f"Guardando documento en:")
print(f"1. {target_downloads}")
print(f"2. {target_docs}")
print(f"3. {target_root}")

doc.save(target_downloads)
shutil.copy2(target_downloads, target_docs)
shutil.copy2(target_downloads, target_root)

print("¡Documento generado y guardado exitosamente en todas las ubicaciones!")
