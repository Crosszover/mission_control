import tkinter as tk
import random
from datetime import datetime
from typing import Dict, Optional

from models.mission_data import MissionData
from ui.telemetry_panel import TelemetryPanel
from ui.control_panel import ControlPanel
from ui.orbit_display import OrbitDisplay, OrbitParameters

class MissionController:
    def __init__(self, root: tk.Tk):
        """
        Controlador principal de la misión
        
        Args:
            root: Ventana principal de la aplicación
        """
        self.root = root
        self.mission_active = False
        self.mission_time = 0
        self.anomaly_chance = 0.01
        
        # Objetivos de la misión
        self.target_altitude = 300  # km
        self.target_velocity = 7.8  # km/s para órbita baja
        
        # Configurar la interfaz principal
        self._setup_interface()
        
        # Inicializar datos de misión
        self.mission_data = MissionData.create_default()
        
        # Estado de sistemas críticos
        self.systems = {
            "PROP": True,    # Propulsión
            "GUID": True,    # Guiado
            "ELEC": True,    # Eléctrico
            "COMM": True,    # Comunicaciones
            "LIFE": True,    # Soporte vital
            "THRM": True     # Térmico
        }
        
        # Configurar callbacks
        self._setup_callbacks()
        
        # Temporizador de actualización
        self.update_timer: Optional[str] = None

    def _setup_interface(self):
        """Configura la interfaz principal"""
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Panel izquierdo
        self.left_panel = tk.Frame(self.main_frame, bg='black')
        self.left_panel.pack(side='left', fill='both', expand=True)
        
        # Panel derecho
        self.right_panel = tk.Frame(self.main_frame, bg='black')
        self.right_panel.pack(side='right', fill='both', expand=True)
        
        # Crear componentes UI
        self.telemetry = TelemetryPanel(self.left_panel)
        self.orbit_display = OrbitDisplay(self.left_panel)
        self.control_panel = ControlPanel(self.right_panel)

    def _setup_callbacks(self):
        """Configura los callbacks para los eventos de la UI"""
        self.control_panel.set_callback("launch", self.start_mission)
        self.control_panel.set_callback("stage", self.next_stage)
        self.control_panel.set_callback("abort", self.abort_mission)
        self.control_panel.set_callback("thrust_up", lambda: self.adjust_thrust(10))
        self.control_panel.set_callback("thrust_down", lambda: self.adjust_thrust(-10))

    def update_mission(self):
        """Actualiza el estado de la misión"""
        if not self.mission_active:
            return
            
        self.mission_time += 1
        
        # Simulación física básica
        self._update_physics()
        
        # Verificar anomalías
        self._check_anomalies()
        
        # Actualizar telemetría
        self._update_telemetry()
        
        # Actualizar visualización orbital
        self._update_orbital_display()
        
        # Verificar condiciones de misión
        self._check_mission_status()
        
        # Programar siguiente actualización
        if self.mission_active:
            self.update_timer = self.root.after(100, self.update_mission)

    def _update_physics(self):
        """Actualiza la física de la misión"""
        # Factores de eficiencia según la etapa
        stage_factors = {
            1: {"altitude": 0.1, "velocity": 0.05, "fuel": 0.2},
            2: {"altitude": 0.05, "velocity": 0.1, "fuel": 0.1}
        }
        
        factors = stage_factors.get(self.mission_data.stage, stage_factors[1])
        
        # Actualizar parámetros basados en el empuje actual
        self.mission_data.altitude += self.mission_data.thrust * factors["altitude"]
        self.mission_data.velocity += self.mission_data.thrust * factors["velocity"]
        self.mission_data.fuel -= self.mission_data.thrust * factors["fuel"]
        
        # Efectos de la gravedad y resistencia atmosférica
        if self.mission_data.altitude < 100:  # Por debajo de 100km
            self.mission_data.velocity -= 0.01  # Resistencia atmosférica
        
        # Consumo de batería
        self.mission_data.battery -= 0.01
        
        # Efectos de temperatura
        if self.mission_data.thrust > 50:
            self.mission_data.temperature += 0.1
        else:
            self.mission_data.temperature = max(20, self.mission_data.temperature - 0.05)

    def _check_anomalies(self):
        """Verifica y genera anomalías aleatorias"""
        if random.random() < self.anomaly_chance:
            anomaly_types = [
                ("PROP", "Propulsion system fluctuation detected", "WARNING"),
                ("GUID", "Guidance system interference detected", "WARNING"),
                ("ELEC", "Power system voltage irregularity", "WARNING"),
                ("COMM", "Communication signal degradation", "WARNING"),
                ("LIFE", "Life support minor pressure variance", "WARNING"),
                ("THRM", "Thermal control deviation detected", "WARNING")
            ]
            
            anomaly = random.choice(anomaly_types)
            self.systems[anomaly[0]] = False
            self.control_panel.log_event(anomaly[1], anomaly[2])

    def _update_telemetry(self):
        """Actualiza los displays de telemetría"""
        updates = {
            "ALTITUDE": self.mission_data.altitude,
            "VELOCITY": self.mission_data.velocity,
            "FUEL": self.mission_data.fuel,
            "STAGE": self.mission_data.stage,
            "THRUST": self.mission_data.thrust,
            "ORIENTATION": self.mission_data.orientation,
            "TEMPERATURE": self.mission_data.temperature,
            "BATTERY": self.mission_data.battery
        }
        
        for key, value in updates.items():
            self.telemetry.update_value(key, value)

    def _update_orbital_display(self):
        """Actualiza el display orbital"""
        orbit_params = OrbitParameters(
            altitude=self.mission_data.altitude,
            angle=(self.mission_time * 2) % 360,
            eccentricity=0.0,
            inclination=0.0
        )
        self.orbit_display.update_display(orbit_params)

    def _check_mission_status(self):
        """Verifica el estado general de la misión"""
        # Verificar combustible
        if self.mission_data.fuel <= 0:
            self.control_panel.log_event("CRITICAL: Fuel depleted", "ERROR")
            self.abort_mission()
            return
            
        # Verificar batería
        if self.mission_data.battery <= 10:
            self.control_panel.log_event("WARNING: Low battery", "WARNING")
            
        # Verificar temperatura
        if self.mission_data.temperature > 100:
            self.control_panel.log_event("CRITICAL: Temperature critical", "ERROR")
            self.abort_mission()
            return
            
        # Verificar órbita objetivo
        if (abs(self.mission_data.altitude - self.target_altitude) < 10 and
            abs(self.mission_data.velocity - self.target_velocity) < 0.1):
            self.control_panel.log_event("SUCCESS: Target orbit achieved!", "SUCCESS")

    def start_mission(self):
        """Inicia la misión"""
        if not self.mission_active:
            self.mission_active = True
            self.control_panel.log_event("MISSION STARTED - T PLUS ZERO", "INFO")
            self.update_mission()

    def next_stage(self):
        """Activa la siguiente etapa"""
        if self.mission_active and self.mission_data.stage < 2:
            self.mission_data.stage += 1
            self.control_panel.log_event(
                f"STAGE {self.mission_data.stage} SEPARATION CONFIRMED",
                "SUCCESS"
            )
            self.orbit_display.clear_trajectory()

    def abort_mission(self):
        """Aborta la misión"""
        if self.mission_active:
            self.mission_active = False
            self.control_panel.log_event("MISSION ABORT COMMANDED", "ERROR")
            if self.update_timer:
                self.root.after_cancel(self.update_timer)
            self.reset_mission()

    def adjust_thrust(self, delta: float):
        """
        Ajusta el empuje del cohete
        
        Args:
            delta: Cambio en el empuje (-100 a 100)
        """
        if self.mission_active:
            self.mission_data.thrust = max(0, min(100, self.mission_data.thrust + delta))
            self.control_panel.log_event(
                f"THRUST ADJUSTED TO {self.mission_data.thrust:.1f}%",
                "INFO"
            )

    def reset_mission(self):
        """Reinicia todos los parámetros de la misión"""
        self.mission_time = 0
        self.mission_data = MissionData.create_default()
        
        # Resetear sistemas
        for system in self.systems:
            self.systems[system] = True
        
        # Limpiar displays
        self.telemetry.reset_values()
        self.orbit_display.clear_trajectory()
        self.control_panel.clear_log()
        self.control_panel.log_event("MISSION RESET COMPLETE", "INFO")
