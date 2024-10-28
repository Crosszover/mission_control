import tkinter as tk
from datetime import datetime
from typing import Callable, Dict, List, Optional

class ControlPanel:
    def __init__(self, parent: tk.Frame):
        """
        Inicializa el panel de control
        
        Args:
            parent: Frame padre donde se colocará el panel
        """
        self.parent = parent
        self._create_panel()
        self._create_event_log()
        
        # Callbacks para los eventos
        self.callbacks: Dict[str, Callable] = {
            "launch": lambda: None,
            "stage": lambda: None,
            "abort": lambda: None,
            "thrust_up": lambda: None,
            "thrust_down": lambda: None
        }

    def _create_panel(self):
        """Crea el panel principal de control"""
        # Marco para controles con borde verde
        self.control_box = tk.Frame(
            self.parent,
            bg='black',
            highlightbackground="#00FF00",
            highlightthickness=1
        )
        self.control_box.pack(fill='x', pady=5)
        
        # Título del panel
        tk.Label(
            self.control_box,
            text="MISSION CONTROL",
            fg="#00FF00",
            bg="black",
            font=('Courier', 12, 'bold')
        ).pack(pady=5)
        
        # Crear botones de control
        self._create_control_buttons()
        self._create_thrust_control()
        
    def _create_control_buttons(self):
        """Crea los botones principales de control"""
        buttons = [
            ("LAUNCH", "launch", "#00FF00"),
            ("STAGE", "stage", "#00FF00"),
            ("ABORT", "abort", "#FF0000")
        ]
        
        for text, callback_key, color in buttons:
            btn = tk.Button(
                self.control_box,
                text=text,
                command=lambda k=callback_key: self.callbacks[k](),
                fg=color,
                bg="black",
                font=('Courier', 10),
                width=20,
                relief=tk.RAISED,
                borderwidth=2
            )
            btn.pack(pady=2)
            
    def _create_thrust_control(self):
        """Crea los controles de empuje"""
        # Título de control de empuje
        tk.Label(
            self.control_box,
            text="THRUST CONTROL",
            fg="#00FF00",
            bg="black",
            font=('Courier', 10)
        ).pack(pady=5)
        
        # Frame para los botones de empuje
        thrust_frame = tk.Frame(self.control_box, bg='black')
        thrust_frame.pack(fill='x', padx=5)
        
        # Botón de reducción de empuje
        tk.Button(
            thrust_frame,
            text="▼",
            command=lambda: self.callbacks["thrust_down"](),
            fg="#00FF00",
            bg="black",
            font=('Courier', 10),
            width=5
        ).pack(side='left', padx=5)
        
        # Botón de aumento de empuje
        tk.Button(
            thrust_frame,
            text="▲",
            command=lambda: self.callbacks["thrust_up"](),
            fg="#00FF00",
            bg="black",
            font=('Courier', 10),
            width=5
        ).pack(side='right', padx=5)

    def _create_event_log(self):
        """Crea el registro de eventos"""
        # Marco para eventos
        event_box = tk.Frame(
            self.parent,
            bg='black',
            highlightbackground="#00FF00",
            highlightthickness=1
        )
        event_box.pack(fill='both', expand=True, pady=5)
        
        # Título del registro
        tk.Label(
            event_box,
            text="EVENT LOG",
            fg="#00FF00",
            bg="black",
            font=('Courier', 12, 'bold')
        ).pack(pady=5)
        
        # Área de texto para eventos
        self.event_list = tk.Text(
            event_box,
            fg="#00FF00",
            bg="black",
            font=('Courier', 9),
            height=10,
            width=40
        )
        self.event_list.pack(fill='both', expand=True, padx=5)
        
        # Scrollbar para el registro
        scrollbar = tk.Scrollbar(event_box, command=self.event_list.yview)
        scrollbar.pack(side='right', fill='y')
        self.event_list.config(yscrollcommand=scrollbar.set)

    def set_callback(self, event: str, callback: Callable):
        """
        Establece un callback para un evento específico
        
        Args:
            event: Nombre del evento ('launch', 'stage', 'abort', etc.)
            callback: Función a llamar cuando ocurra el evento
        """
        if event in self.callbacks:
            self.callbacks[event] = callback

    def log_event(self, message: str, level: str = "INFO"):
        """
        Registra un evento en el log
        
        Args:
            message: Mensaje a registrar
            level: Nivel del mensaje ('INFO', 'WARNING', 'ERROR', etc.)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_tags = {
            "INFO": "#00FF00",
            "WARNING": "#FFFF00",
            "ERROR": "#FF0000",
            "SUCCESS": "#00FF00"
        }
        
        # Crear un tag para el color si no existe
        tag = f"color_{level}"
        if not tag in self.event_list.tag_names():
            self.event_list.tag_configure(tag, foreground=color_tags.get(level, "#00FF00"))
        
        # Insertar el mensaje con el color apropiado
        self.event_list.insert('1.0', f"[{timestamp}] ", (tag,))
        self.event_list.insert('1.0' + str(len(timestamp) + 3), f"{message}\n", (tag,))
        self.event_list.see('1.0')  # Auto-scroll al último mensaje

    def clear_log(self):
        """Limpia el registro de eventos"""
        self.event_list.delete(1.0, tk.END)
