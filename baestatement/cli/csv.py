from argparse import Namespace as Args
from pathlib import Path
from baestatement.cli.util import create_default_argparser, add_default_options
from baestatement.cli.util import parse_statement_from_pdf
from baestatement.format import format_csv

def parse_args() -> Args:
    ap = create_default_argparser()
    add_default_options(ap)
    ap.add_argument("-H", "--no-header", action="store_true", default=False, help="don't emit CSV header line")
    ap.add_argument("-o", "--output",    type=Path,           default=None,  help="path to output CSV file")
    return ap.parse_args()

def main():
    args = parse_args()
    stmt = parse_statement_from_pdf(args.pdf, args)

    formatted = format_csv(stmt, with_header = not args.no_header)
    if args.output is None:
        print(formatted)
    else:
        with open(args.output, "w") as f:
            f.write(formatted + "\n")

if __name__ == '__main__':
    main()
