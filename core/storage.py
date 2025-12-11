import json
import os
from typing import List, Dict, Any, Type, TypeVar
from contextlib import contextmanager

from .models import (
    Estudiante, Docente, Curso,
    RegistroNota, RegistroAsistencia, Registro
)

T = TypeVar("T")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

@contextmanager
def open_json(path: str, mode: str):
    """Context manager para abrir JSON con seguridad."""
    with open(path, mode, encoding="utf-8") as f:
        yield f

def load_list(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open_json(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_list(path: str, data: List[Dict[str, Any]]):
    with open_json(path, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Rutas básicas
ESTUDIANTES_FILE = os.path.join(DATA_DIR, "estudiantes.json")
DOCENTES_FILE = os.path.join(DATA_DIR, "docentes.json")
CURSOS_FILE = os.path.join(DATA_DIR, "cursos.json")
REGISTROS_FILE = os.path.join(DATA_DIR, "registros.json")

# ---------- Funciones genéricas ----------

def load_estudiantes() -> List[Estudiante]:
    raw = load_list(ESTUDIANTES_FILE)
    return [Estudiante.from_dict(d) for d in raw]

def save_estudiantes(estudiantes: List[Estudiante]):
    save_list(ESTUDIANTES_FILE, [e.to_dict() for e in estudiantes])

def load_cursos() -> List[Curso]:
    raw = load_list(CURSOS_FILE)
    return [Curso.from_dict(d) for d in raw]

def save_cursos(cursos: List[Curso]):
    save_list(CURSOS_FILE, [c.to_dict() for c in cursos])

def load_registros() -> List[Registro]:
    raw = load_list(REGISTROS_FILE)
    registros: List[Registro] = []
    for d in raw:
        tipo = d.get("tipo")
        if tipo == "nota":
            registros.append(RegistroNota.from_dict(d))
        elif tipo == "asistencia":
            registros.append(RegistroAsistencia.from_dict(d))
    return registros
def save_registros(registros: List[Registro]):
    save_list(REGISTROS_FILE, [r.to_dict() for r in registros])
