from dataclasses import dataclass

@dataclass
class MissionData:
    """Clase que almacena los datos de la misión actual"""
    altitude: float
    velocity: float
    fuel: float
    orbit_status: str
    stage: int
    thrust: float
    orientation: float
    temperature: float
    battery: float
    comms: bool

    @classmethod
    def create_default(cls):
        """Crea una instancia con valores predeterminados"""
        return cls(
            altitude=0,
            velocity=0,
            fuel=100,
            orbit_status="PRE-LAUNCH",
            stage=1,
            thrust=0,
            orientation=90,
            temperature=20,
            battery=100,
            comms=True
        )
