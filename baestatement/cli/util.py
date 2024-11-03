from argparse import ArgumentParser, Namespace as Args, ArgumentDefaultsHelpFormatter
from pathlib import Path

from baestatement.pdf import pdf_to_page_fields
from baestatement.parse import parse_statement, Statement

def create_default_argparser(*args, **kwargs) -> ArgumentParser:
    kwargs.setdefault("formatter_class", ArgumentDefaultsHelpFormatter)
    return ArgumentParser(*args, **kwargs)

def add_default_options(ap: ArgumentParser, with_positionals: bool = True):
    ap.add_argument("-z", "--zoom",         type=float,          default=1.,    help="zoom factor for pdftohtml")
    ap.add_argument("-k", "--keep-tempdir", action="store_true", default=False, help="don't delete temporary directory")
    ap.add_argument("-p", "--precision",    type=int,            default=4,     help="number of digits of coordinate precision")
    ap.add_argument("-v", "--verbose",      action="store_true", default=False, help="print debug info")

    if with_positionals:
        ap.add_argument("pdf",              type=Path,                          help="path to BankAustria eStatement PDF file")

def parse_statement_from_pdf(args: Args) -> Statement:
    # extract page text and coordinates from pdf
    pages = pdf_to_page_fields(
        args.pdf,
        keep_tempdir = args.keep_tempdir,
        zoom = args.zoom,
        precision = args.precision
    )

    # parse the statement
    return parse_statement(pages)
