from typing import Annotated
from fastapi import Depends, FastAPI
from fasthtml.common import *
from typing import Optional
from sqlmodel import SQLModel, Session, create_engine, select
import uuid
from pathlib import Path
from PIL import Image

from models import ImageEntry, BackgroundColor
from image_processor import ImageProcessor


IMAGE_EXTENSION = "png"
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

engine = create_engine(f"sqlite:///{DB_FILE}")

IMAGE_PROCESSOR = ImageProcessor()

# css = Style(":root {--pico-font-size:90%,--pico-font-family: Pacifico, cursive;}")
css = Style(".fa { margin-right: 6px; } .fa-brands { margin-right: 6px; }")
fontawesome = Link(
    rel="stylesheet",
    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css",
)
app, rt = fast_app(live=False, hdrs=(picolink, fontawesome, css), pico=True)


@app.get("/")
def root():
    content = Div(id="content")
    return (
        Title("PrismBerry"),
        Header(
            Nav(
                Ul(
                    Li(
                        H1(
                            I(cls="fa-brands fa-raspberry-pi"),
                            "PrismBerry",
                            hx_get="/images",
                            hx_trigger="click",
                            target_id="content",
                        )
                    )
                ),
                Ul(
                    Li(A(I(cls="fa fa-cog"), "Settings", cls="contrast")),
                    Li(
                        Button(
                            I(cls="fa fa-plus"),
                            "Add",
                            hx_get=f"/add",
                            hx_trigger="click",
                            target_id="modal-container",
                        )
                    ),
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


def render_image_options(entry: ImageEntry):
    return Fieldset(
        Legend(Strong("Options")),
        Label(
            Input(
                type="checkbox",
                role="switch",
                checked=entry.grayscale,
                name="grayscale",
            ),
            "Grayscale",
        ),
        Label(
            Input(
                type="checkbox", role="switch", checked=entry.dither, name="dithering"
            ),
            "Dithering",
        ),
        Label(
            "Background Color",
            Select(
                Option(
                    "Black",
                    selected=entry.background_color == BackgroundColor.Black,
                    value="black",
                ),
                Option(
                    "White",
                    selected=entry.background_color == BackgroundColor.White,
                    value="white",
                ),
                name="background_color",
            ),
        ),
        id=f"options-{entry.id}",
        hx_trigger=f"change from:#options-{entry.id}",
        hx_include=f"#options-{entry.id} *",
        hx_patch=f"/update/{entry.id}",
        hx_swap="outerHTML",
    )


def render_image(entry: ImageEntry):
    return Article(
        H2(entry.name),
        Grid(
            Figure(
                Img(
                    src=f"/images/original/{entry.id}.{IMAGE_EXTENSION}",
                    style="width: 100%; height: auto;",
                )
            ),
            Div(
                render_image_options(entry),
                Label(Strong(A("Preview Image", href=f"preview/{entry.id}"))),
                Grid(
                    Button(
                        I(cls="fa fa-image"),
                        "Display",
                        hx_post=f"/display/{entry.id}",
                        hx_swap="none",
                    ),
                    Button(
                        I(cls="fa fa-trash"),
                        "Delete",
                        cls="secondary",
                        hx_delete=f"/delete/{entry.id}",
                        target_id=f"article-{entry.id}",
                        hx_swap="outerHTML",
                    ),
                    style="margin-top: auto;",
                ),
                style="display: flex; flex-direction: column; height: 100%;",
            ),
            style="grid-template-columns: 60% 40%; margin: 20px;",
        ),
        id=f"article-{entry.id}",
    )


@app.get("/images")
def render_images():
    articles = []
    with Session(engine) as session:
        for entry in session.exec(select(ImageEntry)):
            articles.append(render_image(entry))

    return Div(reset_modal(), *articles, hx_swap="innerHTML")


# For images, CSS, etc.
@app.get("/{fname:path}.{ext:static}")
def static(fname: str, ext: str):
    return FileResponse(f"{fname}.{ext}")


@app.get("/add")
def build_add_dialogue():
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
                    Label(
                        "Background Color",
                        Select(
                            Option("Black", value="black", selected=True),
                            Option("White", value="white"),
                            id="background_color",
                            name="background_color",
                        ),
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


@app.post("/add")
def add_image(
    name: str,
    file: UploadFile,
    grayscale: Optional[bool] = None,
    dithering: Optional[bool] = None,
    background_color: BackgroundColor = BackgroundColor.Black,
):
    try:
        image = Image.open(file.file)
        id = str(uuid.uuid4())
        new_entry = ImageEntry(
            name=name,
            id=id,
            grayscale=True if grayscale else False,
            dither=True if dithering else False,
            background_color=background_color,
        )
        with Session(engine) as session:
            session.add(new_entry)
            image.save(ORIGINAL_DIR / f"{id}.{IMAGE_EXTENSION}")
            session.commit()
        return message_modal("Success", "Image added successfully!")

    except Exception as e:
        return message_modal("Error", str(e))


@app.patch("/update/{id}")
def update_image(
    id: str,
    grayscale: Optional[bool] = None,
    dithering: Optional[bool] = None,
    background_color: BackgroundColor = BackgroundColor.Black,
):
    with Session(engine) as session:
        statement = select(ImageEntry).where(ImageEntry.id == id)
        result = session.exec(statement)
        entry = result.one_or_none()
        if entry:
            entry.grayscale = True if grayscale else False
            entry.dither = True if dithering else False
            entry.background_color = background_color
            session.add(entry)
            session.commit()
            return render_image_options(entry)


@app.delete("/delete/{id}")
def delete(id: str):
    with Session(engine) as session:
        statement = select(ImageEntry).where(ImageEntry.id == id)
        result = session.exec(statement)
        entry_to_delete = result.one_or_none()

        try:
            if entry_to_delete:
                # Delete the record
                session.delete(entry_to_delete)
                # Commit the transaction
                session.commit()
                # Delete the image
                if (ORIGINAL_DIR / f"{entry_to_delete.id}.{IMAGE_EXTENSION}").exists():
                    (ORIGINAL_DIR / f"{entry_to_delete.id}.{IMAGE_EXTENSION}").unlink()
                if (PROCESSED_DIR / f"{entry_to_delete.id}.{IMAGE_EXTENSION}").exists():
                    (PROCESSED_DIR / f"{entry_to_delete.id}.{IMAGE_EXTENSION}").unlink()
                return None

        except Exception as e:
            return render_image(entry_to_delete)


@app.get("/preview/{id}")
def get_preview(id: str):
    with Session(engine) as session:
        entry = session.get(ImageEntry, id)
        if entry is None:
            return Div(H1("Not Found"))

        image = Image.open(ORIGINAL_DIR / f"{entry.id}.{IMAGE_EXTENSION}")
        processed_image = IMAGE_PROCESSOR(
            image, entry.grayscale, entry.dither, entry.background_color
        )
        processed_image.save(PROCESSED_DIR / f"{entry.id}.{IMAGE_EXTENSION}")
        return Div(
            H1(f"Preview of '{entry.name}'"),
            Img(src=f"/images/processed/{entry.id}.{IMAGE_EXTENSION}"),
        )


if __name__ == "__main__":
    import uvicorn

    SQLModel.metadata.create_all(engine)

    uvicorn.run(app, host="localhost", port=8000)
