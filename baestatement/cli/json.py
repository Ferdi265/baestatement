from argparse import Namespace as Args
from baestatement.cli.util import create_default_argparser, add_default_options
from baestatement.cli.util import find_statement_files, parse_statement_from_path
from baestatement.format import format_json

def parse_args() -> Args:
    ap = create_default_argparser()
    add_default_options(ap)
    return ap.parse_args()

def main():
    args = parse_args()
    stmt = parse_statement_from_path(args.path, args)

    print(format_json(stmt))

if __name__ == '__main__':
    main()
