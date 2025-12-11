from typing import List
from core.models import RegistroNota
from core import storage

from services import student_service

def agregar_nota(estudiante_codigo: str, curso_codigo: str, nota: float):
    if not student_service.existe_estudiante(estudiante_codigo):
        raise ValueError(f"El estudiante con código {estudiante_codigo} no existe.")

    registros = storage.load_registros()
    registros.append(RegistroNota(estudiante_codigo, curso_codigo, nota))
    storage.save_registros(registros)

def listar_notas_por_curso(curso_codigo: str) -> List[RegistroNota]:
    registros = storage.load_registros()
    return [
        r for r in registros
        if isinstance(r, RegistroNota) and r.curso_codigo == curso_codigo
    ]

