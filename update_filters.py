import glob
import re

files = glob.glob('scrapers/*.py')
old_str = 'if any(palabra in titulo_chk for palabra in ["senior", "ssr", "semi-senior", "lead", "jefe", "manager", "principal", "arquitecto", "sr"]):'

new_str = """# Filtro estricto Junior (Excluye niveles Mid/Senior)
                        import re
                        excluir = [r"\\bsenior\\b", r"\\bssr\\b", r"semi-senior", r"semi senior", r"\\bsr\\.?\\b", r"\\blead\\b", r"\\bjefe\\b", r"\\bmanager\\b", r"principal", r"arquitecto", r"experto", r"specialist", r"especialista", r"coordinador", r"supervisor", r"líder", r"lider", r"director", r"\\bhead\\b", r"\\bvp\\b", r"gerente", r"middle", r"mid-level", r"mid level", r"\\bmid\\b", r"experiencia", r"experienced"]
                        if any(re.search(p, titulo_chk) for p in excluir):"""

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if old_str in content:
        # Reemplazar viejo codigo
        content = content.replace(old_str, new_str)
        # Asegurar de que no hay doble filtro
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Mejorado: {f}")
    else:
        print(f"No match in: {f}")

