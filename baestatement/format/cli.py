from typing import Optional
from datetime import datetime
from ..parse import Statement
from .util import fmt_amount, fmt_date, fmt_date_noyear

def format_cli(stmt: Statement) -> str:
    formatted = ""

    for line in stmt.lines:
        text_lines = str(line.text).split("\n")
        for i, text_line in enumerate(text_lines):
            begin_marker, end_marker = "   " + fmt_date_noyear(None), ""
            if i == 0:
                begin_marker = ">> " + fmt_date_noyear(line.booking_date)
            if i == len(text_lines) - 1:
                end_marker = fmt_date_noyear(line.value_date) + " " + fmt_amount(line.amount)

            formatted += f"{begin_marker} {text_line:<57} {end_marker}\n"

    formatted += f">> date:         {fmt_date(stmt.summary.date)}\n"
    if stmt.summary.closing_date is not None and stmt.summary.closing_balance is not None:
        formatted += f"   closing date: {fmt_date(stmt.summary.closing_date)}, closing balance:{fmt_amount(stmt.summary.closing_balance)}\n"
    formatted += f"   sum expenses:{fmt_amount(stmt.summary.sum_expenses)}, sum income:     {fmt_amount(stmt.summary.sum_income) }\n"
    formatted += f"   old balance: {fmt_amount(stmt.summary.old_balance )}, new balance:    {fmt_amount(stmt.summary.new_balance)}\n"
    return formatted.rstrip("\n")
