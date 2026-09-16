import os 
 
js_code = ''' 
<style> 
  .tarjeta-interactiva { cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; } 
  .tarjeta-interactiva:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(248, 206, 236, 0.6); } 
  .asistente-box { display: none; background: #fff; border-radius: 12px; padding: 25px; border: 2px solid #f8ceec; text-align: center; } 
</style> 
<script> 
document.addEventListener('DOMContentLoaded', function() { 
    const contenedor = document.querySelector('.card:last-child, .bg-white:last-child, div.shadow-sm:last-child') || document.body; 
    const tarjetas = document.querySelectorAll('div'); 
    tarjetas.forEach(div => { 
        if (div.innerText && div.innerText.includes('Seleccione una Ficha')) { 
            div.classList.add('tarjeta-interactiva'); 
            div.onclick = function() { 
                div.style.display = 'none'; 
                let box = document.getElementById('panel-asistente'); 
                if (!box) { 
                    box = document.createElement('div'); 
                    box.id = 'panel-asistente'; 
                    box.className = 'asistente-box mt-4'; 
                    box.innerHTML = '<h4 style="color:#4a2e35; font-weight:bold;">? Asistente de Evaluaci¢n Activo</h4><p style="color:#885e6a;">Selecciona la acci¢n para esta ficha:</p><button onclick="alert(\'Cargando alumnos...\')" class="btn me-2" style="background:#f8ceec; color:#4a2e35; font-weight:600;">?? Cargar Lista</button><button onclick="alert(\'Generando PDF...\')" class="btn me-2" style="background:#f06292; color:white; font-weight:600;">?? Reporte RAP</button><button onclick="location.reload()" class="btn btn-outline-secondary">Volver</button>'; 
                    div.parentNode.appendChild(box); 
                } 
                box.style.display = 'block'; 
            }; 
        } 
    }); 
}); 
</script> 
''' 
 
for root, dirs, files in os.walk('.'): 
    for f in files: 
        if 'evaluaci' in f.lower() and f.endswith('.html'): 
            p = os.path.join(root, f) 
            with open(p, 'r', encoding='utf-8') as file: content = file.read() 
            with open(p, 'w', encoding='utf-8') as file: file.write(content + js_code) 
            print('LISTO: Interactividad inyectada en ' + p) 
