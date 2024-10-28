import tkinter as tk
import math
from typing import Tuple, Optional
from dataclasses import dataclass

@dataclass
class OrbitParameters:
    """Parámetros de la órbita actual"""
    altitude: float  # en km
    angle: float    # en grados
    eccentricity: float = 0.0
    inclination: float = 0.0

class OrbitDisplay:
    def __init__(self, parent: tk.Frame):
        """
        Inicializa el display orbital
        
        Args:
            parent: Frame padre donde se colocará el display
        """
        self.parent = parent
        self.center_x = 150
        self.center_y = 150
        self.earth_radius = 50
        self.scale_factor = 10  # km por pixel
        
        self._create_display()
        self._create_legend()
        
        # Estado actual
        self.current_orbit: Optional[OrbitParameters] = None
        self.trajectory_points: list[Tuple[float, float]] = []
        self.max_trajectory_points = 50

    def _create_display(self):
        """Crea el canvas principal del display orbital"""
        # Frame contenedor
        self.frame = tk.Frame(
            self.parent,
            bg='black',
            highlightbackground="#00FF00",
            highlightthickness=1
        )
        self.frame.pack(pady=5)
        
        # Título
        tk.Label(
            self.frame,
            text="ORBITAL DISPLAY",
            fg="#00FF00",
            bg="black",
            font=('Courier', 12, 'bold')
        ).pack(pady=5)
        
        # Canvas para el display orbital
        self.canvas = tk.Canvas(
            self.frame,
            width=300,
            height=300,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(pady=5)
        
        # Crear grid de referencia
        self._draw_grid()

    def _create_legend(self):
        """Crea la leyenda del display"""
        legend_frame = tk.Frame(self.frame, bg='black')
        legend_frame.pack(fill='x', padx=5)
        
        items = [
            ("Spacecraft", "#00FF00"),
            ("Earth", "#004400"),
            ("Orbit", "#0000FF"),
            ("Target", "#FF0000")
        ]
        
        for text, color in items:
            item_frame = tk.Frame(legend_frame, bg='black')
            item_frame.pack(side='left', padx=5)
            
            # Indicador de color
            tk.Label(
                item_frame,
                text="■",
                fg=color,
                bg='black',
                font=('Courier', 8)
            ).pack(side='left')
            
            # Texto
            tk.Label(
                item_frame,
                text=text,
                fg="#00FF00",
                bg='black',
                font=('Courier', 8)
            ).pack(side='left')

    def _draw_grid(self):
        """Dibuja el grid de referencia"""
        # Líneas de grid
        for i in range(0, 301, 50):
            # Líneas verticales
            self.canvas.create_line(
                i, 0, i, 300,
                fill='#001100',
                dash=(2, 4)
            )
            # Líneas horizontales
            self.canvas.create_line(
                0, i, 300, i,
                fill='#001100',
                dash=(2, 4)
            )

    def _draw_earth(self):
        """Dibuja la Tierra"""
        self.canvas.create_oval(
            self.center_x - self.earth_radius,
            self.center_y - self.earth_radius,
            self.center_x + self.earth_radius,
            self.center_y + self.earth_radius,
            fill='#004400',
            outline='#00FF00'
        )
        
        # Línea del ecuador
        self.canvas.create_line(
            self.center_x - self.earth_radius, self.center_y,
            self.center_x + self.earth_radius, self.center_y,
            fill='#008800',
            dash=(2, 2)
        )

    def _calculate_spacecraft_position(self, orbit: OrbitParameters) -> Tuple[float, float]:
        """
        Calcula la posición de la nave en el canvas
        
        Args:
            orbit: Parámetros orbitales actuales
            
        Returns:
            Tuple con las coordenadas (x, y) en el canvas
        """
        # Calcular radio de la órbita en pixels
        orbit_radius = self.earth_radius + (orbit.altitude / self.scale_factor)
        
        # Calcular posición considerando excentricidad e inclinación
        base_x = orbit_radius * math.cos(math.radians(orbit.angle))
        base_y = orbit_radius * math.sin(math.radians(orbit.angle))
        
        # Aplicar inclinación
        x = base_x
        y = base_y * math.cos(math.radians(orbit.inclination))
        
        return (
            self.center_x + x,
            self.center_y + y
        )

    def update_display(self, orbit: OrbitParameters):
        """
        Actualiza el display con nuevos datos orbitales
        
        Args:
            orbit: Nuevos parámetros orbitales
        """
