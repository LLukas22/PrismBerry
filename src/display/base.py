from abc import ABC, abstractmethod
from PIL import Image
import logging


class Display(ABC):
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    @abstractmethod
    def init(self):
        """
        Initialize the display
        """
        pass

    @abstractmethod
    def clear(self):
        """
        Clear the display
        """
        pass

    @abstractmethod
    def display(self, image_data: list[int]):
        """
        Display the image on the display
        """
        pass

    @abstractmethod
    def get_buffer(self, image: Image) -> list[int]:
        """
        Convert the image to the display buffer
        """
        pass

    @abstractmethod
    def sleep(self):
        """
        Put the display to sleep
        """
        pass


class DummyDisplay(Display):
    def __init__(self):
        super().__init__(800, 480)
        self.logger = logging.getLogger("uvicorn.error")

    def init(self):
        self.logger.info("Dummy display initialized")

    def clear(self):
        self.logger.info("Dummy display cleared")

    def display(self, image_data: list[int]):
        self.logger.info("Dummy display showing image")

    def get_buffer(self, image: Image) -> list[int]:
        self.logger.info("Dummy display getting buffer")
        return [0] * self.width * self.height

    def sleep(self):
        self.logger.info("Dummy display going to sleep")
