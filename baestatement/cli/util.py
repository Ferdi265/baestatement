from argparse import ArgumentParser, Namespace as Args, ArgumentDefaultsHelpFormatter
from datetime import datetime
from pathlib import Path
from glob import glob

from baestatement.pdf import pdf_to_page_fields
from baestatement.parse import parse_statement, Statement
from baestatement.format.json import parse_json

def create_default_argparser(*args, **kwargs) -> ArgumentParser:
    kwargs.setdefault("formatter_class", ArgumentDefaultsHelpFormatter)
    return ArgumentParser(*args, **kwargs)


def add_default_options(ap: ArgumentParser, with_date_options: bool = False, with_positionals: bool = True):
    ap.add_argument("-z", "--zoom",         type=float,          default=1.,    help="zoom factor for pdftohtml")
    ap.add_argument("-k", "--keep-tempdir", action="store_true", default=False, help="don't delete temporary directory")
    ap.add_argument("-p", "--precision",    type=int,            default=4,     help="number of digits of coordinate precision")
    ap.add_argument("-s", "--strip",        action="store_true", default=False, help="remove comments from bank statement")
    ap.add_argument("-v", "--verbose",      action="store_true", default=False, help="print debug info")

    if with_date_options:
        parse_date = lambda s: datetime.strptime(s, "%Y.%m.%d")
        ap.add_argument("--start-date",     type=parse_date,    default=None,   help="start date of analysis (YYYY.mm.dd)")
        ap.add_argument("--end-date",       type=parse_date,    default=None,   help="end date of analysis (YYYY.mm.dd)")

    if with_positionals:
        ap.add_argument("path",             type=Path,                          help="path to BankAustria eStatement file")

def parse_statement_from_pdf(pdf: Path, args: Args) -> Statement:
    # extract page text and coordinates from pdf
    pages = pdf_to_page_fields(
        pdf,
        keep_tempdir = args.keep_tempdir,
        zoom = args.zoom,
        precision = args.precision
    )

    # parse the statement
    return parse_statement(
        pages,
        strip = args.strip
    )

def parse_statement_from_json(json: Path) -> Statement:
    with open(json, "r") as f:
        return parse_json(f.read())

def parse_statement_from_path(path: Path, args: Args) -> Statement:
    if path.name.endswith(".pdf"):
        return parse_statement_from_pdf(path, args)
    elif path.name.endswith(".json"):
        return parse_statement_from_json(path)
    else:
        raise ValueError(f"unexpected file type '{path.name}'")

def find_statement_files(path: Path) -> list[Path]:
    if path.is_dir():
        return [Path(p) for p in sorted(glob(str(path / "*.pdf")) + glob(str(path / "*.json")))]
    else:
        return [path]
