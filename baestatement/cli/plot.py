from argparse import Namespace as Args
from pathlib import Path
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from baestatement.cli.util import create_default_argparser, add_default_options
from baestatement.cli.util import parse_statement_from_pdf
from baestatement.stats import analyze, take_date_range

def parse_args() -> Args:
    ap = create_default_argparser()
    add_default_options(ap, with_date_options=True, with_positionals=False)
    ap.add_argument("--avg-period", type=int, default=31, help="averaging period (default is 31 days)")
    ap.add_argument("--difference", action="store_true", default=False, help="plot differences instead of absolute balances")
    ap.add_argument("dir", type=Path, help="path to folder with BankAustria eStatement PDF files")
    return ap.parse_args()

def main():
    args = parse_args()
    pdfs = glob(str(args.dir / "*.pdf"))

    stmts = [parse_statement_from_pdf(pdf, args) for pdf in pdfs]
    stmts = take_date_range(stmts, args.start_date, args.end_date)
    stats = analyze(stmts, avg_period=args.avg_period, difference=args.difference)

    fig, ax = plt.subplots()
    ax.set_title("Account Balance Difference" if args.difference else "Account Balance")
    if args.difference:
        ax.axhline(y = 0, color="black")
    ax.plot(stats.datetime, stats.avg_balance, c="red", label="average balance " + ("difference" if args.difference else ""))
    ax.fill_between(stats.datetime, stats.min_balance, stats.max_balance, alpha=0.3, facecolor="red", label="min/max balance " + ("difference" if args.difference else ""))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%d €"))
    ax.legend()
    plt.show()

if __name__ == '__main__':
    main()
