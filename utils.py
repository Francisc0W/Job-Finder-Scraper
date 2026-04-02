import re

# Compilamos las expresiones regulares una sola vez al cargar el módulo para mejorar el rendimiento
EXCLUIR_TERMS = [
    r"\bsenior\b", r"\bssr\b", r"semi-senior", r"semi senior", r"\bsr\.?\b", 
    r"\blead\b", r"\bjefe\b", r"\bmanager\b", r"principal", r"arquitecto", 
    r"experto", r"specialist", r"especialista", r"coordinador", r"supervisor", 
    r"líder", r"lider", r"director", r"\bhead\b", r"\bvp\b", r"gerente", 
    r"middle", r"mid-level", r"mid level", r"\bmid\b", r"experiencia", r"experienced"
]

EXCLUIR_REGEXES = [re.compile(term, re.IGNORECASE) for term in EXCLUIR_TERMS]

def es_valido_para_junior(titulo: str) -> bool:
    """
    Evalúa si un título de trabajo es adecuado para un perfil Junior.
    Excluye explícitamente perfiles Mid o Senior basados en la lista de términos.
    """
    # Si alguna expresión regular coincide con el título, significa que NO es para junior
    for regex in EXCLUIR_REGEXES:
        if regex.search(titulo):
            return False
    return True
