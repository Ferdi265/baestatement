from subprocess import check_call, DEVNULL
from bs4 import BeautifulSoup, Comment, Tag
from tempfile import TemporaryDirectory
from pathlib import Path

def pdf_to_html(pdf: Path, html: Path, zoom: float = 1):
    assert html.suffix == ".html", "invalid html filename"
    check_call(["pdftohtml", "-s", "-noframes", "-dataurls", "-zoom", str(zoom), pdf, html.with_suffix("")], stdout=DEVNULL)
    assert html.exists(), "pdftohtml failed to create html output file"

def pdf_to_soup(pdf: Path, keep_tempdir: bool = True, *args, **kwargs) -> BeautifulSoup:
    with TemporaryDirectory(prefix="baestatement.", delete = not keep_tempdir) as tmpdir:
        html = Path(tmpdir) / "index.html"
        pdf_to_html(pdf, html)

        with open(html, "r") as f:
            return BeautifulSoup(f.read(), "html.parser")

def extract_pdf_pages(soup: BeautifulSoup) -> list[Tag]:
    return soup.find_all("div", attrs = { "id": lambda cls: cls and cls.startswith("page") })

def extract_tag_css(tag: Tag) -> dict[str, str]:
    props: dict[str, str] = {}
    for prop in tag.attrs["style"].split(";"):
        prop = prop.strip()
        if prop == "":
            continue

        key, value = prop.split(":")
        props[key.strip()] = value.strip()

    return props

def extract_tag_css_size(tag: Tag) -> tuple[int, int]:
    css = extract_tag_css(tag)
    return int(css["width"].removesuffix("px")), int(css["height"].removesuffix("px"))

def extract_tag_css_position(tag: Tag) -> tuple[int, int]:
    css = extract_tag_css(tag)
    return int(css["left"].removesuffix("px")), int(css["top"].removesuffix("px"))

def extract_page_fields(page: Tag, precision: int = 4, *args, **kwargs) -> dict[tuple[float, float], str]:
    width, height = extract_tag_css_size(page)
    fields: dict[tuple[float, float], str] = {}

    for field in page.find_all("p"):
        abs_x, abs_y = extract_tag_css_position(field)
        x, y = abs_x / width, abs_y / height
        x, y = round(x, precision), round(y, precision)
        fields[(x, y)] = field.text.replace("\xa0", " ")

    return fields

def pdf_to_page_fields(pdf: Path, *args, **kwargs) -> list[dict[tuple[float, float], str]]:
    soup = pdf_to_soup(pdf, *args, **kwargs)
    pages = extract_pdf_pages(soup)

    return [extract_page_fields(page, *args, **kwargs) for page in pages]
