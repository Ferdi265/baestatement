from typing import Optional
from datetime import datetime
from ..parse import Statement, StatementLine, StatementSummary

def fmt_amount(amount: Optional[float]) -> str:
    if amount is None:
        return str(amount)

    return f"{amount:.2f}"

def fmt_date(date: Optional[datetime]) -> str:
    if date is None:
        return str(date)

    return f"datetime({date.year}, {date.month}, {date.day})"

def dump_line(line: StatementLine) -> str:
    formatted = "        StatementLine(\n"
    formatted += f"            text=(\n"

    text_lines = line.text.split("\n")
    for i, text_line in enumerate(text_lines):
        if i == 0:
            formatted += f"                {repr(text_line + '\n')}\n"
        elif i < len(text_lines) - 1:
            formatted += f"                {repr(text_line + '\n')}\n"
        else:
            formatted += f"                {repr(text_line + '\n')}\n"

    formatted += f"            ),\n"
    formatted += f"            amount={fmt_amount(line.amount)}, booking_date={fmt_date(line.booking_date)}, value_date={fmt_date(line.value_date)},\n"
    formatted += "        ),\n"
    return formatted

def dump_summary(summary: StatementSummary) -> str:
    formatted = "    summary=StatementSummary(\n"
    formatted += f"        date={fmt_date(summary.date)},\n"
    formatted += f"        sum_expenses={summary.sum_expenses:.2f}, sum_income={summary.sum_income:.2f},\n"
    formatted += f"        old_balance={summary.old_balance:.2f}, new_balance={summary.new_balance:.2f},\n"
    formatted += "    ),\n"
    return formatted

def dump_statement(stmt: Statement) -> str:
    formatted = "Statement(\n"
    formatted += "    lines=[\n"

    for line in stmt.lines:
        formatted += dump_line(line)

    formatted += "    ],\n"
    formatted += dump_summary(stmt.summary)
    formatted += ")"
    return formatted

def format_dump(stmt: Statement) -> str:
    return dump_statement(stmt)
