from argparse import Namespace as Args
from baestatement.cli.util import create_default_argparser, add_default_options
from baestatement.cli.util import parse_statement_from_pdf
from baestatement.format import format_csv

def parse_args() -> Args:
    ap = create_default_argparser()
    add_default_options(ap)
    return ap.parse_args()

def main():
    args = parse_args()
    stmt = parse_statement_from_pdf(args)

    print(format_csv(stmt))

if __name__ == '__main__':
    main()
