import tkinter as tk
import sys
import os
from tkinter import ttk

# Asegurarse de que podemos importar desde los subdirectorios
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from systems.mission_controller import MissionController

class SpaceProgram:
    def __init__(self, root):
        self.root = root
        self.root.title("Space Program v0.2")
        self.root.configure(bg='black')
        
        # Configurar estilo para pestañas
        self.setup_styles()
        
        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Crear las diferentes secciones
        self.create_mission_control()
        self.create_research_tab()
        self.create_spacecraft_designer()
        
    def setup_styles(self):
        """Configura los estilos personalizados"""
        style = ttk.Style()
        style.configure('Custom.TNotebook', background='black')
        style.configure('Custom.TNotebook.Tab', 
                       background='black',
                       foreground='#00FF00',
                       padding=[10, 2],
                       font=('Courier', 10))
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', '#004400')],
                 foreground=[('selected', '#00FF00')])
        
        self.notebook.configure(style='Custom.TNotebook')
        
    def create_mission_control(self):
        """Crea la pestaña de Control de Misión"""
        mission_frame = tk.Frame(self.notebook, bg='black')
        self.mission_controller = MissionController(mission_frame)
        self.notebook.add(mission_frame, text='MISSION CONTROL')
        
    def create_research_tab(self):
        """Crea la pestaña de Investigación"""
        research_frame = tk.Frame(self.notebook, bg='black')
        # Aquí añadiremos el sistema de investigación
        self.notebook.add(research_frame, text='RESEARCH & DEVELOPMENT')
        
    def create_spacecraft_designer(self):
        """Crea la pestaña de Diseño de Naves"""
        design_frame = tk.Frame(self.notebook, bg='black')
        # Aquí añadiremos el diseñador de naves
        self.notebook.add(design_frame, text='SPACECRAFT DESIGN')

def create_directories():
    """Crea la estructura de directorios necesaria"""
    directories = ['models', 'ui', 'systems', 'research', 'spacecraft']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            with open(os.path.join(directory, '__init__.py'), 'w') as f:
                pass

def main():
    """Función principal que inicia la aplicación"""
    create_directories()
    root = tk.Tk()
    root.geometry("1200x800")  # Tamaño inicial de ventana
    
    # Configurar el ícono y título
    root.title("Space Program v0.2")
    
    # Crear la aplicación
    app = SpaceProgram(root)
    
    # Iniciar el loop principal
    root.mainloop()

if __name__ == "__main__":
    main()
