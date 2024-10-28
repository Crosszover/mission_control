from dataclasses import dataclass
from typing import Dict, List, Optional
import json
import math

@dataclass
class ComponentSpec:
    """Especificaciones base para componentes"""
    id: str
    name: str
    description: str
    mass: float  # kg
    cost: float
    power_required: float  # kW
    tech_requirement: str  # ID de la tecnología requerida
    category: str
    size: Dict[str, float]  # dimensiones en metros
    reliability: float  # 0-1

@dataclass
class PropulsionComponent(ComponentSpec):
    thrust: float  # kN
    isp: float    # segundos
    fuel_type: str
    fuel_consumption: float  # kg/s
    
@dataclass
class PowerComponent(ComponentSpec):
    power_output: float  # kW
    efficiency: float   # 0-1
    
@dataclass
class StorageComponent(ComponentSpec):
    volume: float      # m³
    max_mass: float    # kg
    contents_type: str # "FUEL", "CARGO", "LIFE_SUPPORT"

@dataclass
class ControlComponent(ComponentSpec):
    control_power: float  # Capacidad de control
    redundancy: float    # Sistemas de respaldo

@dataclass
class LifeSupportComponent(ComponentSpec):
    crew_capacity: int
    oxygen_generation: float  # kg/day
    water_recycling: float   # efficiency 0-1

class SpacecraftDesign:
    def __init__(self, name: str):
        self.name = name
        self.components: Dict[str, ComponentSpec] = {}
        self.layout: Dict[str, Dict[str, float]] = {}  # posición x,y,z de cada componente
        
        # Estadísticas calculadas
        self._mass = 0
        self._cost = 0
        self._power_balance = 0
        self._delta_v = 0
        self._reliability = 0
        
    def add_component(self, component: ComponentSpec, position: Dict[str, float]) -> bool:
        """Añade un componente a la nave"""
        if self._check_collision(component, position):
            return False
            
        component_id = f"{component.id}_{len(self.components)}"
        self.components[component_id] = component
        self.layout[component_id] = position
        
        self._update_statistics()
        return True
        
    def remove_component(self, component_id: str) -> bool:
        """Elimina un componente de la nave"""
        if component_id in self.components:
            del self.components[component_id]
            del self.layout[component_id]
            self._update_statistics()
            return True
        return False
        
    def _check_collision(self, new_component: ComponentSpec, position: Dict[str, float]) -> bool:
        """Verifica si hay colisiones con otros componentes"""
        for comp_id, comp in self.components.items():
            other_pos = self.layout[comp_id]
            if self._components_overlap(
                new_component.size, position,
                comp.size, other_pos
            ):
                return True
        return False
        
    def _components_overlap(
        self,
        size1: Dict[str, float],
        pos1: Dict[str, float],
        size2: Dict[str, float],
        pos2: Dict[str, float]
    ) -> bool:
        """Verifica si dos componentes se solapan"""
        for axis in ['x', 'y', 'z']:
            if not (
                pos1[axis] + size1[axis] < pos2[axis] or
                pos1[axis] > pos2[axis] + size2[axis]
            ):
                return True
        return False
        
    def _update_statistics(self):
        """Actualiza las estadísticas de la nave"""
        # Reiniciar estadísticas
        self._mass = 0
        self._cost = 0
        self._power_balance = 0
        self._reliability = 1.0
        
        # Calcular masa y costo base
        for component in self.components.values():
            self._mass += component.mass
            self._cost += component.cost
            self._power_balance -= component.power_required
            self._reliability *= component.reliability
            
            # Añadir generación de energía
            if isinstance(component, PowerComponent):
                self._power_balance += component.power_output
                
        # Calcular delta-v usando la ecuación de Tsiolkovsky
        total_fuel = 0
        total_thrust = 0
        avg_isp = 0
        num_engines = 0
        
        for component in self.components.values():
            if isinstance(component, PropulsionComponent):
                total_thrust += component.thrust
                avg_isp += component.isp
                num_engines += 1
            elif isinstance(component, StorageComponent):
                if component.contents_type == "FUEL":
                    total_fuel += component.max_mass
                    
        if num_engines > 0 and total_fuel > 0:
            avg_isp /= num_engines
            dry_mass = self._mass - total_fuel
            self._delta_v = avg_isp * 9.81 * math.log(self._mass / dry_mass)
    
    def get_summary(self) -> Dict[str, float]:
        """Retorna un resumen de las estadísticas de la nave"""
        return {
            "mass": self._mass,
            "cost": self._cost,
            "power_balance": self._power_balance,
            "delta_v": self._delta_v,
            "reliability": self._reliability,
            "component_count": len(self.components)
        }



