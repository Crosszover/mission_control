import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional
import math

from systems.research_system import ResearchSystem, Technology, ResearchProject

class TechTreeNode:
    def __init__(self, canvas: tk.Canvas, x: int, y: int, technology: Technology):
        """
        Representa un nodo en el árbol de tecnologías
        
        Args:
            canvas: Canvas donde se dibujará el nodo
            x, y: Coordenadas del nodo
            technology: Tecnología asociada al nodo
        """
        self.canvas = canvas
        self.x = x
        self.y = y
        self.technology = technology
        self.width = 120
        self.height = 60
        self.node_id = None
        self.text_id = None
        self.progress_bar_id = None
        self.progress = 0
        
    def draw(self, is_available: bool, is_researched: bool):
        """Dibuja el nodo con el estado apropiado"""
        # Determinar color según estado
        if is_researched:
            color = "#00FF00"
            text_color = "#000000"
            bg_color = "#008800"
        elif is_available:
            color = "#FFFF00"
            text_color = "#000000"
            bg_color = "#888800"
        else:
            color = "#444444"
            text_color = "#888888"
            bg_color = "#222222"
            
        # Dibujar nodo
        self.node_id = self.canvas.create_rectangle(
            self.x - self.width//2,
            self.y - self.height//2,
            self.x + self.width//2,
            self.y + self.height//2,
            fill=bg_color,
            outline=color,
            width=2
        )
        
        # Dibujar texto
        self.text_id = self.canvas.create_text(
            self.x,
            self.y - 10,
            text=self.technology.name,
            fill=text_color,
            font=("Courier", 8, "bold"),
            width=self.width - 10
        )
        
        # Dibujar barra de progreso
        if not is_researched:
            self.progress_bar_id = self.canvas.create_rectangle(
                self.x - self.width//2 + 5,
                self.y + 10,
                self.x + self.width//2 - 5,
                self.y + 20,
                fill="black",
                outline=color
            )
            self.update_progress(self.progress)
            
    def update_progress(self, progress: float):
        """Actualiza la barra de progreso"""
        self.progress = progress
        if self.progress_bar_id:
            bar_width = self.width - 10
            progress_width = bar_width * (progress / 100)
            
            self.canvas.coords(
                self.progress_bar_id,
                self.x - self.width//2 + 5,
                self.y + 10,
                self.x - self.width//2 + 5 + progress_width,
                self.y + 20
            )

