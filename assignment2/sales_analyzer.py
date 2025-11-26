"""
Assignment 2: CSV Data Analysis with Functional Programming

This module demonstrates:
- map / filter / reduce
- lambda expressions
- grouping via dictionary aggregation
- stream-style chained transformations
- readable, Pythonic functional programming

It provides:
- SalesRecord  → representation of a CSV row
- SalesDataStream → functional utilities over a list of records
- SalesAnalyzer → analytical queries over the dataset
"""

from __future__ import annotations
import csv
from dataclasses import dataclass
from datetime import datetime
from functools import reduce
from typing import Callable, Any, List, Dict, Optional
from collections import defaultdict


# Part 1: SalesRecord
@dataclass
class SalesRecord:
    """
    Represents a single sales transaction in the dataset.
    """
    order_id: int
    date: datetime
    product_category: str
    product_name: str
    quantity: int
    unit_price: float
    customer_region: str
    customer_segment: str
    payment_method: str

    @property
    def total_amount(self) -> float:
        """Compute revenue for this transaction."""
        return self.quantity * self.unit_price

    @classmethod
    def from_csv_row(cls, row: Dict[str, str]) -> "SalesRecord":
        """Create a record from a CSV row."""
        return cls(
            order_id=int(row["order_id"]),
            date=datetime.strptime(row["date"], "%Y-%m-%d"),
            product_category=row["product_category"],
            product_name=row["product_name"],
            quantity=int(row["quantity"]),
            unit_price=float(row["unit_price"]),
            customer_region=row["customer_region"],
            customer_segment=row["customer_segment"],
            payment_method=row["payment_method"],
        )


# Part 2: SalesDataStream (Functional Operations)

class SalesDataStream:
    """
    Lightweight stream-like API providing functional programming helpers.
    """

    def __init__(self, records: List[SalesRecord]):
        self._records = records

    # Functional Filters
    def filter(self, predicate: Callable[[SalesRecord], bool]) -> "SalesDataStream":
        return SalesDataStream(list(filter(predicate, self._records)))

    # Mapping / Reducing
    def map(self, mapper: Callable[[SalesRecord], Any]) -> List[Any]:
        return list(map(mapper, self._records))

    def reduce(self, reducer: Callable[[Any, SalesRecord], Any], initial: Any) -> Any:
        return reduce(reducer, self._records, initial)

    # Sorting / Distinct
    def sorted_by(self, key: Callable[[SalesRecord], Any], reverse: bool = False) -> "SalesDataStream":
        return SalesDataStream(sorted(self._records, key=key, reverse=reverse))

    def distinct_by(self, key: Callable[[SalesRecord], Any]) -> "SalesDataStream":
        seen = set()
        unique = []
        for r in self._records:
            k = key(r)
            if k not in seen:
                seen.add(k)
                unique.append(r)
        return SalesDataStream(unique)

    # Subset operations
    def take(self, n: int) -> "SalesDataStream":
        return SalesDataStream(self._records[:n])

    def skip(self, n: int) -> "SalesDataStream":
        return SalesDataStream(self._records[n:])

    # Matching / Finding
    def any_match(self, predicate: Callable[[SalesRecord], bool]) -> bool:
        return any(map(predicate, self._records))

    def all_match(self, predicate: Callable[[SalesRecord], bool]) -> bool:
        return all(map(predicate, self._records))

    def find_first(self, predicate: Optional[Callable[[SalesRecord], bool]] = None) -> Optional[SalesRecord]:
        if not self._records:
            return None
        if predicate is None:
            return self._records[0]
        for r in self._records:
            if predicate(r):
                return r
        return None

    def max_by(self, key: Callable[[SalesRecord], Any]) -> Optional[SalesRecord]:
        return max(self._records, key=key) if self._records else None

    def min_by(self, key: Callable[[SalesRecord], Any]) -> Optional[SalesRecord]:
        return min(self._records, key=key) if self._records else None

    # Utility
    def count(self) -> int:
        return len(self._records)

    def to_list(self) -> List[SalesRecord]:
        return list(self._records)

    def group_by(self, key: Callable[[SalesRecord], Any]) -> Dict[Any, List[SalesRecord]]:
        groups = defaultdict(list)
        for r in self._records:
            groups[key(r)].append(r)
        return dict(groups)


# Part 3: SalesAnalyzer

class SalesAnalyzer:
    """
    Loads CSV data into SalesRecord objects and performs analytical queries.
    Each method demonstrates a functional-programming concept.
    """

    def __init__(self, csv_path: str):
        self.records: List[SalesRecord] = self._load(csv_path)
        self.stream = SalesDataStream(self.records)

    # CSV Loading
    def _load(self, csv_path: str) -> List[SalesRecord]:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [SalesRecord.from_csv_row(row) for row in reader]

    # Analytical Methods
    def total_revenue(self) -> float:
        return self.stream.reduce(lambda acc, r: acc + r.total_amount, 0.0)

    def revenue_by_category(self) -> Dict[str, float]:
        groups = self.stream.group_by(lambda r: r.product_category)
        return {cat: sum(r.total_amount for r in records) for cat, records in groups.items()}

    def revenue_by_region(self) -> Dict[str, float]:
        groups = self.stream.group_by(lambda r: r.customer_region)
        return {region: sum(r.total_amount for r in records) for region, records in groups.items()}

    def average_order_by_segment(self) -> Dict[str, float]:
        groups = self.stream.group_by(lambda r: r.customer_segment)
        return {
            seg: sum(r.total_amount for r in recs) / len(recs)
            for seg, recs in groups.items()
        }

    def top_products_by_revenue(self, n: int = 5) -> List[tuple[str, float]]:
        groups = self.stream.group_by(lambda r: r.product_name)
        revenue_list = [
            (product, sum(r.total_amount for r in recs))
            for product, recs in groups.items()
        ]
        return sorted(revenue_list, key=lambda x: x[1], reverse=True)[:n]

    def sales_count_by_payment_method(self) -> Dict[str, int]:
        groups = self.stream.group_by(lambda r: r.payment_method)
        return {method: len(records) for method, records in groups.items()}

    def monthly_revenue(self) -> Dict[str, float]:
        groups = self.stream.group_by(lambda r: r.date.strftime("%Y-%m"))
        return {month: sum(r.total_amount for r in recs) for month, recs in groups.items()}

    def high_value_orders(self, threshold: float = 200.0) -> List[SalesRecord]:
        return (
            self.stream
                .filter(lambda r: r.total_amount >= threshold)
                .sorted_by(lambda r: r.total_amount, reverse=True)
                .to_list()
        )

    def quantity_statistics(self) -> Dict[str, float]:
        quantities = self.stream.map(lambda r: r.quantity)
        return {
            "total": sum(quantities),
            "average": sum(quantities) / len(quantities),
            "min": min(quantities),
            "max": max(quantities),
        }

    def expensive_products_analysis(self, price_threshold: float = 100.0) -> Dict[str, Any]:
        filtered = self.stream.filter(lambda r: r.unit_price >= price_threshold)

        if filtered.count() == 0:
            return {"count": 0, "categories": {}, "total_revenue": 0, "products": []}

        by_category = filtered.group_by(lambda r: r.product_category)

        return {
            "count": filtered.count(),
            "categories": {cat: len(records) for cat, records in by_category.items()},
            "total_revenue": sum(filtered.map(lambda r: r.total_amount)),
            "products": list(set(filtered.map(lambda r: r.product_name))),
        }
