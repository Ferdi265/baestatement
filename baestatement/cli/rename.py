from argparse import Namespace as Args
from pathlib import Path
from glob import glob
import sys
from baestatement.cli.util import create_default_argparser, add_default_options
from baestatement.cli.util import find_statement_files, parse_statement_from_path

def parse_args() -> Args:
    ap = create_default_argparser()
    add_default_options(ap, with_positionals=False)
    ap.add_argument("dir", type=Path, help="path to folder with BankAustria eStatement PDF files")
    return ap.parse_args()

def main():
    args = parse_args()
    files = find_statement_files(args.path)

    error = False
    stmts = { Path(file): parse_statement_from_path(file, args) for file in files }
    for file, stmt in stmts.items():
        expected_name = f"estatement-{stmt.summary.date:%Y-%m-%d}.file"
        expected_path = file.parent / expected_name
        if file == expected_path:
            continue

        if expected_path.exists():
            print(f"error: can't rename {file.name!r} to {expected_name!r}, new name already exists")
            error = True
            continue

        file.rename(expected_path)
        print(f"info: renamed {file.name!r} to {expected_name!r}")

    if error:
        sys.exit(1)

if __name__ == '__main__':
    main()
