from typing import List
from core.models import RegistroAsistencia
from core import storage

from services import student_service

def registrar_asistencia(estudiante_codigo: str, curso_codigo: str, fecha: str, presente: bool):
    if not student_service.existe_estudiante(estudiante_codigo):
        raise ValueError(f"El estudiante con código {estudiante_codigo} no existe.")

    registros = storage.load_registros()
    registros.append(RegistroAsistencia(estudiante_codigo, curso_codigo, fecha, presente))
    storage.save_registros(registros)

def listar_asistencia_por_curso(curso_codigo: str) -> List[RegistroAsistencia]:
    registros = storage.load_registros()
    return [
        r for r in registros
        if isinstance(r, RegistroAsistencia) and r.curso_codigo == curso_codigo
    ]

