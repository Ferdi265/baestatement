from argparse import Namespace as Args
from pathlib import Path
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from baestatement.cli.util import create_default_argparser, add_default_options
from baestatement.cli.util import parse_statement_from_pdf
from baestatement.stats import analyze_period, analyze_yearly, analyze_monthly, analyze_weekly

def parse_args() -> Args:
    ap = create_default_argparser()
    add_default_options(ap, with_date_options=True, with_positionals=False)
    ap.add_argument("--weekly", dest="period", action="store_const", const="week", help="plot weekly expenses")
    ap.add_argument("--monthly", dest="period", action="store_const", const="month", help="plot monthly expenses (default)")
    ap.add_argument("--yearly", dest="period", action="store_const", const="year", help="plot yearly expenses")
    ap.add_argument("--cumulative", action="store_true", default=False, help="plot cumulative expenses")
    ap.add_argument("dir", type=Path, help="path to folder with BankAustria eStatement PDF files")
    return ap.parse_args()

def main():
    args = parse_args()
    pdfs = glob(str(args.dir / "*.pdf"))
    if args.period is None:
        args.period = "month"

    stmts = [parse_statement_from_pdf(pdf, args) for pdf in pdfs]
    stmts, args.start_date, args.end_date = take_date_range(stmts, args.start_date, args.end_date)
    match args.period:
        case "month":
            stats = analyze_monthly(stmts, cumulative = args.cumulative)
        case "week":
            stats = analyze_weekly(stmts, cumulative = args.cumulative)
        case "year":
            stats = analyze_yearly(stmts, cumulative = args.cumulative)
        case period:
            raise ValueError(f"unknown period '{period}'")

    fig, ax = plt.subplots()
    ax.set_title(("Cumulative " if args.cumulative else "") + f"{args.period.title()}ly Expenses")
    ax.plot(stats.labels, stats.avg_expenses, c="red", label="average expenses")
    ax.fill_between(stats.labels, stats.min_expenses, stats.max_expenses, alpha=0.3, facecolor="red", label="min/max expenses")
    ax.yaxis.set_major_formatter(FormatStrFormatter("%d €"))
    ax.legend()
    plt.show()

if __name__ == '__main__':
    main()
