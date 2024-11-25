from argparse import Namespace as Args
from pathlib import Path
from glob import glob
import sys
from baestatement.cli.util import create_default_argparser, add_default_options
from baestatement.cli.util import parse_statement_from_pdf

def parse_args() -> Args:
    ap = create_default_argparser()
    add_default_options(ap, with_positionals=False)
    ap.add_argument("dir", type=Path, help="path to folder with BankAustria eStatement PDF files")
    return ap.parse_args()

def main():
    args = parse_args()
    pdfs = glob(str(args.dir / "*.pdf"))

    error = False
    stmts = { Path(pdf): parse_statement_from_pdf(pdf, args) for pdf in pdfs }
    for pdf, stmt in stmts.items():
        expected_name = f"estatement-{stmt.summary.date:%Y-%m-%d}.pdf"
        expected_path = pdf.parent / expected_name
        if pdf == expected_path:
            continue

        if expected_path.exists():
            print(f"error: can't rename {pdf.name!r} to {expected_name!r}, new name already exists")
            error = True
            continue

        pdf.rename(expected_path)
        print(f"info: renamed {pdf.name!r} to {expected_name!r}")

    if error:
        sys.exit(1)

if __name__ == '__main__':
    main()
