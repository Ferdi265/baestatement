from typing import Optional
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime
import re

@dataclass
class StatementLine:
    text: str
    amount: Optional[float] = None
    booking_date: Optional[datetime] = None
    value_date: Optional[datetime] = None

    def is_empty(self) -> bool:
        return (
            self.text.strip() == "" and
            self.amount is None and
            self.booking_date is None and
            self.value_date is None
        )

    def is_comment(self) -> bool:
        return (
            self.amount is None and
            self.booking_date is None and
            self.value_date is None
        )

@dataclass
class IncompleteStatementLine:
    text: Optional[str] = None
    amount: Optional[float] = None
    booking_date: Optional[datetime | tuple[int, int]] = None
    value_date: Optional[datetime | tuple[int, int]] = None

    def is_empty(self) -> bool:
        return (
            (self.text is None or self.text.strip() == "") and
            self.amount is None and
            self.booking_date is None and
            self.value_date is None
        )

    def assert_complete(self) -> StatementLine:
        assert self.text is not None, f"statement line has no text: {self}"
        assert not isinstance(self.booking_date, tuple), f"statement line has no valid booking date: {self}"
        assert not isinstance(self.value_date, tuple), f"statement line has no valid value date: {self}"
        return StatementLine(self.text, self.amount, self.booking_date, self.value_date)

@dataclass
class StatementSummary:
    date: datetime
    sum_expenses: float
    sum_income: float
    old_balance: float
    new_balance: float
    closing_date: Optional[datetime] = None
    closing_balance: Optional[float] = None

@dataclass
class IncompleteStatementSummary:
    date: Optional[datetime] = None
    sum_expenses: Optional[float] = None
    sum_income: Optional[float] = None
    old_balance: Optional[float] = None
    new_balance: Optional[float] = None
    closing_date: Optional[datetime] = None
    closing_balance: Optional[float] = None

    def assert_complete(self) -> StatementSummary:
        assert self.date is not None, f"statement summary has no date: {self}"
        assert self.old_balance is not None, f"statement summary has no old balance: {self}"
        assert self.sum_expenses is not None, f"statement summary has no sum of expenses: {self}"
        assert self.sum_income is not None, f"statement summary has no sum of income: {self}"
        assert self.new_balance is not None, f"statement summary has no new balance: {self}"
        return StatementSummary(self.date, self.sum_expenses, self.sum_income, self.old_balance, self.new_balance, self.closing_date, self.closing_balance)

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

def parse_field_amount(field: str) -> Optional[float]:
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
def extract_statement_lines(fields: dict[tuple[float, float], str]) -> list[IncompleteStatementLine]:
    lines: defaultdict[float, IncompleteStatementLine] = defaultdict(IncompleteStatementLine)

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
def extract_statement_summary(fields: dict[tuple[float, float], str]) -> IncompleteStatementSummary:
    summary = IncompleteStatementSummary()

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

def combine_statement_lines(lines: list[IncompleteStatementLine]) -> list[IncompleteStatementLine]:
    combined_lines: list[IncompleteStatementLine] = []
    combined_line = IncompleteStatementLine()

    def next_line():
        nonlocal combined_line
        if not combined_line.is_empty():
            combined_lines.append(combined_line)
            combined_line = IncompleteStatementLine()

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

def infer_statement_line_dates(lines: list[IncompleteStatementLine], statement_date: datetime) -> list[StatementLine]:
    complete_lines: list[StatementLine] = []
    prev_date = statement_date

    def infer_date(incomplete_date: datetime | tuple[int, int]) -> datetime:
        nonlocal prev_date
        if isinstance(incomplete_date, datetime):
            return incomplete_date

        day, month = incomplete_date
        match (prev_date.month, month):
            case (1, 12):
                year = prev_date.year - 1
            case (12, 1):
                year = prev_date.year + 1
            case _:
                assert abs(prev_date.month - month) <= 1, f"statement booking date jumped from {prev_date:%d.%m.%Y} to {day:02}.{month:02}: {line}"
                year = prev_date.year

        return datetime(year, month, day)

    for line in reversed(lines):
        if line.value_date is not None:
            line.value_date = infer_date(line.value_date)

        if line.booking_date is not None:
            prev_date = infer_date(line.booking_date)
            line.booking_date = prev_date

        complete_lines.append(line.assert_complete())

    return list(reversed(complete_lines))

CLOSING_BOOKING = r"Ihr Kontostand per ([0-9]{2}\.[0-9]{2}\.[0-9]{4}): EUR ([0-9.,]+)"
def infer_closing_booking(lines: list[StatementLine]) -> Optional[datetime]:
    for line in lines:
        if not line.is_comment():
            continue

        m = re.match(CLOSING_BOOKING, line.text)
        if m is not None:
            return datetime.strptime(m.group(1), "%d.%m.%Y"), parse_field_amount(m.group(2))

    return None, None

def strip_comments(lines: list[StatementLine]) -> list[StatementLine]:
    stripped: list[StatementLine] = []

    for line in lines:
        if line.is_comment():
            continue

        stripped.append(line)

    return stripped

def parse_statement(pages: list[dict[tuple[float, float], str]], strip: bool) -> Statement:
    lines: list[IncompleteStatementLine] = []
    for page in pages[1:]:
        lines += extract_statement_lines(page)

    lines = combine_statement_lines(lines)
    summary = extract_statement_summary(pages[-1])
    complete_lines = infer_statement_line_dates(lines, summary.date)
    summary.closing_date, summary.closing_balance = infer_closing_booking(complete_lines)

    if strip:
        complete_lines = strip_comments(complete_lines)

    return Statement(complete_lines, summary.assert_complete())
