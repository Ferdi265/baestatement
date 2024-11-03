from argparse import ArgumentParser, Namespace as Args, ArgumentDefaultsHelpFormatter
from pathlib import Path
from baestatement.pdf import pdf_to_page_fields
from baestatement.parse import parse_statement
from baestatement.format import format_cli

def parse_args() -> Args:
    ap = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    ap.add_argument("-z", "--zoom",         type=float,          default=1.,     help="zoom factor for pdftohtml")
    ap.add_argument("-k", "--keep-tempdir", action="store_true", default=False, help="don't delete temporary directory")
    ap.add_argument("-p", "--precision",    type=int,            default=4,     help="number of digits of coordinate precision")
    ap.add_argument("-v", "--verbose",      action="store_true", default=False, help="print debug info")
    ap.add_argument("pdf",                  type=Path,                          help="path to BankAustria eStatement PDF file")

    return ap.parse_args()

def main():
    args = parse_args()

    # extract page text and coordinates from pdf
    pages = pdf_to_page_fields(
        args.pdf,
        keep_tempdir = args.keep_tempdir,
        zoom = args.zoom,
        precision = args.precision
    )

    # parse the statement
    stmt = parse_statement(pages)

    # print it
    print(format_cli(stmt))

if __name__ == '__main__':
    main()
