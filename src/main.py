from typing import Annotated
from fastapi import Depends, FastAPI
from fasthtml.common import *
from typing import Optional
from sqlmodel import Field, SQLModel, Session, create_engine, select
import uuid
from pathlib import Path
from PIL import Image

from image_processor import ImageProcessor


ROOT = Path(__file__).parent.parent
IMAGE_DIR = ROOT / "images"
IMAGE_DIR.mkdir(exist_ok=True)
ORIGINAL_DIR = IMAGE_DIR / "original"
ORIGINAL_DIR.mkdir(exist_ok=True)
PROCESSED_DIR = IMAGE_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)
DB_DIR = ROOT / "db"
DB_DIR.mkdir(exist_ok=True)
DB_FILE = DB_DIR / "database.db"
if DB_FILE.exists():
    # DB_FILE.unlink()
    pass

engine = create_engine(f"sqlite:///{DB_FILE}")

IMAGE_PROCESSOR = ImageProcessor()

css = Style(":root {--pico-font-size:90%,--pico-font-family: Pacifico, cursive;}")
app, rt = fast_app(live=False, hdrs=(picolink, css), pico=True)


class ImageEntry(SQLModel, table=True):
    id: str = Field(..., primary_key=True)
    dither: bool = True
    grayscale: bool = False
    name: str


@rt("/")
def get():
    content = Div(id="content")
    return (
        Title("Hello World"),
        Header(
            Nav(
                Ul(
                    Li(
                        Strong(
                            "PrismBerry",
                            hx_get="/images",
                            hx_trigger="click",
                            target_id="content",
                        )
                    )
                ),
                Ul(
                    Li(
                        Button(
                            "Add",
                            hx_get=f"/add",
                            hx_trigger="click",
                            target_id="modal-container",
                        )
                    )
                ),
            ),
            cls="container",
        ),
        Main(
            Div(hx_get="/images", hx_trigger="load", target_id="content"),
            content,
            cls="container",
        ),
        Footer(Small("Build with love <3"), cls="container"),
    )


@rt("/images")
def get():
    articles = []
    with Session(engine) as session:
        for entry in session.exec(select(ImageEntry)):
            articles.append(
                Article(
                    H2(entry.name),
                    Figure(
                        Img(
                            src=f"/images/original/{entry.id}.png",
                            style="width: 50%; height: auto;",
                        ),
                        Figcaption(A("Preview", href=f"preview/{entry.id}")),
                    ),
                    Fieldset(
                        Legend(Strong("Options")),
                        Label(
                            Input(
                                type="checkbox", role="switch", checked=entry.grayscale
                            ),
                            "Grayscale",
                        ),
                        Label(
                            Input(type="checkbox", role="switch", checked=entry.dither),
                            "Dithering",
                        ),
                    ),
                    Grid(
                        Button(
                            "Display", hx_post=f"/display/{entry.id}", hx_swap="none"
                        ),
                        Button(
                            "Delete",
                            cls="secondary",
                            hx_delete=f"/delete/{entry.id}",
                            hx_swap="none",
                        ),
                    ),
                )
            )
    return Div(reset_modal(), *articles, hx_swap="innerHTML")


# For images, CSS, etc.
@app.get("/{fname:path}.{ext:static}")
def static(fname: str, ext: str):
    return FileResponse(f"{fname}.{ext}")


@rt("/add")
def get():
    return Dialog(
        Article(
            Header(H2("Add Image")),
            Form(
                Label(
                    Strong("Name"),
                    Input(type="text", id="name", name="name", placeholder="Name"),
                ),
                Label(Strong("File"), Input(type="file", id="file", name="file")),
                Fieldset(
                    Legend(Strong("Options")),
                    Label(
                        Input(
                            type="checkbox",
                            id="grayscale",
                            name="grayscale",
                            role="switch",
                            checked=False,
                        ),
                        "Grayscale",
                    ),
                    Label(
                        Input(
                            type="checkbox",
                            id="dithering",
                            name="dithering",
                            role="switch",
                            checked=True,
                        ),
                        "Dithering",
                    ),
                ),
                Input(type="submit", value="Add"),
                hx_post="/add",
                hx_trigger="submit",
                target_id="modal-container",
            ),
        ),
        open=True,
    )


@app.get("/reset_modal")
def reset_modal():
    return Div(id="modal-container")


def message_modal(title: str, message: str, content_route: str = "/images") -> Dialog:
    return Dialog(
        Article(
            Header(
                Button(
                    aria_label="Close",
                    rel="prev",
                    hx_get=content_route,
                    hx_trigger="click",
                    target_id="content",
                ),
                P(Strong(title)),
            ),
            P(message),
            Footer(
                Button(
                    "Close",
                    hx_get=content_route,
                    hx_trigger="click",
                    target_id="content",
                )
            ),
        ),
        open=True,
    )


@rt("/add")
def post(
    name: str,
    file: UploadFile,
    grayscale: Optional[bool] = None,
    dithering: Optional[bool] = None,
):
    print(name)
    print(file)
    try:
        image = Image.open(file.file)
        id = str(uuid.uuid4())
        new_entry = ImageEntry(
            name=name,
            id=id,
            grayscale=True if grayscale else False,
            dither=True if dithering else False,
        )
        with Session(engine) as session:
            session.add(new_entry)
            image.save(ORIGINAL_DIR / f"{id}.png")
            session.commit()
        return message_modal("Success", "Image added successfully!")

    except Exception as e:
        return message_modal("Error", str(e))


@rt("/delete/{id}")
def delete(id: str):
    print(id)


@rt("/preview/{id}")
def get(id: str):
    with Session(engine) as session:
        entry = session.get(ImageEntry, id)
        if entry is None:
            return Div(H1("Not Found"))

        image = Image.open(ORIGINAL_DIR / f"{entry.id}.png")
        processed_image = IMAGE_PROCESSOR(image, entry.grayscale, entry.dither)
        processed_image.save(PROCESSED_DIR / f"{entry.id}.png")
        return Div(
            H1(entry.name),
            Img(src=f"/images/processed/{entry.id}.png"),
        )


if __name__ == "__main__":
    import uvicorn

    SQLModel.metadata.create_all(engine)
    # with Session(engine) as session:
    #     session.add(
    #         ImageEntry(
    #             name="Cat", id="6b86232f-5415-4bfd-982a-3e7e24297ed1", grayscale=True
    #         )
    #     )
    #     session.add(
    #         ImageEntry(name="Victor", id="fb6c3e30-7047-48f1-b1fc-b1868663fa32")
    #     )
    #     session.commit()

    uvicorn.run(app, host="localhost", port=8000)
