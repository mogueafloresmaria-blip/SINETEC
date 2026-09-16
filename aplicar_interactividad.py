import os 
 
def agregar(): 
    for root, dirs, files in os.walk('.'): 
        for file in files: 
            if 'evaluaci' in file.lower() and file.endswith('.html'): 
                ruta = os.path.join(root, file) 
                with open(ruta, 'r', encoding='utf-8') as f: html = f.read() 
                js = """<style>.tarjeta-interactiva{cursor:pointer;transition:all 0.3s}.tarjeta-interactiva:hover{transform:translateY(-4px)}.asistente-container{display:none;background:#fff;border-radius:12px;padding:25px;border:2px solid #f8ceec}</style><script>document.addEventListener('DOMContentLoaded',function(){const c=document.querySelector('.tarjeta-vacia, .text-center.p-5, div:has(svg), div:has(i)');if(c){c.classList.add('tarjeta-interactiva');const p=document.createElement('div');p.className='asistente-container mt-4 text-center';p.innerHTML='^<h4 style="color:#4a2e35;font-weight:bold"^>? Asistente Inteligente de Evaluaci¢n^</h4^>^<p style="color:#885e6a"^>Selecciona una acci¢n r pida:^</p^>^<button onclick="alert(\'Cargando lista...\')" class="btn me-2" style="background:#f8ceec;color:#4a2e35;font-weight:600;border:none;padding:10px 20px"^>?? Cargar Lista^</button^>^<button onclick="alert(\'Generando reporte...\')" class="btn" style="background:#f06292;color:white;font-weight:600;border:none;padding:10px 20px"^>?? Reporte R pido^</button^>^<button id="btn-cerrar" class="btn btn-sm btn-outline-secondary ms-2"^>Cerrar^</button^>';c.parentNode.insertBefore(p,c.nextSibling);c.addEventListener('click',function(){c.style.display='none';p.style.display='block'});document.addEventListener('click',function(e){if(e.target^&^&e.target.id==='btn-cerrar'){p.style.display='none';c.style.display='block'}})}});</script>""" 
                else: html = html + js 
                with open(ruta, 'w', encoding='utf-8') as f: f.write(html) 
                print(f'EXITO: Modificado en {ruta}') 
                return 
agregar() 
