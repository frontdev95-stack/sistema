import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import VentanaPrincipal
from PyQt6.QtCore import QFile, QTextStream # Importaciones necesarias para manejar archivos

def main():
    app = QApplication(sys.argv)
    
    # ==========================================================
    # 1. Cargar la Hoja de Estilos (style.qss)
    # ==========================================================
    # Intentamos abrir el archivo style.qss
    style_file = QFile("style.qss")
    if style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
        # Crear un lector de texto (stream) para leer el contenido del archivo
        stream = QTextStream(style_file)
        
        # Leer todo el contenido del archivo
        stylesheet = stream.readAll()
        
        # 2. Aplicar la Hoja de Estilos a la aplicación (QApplication)
        app.setStyleSheet(stylesheet)
        
        style_file.close()
    else:
        print("Advertencia: No se pudo cargar el archivo style.qss. La interfaz usará el estilo predeterminado.")
    
    # ==========================================================
    
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()