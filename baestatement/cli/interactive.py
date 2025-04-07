from pathlib import Path
from glob import glob
from argparse import Namespace as Args
from baestatement.pdf import pdf_to_page_fields
from baestatement.parse import parse_statement, Statement

def parse_pdf(pdf: Path, strip: bool = False, *args, **kwargs) -> Statement:
    pages = pdf_to_page_fields(pdf, *args, **kwargs)
    return parse_statement(pages, strip)

def parse_dir(dir: Path, *args, **kwargs) -> list[Statement]:
    pdfs = glob(str(dir / "*.pdf"))
    return [parse_pdf(pdf, *args, **kwargs) for pdf in pdfs]
