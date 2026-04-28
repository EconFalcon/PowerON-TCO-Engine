"""NPV and break-even calculations."""
from typing import List, Optional
import numpy as np


def npv(yearly_totals: List[float], discount_rate: float) -> float:
    """
    Net Present Value using SUMPRODUCT of costs * discount factors.
    Year index 0 = Year 1 (first operating year) — not discounted.
    """
    factors = np.array([1 / (1 + discount_rate) ** y for y in range(len(yearly_totals))])
    return float(np.dot(np.array(yearly_totals), factors))


def cumulative(yearly_totals: List[float]) -> List[float]:
    result = []
    running = 0.0
    for v in yearly_totals:
        running += v
        result.append(running)
    return result


def break_even_year(ev_yearly: List[float], ice_yearly: List[float]) -> Optional[int]:
    """
    Return the first year (1-indexed) where EV cumulative cost < ICE cumulative cost.
    Returns None if no break-even within the analysis period.
    """
    ev_cum = cumulative(ev_yearly)
    ice_cum = cumulative(ice_yearly)
    for i, (ev, ice) in enumerate(zip(ev_cum, ice_cum)):
        if ev < ice:
            return i + 1
    return None
