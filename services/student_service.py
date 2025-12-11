from typing import List
from core import storage
from core.models import Estudiante

def crear_estudiante(codigo: str, nombre: str, email: str) -> None:
    """Crea un nuevo estudiante y lo guarda."""
    estudiantes = storage.load_estudiantes()
    
    if any(e.codigo == codigo for e in estudiantes):
        raise ValueError(f"El estudiante con código {codigo} ya existe.")
    
    from datetime import date
    fecha_hoy = date.today().strftime("%Y-%m-%d")

    nuevo_estudiante = Estudiante(
        codigo=codigo, 
        nombre=nombre, 
        email=email, 
        fecha_creacion=fecha_hoy
    )
    estudiantes.append(nuevo_estudiante)
    storage.save_estudiantes(estudiantes)

def obtener_estudiantes() -> List[Estudiante]:
    """Obtiene la lista de todos los estudiantes."""
    return storage.load_estudiantes()

def existe_estudiante(codigo: str) -> bool:
    """Verifica si un estudiante existe por su código."""
    estudiantes = storage.load_estudiantes()
    return any(e.codigo == codigo for e in estudiantes)
