from abc import ABC, abstractmethod
from typing import Dict
from google_okf.core.models import Concept

class BaseProducer(ABC):
    """
    Abstract Base Class for all OKF Producers.
    Producers are responsible for connecting to a source system,
    fetching metadata or documents, and mapping them to OKF Concepts.
    """
    
    @abstractmethod
    def produce(self) -> Dict[str, Concept]:
        """
        Run the extraction process.
        
        Returns:
            A dictionary mapping concept IDs (e.g. 'tables/users') to Concept objects.
        """
        pass
