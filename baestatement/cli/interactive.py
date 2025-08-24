from pathlib import Path
from glob import glob
from argparse import Namespace as Args
from baestatement.pdf import pdf_to_page_fields
from baestatement.parse import parse_statement, Statement
from baestatement.cli.util import find_statement_files
from baestatement.format.json import parse_json

def parse_path(path: Path, *args, **kwargs) -> Statement:
    if path.name.endswith(".pdf"):
        return parse_pdf(path, *args, **kwargs)
    elif path.name.endswith(".json"):
        return parse_json(path, *args, **kwargs)
    else:
        raise ValueError(f"unexpected file type '{path.name}'")

def parse_pdf(pdf: Path, strip: bool = False, *args, **kwargs) -> Statement:
    pages = pdf_to_page_fields(pdf, *args, **kwargs)
    return parse_statement(pages, strip)

def parse_dir(dir: Path, *args, **kwargs) -> list[Statement]:
    files = find_statement_files(path)
    return [parse_path(file, *args, **kwargs) for file in files]
