from typing import Optional
from datetime import datetime

def fmt_amount(amount: Optional[float]) -> str:
    if amount is None:
        return ""

    return f"{amount:+10.2f}€"

def fmt_amount_repr(amount: Optional[float]) -> str:
    if amount is None:
        return str(amount)

    return f"{amount:.2f}"

def fmt_date(date: Optional[datetime]) -> str:
    if date is None:
        return ""

    return f"{date:%d.%m.%Y}"

def fmt_date_noyear(date: Optional[datetime]) -> str:
    if date is None:
        return "     "

    return f"{date:%d.%m}"

def fmt_date_repr(date: Optional[datetime]) -> str:
    if date is None:
        return str(date)

    return f"datetime({date.year}, {date.month}, {date.day})"

