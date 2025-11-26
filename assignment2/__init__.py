"""
Assignment 2: CSV Data Analysis with Functional Programming

This package exposes:
- SalesRecord: structured representation of a sales transaction
- SalesDataStream: functional/stream-like operations on collections
- SalesAnalyzer: higher-level analytics built on functional primitives
"""

from .sales_analyzer import (
    SalesRecord,
    SalesDataStream,
    SalesAnalyzer,
)

__all__ = [
    "SalesRecord",
    "SalesDataStream",
    "SalesAnalyzer",
]