class ResearchPanel:
    def __init__(self, parent: tk.Frame):
        """
        Panel principal de investigación
        
        Args:
            parent: Frame padre donde se colocará el panel
        """
        self.parent = parent
        self.research_system = ResearchSystem()
        
        # Crear interfaz
        self._create_interface()
        
        # Temporizador de actualización
        self.update_timer = None
        self.start_update_loop()
        
    def _create_interface(self):
        """Crea la interfaz principal del panel de investigación"""
        # Frame principal dividido en dos
        self.main_frame = tk.Frame(self.parent, bg='black')
        self.main_frame.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Panel izquierdo (árbol de tecnologías)
        self.tree_frame = tk.Frame(self.main_frame, bg='black')
        self.tree_frame.pack(side='left', fill='both', expand=True)
        
        # Panel derecho (detalles y controles)
        self.details_frame = tk.Frame(self.main_frame, bg='black')
        self.details_frame.pack(side='right', fill='y', padx=5)
        
        self._create_tech_tree()
        self._create_details_panel()
        
    def _create_tech_tree(self):
        """Crea el visualizador del árbol de tecnologías"""
        # Frame para el canvas con scrollbars
        self.canvas_frame = tk.Frame(
            self.tree_frame,
            bg='black',
            highlightbackground="#00FF00",
            highlightthickness=1
        )
        self.canvas_frame.pack(expand=True, fill='both')
        
        # Scrollbars
        self.v_scrollbar = tk.Scrollbar(self.canvas_frame)
        self.v_scrollbar.pack(side='right', fill='y')
        
        self.h_scrollbar = tk.Scrollbar(
            self.canvas_frame,
            orient='horizontal'
        )
        self.h_scrollbar.pack(side='bottom', fill='x')
        
        # Canvas para el árbol
        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg='black',
            width=800,
            height=600,
            scrollregion=(0, 0, 1600, 1200),
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )
        self.canvas.pack(side='left', expand=True, fill='both')
        
        # Configurar scrollbars
        self.v_scrollbar.config(command=self.canvas.yview)
        self.h_scrollbar.config(command=self.canvas.xview)
        
        # Crear nodos del árbol
        self.nodes: Dict[str, TechTreeNode] = {}
        self._create_tech_nodes()
        
        # Binding para selección de tecnología
        self.canvas.bind('<Button-1>', self._on_canvas_click)
        
    def _create_tech_nodes(self):
        """Crea y posiciona los nodos del árbol de tecnologías"""
        # Organizar tecnologías por niveles
        tech_levels: Dict[int, list] = {}
        for tech in self.research_system.technologies.values():
            if tech.level not in tech_levels:
                tech_levels[tech.level] = []
            tech_levels[tech.level].append(tech)
            
        # Posicionar nodos
        x_spacing = 200
        y_spacing = 150
        for level, techs in tech_levels.items():
            x = level * x_spacing + 100
            for i, tech in enumerate(techs):
                y = (i + 1) * y_spacing
                self.nodes[tech.id] = TechTreeNode(self.canvas, x, y, tech)
                
        # Dibujar conexiones y nodos
        self._draw_connections()
        self._update_nodes()
        
    def _draw_connections(self):
        """Dibuja las conexiones entre nodos"""
        for tech_id, node in self.nodes.items():
            tech = node.technology
            for prereq_id in tech.prerequisites:
                if prereq_id in self.nodes:
                    prereq_node = self.nodes[prereq_id]
                    self.canvas.create_line(
                        prereq_node.x + prereq_node.width//2,
                        prereq_node.y,
                        node.x - node.width//2,
                        node.y,
                        fill="#00FF00",
                        width=2
                    )
                    
    def _create_details_panel(self):
        """Crea el panel de detalles de tecnología"""
        # Marco para detalles
        details_box = tk.Frame(
            self.details_frame,
            bg='black',
            highlightbackground="#00FF00",
            highlightthickness=1
        )
        details_box.pack(fill='both', expand=True)
        
        # Título
        self.tech_name = tk.Label(
            details_box,
            text="Select Technology",
            fg="#00FF00",
            bg="black",
            font=('Courier', 12, 'bold')
        )
        self.tech_name.pack(pady=5)
        
        # Descripción
        self.tech_description = tk.Text(
            details_box,
            fg="#00FF00",
            bg="black",
            font=('Courier', 10),
            height=5,
            width=30,
            wrap=tk.WORD
        )
        self.tech_description.pack(padx=5, pady=5)
        
        # Costos y requisitos
        self.tech_costs = tk.Label(
            details_box,
            text="",
            fg="#00FF00",
            bg="black",
            font=('Courier', 10),
            justify=tk.LEFT
        )
        self.tech_costs.pack(pady=5)
        
        # Control de científicos
        scientist_frame = tk.Frame(details_box, bg='black')
        scientist_frame.pack(pady=5)
        
        tk.Label(
            scientist_frame,
            text="Scientists: ",
            fg="#00FF00",
            bg="black",
            font=('Courier', 10)
        ).pack(side='left')
        
        self.scientist_var = tk.StringVar(value="0")
        self.scientist_spinbox = tk.Spinbox(
            scientist_frame,
            from_=0,
            to=10,
            width=5,
            textvariable=self.scientist_var,
            bg="black",
            fg="#00FF00"
        )
        self.scientist_spinbox.pack(side='left')
        
        # Botones de control
        self.start_button = tk.Button(
            details_box,
            text="START RESEARCH",
            command=self._start_selected_research,
            fg="#00FF00",
            bg="black",
            font=('Courier', 10)
        )
        self.start_button.pack(pady=5)
        
        # Información de recursos
        self.resource_info = tk.Label(
            details_box,
            text="",
            fg="#00FF00",
            bg="black",
            font=('Courier', 10)
        )
        self.resource_info.pack(pady=5)
        
        self._update_resource_info()
        
    def _update_resource_info(self):
        """Actualiza la información de recursos disponibles"""
        self.resource_info.config(
            text=f"Available Scientists: {self.research_system.available_scientists}\n"
                 f"Research Points: {self.research_system.research_points}"
        )
        
    def _on_canvas_click(self, event):
        """Maneja el click en el canvas"""
        # Convertir coordenadas del evento a coordenadas del canvas
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Buscar nodo clickeado
        for tech_id, node in self.nodes.items():
            if (abs(canvas_x - node.x) < node.width//2 and 
                abs(canvas_y - node.y) < node.height//2):
                self._show_tech_details(node.technology)
                break
                
    def _show_tech_details(self, technology: Technology):
        """Muestra los detalles de una tecnología"""
        self.selected_tech = technology
        
        # Actualizar información
        self.tech_name.config(text=technology.name)
        self.tech_description.delete(1.0, tk.END)
        self.tech_description.insert(1.0, technology.description)
        
        # Mostrar costos y requisitos
        costs_text = f"Cost: {technology.cost} RP\n"
        costs_text += f"Time: {technology.research_time} days\n"
        if technology.prerequisites:
            costs_text += "Requires: " + ", ".join(technology.prerequisites)
        self.tech_costs.config(text=costs_text)
        
        # Actualizar estado del botón
        is_available = technology.id not in self.research_system.researched_technologies
        self.start_button.config(state="normal" if is_available else "disabled")
        
    def _start_selected_research(self):
        """Inicia la investigación de la tecnología seleccionada"""
        if hasattr(self, 'selected_tech'):
            scientists = int(self.scientist_var.get())
            if self.research_system.start_research(self.selected_tech.id, scientists):
                self._update_nodes()
                self._update_resource_info()
                
# ... (código anterior sin cambios hasta la línea del error)

    def _update_nodes(self):
        """Actualiza el estado visual de todos los nodos"""
        # Limpiar canvas
        self.canvas.delete('all')
        
        # Redibujar conexiones
        self._draw_connections()
        
        # Actualizar cada nodo
        for tech_id, node in self.nodes.items():
            is_researched = tech_id in self.research_system.researched_technologies
            is_available = node.technology.is_available(self.research_system.researched_technologies)
            
            node.draw(is_available, is_researched)
            
            # Actualizar progreso si está en investigación
            if tech_id in self.research_system.active_projects:
                progress = self.research_system.get_research_progress(tech_id)
                if progress is not None:
                    node.update_progress(progress)

# ... (resto del código sin cambios)
                    
    def start_update_loop(self):
        """Inicia el loop de actualización"""
        self._update()
        
    def _update(self):
        """Actualiza el estado de la investigación"""
        self.research_system.update_research()
        self._update_nodes()
        self._update_resource_info()
        
        # Programar siguiente actualización
        self.update_timer = self.parent.after(1000, self._update)
