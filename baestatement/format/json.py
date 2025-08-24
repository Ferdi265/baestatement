from ..parse import Statement, StatementSummary, StatementLine
from ..parse import IncompleteStatementSummary, IncompleteStatementLine
from .util import fmt_date
from datetime import datetime
import json

def format_dict_summary(summary: StatementSummary) -> dict:
    return {
        "date": summary.date.isoformat(),
        "sum_expenses": summary.sum_expenses,
        "sum_income": summary.sum_income,
        "old_balance": summary.old_balance,
        "new_balance": summary.new_balance,
        "closing_date": summary.closing_date and summary.closing_date.isoformat(),
        "closing_balance": summary.closing_balance
    }

def parse_dict_summary(summary: dict) -> StatementSummary:
    return IncompleteStatementSummary(
        date = datetime.fromisoformat(summary["date"]),
        sum_expenses = summary["sum_expenses"],
        sum_income = summary["sum_income"],
        old_balance = summary["old_balance"],
        new_balance = summary["new_balance"],
        closing_date = summary["closing_date"] and datetime.fromisoformat(summary["closing_date"]),
        closing_balance = summary["closing_balance"]
    ).assert_complete()

def format_dict_line(line: StatementLine) -> dict:
    return {
        "text": line.text,
        "amount": line.amount,
        "booking_date": line.booking_date and line.booking_date.isoformat(),
        "value_date": line.value_date and line.value_date.isoformat()
    }

def parse_dict_line(line: dict) -> StatementLine:
    return IncompleteStatementLine(
        text = line["text"],
        amount = line["amount"],
        booking_date = line["booking_date"] and datetime.fromisoformat(line["booking_date"]),
        value_date = line["value_date"] and datetime.fromisoformat(line["value_date"])
    ).assert_complete()


def format_json(stmt: Statement) -> str:
    return json.dumps({
        "lines": [format_dict_line(line) for line in stmt.lines],
        "summary": format_dict_summary(stmt.summary)
    })


def parse_json(s: str) -> Statement:
    stmt = json.loads(s)

    return Statement(
        lines = [parse_dict_line(line) for line in stmt["lines"]],
        summary = parse_dict_summary(stmt["summary"])
    )
