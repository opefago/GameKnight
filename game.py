from abc import ABC, abstractmethod
class Game(ABC):
    @abstractmethod
    def name(self):
        pass    
    @abstractmethod
    def play(self):
        pass