from argparse import Namespace as Args
from glob import glob
from baestatement.cli.util import create_default_argparser, add_default_options
from baestatement.cli.util import find_statement_files, parse_statement_from_path
from baestatement.format import format_cli

def parse_args() -> Args:
    ap = create_default_argparser()
    add_default_options(ap)
    return ap.parse_args()

def main():
    args = parse_args()
    files = find_statement_files(args.path)

    stmts = [parse_statement_from_path(file, args) for file in files]
    for stmt in stmts:
        print(format_cli(stmt))

if __name__ == '__main__':
    main()
