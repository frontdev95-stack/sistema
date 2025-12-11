from typing import List
from core import storage
from core.models import Curso

def crear_curso(codigo: str, nombre: str, fecha_creacion: str) -> None:
    """Crea un nuevo curso y lo guarda en el almacenamiento."""
    cursos = storage.load_cursos()
    
    # Verificar si ya existe
    if any(c.codigo == codigo for c in cursos):
        raise ValueError(f"El curso con código {codigo} ya existe.")
    
    nuevo_curso = Curso(codigo=codigo, nombre=nombre, fecha_creacion=fecha_creacion)
    cursos.append(nuevo_curso)
    storage.save_cursos(cursos)

def obtener_cursos() -> List[Curso]:
    """Obtiene la lista de todos los cursos."""
    return storage.load_cursos()
