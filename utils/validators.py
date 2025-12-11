import re

# Regex básicos (puedes adaptarlos a tu institución)
RE_CODIGO = re.compile(r"^[A-Z]{3}\d{3}$")           # Ej: ABC123
RE_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÑáéíóúñ ]{2,50}$")
RE_EMAIL = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")
# Nota 0–20 con decimales opcionales
RE_NOTA = re.compile(r"^(20(\.0{1,2})?|[0-1]?\d(\.\d{1,2})?)$")

def validar_codigo(codigo: str) -> bool:
    return bool(RE_CODIGO.fullmatch(codigo))

def validar_nombre(nombre: str) -> bool:
    return bool(RE_NOMBRE.fullmatch(nombre.strip()))

def validar_email(email: str) -> bool:
    return bool(RE_EMAIL.fullmatch(email.strip()))

def validar_nota(nota_str: str) -> bool:
    return bool(RE_NOTA.fullmatch(nota_str.strip()))

