import os
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QMainWindow, QMessageBox, QTableWidgetItem,
    QFileDialog, QInputDialog, QPushButton
)
from PyQt6.QtCore import QRegularExpression, QDate, Qt 
from PyQt6.QtGui import QRegularExpressionValidator


# Módulos de lógica de negocio y persistencia
# Se asume que estos archivos y clases existen en la estructura del proyecto
from utils import validators
from services import grade_service, attendance_service, course_service, student_service
from core import storage
from core.models import RegistroNota, RegistroAsistencia, Estudiante, Curso
from core.reports import ReporteNotas, ReporteAsistencias 

class VentanaPrincipal(QMainWindow):
    """
    Clase principal que maneja la interfaz de usuario.
    Centraliza la interacción entre los widgets (UI) y la lógica de negocio (Services).
    """
    def __init__(self):
        super().__init__()
        # 1. Carga de la interfaz gráfica (Diseño creado en Qt Designer)
        ruta_ui = os.path.join(os.path.dirname(__file__), "main_window.ui")
        uic.loadUi(ruta_ui, self) 

        # 2. Configuración inicial de la aplicación
        # Estas llamadas configuran el estado inicial de la ventana antes de mostrarse.
        self._configurar_validadores()
        self._configurar_fechas()
        self._configurar_menu() 
        self._conectar_signals() # Conexión de botones y eventos de búsqueda
        self._cargar_datos_iniciales()
    
    # ----------------------------------------------------------------------
    # MÉTODOS AUXILIARES Y DE ENCAPSULAMIENTO
    # ----------------------------------------------------------------------
    
    def _obtener_texto_limpio(self, line_edit) -> str:
        """
        Función de utilidad para extraer el texto de un QLineEdit y eliminar espacios
        innecesarios al inicio o final (strip).
        """
        return line_edit.text().strip()
    
    def _obtener_codigo_combo(self, combo_box) -> str:
        """
        Extrae la clave principal (código) del elemento seleccionado en un QComboBox.
        Utiliza currentData() para obtener el valor asociado, si existe, para asegurar la integridad.
        """
        codigo = combo_box.currentData()
        if not codigo:
            # Fallback si currentData no está configurado, asumiendo el formato "CODIGO - Nombre"
            try:
                codigo = combo_box.currentText().split(" - ")[0].strip()
            except:
                codigo = ""
        return codigo

    def _mensaje(self, titulo: str, texto: str):
        """
        Función auxiliar para mostrar mensajes de información al usuario de forma consistente.
        """
        QMessageBox.information(self, titulo, texto)
    
    # ----------------------------------------------------------------------
    # 🟢 Métodos de Configuración Inicial
    # ----------------------------------------------------------------------
    
    def _configurar_fechas(self):
        """
        Define las restricciones de fecha para los widgets QDateEdit según las reglas de negocio.
        """
        fecha_actual = QDate.currentDate()

        # Asistencia: Solo se puede registrar la asistencia del día actual.
        self.dtFechaAsis.setDate(fecha_actual) 
        self.dtFechaAsis.setMinimumDate(fecha_actual)
        self.dtFechaAsis.setMaximumDate(fecha_actual) 
        
        # Cursos: La fecha de creación solo puede ser hoy o en el pasado.
        self.dtFechaCursos.setDate(fecha_actual)
        self.dtFechaCursos.setMaximumDate(fecha_actual)
    
    def _configurar_validadores(self):
        """
        Aplica expresiones regulares (QRegularExpressionValidator) a los campos de texto
        para forzar el formato correcto (e.g., código de curso, nota, email).
        Esto mejora la experiencia del usuario y protege la integridad de los datos.
        """
        # Validador para códigos (ej: ABC123)
        re_codigo = QRegularExpression(r"^[A-Z]{3}\d{3}$")
        val_codigo = QRegularExpressionValidator(re_codigo)

        self.txtCodigoEstudianteNota.setValidator(val_codigo)
        self.txtCodigoEstudianteAsis.setValidator(val_codigo)
        self.txtCodigoCurso.setValidator(val_codigo)
        self.txtCodigoEstudiante.setValidator(val_codigo)

        # Validador para nombre, email y nota (asumiendo que se definen en 'validators')
        re_nombre = QRegularExpression(validators.RE_NOMBRE.pattern)
        val_nombre = QRegularExpressionValidator(re_nombre)
        self.txtNombreEstudiante.setValidator(val_nombre)

        re_email = QRegularExpression(validators.RE_EMAIL.pattern)
        val_email = QRegularExpressionValidator(re_email)
        self.txtEmailEstudiante.setValidator(val_email)

        re_nota = QRegularExpression(validators.RE_NOTA.pattern)
        val_nota = QRegularExpressionValidator(re_nota)
        self.txtNota.setValidator(val_nota)

    def _configurar_menu(self):
        """
        Crea y conecta las acciones del menú superior (menubar) para la funcionalidad de Reportes.
        """
        barra = self.menuBar()
        menu_reportes = barra.addMenu("Reportes")

        self.actReporteNotasEst = menu_reportes.addAction(
            "Exportar reporte de notas por estudiante"
        )
        self.actReporteAsisEst = menu_reportes.addAction(
            "Exportar reporte de asistencia por estudiante"
        )

        self.actReporteNotasEst.triggered.connect(
            self.exportar_reporte_notas_por_estudiante
        )
        self.actReporteAsisEst.triggered.connect(
            self.exportar_reporte_asistencia_por_estudiante
        )

    def _conectar_signals(self):
        """
        Define las conexiones entre las acciones del usuario (clicks, texto cambiado)
        y los métodos de la clase que manejan la lógica.
        """
        # Conexión de botones de REGISTRO
        self.btnAgregarNota.clicked.connect(self.agregar_nota)
        self.btnRegistrarAsistencia.clicked.connect(self.registrar_asistencia)
        self.btnAgregarCurso.clicked.connect(self.agregar_curso)
        self.btnAgregarEstudiante.clicked.connect(self.agregar_estudiante)
        
        # Conexión de botones de BÚSQUEDA (Para búsqueda manual si se desea)
        self.btnBuscarEstudiantes.clicked.connect(self.buscar_estudiantes)
        self.btnBuscarCursos.clicked.connect(self.buscar_cursos)
        self.btnBuscarNotas.clicked.connect(self.buscar_notas)
        self.btnBuscarAsistencias.clicked.connect(self.buscar_asistencias)
        
        # 🟢 Conexión de BÚSQUEDA EN TIEMPO REAL: 
        # Llama a la función de búsqueda cada vez que el texto cambia en el QLineEdit.
        self.txtBuscarEstudiantes.textChanged.connect(self.buscar_estudiantes)
        self.txtBuscarCursos.textChanged.connect(self.buscar_cursos)
        self.txtBuscarNotas.textChanged.connect(self.buscar_notas)
        self.txtBuscarAsistencias.textChanged.connect(self.buscar_asistencias)


    def _cargar_datos_iniciales(self):
        """
        Método llamado al inicio para popular todas las tablas y Combobox con 
        los datos persistentes.
        """
        self._cargar_tabla_notas()
        self._cargar_tabla_asistencias()
        self._cargar_tabla_cursos()
        self._cargar_tabla_estudiantes()
        self._cargar_combo_cursos()

    # ----------------------------------------------------------------------
    # 🔎 Lógica de Búsqueda y Actualización de Tablas
    # Nota: Los métodos 'buscar_X' solo obtienen el filtro y llaman a '_cargar_tabla_X'
    # ----------------------------------------------------------------------

    def buscar_estudiantes(self):
        """Obtiene el texto de búsqueda del estudiante y dispara la actualización de la tabla."""
        texto_busqueda = self._obtener_texto_limpio(self.txtBuscarEstudiantes).upper()
        self._cargar_tabla_estudiantes(texto_busqueda)

    def _cargar_tabla_estudiantes(self, filtro: str = ""):
        """Filtra y actualiza la tabla de estudiantes, buscando coincidencias en Código, Nombre o Email."""
        estudiantes = student_service.obtener_estudiantes()
        
        if filtro:
            estudiantes = [
                e for e in estudiantes 
                if filtro in e.codigo.upper() or filtro in e.nombre.upper() or filtro in e.email.upper()
            ]

        self.tblEstudiantes.setRowCount(len(estudiantes))
        self.tblEstudiantes.setColumnCount(3)
        self.tblEstudiantes.setHorizontalHeaderLabels(["Código", "Nombre", "Email"])

        for i, est in enumerate(estudiantes):
            self.tblEstudiantes.setItem(i, 0, QTableWidgetItem(est.codigo))
            self.tblEstudiantes.setItem(i, 1, QTableWidgetItem(est.nombre))
            self.tblEstudiantes.setItem(i, 2, QTableWidgetItem(est.email))

        self.tblEstudiantes.resizeColumnsToContents()

    def buscar_cursos(self):
        """Obtiene el texto de búsqueda del curso y dispara la actualización de la tabla."""
        texto_busqueda = self._obtener_texto_limpio(self.txtBuscarCursos).upper()
        self._cargar_tabla_cursos(texto_busqueda)

    def _cargar_tabla_cursos(self, filtro: str = ""):
        """Filtra y actualiza la tabla de cursos, buscando coincidencias en Código o Nombre."""
        cursos = course_service.obtener_cursos()
        
        if filtro:
            cursos = [
                c for c in cursos 
                if filtro in c.codigo.upper() or filtro in c.nombre.upper()
            ]

        self.tblCursos.setRowCount(len(cursos))
        self.tblCursos.setColumnCount(3)
        self.tblCursos.setHorizontalHeaderLabels(["Código", "Nombre", "Fecha Creación"])

        for row, c in enumerate(cursos):
            self.tblCursos.setItem(row, 0, QTableWidgetItem(c.codigo))
            self.tblCursos.setItem(row, 1, QTableWidgetItem(c.nombre))
            self.tblCursos.setItem(row, 2, QTableWidgetItem(c.fecha_creacion))
        
        self.tblCursos.resizeColumnsToContents()

    def buscar_notas(self):
        """Obtiene el código de estudiante para buscar y filtrar la tabla de notas."""
        codigo_estudiante = self._obtener_texto_limpio(self.txtBuscarNotas).upper()
        self._cargar_tabla_notas(codigo_estudiante)

    def _cargar_tabla_notas(self, filtro_estudiante: str = ""):
        """Filtra y actualiza la tabla de notas por código de estudiante."""
        registros = storage.load_registros()
        notas = [r for r in registros if isinstance(r, RegistroNota)]
        
        if filtro_estudiante:
            notas = [
                n for n in notas 
                if filtro_estudiante in n.estudiante_codigo.upper()
            ]
            
        self.tblNotas.setRowCount(len(notas))
        self.tblNotas.setColumnCount(3)
        self.tblNotas.setHorizontalHeaderLabels(["Estudiante", "Curso", "Nota"])

        for row, r in enumerate(notas):
            self.tblNotas.setItem(row, 0, QTableWidgetItem(r.estudiante_codigo))
            self.tblNotas.setItem(row, 1, QTableWidgetItem(r.curso_codigo))
            self.tblNotas.setItem(row, 2, QTableWidgetItem(str(r.nota)))

        self.tblNotas.resizeColumnsToContents()

    def buscar_asistencias(self):
        """Obtiene el texto de búsqueda para filtrar la tabla de asistencias por estudiante o curso."""
        texto_busqueda = self._obtener_texto_limpio(self.txtBuscarAsistencias).upper()
        self._cargar_tabla_asistencias(texto_busqueda)

    def _cargar_tabla_asistencias(self, filtro: str = ""):
        """Filtra y actualiza la tabla de asistencias por código de estudiante o código de curso."""
        registros = storage.load_registros()
        asistencias = [r for r in registros if isinstance(r, RegistroAsistencia)]
        
        if filtro:
            asistencias = [
                a for a in asistencias 
                if filtro in a.estudiante_codigo.upper() or filtro in a.curso_codigo.upper()
            ]

        self.tblAsistencias.setRowCount(len(asistencias))
        self.tblAsistencias.setColumnCount(4)
        self.tblAsistencias.setHorizontalHeaderLabels(
            ["Fecha", "Estudiante", "Curso", "Estado"]
        )

        for row, r in enumerate(asistencias):
            estado = "Presente" if r.presente else "Ausente"
            self.tblAsistencias.setItem(row, 0, QTableWidgetItem(r.fecha))
            self.tblAsistencias.setItem(row, 1, QTableWidgetItem(r.estudiante_codigo))
            self.tblAsistencias.setItem(row, 2, QTableWidgetItem(r.curso_codigo))
            self.tblAsistencias.setItem(row, 3, QTableWidgetItem(estado))

        self.tblAsistencias.resizeColumnsToContents()

    # ----------------------------------------------------------------------
    # 💾 Lógica de Registro (CRUD - Creación)
    # ----------------------------------------------------------------------

    def agregar_nota(self):
        """Procesa la entrada del formulario de Nota y llama al servicio para registrarla."""
        cod_est = self._obtener_texto_limpio(self.txtCodigoEstudianteNota).upper()
        cod_curso = self._obtener_codigo_combo(self.cbCursos).upper()
        nota_str = self._obtener_texto_limpio(self.txtNota)

        if not (cod_est and cod_curso and nota_str):
            self._mensaje("Error", "Complete todos los campos de nota.")
            return

        if not validators.validar_nota(nota_str):
            self._mensaje("Error", "La nota debe estar entre 0 y 20 (con decimales opcionales).")
            return

        nota = float(nota_str)
        try:
            grade_service.agregar_nota(cod_est, cod_curso, nota)
            self._cargar_tabla_notas() # Recargar la tabla para mostrar el nuevo registro
            self.txtNota.clear()
            self.txtCodigoEstudianteNota.clear()
        except ValueError as e:
            self._mensaje("Error", str(e))

    def registrar_asistencia(self):
        """Procesa la entrada del formulario de Asistencia y llama al servicio para registrarla."""
        cod_est = self._obtener_texto_limpio(self.txtCodigoEstudianteAsis).upper()
        cod_curso = self._obtener_codigo_combo(self.cbCursosAsistencia).upper()
        
        fecha = self.dtFechaAsis.date().toString("yyyy-MM-dd")
        presente = self.chkPresente.isChecked()
        
        if not (cod_est and cod_curso):
            self._mensaje("Error", "Complete los campos de estudiante y curso.")
            return

        try:
            attendance_service.registrar_asistencia(cod_est, cod_curso, fecha, presente)
            self._cargar_tabla_asistencias() # Recargar la tabla para mostrar el nuevo registro
            self.txtCodigoEstudianteAsis.clear()
        except ValueError as e:
            self._mensaje("Error", str(e))

    def agregar_curso(self):
        """Procesa el formulario de Curso, llama al servicio y actualiza las tablas y combos."""
        codigo = self._obtener_texto_limpio(self.txtCodigoCurso).upper()
        nombre = self._obtener_texto_limpio(self.txtNombreCurso)
        fecha = self.dtFechaCursos.date().toString("yyyy-MM-dd")

        if not (codigo and nombre):
            self._mensaje("Error", "Complete código y nombre del curso.")
            return

        try:
            course_service.crear_curso(codigo, nombre, fecha)
            self._mensaje("Éxito", "Curso creado correctamente.")
            self._cargar_tabla_cursos()
            self._cargar_combo_cursos() # Es vital recargar el combo para usar el nuevo curso
            
            self.txtCodigoCurso.clear()
            self.txtNombreCurso.clear()
        except ValueError as e:
            self._mensaje("Error", str(e))

    def _cargar_combo_cursos(self):
        """
        Carga la lista de cursos disponibles en los QComboBox de las pestañas
        de Notas y Asistencias.
        """
        cursos = course_service.obtener_cursos()
        self.cbCursos.clear()
        self.cbCursosAsistencia.clear()
        for c in cursos:
            text = f"{c.codigo} - {c.nombre}"
            # Usamos c.codigo como 'userData' para una extracción precisa
            self.cbCursos.addItem(text, c.codigo)
            self.cbCursosAsistencia.addItem(text, c.codigo)

    def agregar_estudiante(self):
        """Procesa el formulario de Estudiante y llama al servicio para registrarlo."""
        codigo = self._obtener_texto_limpio(self.txtCodigoEstudiante).upper()
        nombre = self._obtener_texto_limpio(self.txtNombreEstudiante)
        email = self._obtener_texto_limpio(self.txtEmailEstudiante)

        if not codigo or not nombre or not email:
            self._mensaje("Error", "Debe completar todos los campos del estudiante.")
            return

        if not validators.validar_email(email):
            self._mensaje("Error", "El formato del correo electrónico no es válido.")
            return

        try:
            student_service.crear_estudiante(codigo, nombre, email)
            self._mensaje("Éxito", "Estudiante agregado correctamente.")
            
            self.txtCodigoEstudiante.clear()
            self.txtNombreEstudiante.clear()
            self.txtEmailEstudiante.clear()
            self._cargar_tabla_estudiantes() # Recargar tabla
        except ValueError as e:
            self._mensaje("Error", str(e))
    
    # ----------------------------------------------------------------------
    # 📝 Lógica de Reportes
    # ----------------------------------------------------------------------

    def exportar_reporte_notas_por_estudiante(self):
        """Genera un reporte de notas en un archivo .txt para un estudiante específico."""
        codigo, ok = QInputDialog.getText(
            self,
            "Reporte de notas",
            "Ingrese el Código de estudiante:"
        )
        if not ok or not codigo.strip():
            return

        codigo = codigo.strip().upper()
        registros = storage.load_registros()
        registros_est = [
            r for r in registros
            if isinstance(r, RegistroNota) and r.estudiante_codigo.upper() == codigo
        ]

        if not registros_est:
            self._mensaje("Sin datos", f"No hay notas registradas para el estudiante {codigo}.")
            return

        reporte = ReporteNotas() # Uso de patrón Polimorfismo
        texto = reporte.generar(registros_est)

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar reporte de notas",
            f"reporte_notas_{codigo}.txt",
            "Archivos de texto (*.txt)"
        )
        if not ruta:
            return

        try:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(texto)
            self._mensaje("Éxito", f"Reporte de notas guardado en:\n{ruta}")
        except Exception as e:
            self._mensaje("Error", f"No se pudo guardar el reporte:\n{e}")

    def exportar_reporte_asistencia_por_estudiante(self):
        """Genera un reporte de asistencia en un archivo .txt para un estudiante específico."""
        codigo, ok = QInputDialog.getText(
            self,
            "Reporte de asistencia",
            "Ingrese el Código de estudiante:"
        )
        if not ok or not codigo.strip():
            return

        codigo = codigo.strip().upper()
        registros = storage.load_registros()
        registros_est = [
            r for r in registros
            if isinstance(r, RegistroAsistencia) and r.estudiante_codigo.upper() == codigo
        ]

        if not registros_est:
            self._mensaje("Sin datos", f"No hay asistencias registradas para el estudiante {codigo}.")
            return

        reporte = ReporteAsistencias() # Uso de patrón Polimorfismo
        texto = reporte.generar(registros_est)

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar reporte de asistencia",
            f"reporte_asistencia_{codigo}.txt",
            "Archivos de texto (*.txt)"
        )
        if not ruta:
            return

        try:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(texto)
            self._mensaje("Éxito", f"Reporte de asistencia guardado en:\n{ruta}")
        except Exception as e:
            self._mensaje("Error", f"No se pudo guardar el reporte:\n{e}")