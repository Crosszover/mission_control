import tkinter as tk
from typing import Dict, Any

class TelemetryPanel:
    def __init__(self, parent: tk.Frame):
        """
        Inicializa el panel de telemetría
        
        Args:
            parent: Frame padre donde se colocará el panel
        """
        self.parent = parent
        self.telemetry_vars: Dict[str, tk.StringVar] = {}
        self._create_panel()
        
    def _create_panel(self):
        """Crea el panel principal de telemetría"""
        # Marco para telemetría con borde verde
        self.telemetry_box = tk.Frame(
            self.parent,
            bg='black',
            highlightbackground="#00FF00",
            highlightthickness=1
        )
        self.telemetry_box.pack(fill='x', pady=5)
        
        # Título del panel
        tk.Label(
            self.telemetry_box,
            text="TELEMETRY",
            fg="#00FF00",
            bg="black",
            font=('Courier', 12, 'bold')
        ).pack(pady=5)
        
        # Crear indicadores de telemetría
        self._create_telemetry_indicators()
        
    def _create_telemetry_indicators(self):
        """Crea los indicadores individuales de telemetría"""
        telemetry_items = [
            ("ALTITUDE", "km"),
            ("VELOCITY", "km/s"),
            ("FUEL", "%"),
            ("STAGE", ""),
            ("THRUST", "%"),
            ("ORIENTATION", "°"),
            ("TEMPERATURE", "°C"),
            ("BATTERY", "%")
        ]
        
        for item, unit in telemetry_items:
            self._create_telemetry_row(item, unit)
    
    def _create_telemetry_row(self, item: str, unit: str):
        """
        Crea una fila de telemetría
        
        Args:
            item: Nombre del indicador
            unit: Unidad de medida
        """
        frame = tk.Frame(self.telemetry_box, bg='black')
        frame.pack(fill='x', padx=5)
        
        # Etiqueta con el nombre del indicador
        tk.Label(
            frame,
            text=f"{item}:",
            fg="#00FF00",
            bg="black",
            font=('Courier', 10),
            width=15,
            anchor='w'
        ).pack(side='left')
        
        # Variable para el valor
        var = tk.StringVar(value="0")
        self.telemetry_vars[item] = var
        
        # Etiqueta para mostrar el valor
        tk.Label(
            frame,
            textvariable=var,
            fg="#00FF00",
            bg="black",
            font=('Courier', 10)
        ).pack(side='right')
        
        if unit:  # Si hay unidad, mostrarla
            tk.Label(
                frame,
                text=unit,
                fg="#00FF00",
                bg="black",
                font=('Courier', 10)
            ).pack(side='right', padx=(0, 5))

    def update_value(self, key: str, value: Any):
        """
        Actualiza el valor de un indicador
        
        Args:
            key: Nombre del indicador
            value: Nuevo valor
        """
        if key in self.telemetry_vars:
            if isinstance(value, float):
                self.telemetry_vars[key].set(f"{value:.1f}")
            else:
                self.telemetry_vars[key].set(str(value))

    def reset_values(self):
        """Reinicia todos los valores a 0"""
        for var in self.telemetry_vars.values():
            var.set("0")
