from typing import Callable, Optional
from dataclasses import dataclass, field
from datetime import timedelta, datetime
from collections import deque
import itertools
import calendar
import numpy as np
import numpy.typing as npt

from .parse import Statement, StatementLine, IncompleteStatementSummary

@dataclass
class StatementStats:
    datetime: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype='datetime64'))
    cur_balance: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype='float64'))
    avg_balance: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype='float64'))
    min_balance: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype='float64'))
    max_balance: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype='float64'))

def sort(statements: list[Statement]) -> list[Statement]:
    return list(sorted(statements, key=lambda stmt: stmt.summary.date))

def take_date_range(statements: list[Statement], start_date: Optional[datetime], end_date: Optional[datetime]) -> list[Statement]:
    # do nothing if no dates given
    if start_date is None and end_date is None:
        return statements

    # fill in missing start/end date
    statements = list(sorted(statements, key=lambda stmt: stmt.summary.date))
    all_lines = itertools.chain.from_iterable(stmt.lines for stmt in statements)
    all_lines = filter(lambda line: line.value_date is not None and line.amount, all_lines)
    all_lines = list(sorted(all_lines, key=lambda line: line.value_date))
    if start_date is None:
        start_date = all_lines[0].value_date
    if end_date is None:
        end_date = all_lines[-1].value_date

    # process statements
    new_statements: list[Statement] = []
    for stmt in statements:
        stmt_lines = filter(lambda line: line.value_date is not None and line.amount, stmt.lines)
        stmt_lines = list(sorted(stmt_lines, key=lambda line: line.value_date))

        # stmt dates fully outside range
        if stmt_lines[-1].value_date < start_date or stmt_lines[0].value_date > end_date:
            continue
        # stmt dates fully inside range
        elif stmt_lines[0].value_date >= start_date and stmt_lines[-1].value_date <= end_date:
            new_statements.append(stmt)
        # stmt dates partially inside range
        else:
            # need to reconstruct new statement summary
            range_lines = list(filter(lambda line: line.value_date >= start_date and line.value_date <= end_date, stmt_lines))
            cur_balance = stmt.summary.old_balance
            summary = IncompleteStatementSummary(
                date = min(stmt.summary.date, end_date),
                sum_income = 0.,
                sum_expenses = 0.,
                old_balance = cur_balance,
                new_balance = cur_balance,
            )
            # loop over stmt_lines to reconstruct balance
            for line in stmt_lines:
                cur_balance += line.amount
                if line.value_date < start_date:
                    summary.old_balance = cur_balance
                if line.value_date <= end_date:
                    summary.new_balance = cur_balance
                if line.value_date >= start_date and line.value_date <= end_date:
                    if line.amount > 0:
                        summary.sum_income += line.amount
                    else:
                        summary.sum_expenses += line.amount
            # reconstruct Statement
            assert summary.sum_income <= stmt.summary.sum_income, f"partial statement has more income ({summary.sum_income} vs {stmt.summary.sum_income})"
            assert summary.sum_expenses >= stmt.summary.sum_expenses, f"partial statement has more expenses ({summary.sum_expenses} vs {stmt.summary.sum_expenses})"
            new_statements.append(Statement(
                lines = range_lines,
                summary = summary.assert_complete()
            ))

    return new_statements


def analyze(statements: list[Statement], avg_period: int = 31, difference: bool = False) -> StatementStats:
    statements = sort(statements)

    lines = itertools.chain.from_iterable(stmt.lines for stmt in statements)
    lines = filter(lambda line: line.value_date is not None and line.amount, lines)
    lines = list(sorted(lines, key=lambda line: line.value_date))

    start_balance = statements[0].summary.old_balance
    end_balance = statements[-1].summary.new_balance
    start_date = lines[0].value_date
    end_date = lines[-1].value_date
    num_days = (end_date - start_date).days + 1
    dates = iter((i, start_date + timedelta(days=i)) for i in range(num_days))

    stats = StatementStats(
        datetime    = np.zeros(num_days, dtype='datetime64[h]'),
        cur_balance = np.zeros(num_days, dtype='float64'),
        avg_balance = np.zeros(num_days, dtype='float64'),
        min_balance = np.zeros(num_days, dtype='float64'),
        max_balance = np.zeros(num_days, dtype='float64'),
    )

    i, cur_date = next(dates)
    cur_balance = start_balance
    cur_difference = 0
    last_balances: deque[float] = deque([cur_balance], maxlen = avg_period)
    last_differences: deque[float] = deque([cur_difference], maxlen = avg_period)
    def next_date():
        nonlocal i, cur_date, cur_difference
        # update history table
        last_balances.append(cur_balance)
        cur_difference = cur_balance - last_balances[0]
        last_differences.append(cur_difference)
        # add date to stats
        stats.datetime[i] = cur_date
        stats.cur_balance[i] = cur_difference if difference else cur_balance
        stats.avg_balance[i] = np.average(last_differences if difference else last_balances)
        stats.min_balance[i] = np.min(last_differences if difference else last_balances)
        stats.max_balance[i] = np.max(last_differences if difference else last_balances)
        # go to next date
        i, cur_date = next(dates)

    for line in lines:
        assert line.value_date is not None
        assert line.amount is not None

        while cur_date < line.value_date:
            next_date()

        # update balance
        cur_balance += line.amount

    # consume all remaining dates
    try:
        while True:
            next_date()
    except StopIteration:
        pass

    return stats

