from dataclasses import dataclass, field
from datetime import timedelta
from collections import deque
import itertools
import numpy as np
import numpy.typing as npt

from .parse import Statement

@dataclass
class StatementStats:
    datetime: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype='datetime64'))
    cur_balance: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype='float64'))
    avg_balance: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype='float64'))
    min_balance: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype='float64'))
    max_balance: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype='float64'))

def sort(statements: list[Statement]) -> list[Statement]:
    return list(sorted(statements, key=lambda stmt: stmt.summary.date))

def analyze(statements: list[Statement], avg_period: int = 31) -> StatementStats:
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
    last_balances: deque[float] = deque([cur_balance], maxlen = avg_period)
    def next_date():
        nonlocal i, cur_date
        # add date to stats
        last_balances.append(cur_balance)
        stats.datetime[i] = cur_date
        stats.cur_balance[i] = cur_balance
        stats.avg_balance[i] = np.average(last_balances)
        stats.min_balance[i] = np.min(last_balances)
        stats.max_balance[i] = np.max(last_balances)
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
