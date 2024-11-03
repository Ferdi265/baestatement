from typing import Optional
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime
import re

@dataclass
class StatementLine:
    text: Optional[str] = None
    amount: Optional[float] = None
    booking_date: Optional[tuple[int, int]] = None
    value_date: Optional[tuple[int, int]] = None

    def is_empty(self) -> bool:
        return (
            (self.text is None or self.text.strip() == "") and
            self.amount is None and
            self.booking_date is None and
            self.value_date is None
        )

@dataclass
class StatementSummary:
    date: Optional[datetime] = None
    old_balance: Optional[float] = None
    sum_expenses: Optional[float] = None
    sum_income: Optional[float] = None
    new_balance: Optional[float] = None

@dataclass
class Statement:
    lines: list[StatementLine]
    summary: StatementSummary

def parse_field_date(field: str) -> Optional[tuple[int, int]]:
    field = field.strip()
    if field == "":
        return None

    day, month = field.split(".")
    return int(day), int(month)

def parse_field_amount(field: str) -> float:
    field = field.strip()
    if field == "":
        return None

    if field.endswith("-"):
        field = "-" + field.rstrip("-")

    REPLACEMENTS = { ".": "", ",": "." }
    field = re.sub("[.,]", lambda match: REPLACEMENTS[match.group()], field)
    return float(field)

STATEMENT_LINE_AREA_MIN: tuple[float, float] = (220/1782, 300/864)
STATEMENT_LINE_AREA_MAX: tuple[float, float] = (1500/1782, 720/864)
STATEMENT_LINE_BOOKING_DATE_END: float  = 330/1782
STATEMENT_LINE_TEXT_END: float          = 1200/1782
STATEMENT_LINE_VALUE_DATE_END: float    = 1400/1782
STATEMENT_LINE_AMOUNT_END: float        = STATEMENT_LINE_AREA_MAX[0]
def extract_statement_lines(fields: dict[tuple[float, float], str]) -> list[StatementLine]:
    lines: defaultdict[float, StatementLine] = defaultdict(StatementLine)

    for (x, y), field in fields.items():
        if (
            x < STATEMENT_LINE_AREA_MIN[0] or y < STATEMENT_LINE_AREA_MIN[1] or
            x > STATEMENT_LINE_AREA_MAX[0] or y > STATEMENT_LINE_AREA_MAX[1]
        ):
            continue

        if x < STATEMENT_LINE_BOOKING_DATE_END:
            lines[y].booking_date = parse_field_date(field)
        elif x < STATEMENT_LINE_TEXT_END:
            lines[y].text = field
        elif x < STATEMENT_LINE_VALUE_DATE_END:
            lines[y].value_date = parse_field_date(field)
        elif x < STATEMENT_LINE_AMOUNT_END:
            lines[y].amount = parse_field_amount(field)

    return [value for _key, value in sorted(lines.items())]

STATEMENT_SUMMARY_AREA_MIN: tuple[float, float] = (200/1782, 760/864)
STATEMENT_SUMMARY_AREA_MAX: tuple[float, float] = (1500/1782, 800/864)
STATEMENT_SUMMARY_OLD_BALANCE_END: float    = 400/1782
STATEMENT_SUMMARY_SUM_EXPENSES_END: float   = 900/1782
STATEMENT_SUMMARY_SUM_INCOME_END: float     = 1300/1782
STATEMENT_SUMMARY_NEW_BALANCE_END: float    = STATEMENT_SUMMARY_AREA_MAX[0]
STATEMENT_DATE_AREA_MIN: tuple[float, float] = (900/1782, 160/864)
STATEMENT_DATE_AREA_MAX: tuple[float, float] = (1000/1782, 200/864)
def extract_statement_summary(fields: dict[tuple[float, float], str]) -> StatementSummary:
    summary = StatementSummary()

    for (x, y), field in fields.items():
        if (
            x >= STATEMENT_SUMMARY_AREA_MIN[0] and y >= STATEMENT_SUMMARY_AREA_MIN[1] and
            x <= STATEMENT_SUMMARY_AREA_MAX[0] and y <= STATEMENT_SUMMARY_AREA_MAX[1]
        ):
            if x < STATEMENT_SUMMARY_OLD_BALANCE_END:
                summary.old_balance = parse_field_amount(field)
            elif x < STATEMENT_SUMMARY_SUM_EXPENSES_END:
                summary.sum_expenses = parse_field_amount(field)
            elif x < STATEMENT_SUMMARY_SUM_INCOME_END:
                summary.sum_income = parse_field_amount(field)
            elif x < STATEMENT_SUMMARY_NEW_BALANCE_END:
                summary.new_balance = parse_field_amount(field)
        elif (
            x >= STATEMENT_DATE_AREA_MIN[0] and y >= STATEMENT_DATE_AREA_MIN[1] and
            x <= STATEMENT_DATE_AREA_MAX[0] and y <= STATEMENT_DATE_AREA_MAX[1]
        ):
            field = field.strip().split(" ", 2)[0]
            summary.date = datetime.strptime(field, "%d.%m.%Y")

    return summary

def combine_statement_lines(lines: list[StatementLine]) -> list[StatementLine]:
    combined_lines: list[StatementLine] = []
    combined_line = StatementLine()

    def next_line() -> StatementLine:
        nonlocal combined_line
        if not combined_line.is_empty():
            combined_lines.append(combined_line)
            combined_line = StatementLine()

    for line in lines:
        if line.is_empty():
            continue

        if line.booking_date is not None:
            next_line()
            combined_line.booking_date = line.booking_date

        if line.text is not None:
            if combined_line.text is None:
                combined_line.text = line.text
            else:
                combined_line.text += "\n" + line.text

        if line.amount is not None:
            assert combined_line.amount is None, f"statement booking has multiple amounts: {combined_line}, {line}"
            combined_line.amount = line.amount

        if line.value_date is not None:
            assert combined_line.value_date is None, f"statement booking has multiple value dates: {combined_line}, {line}"
            combined_line.value_date = line.value_date
            next_line()

    next_line()
    return combined_lines

def parse_statement(pages: list[dict[tuple[float, float], str]]) -> Statement:
    lines: list[StatementLine] = []
    for page in pages[1:]:
        lines += extract_statement_lines(page)

    lines = combine_statement_lines(lines)
    summary = extract_statement_summary(pages[-1])

    return Statement(lines, summary)
