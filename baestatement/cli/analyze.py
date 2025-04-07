from argparse import Namespace as Args
from pathlib import Path
from glob import glob
import numpy as np
from baestatement.cli.util import create_default_argparser, add_default_options
from baestatement.cli.util import parse_statement_from_pdf
from baestatement.stats import analyze, take_date_range
from baestatement.format.util import fmt_amount, fmt_date

def parse_args() -> Args:
    ap = create_default_argparser()
    add_default_options(ap, with_date_options=True, with_positionals=False)
    ap.add_argument("--avg-period", type=int, default=31, help="averaging period (default is 31 days)")
    ap.add_argument("dir", type=Path, help="path to folder with BankAustria eStatement PDF files")
    return ap.parse_args()

def main():
    args = parse_args()
    pdfs = glob(str(args.dir / "*.pdf"))

    stmts = [parse_statement_from_pdf(pdf, args) for pdf in pdfs]
    stmts, args.start_date, args.end_date = take_date_range(stmts, args.start_date, args.end_date)
    stats = analyze(stmts, avg_period=args.avg_period, difference=True)

    sum_expenses = sum(stmt.summary.sum_expenses for stmt in stmts)
    sum_income = sum(stmt.summary.sum_income for stmt in stmts)

    num_days = (args.end_date - args.start_date).days + 1
    avg_expenses = sum_expenses / num_days * args.avg_period
    avg_income = sum_income / num_days * args.avg_period
    avg_difference = np.average(stats.cur_balance)

    print(f"start   date:       {fmt_date(args.start_date)}")
    print(f"end     date:       {fmt_date(args.end_date)}")
    print(f"num     days:       {num_days}")
    print(f"average period:     {args.avg_period}")
    print(f"start   balance:    {fmt_amount(stmts[0].summary.old_balance)}")
    print(f"end     balance:    {fmt_amount(stmts[-1].summary.new_balance)}")
    print(f"balance difference: {fmt_amount(stmts[-1].summary.new_balance - stmts[0].summary.old_balance)}")
    print(f"sum     expenses:   {fmt_amount(sum_expenses)}")
    print(f"sum     income:     {fmt_amount(sum_income)}")
    print(f"average expenses:   {fmt_amount(avg_expenses)}")
    print(f"average income:     {fmt_amount(avg_income)}")
    print(f"average difference: {fmt_amount(avg_difference)}")

if __name__ == '__main__':
    main()
