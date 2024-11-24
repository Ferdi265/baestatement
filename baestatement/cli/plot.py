from argparse import Namespace as Args
from pathlib import Path
from glob import glob
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from baestatement.cli.util import create_default_argparser, add_default_options
from baestatement.cli.util import parse_statement_from_pdf
from baestatement.stats import analyze

def parse_args() -> Args:
    ap = create_default_argparser()
    add_default_options(ap, with_positionals=False)
    ap.add_argument("dir", type=Path, help="path to folder with BankAustria eStatement PDF files")
    return ap.parse_args()

def main():
    args = parse_args()
    pdfs = glob(str(args.dir / "*.pdf"))

    stmts = [parse_statement_from_pdf(pdf, args) for pdf in pdfs]
    stats = analyze(stmts)
    print(stats.datetime)

    fig, ax = plt.subplots()
    ax.plot(stats.datetime, stats.avg_balance, c="red")
    ax.fill_between(stats.datetime, stats.min_balance, stats.max_balance, alpha=0.3, facecolor="red")
    ax.yaxis.set_major_formatter(FormatStrFormatter("%d €"))
    plt.show()

if __name__ == '__main__':
    main()
