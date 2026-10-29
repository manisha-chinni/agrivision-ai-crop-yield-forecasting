from abc import ABC, abstractmethod
from datetime import date

class SatelliteDataProvider(ABC):
    name = "abstract"
    @abstractmethod
    def analyze(self, latitude: float, longitude: float, start: date, end: date, cloud_threshold: int) -> dict: ...
