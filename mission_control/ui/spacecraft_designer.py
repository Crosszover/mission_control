import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Tuple, Any
import math

from systems.spacecraft_system import SpacecraftFactory, ComponentSpec, SpacecraftDesign

class DraggableComponent:
    def __init__(self, canvas: tk.Canvas, component: ComponentSpec, x: int, y: int):
        self.canvas = canvas
        self.component = component
        self.x = x
        self.y = y
        
        # Calcular dimensiones en pixels con un tamaño mínimo
        scale = 40  # pixels por metro
        self.width = max(60, int(component.size['x'] * scale))  # mínimo 60 pixels
        self.height = max(40, int(component.size['z'] * scale))  # mínimo 40 pixels
        
        # Crear representación visual
        self.create_visual()
        
    def create_visual(self):
        """Crea la representación visual del componente"""
        # Color según categoría
        colors = {
            "PROPULSION": "#FF0000",
            "STORAGE": "#00FF00",
            "POWER": "#FFFF00",
            "CONTROL": "#00FFFF",
            "LIFE_SUPPORT": "#FF00FF"
        }
        color = colors.get(self.component.category, "#FFFFFF")
        
        # Crear rectángulo principal
        self.shape = self.canvas.create_rectangle(
            self.x - self.width//2,
            self.y - self.height//2,
            self.x + self.width//2,
            self.y + self.height//2,
            fill=color,
            outline="#00FF00",  # Verde brillante para mejor visibilidad
            width=2
        )
        
        # Añadir texto
        self.label = self.canvas.create_text(
            self.x,
            self.y,
            text=self.component.name,
            fill="#000000",
            font=("Courier", 10, "bold"),  # Fuente más grande y negrita
            width=self.width - 8
        )
        
    def move(self, dx: int, dy: int):
        """Mueve el componente"""
        self.x += dx
        self.y += dy
        self.canvas.move(self.shape, dx, dy)
        self.canvas.move(self.label, dx, dy)
        
    def get_bounds(self) -> Tuple[int, int, int, int]:
        """Obtiene los límites del componente"""
        return (
            self.x - self.width//2,
            self.y - self.height//2,
            self.x + self.width//2,
            self.y + self.height//2
        )

    def transfer_to_canvas(self, new_canvas: tk.Canvas, x: int, y: int):
        """Transfiere el componente a un nuevo canvas"""
        # Guardar coordenadas nuevas
        self.x = x
        self.y = y
        
        # Eliminar del canvas antiguo
        old_canvas = self.canvas
        old_canvas.delete(self.shape)
        old_canvas.delete(self.label)
        
        # Actualizar canvas y recrear visual
        self.canvas = new_canvas
        self.create_visual()

