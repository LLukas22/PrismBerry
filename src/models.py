from enum import Enum
from sqlmodel import Field, SQLModel


class BackgroundColor(str, Enum):
    White = "white"
    Black = "black"


class ImageEntry(SQLModel, table=True):
    id: str = Field(..., primary_key=True)
    dither: bool = True
    grayscale: bool = False
    background_color: BackgroundColor = BackgroundColor.Black
    name: str
