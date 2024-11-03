from typing import Optional
from datetime import datetime
from ..parse import Statement

def fmt_field_date(date: Optional[tuple[int, int]]) -> str:
    if date is None:
        return "     "

    return f"{date[0]:02}.{date[1]:02}"

def fmt_field_datetime(date: Optional[datetime]) -> str:
    if date is None:
        return ""

    return f" {date:%d.%m.%Y}"

def fmt_field_amount(amount: Optional[float]) -> str:
    if amount is None:
        return ""

    return f" {amount:+10.2f}€"

def format_cli(stmt: Statement) -> str:
    formatted = ""

    for line in stmt.lines:
        text_lines = str(line.text).split("\n")
        for i, text_line in enumerate(text_lines):
            begin_marker, end_marker = "   " + fmt_field_date(None), ""
            if i == 0:
                begin_marker = ">> " + fmt_field_date(line.booking_date)
            if i == len(text_lines) - 1:
                end_marker = fmt_field_date(line.value_date) + fmt_field_amount(line.amount)

            formatted += f"{begin_marker} {text_line:<57}{end_marker}\n"

    formatted += f">> date:{fmt_field_datetime(stmt.summary.date)}\n"
    formatted += f"   sum expenses:{fmt_field_amount(stmt.summary.sum_expenses)}, sum income: {fmt_field_amount(stmt.summary.sum_income) }\n"
    formatted += f"   old balance: {fmt_field_amount(stmt.summary.old_balance )}, new balance:{fmt_field_amount(stmt.summary.new_balance)}"
    return formatted
