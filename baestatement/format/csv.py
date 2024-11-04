from io import StringIO
from csv import writer as csv_writer
from ..parse import Statement, StatementLine
from .util import fmt_date

def format_csv(stmt: Statement) -> str:
    f = StringIO("")

    writer = csv_writer(f)
    writer.writerow(("text", "booking date", "value date", "amount"))
    for line in stmt.lines:
        writer.writerow((
            line.text,
            fmt_date(line.booking_date),
            fmt_date(line.value_date),
            line.amount
        ))

    return f.getvalue()
