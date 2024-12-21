from enum import Enum
from sqlmodel import Field, SQLModel


class BackgroundColor(str, Enum):
    White = "white"
    Black = "black"


class Rotation(int, Enum):
    _None = 0
    _90 = 90
    _180 = 180
    _270 = 270

    @classmethod
    def from_str(cls, value: str) -> "Rotation":
        return getattr(cls, f"_{value}")


class ImageEntry(SQLModel, table=True):
    id: str = Field(..., primary_key=True)
    dither: bool = True
    grayscale: bool = False
    background_color: BackgroundColor = BackgroundColor.Black
    rotation: Rotation = Rotation._None
    name: str


class Settings(SQLModel, table=True):
    id: int = Field(1, primary_key=True)
    cycle: bool = True
    cycle_time: int = 30
