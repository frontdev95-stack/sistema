from __future__ import annotations
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import date

# ---------- Base con polimorfismo ----------

class Serializable(ABC):
    """Clase base para modelos que se guardan en JSON."""
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        ...

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Serializable":
        ...

# ---------- Persona, Estudiante, Docente ----------

@dataclass
class Persona(Serializable):
    codigo: str
    nombre: str
    email: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Persona":
        return cls(**data)

@dataclass
class Estudiante(Persona):
    carrera: str = ""
    fecha_creacion: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["tipo"] = "estudiante"
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Estudiante":
        return cls(
            codigo=data["codigo"],
            nombre=data["nombre"],
            email=data.get("email", ""),  # Make email optional/default safe
            carrera=data.get("carrera", ""),
            fecha_creacion=data.get("fecha_creacion", "")
        )

@dataclass
class Docente(Persona):
    departamento: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["tipo"] = "docente"
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Docente":
        return cls(
            codigo=data["codigo"],
            nombre=data["nombre"],
            email=data["email"],
            departamento=data.get("departamento", "")
        )


# ---------- Curso ----------

@dataclass
class Curso(Serializable):
    codigo: str
    nombre: str
    fecha_creacion: str = ""
    creditos: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Curso":
        return cls(
            codigo=data["codigo"],
            nombre=data["nombre"],
            fecha_creacion=data.get("fecha_creacion", ""),
            creditos=data.get("creditos", 0)
        )

# ---------- Registros base (para polimorfismo en reportes) ----------

class Registro(Serializable, ABC):
    @abstractmethod
    def get_tipo(self) -> str:
        ...

@dataclass
class RegistroNota(Registro):
    estudiante_codigo: str
    curso_codigo: str
    nota: float

    def get_tipo(self) -> str:
        return "nota"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["tipo"] = self.get_tipo()
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RegistroNota":
        return cls(
            estudiante_codigo=data["estudiante_codigo"],
            curso_codigo=data["curso_codigo"],
            nota=data["nota"]
        )

@dataclass
class RegistroAsistencia(Registro):
    estudiante_codigo: str
    curso_codigo: str
    fecha: str   # "YYYY-MM-DD"
    presente: bool

    def get_tipo(self) -> str:
        return "asistencia"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["tipo"] = self.get_tipo()
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RegistroAsistencia":
        return cls(
            estudiante_codigo=data["estudiante_codigo"],
            curso_codigo=data["curso_codigo"],
            fecha=data["fecha"],
            presente=data["presente"]
        )
