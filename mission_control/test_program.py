import tkinter as tk
from tkinter import ttk
import os
import sys

# Asegurarse de que existen los directorios necesarios
directories = ['models', 'ui', 'systems', 'research', 'spacecraft']
for directory in directories:
    if not os.path.exists(directory):
        os.makedirs(directory)
        with open(os.path.join(directory, '__init__.py'), 'w') as f:
            pass

# Importar los sistemas necesarios
from systems.research_system import ResearchSystem
from systems.spacecraft_system import SpacecraftFactory
from ui.research_panel import ResearchPanel
from ui.spacecraft_designer import SpacecraftDesignerPanel

class MissionControlTemp:
    """Versión temporal del control de misión"""
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg='black')
        self.frame.pack(expand=True, fill='both')
        
        # Mensaje temporal
        tk.Label(
            self.frame,
            text="MISSION CONTROL\n\nEn desarrollo...",
            fg="#00FF00",
            bg="black",
            font=('Courier', 20)
        ).pack(expand=True)

class TestProgram:
    def __init__(self):
        # Crear la ventana principal
        self.root = tk.Tk()
        self.root.title("Space Program Test")
        self.root.geometry("1200x800")
        self.root.configure(bg='black')
        
        # Crear frame principal
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(expand=True, fill='both')
        
        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Configurar estilo mejorado
        style = ttk.Style()
        style.theme_use('default')  # Usar tema por defecto como base
        
        style.configure('Custom.TNotebook', 
                       background='black',
                       borderwidth=0)
        
        style.configure('Custom.TNotebook.Tab', 
                       background='#004400',
                       foreground='white',
                       padding=[15, 5],
                       font=('Courier', 12, 'bold'),
                       borderwidth=2)
        
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', '#008800')],
                 foreground=[('selected', 'white')],
                 expand=[('selected', [1, 1, 1, 0])])
        
        self.notebook.configure(style='Custom.TNotebook')
        
        # Crear frames para cada pestaña
        self.research_frame = tk.Frame(self.notebook, bg='black')
        self.design_frame = tk.Frame(self.notebook, bg='black')
        self.mission_frame = tk.Frame(self.notebook, bg='black')
        
        # Inicializar sistemas
        self.research_system = ResearchSystem()
        self.spacecraft_factory = SpacecraftFactory(self.research_system)
        
        # Crear paneles
        self.research_panel = ResearchPanel(self.research_frame)
        self.design_panel = SpacecraftDesignerPanel(self.design_frame, self.spacecraft_factory)
        self.mission_panel = MissionControlTemp(self.mission_frame)  # Versión temporal
        
        # Añadir pestañas con padding adicional
        self.notebook.add(self.research_frame, text=' RESEARCH & DEVELOPMENT ')
        self.notebook.add(self.design_frame, text=' SPACECRAFT DESIGN ')
        self.notebook.add(self.mission_frame, text=' MISSION CONTROL ')
        
        # Crear panel de instrucciones
        self.instructions_frame = tk.Frame(self.main_frame, bg='black', height=100)
        self.instructions_frame.pack(fill='x', padx=5, pady=5)
        
        self.instruction_text = tk.Label(
            self.instructions_frame,
            text="",
            fg="#00FF00",
            bg="black",
            font=('Courier', 10),
            justify='left',
            wraplength=1150
        )
        self.instruction_text.pack(pady=5)
        
        # Vincular cambio de pestaña con actualización de instrucciones
        self.notebook.bind('<<NotebookTabChanged>>', self._update_instructions)
        
        # Mostrar instrucciones iniciales
        self._update_instructions(None)
        
    def _update_instructions(self, event):
        """Actualiza las instrucciones según la pestaña activa"""
        current_tab = self.notebook.select()
        tab_id = self.notebook.index(current_tab)
        
        instructions = {
            0: """RESEARCH & DEVELOPMENT:
• Haz clic en una tecnología para ver sus detalles
• Asigna científicos usando el control numérico
• Presiona START RESEARCH para comenzar la investigación""",
            
            1: """SPACECRAFT DESIGN:
• Arrastra componentes desde el panel izquierdo al área de diseño
• Los componentes se desbloquean al investigar sus tecnologías
• Observa las estadísticas de tu nave en el panel derecho""",
            
            2: """MISSION CONTROL:
• Selecciona una nave diseñada para lanzar
• Monitorea los sistemas durante el lanzamiento
• Usa los controles de empuje para ajustar la trayectoria
• Mantén un ojo en el consumo de combustible y las anomalías"""
        }
        
        # Actualizar texto de instrucciones
        self.instruction_text.config(text=instructions.get(tab_id, ""))

def main():
    app = TestProgram()
    app.root.mainloop()

if __name__ == "__main__":
    main()
