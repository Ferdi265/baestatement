from argparse import Namespace as Args
from glob import glob
from baestatement.cli.util import create_default_argparser, add_default_options
from baestatement.cli.util import parse_statement_from_pdf
from baestatement.format import format_cli

def parse_args() -> Args:
    ap = create_default_argparser()
    add_default_options(ap)
    return ap.parse_args()

def main():
    args = parse_args()
    if args.pdf.is_dir():
        pdfs = sorted(glob(str(args.pdf / "*.pdf")))
    else:
        pdfs = [args.pdf]

    stmts = [parse_statement_from_pdf(pdf, args) for pdf in pdfs]
    for stmt in stmts:
        print(format_cli(stmt))

if __name__ == '__main__':
    main()