class ComponentLibrary:
    def __init__(self):
        self.components: Dict[str, ComponentSpec] = {}
        self._load_default_components()
        
    def _load_default_components(self):
        """Carga los componentes predefinidos"""
        # Componentes básicos (sin requisitos de tecnología)
        self.components["BASIC_ANTENNA"] = ControlComponent(
            id="BASIC_ANTENNA",
            name="Basic Antenna",
            description="Simple communication antenna for short-range transmission",
            mass=10,
            cost=500,
            power_required=0.1,
            tech_requirement="",  # Sin requisito de tecnología
            category="CONTROL",
            size={"x": 0.5, "y": 0.5, "z": 1},
            reliability=0.98,
            control_power=0.5,
            redundancy=0.0
        )
        
        self.components["BASIC_RADIO"] = ControlComponent(
            id="BASIC_RADIO",
            name="Basic Radio",
            description="Basic communication radio for mission control contact",
            mass=5,
            cost=300,
            power_required=0.2,
            tech_requirement="",  # Sin requisito de tecnología
            category="CONTROL",
            size={"x": 0.3, "y": 0.3, "z": 0.3},
            reliability=0.99,
            control_power=0.3,
            redundancy=0.0
        )

        # Componentes que requieren tecnología
        self.components["BASIC_ENGINE"] = PropulsionComponent(
            id="BASIC_ENGINE",
            name="Basic Rocket Engine",
            description="Simple liquid fuel rocket engine",
            mass=1000,
            cost=10000,
            power_required=10,
            tech_requirement="BASIC_ROCKETRY",
            category="PROPULSION",
            size={"x": 2, "y": 2, "z": 3},
            reliability=0.95,
            thrust=100,
            isp=280,
            fuel_type="LIQUID",
            fuel_consumption=0.5
        )
        
        # Tanques
        self.components["BASIC_TANK"] = StorageComponent(
            id="BASIC_TANK",
            name="Basic Fuel Tank",
            description="Standard fuel tank",
            mass=500,
            cost=5000,
            power_required=0,
            tech_requirement="BASIC_ROCKETRY",
            category="STORAGE",
            size={"x": 2, "y": 2, "z": 4},
            reliability=0.98,
            volume=10,
            max_mass=10000,
            contents_type="FUEL"
        )
        
        # Sistemas de energía
        self.components["SOLAR_PANEL"] = PowerComponent(
            id="SOLAR_PANEL",
            name="Basic Solar Panel",
            description="Standard solar power generation",
            mass=100,
            cost=15000,
            power_required=0,
            tech_requirement="LIQUID_FUEL",
            category="POWER",
            size={"x": 4, "y": 0.1, "z": 2},
            reliability=0.96,
            power_output=5,
            efficiency=0.20
        )
        
        # Control
        self.components["BASIC_COMPUTER"] = ControlComponent(
            id="BASIC_COMPUTER",
            name="Basic Flight Computer",
            description="Standard guidance system",
            mass=50,
            cost=20000,
            power_required=0.5,
            tech_requirement="BASIC_ROCKETRY",
            category="CONTROL",
            size={"x": 0.5, "y": 0.5, "z": 0.5},
            reliability=0.99,
            control_power=1.0,
            redundancy=0.5
        )
        
    def get_available_components(self, researched_techs: List[str]) -> Dict[str, ComponentSpec]:
        """Retorna los componentes disponibles según las tecnologías investigadas"""
        print("\n=== DEBUG ComponentLibrary.get_available_components ===")
        print("Buscando componentes para tecnologías:", researched_techs)
        available = {}
        for comp_id, comp in self.components.items():
            print(f"Verificando {comp.name} (requiere: {comp.tech_requirement})")
            if not comp.tech_requirement or comp.tech_requirement in researched_techs:  # Modificado para incluir componentes sin requisitos
                print(f"-> Componente {comp.name} disponible")
                available[comp_id] = comp
            else:
                print(f"-> Componente {comp.name} NO disponible")
        print("=============================================\n")
        return available

# ... (rest of the code remains the same)

    def get_component_by_id(self, component_id: str) -> Optional[ComponentSpec]:
        """Obtiene un componente por su ID"""
        return self.components.get(component_id)

class SpacecraftFactory:
    def __init__(self, research_system):
        self.component_library = ComponentLibrary()
        self.research_system = research_system
        self.designs: Dict[str, SpacecraftDesign] = {}
        
    def create_design(self, name: str) -> SpacecraftDesign:
        """Crea un nuevo diseño de nave"""
        design = SpacecraftDesign(name)
        self.designs[name] = design
        return design
        
    def get_available_components(self) -> Dict[str, ComponentSpec]:
        """Obtiene los componentes disponibles según la investigación actual"""
        print("\n=== DEBUG SpacecraftFactory.get_available_components ===")
        researched_techs = self.research_system.researched_technologies
        print("Research System ID:", id(self.research_system))
        print("Tecnologías investigadas:", researched_techs)
        components = self.component_library.get_available_components(researched_techs)
        print("Componentes disponibles:", [comp.name for comp in components.values()])
        print("=================================================\n")
        return components
    
    def debug_state(self):
        """Imprime el estado actual del sistema"""
        print("\n=== DEBUG SPACECRAFT FACTORY ===")
        print("Research System ID:", id(self.research_system))
        print("Research Technologies:", self.research_system.researched_technologies)
        print("Component Library Size:", len(self.component_library.components))
        comps = self.get_available_components()
        print("Available Components:", [comp.name for comp in comps.values()])
        print("Tech Requirements:", [(comp.name, comp.tech_requirement) 
                                   for comp in self.component_library.components.values()])
        print("===============================\n")
        
    def save_design(self, design: SpacecraftDesign, filename: str):
        """Guarda un diseño en un archivo"""
        # Implementar serialización del diseño
        pass
        
    def load_design(self, filename: str) -> Optional[SpacecraftDesign]:
        """Carga un diseño desde un archivo"""
        # Implementar deserialización del diseño
        pass
