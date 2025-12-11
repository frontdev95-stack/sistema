from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from .models import Registro, RegistroNota, RegistroAsistencia

class Reporte(ABC):
    @abstractmethod
    def generar(self, registros: List[Registro]) -> str:
        ...

class ReporteNotas(Reporte):
    def generar(self, registros: List[Registro]) -> str:
        lineas = ["REPORTE DE NOTAS\n"]
        for r in registros:
            if isinstance(r, RegistroNota):
                lineas.append(
                    f"Estudiante: {r.estudiante_codigo} | "
                    f"Curso: {r.curso_codigo} | Nota: {r.nota}"
                )
        return "\n".join(lineas)

class ReporteAsistencias(Reporte):
    def generar(self, registros: List[Registro]) -> str:
        lineas = ["REPORTE DE ASISTENCIAS\n"]
        for r in registros:
            if isinstance(r, RegistroAsistencia):
                estado = "Presente" if r.presente else "Ausente"
                lineas.append(
                    f"{r.fecha} - Est: {r.estudiante_codigo} "
                    f"Curso: {r.curso_codigo} | {estado}"
                )
        return "\n".join(lineas)
