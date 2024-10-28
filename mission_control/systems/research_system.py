from dataclasses import dataclass
from typing import Dict, List, Optional
import json
import os

@dataclass
class Technology:
    id: str
    name: str
    description: str
    cost: int
    research_time: int  # en días
    prerequisites: List[str]
    category: str
    level: int
    effects: Dict[str, float]
    unlocks: List[str]  # IDs de componentes o tecnologías que desbloquea
    
    def is_available(self, researched_technologies: List[str]) -> bool:
        """Verifica si la tecnología está disponible para investigar"""
        print(f"\n=== DEBUG Technology.is_available ===")
        print(f"Verificando disponibilidad de: {self.id}")
        print(f"Prerrequisitos: {self.prerequisites}")
        print(f"Tecnologías investigadas: {researched_technologies}")
        
        # Si no hay prerrequisitos, está disponible
        if not self.prerequisites:
            print("No tiene prerrequisitos -> Disponible")
            print("===================================\n")
            return True
            
        # Si tiene prerrequisitos, todos deben estar investigados
        available = all(prereq in researched_technologies for prereq in self.prerequisites)
        print(f"Resultado: {'Disponible' if available else 'No disponible'}")
        print("===================================\n")
        return available

@dataclass
class ResearchProject:
    technology: Technology
    progress: float  # 0 a 100
    scientists_assigned: int
    status: str  # "ACTIVE", "PAUSED", "COMPLETED"
    
    def update_progress(self, efficiency: float) -> bool:
        """Actualiza el progreso del proyecto"""
        if self.status == "ACTIVE":
            progress_increase = (self.scientists_assigned * efficiency) / self.technology.research_time
            self.progress = min(100, self.progress + progress_increase)
            
            if self.progress >= 100:
                self.status = "COMPLETED"
                return True
        return False

class ResearchSystem:
    def __init__(self):
        self.technologies: Dict[str, Technology] = {}
        self.active_projects: Dict[str, ResearchProject] = {}
        self.researched_technologies: List[str] = []
        self.available_scientists = 10
        self.research_points = 1000
        self.efficiency = 1.0
        
        # Cargar tecnologías
        self.load_technologies()
        
    def load_technologies(self):
        """Carga la base de datos de tecnologías"""
        # Ejemplo de tecnologías predefinidas
        basic_techs = {
            "BASIC_ROCKETRY": Technology(
                id="BASIC_ROCKETRY",
                name="Basic Rocketry",
                description="Fundamentos de la ingeniería de cohetes",
                cost=100,
                research_time=5,
                prerequisites=[],
                category="PROPULSION",
                level=1,
                effects={"thrust_efficiency": 1.1},
                unlocks=["LIQUID_FUEL"]
            ),
            "LIQUID_FUEL": Technology(
                id="LIQUID_FUEL",
                name="Liquid Fuel Systems",
                description="Sistemas avanzados de combustible líquido",
                cost=200,
                research_time=10,
                prerequisites=["BASIC_ROCKETRY"],
                category="PROPULSION",
                level=2,
                effects={"fuel_efficiency": 1.2},
                unlocks=["ADVANCED_PROPULSION"]
            ),
        }
        
        self.technologies.update(basic_techs)
        print("\n=== DEBUG Research System Initialized ===")
        print(f"Tecnologías cargadas: {list(self.technologies.keys())}")
        print("=====================================\n")
    
    def start_research(self, tech_id: str, scientists: int) -> bool:
        """Inicia un nuevo proyecto de investigación"""
        print(f"\n=== DEBUG start_research ===")
        print(f"Iniciando investigación de: {tech_id}")
        print(f"Científicos asignados: {scientists}")
        
        if tech_id not in self.technologies:
            print("Tecnología no encontrada")
            print("========================\n")
            return False
            
        tech = self.technologies[tech_id]
        
        if not tech.is_available(self.researched_technologies):
            print("Tecnología no disponible (prerrequisitos no cumplidos)")
            print("========================\n")
            return False
            
        if tech_id in self.researched_technologies:
            print("Tecnología ya investigada")
            print("========================\n")
            return False
            
        if scientists > self.available_scientists:
            print("No hay suficientes científicos disponibles")
            print("========================\n")
            return False
            
        if tech.cost > self.research_points:
            print("No hay suficientes puntos de investigación")
            print("========================\n")
            return False
            
        self.active_projects[tech_id] = ResearchProject(
            technology=tech,
            progress=0,
            scientists_assigned=scientists,
            status="ACTIVE"
        )
        
        self.available_scientists -= scientists
        self.research_points -= tech.cost
        
        print("Investigación iniciada exitosamente")
        print("========================\n")
        return True
    
    def update_research(self):
        """Actualiza el progreso de todos los proyectos activos"""
        completed_techs = []
        print("\n=== DEBUG update_research ===")
        print("Proyectos activos:", list(self.active_projects.keys()))
        
        for tech_id, project in self.active_projects.items():
            print(f"Actualizando proyecto {tech_id}, progreso actual: {project.progress}")
            if project.update_progress(self.efficiency):
                completed_techs.append(tech_id)
                if tech_id not in self.researched_technologies:
                    self.researched_technologies.append(tech_id)
                    print(f"¡Tecnología completada y añadida!: {tech_id}")
                self.available_scientists += project.scientists_assigned
        
        # Eliminar proyectos completados
        for tech_id in completed_techs:
            if tech_id in self.active_projects:
                del self.active_projects[tech_id]
        
        print(f"Estado actual de tecnologías: {self.researched_technologies}")
        print("========================\n")
        return completed_techs
    
    def get_available_technologies(self) -> List[Technology]:
        """Retorna lista de tecnologías disponibles para investigar"""
        print("\n=== DEBUG get_available_technologies ===")
        available = [tech for tech_id, tech in self.technologies.items()
                    if tech.is_available(self.researched_technologies) 
                    and tech_id not in self.researched_technologies]
        print(f"Tecnologías disponibles: {[tech.id for tech in available]}")
        print("====================================\n")
        return available
    
    def is_technology_researched(self, tech_id: str) -> bool:
        """Verifica si una tecnología está investigada"""
        return tech_id in self.researched_technologies
    
    def get_research_progress(self, tech_id: str) -> Optional[float]:
        """Obtiene el progreso de una investigación"""
        if tech_id in self.active_projects:
            return self.active_projects[tech_id].progress
        return None
    
    def pause_research(self, tech_id: str) -> bool:
        """Pausa un proyecto de investigación"""
        if tech_id in self.active_projects:
            project = self.active_projects[tech_id]
            project.status = "PAUSED"
            self.available_scientists += project.scientists_assigned
            project.scientists_assigned = 0
            return True
        return False
    
    def resume_research(self, tech_id: str, scientists: int) -> bool:
        """Reanuda un proyecto de investigación"""
        if tech_id in self.active_projects and scientists <= self.available_scientists:
            project = self.active_projects[tech_id]
            project.status = "ACTIVE"
            project.scientists_assigned = scientists
            self.available_scientists -= scientists
            return True
        return False

    def get_debug_info(self):
        """Imprime información de depuración detallada"""
        print("\n=== ESTADO DEL SISTEMA DE INVESTIGACIÓN ===")
        print("ID del sistema:", id(self))
        print("Tecnologías disponibles:", list(self.technologies.keys()))
        print("Tecnologías investigadas:", self.researched_technologies)
        print("Proyectos activos:", list(self.active_projects.keys()))
        print("Científicos disponibles:", self.available_scientists)
        print("Puntos de investigación:", self.research_points)
        print("========================================\n")