class SpacecraftDesignerPanel:
    def __init__(self, parent: tk.Frame, spacecraft_factory: SpacecraftFactory):
        self.parent = parent
        self.spacecraft_factory = spacecraft_factory
        self.current_design: Optional[SpacecraftDesign] = None
        self.dragged_component: Optional[DraggableComponent] = None
        self.components: Dict[str, DraggableComponent] = {}
        
        # Crear y configurar la interfaz
        self._create_interface()

    def _debug_info(self):
        """Muestra información de depuración"""
        print("\n=== DEBUG DETALLADO ===")
        print("Tecnologías investigadas:", self.spacecraft_factory.research_system.researched_technologies)
        print("Componentes disponibles:", [comp.name for comp in self.spacecraft_factory.get_available_components().values()])
        print("Componentes en pantalla:", list(self.components.keys()))
        print("=====================\n")

    def reload_components(self):
        """Recarga los componentes disponibles"""
        print("Forzando recarga de componentes...")
        self._load_available_components()

    def _create_interface(self):
            """Crea la interfaz principal"""
            # Frame principal dividido en tres secciones
            self.main_frame = tk.Frame(self.parent, bg='black')
            self.main_frame.pack(expand=True, fill='both', padx=5, pady=5)
            
            # Panel izquierdo (componentes disponibles)
            self.components_frame = tk.Frame(self.main_frame, bg='black')
            self.components_frame.pack(side='left', fill='y', padx=5)
            
            # Panel central (área de diseño)
            self.design_frame = tk.Frame(self.main_frame, bg='black')
            self.design_frame.pack(side='left', fill='both', expand=True)
            
            # Panel derecho (estadísticas y controles)
            self.stats_frame = tk.Frame(self.main_frame, bg='black')
            self.stats_frame.pack(side='right', fill='y', padx=5)
            
            self._create_components_panel()
            self._create_design_area()
            self._create_stats_panel()
        
    def _create_components_panel(self):
        """Crea el panel de componentes disponibles"""
        # Marco con título
        components_box = tk.Frame(
            self.components_frame,
            bg='black',
            highlightbackground="#00FF00",
            highlightthickness=1
        )
        components_box.pack(fill='both', expand=True)
        
        tk.Label(
            components_box,
            text="COMPONENTS",
            fg="#00FF00",
            bg="black",
            font=('Courier', 12, 'bold')
        ).pack(pady=5)
        
        # Frame para el canvas y scrollbar
        scroll_frame = tk.Frame(components_box, bg='black')
        scroll_frame.pack(fill='both', expand=True, pady=5)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(scroll_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Lista de componentes con scrollbar
        self.component_list = tk.Canvas(
            scroll_frame,
            bg='black',
            width=200,
            height=600,
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.component_list.pack(side='left', fill='both', expand=True)
        
        # Configurar scrollbar
        scrollbar.config(command=self.component_list.yview)
        
        # Cargar componentes disponibles
        self._load_available_components()
        
        # Bindings para drag & drop
        self.component_list.bind('<ButtonPress-1>', self._start_drag)
        self.component_list.bind('<B1-Motion>', self._drag)
        self.component_list.bind('<ButtonRelease-1>', self._end_drag)
        
    def _create_design_area(self):
        """Crea el área de diseño principal"""
        # Marco con título
        design_box = tk.Frame(
            self.design_frame,
            bg='black',
            highlightbackground="#00FF00",
            highlightthickness=1
        )
        design_box.pack(fill='both', expand=True)
        
        tk.Label(
            design_box,
            text="DESIGN AREA",
            fg="#00FF00",
            bg="black",
            font=('Courier', 12, 'bold')
        ).pack(pady=5)
        
        # Canvas para el diseño
        self.design_canvas = tk.Canvas(
            design_box,
            bg='black',
            width=600,
            height=600,
            highlightthickness=0
        )
        self.design_canvas.pack(pady=5)
        
        # Grid de referencia
        self._draw_grid()
        
        # Bindings para el canvas de diseño
        self.design_canvas.bind('<ButtonPress-1>', self._start_drag)
        self.design_canvas.bind('<B1-Motion>', self._drag)
        self.design_canvas.bind('<ButtonRelease-1>', self._end_drag)
        
    def _create_stats_panel(self):
        """Crea el panel de estadísticas"""
        # Marco con título
        stats_box = tk.Frame(
            self.stats_frame,
            bg='black',
            highlightbackground="#00FF00",
            highlightthickness=1
        )
        stats_box.pack(fill='both', expand=True)
        
        tk.Label(
            stats_box,
            text="STATISTICS",
            fg="#00FF00",
            bg="black",
            font=('Courier', 12, 'bold')
        ).pack(pady=5)
        
        # Variables de estadísticas
        self.stat_vars = {}
        stats = [
            "Mass", "Cost", "Power",
            "Delta-V", "Reliability"
        ]
        
        for stat in stats:
            frame = tk.Frame(stats_box, bg='black')
            frame.pack(fill='x', padx=5, pady=2)
            
            tk.Label(
                frame,
                text=f"{stat}:",
                fg="#00FF00",
                bg="black",
                font=('Courier', 10),
                width=12,
                anchor='w'
            ).pack(side='left')
            
            var = tk.StringVar(value="0")
            self.stat_vars[stat] = var
            
            tk.Label(
                frame,
                textvariable=var,
                fg="#00FF00",
                bg="black",
                font=('Courier', 10)
            ).pack(side='right')
            
        # Botones de control
        buttons_frame = tk.Frame(stats_box, bg='black')
        buttons_frame.pack(fill='x', pady=10)
        
        # Crear botones
        self._create_control_buttons(buttons_frame)

    def _create_control_buttons(self, parent_frame):
        """Crea los botones de control"""
        buttons = [
            ("New Design", self._new_design),
            ("Save Design", self._save_design),
            ("Load Design", self._load_design),
            ("Refresh Components", self.reload_components),
            ("DEBUG", self._debug_info)
        ]
        
        for text, command in buttons:
            tk.Button(
                parent_frame,
                text=text,
                command=command,
                fg="#00FF00",
                bg="black",
                font=('Courier', 10)
            ).pack(fill='x', pady=2)


    def _draw_grid(self):
            """Dibuja el grid de referencia"""
            for i in range(0, 601, 20):
                # Líneas verticales
                self.design_canvas.create_line(
                    i, 0, i, 600,
                    fill='#001100',
                    dash=(2, 4)
                )
                # Líneas horizontales
                self.design_canvas.create_line(
                    0, i, 600, i,
                    fill='#001100',
                    dash=(2, 4)
                )
                
    def _load_available_components(self):
        """Carga los componentes disponibles"""
        y_pos = 40  # Posición vertical inicial
        
        # Limpieza previa
        self.component_list.delete('all')
        self.components.clear()
        
        available_components = self.spacecraft_factory.get_available_components()
        
        print("\n=== DEBUG COMPONENTES ===")
        print("Número de componentes disponibles:", len(available_components))
        print("Componentes disponibles:", [comp.name for comp in available_components.values()])
        
        for component in available_components.values():
            comp = DraggableComponent(
                self.component_list,
                component,
                100,  # x centrado
                y_pos
            )
            self.components[component.id] = comp
            y_pos += 100  # Espaciado entre componentes
        
        # Ajustar el scrollregion
        self.component_list.configure(scrollregion=(0, 0, 200, y_pos + 40))
        
    def _start_drag(self, event):
        """Inicia el arrastre de un componente"""
        canvas = event.widget
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        
        items = canvas.find_overlapping(x-2, y-2, x+2, y+2)
        if items:
            for component in self.components.values():
                if component.shape in items or component.label in items:
                    self.dragged_component = component
                    self.drag_start = (x, y)
                    # Crear una copia temporal para el arrastre
                    temp_comp = DraggableComponent(
                        canvas,
                        component.component,
                        x, y
                    )
                    self.temp_drag = temp_comp
                    break
                    
    def _drag(self, event):
        """Maneja el arrastre de componentes"""
        if self.dragged_component and hasattr(self, 'temp_drag'):
            canvas = event.widget
            x = canvas.canvasx(event.x)
            y = canvas.canvasy(event.y)
            
            dx = x - self.drag_start[0]
            dy = y - self.drag_start[1]
            
            self.temp_drag.move(dx, dy)
            self.drag_start = (x, y)
            
    def _end_drag(self, event):
        """Finaliza el arrastre de componentes"""
        if self.dragged_component:
            canvas = event.widget
            x = canvas.canvasx(event.x)
            y = canvas.canvasy(event.y)
            
            # Si el destino es el canvas de diseño
            if canvas == self.design_canvas:
                new_comp = DraggableComponent(
                    self.design_canvas,
                    self.dragged_component.component,
                    x, y
                )
                self.components[f"design_{len(self.components)}"] = new_comp
                self._add_component_to_design(new_comp)
            
            # Limpiar componente temporal
            if hasattr(self, 'temp_drag'):
                self.temp_drag.canvas.delete(self.temp_drag.shape)
                self.temp_drag.canvas.delete(self.temp_drag.label)
                delattr(self, 'temp_drag')
            
            self.dragged_component = None
            
    def _add_component_to_design(self, component: DraggableComponent):
        """Añade un componente al diseño actual"""
        if self.current_design:
            # Convertir posición de pixels a metros
            scale = 20  # pixels por metro
            position = {
                'x': component.x / scale,
                'y': 0,  # Por ahora solo 2D
                'z': component.y / scale
            }
            
            if self.current_design.add_component(component.component, position):
                # Actualizar estadísticas
                self._update_stats()
            else:
                # Si no se puede añadir, eliminar el componente visual
                self.design_canvas.delete(component.shape)
                self.design_canvas.delete(component.label)
                
    def _update_stats(self):
        """Actualiza las estadísticas mostradas"""
        if self.current_design:
            stats = self.current_design.get_summary()
            
            self.stat_vars["Mass"].set(f"{stats['mass']:.1f} kg")
            self.stat_vars["Cost"].set(f"{stats['cost']:.0f} $")
            self.stat_vars["Power"].set(f"{stats['power_balance']:.1f} kW")
            self.stat_vars["Delta-V"].set(f"{stats['delta_v']:.0f} m/s")
            self.stat_vars["Reliability"].set(f"{stats['reliability']:.3f}")
            
    def _new_design(self):
        """Crea un nuevo diseño"""
        self.current_design = self.spacecraft_factory.create_design("New Design")
        self._clear_design_area()
        self._update_stats()
        
    def _clear_design_area(self):
        """Limpia el área de diseño"""
        self.design_canvas.delete('all')
        self._draw_grid()
        self.components.clear()
        
    def _save_design(self):
        """Guarda el diseño actual"""
        print("\n=== DEBUG Guardando diseño ===")
        if self.current_design:
            print(f"Diseño tiene {len(self.current_design.components)} componentes")
        else:
            print("No hay diseño activo")
        print("=========================\n")
        
    def _load_design(self):
        """Carga un diseño guardado"""
        print("\n=== DEBUG Cargando diseño ===")
        print("Función de carga no implementada")
        print("=========================\n")