@dataclass
class StatementPeriodStats:
    labels: list[str] | list[int] = field(default_factory=list)
    avg_expenses: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype='float64'))
    min_expenses: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype='float64'))
    max_expenses: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype='float64'))
    avg_income: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype='float64'))
    min_income: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype='float64'))
    max_income: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype='float64'))

def analyze_period(statements: list[Statement], categorize: Callable[[StatementLine], int], cumulative: bool = False) -> StatementPeriodStats:
    statements = sort(statements)

    lines = itertools.chain.from_iterable(stmt.lines for stmt in statements)
    lines = filter(lambda line: line.value_date is not None and line.amount, lines)
    lines = list(sorted(lines, key=lambda line: line.value_date))

    num_categories = max(categorize(line) for line in lines) + 1
    num_expenses = np.zeros(num_categories, dtype=int)
    sum_expenses = np.zeros(num_categories, dtype='float64')
    num_income = np.zeros(num_categories, dtype=int)
    sum_income = np.zeros(num_categories, dtype='float64')
    stats = StatementPeriodStats(
        labels = list(range(num_categories)),
        avg_expenses = np.zeros(num_categories, dtype='float64'),
        min_expenses = np.zeros(num_categories, dtype='float64'),
        max_expenses = np.zeros(num_categories, dtype='float64'),
        avg_income = np.zeros(num_categories, dtype='float64'),
        min_income = np.zeros(num_categories, dtype='float64'),
        max_income = np.zeros(num_categories, dtype='float64'),
    )

    stats.min_expenses[:] = np.inf
    stats.min_income[:] = np.inf

    category: int | None = None
    next_category: int
    cur_expense_sum: float = 0.
    cur_income_sum: float = 0.
    def add_stats():
        nonlocal category, cur_expense_sum, cur_income_sum
        if category is None:
            return

        num_expenses[category] += 1
        sum_expenses[category] += cur_expense_sum
        stats.min_expenses[category] = min(stats.min_expenses[category], cur_expense_sum)
        stats.max_expenses[category] = max(stats.max_expenses[category], cur_expense_sum)

        num_income[category] += 1
        sum_income[category] += cur_income_sum
        stats.min_income[category] = min(stats.min_income[category], cur_income_sum)
        stats.max_income[category] = max(stats.max_income[category], cur_income_sum)

        if not cumulative or next_category < category:
            cur_income_sum = 0.
            cur_expense_sum = 0.

    for line in lines:
        next_category = categorize(line)
        if next_category != category:
            add_stats()
            category = next_category

        if line.amount < 0:
            cur_expense_sum += abs(line.amount)
        else:
            cur_income_sum += abs(line.amount)

    add_stats()

    stats.avg_expenses = sum_expenses / num_expenses
    stats.avg_income = sum_income / num_income

    return stats

def analyze_yearly(statements: list[Statement], cumulative: bool = False) -> StatementPeriodStats:
    categorize = lambda stmt: stmt.value_date.month - 1
    stats = analyze_period(statements, categorize, cumulative = cumulative)
    stats.labels = [calendar.month_name[i+1] for i in stats.labels]
    return stats

def analyze_monthly(statements: list[Statement], cumulative: bool = False) -> StatementPeriodStats:
    categorize = lambda stmt: stmt.value_date.day - 1
    stats = analyze_period(statements, categorize, cumulative = cumulative)
    stats.labels = [i+1 for i in stats.labels]
    return stats

def analyze_weekly(statements: list[Statement], cumulative: bool = False) -> StatementPeriodStats:
    categorize = lambda stmt: stmt.value_date.weekday()
    stats = analyze_period(statements, categorize, cumulative = cumulative)
    stats.labels = [calendar.day_name[i] for i in stats.labels]
    return stats
