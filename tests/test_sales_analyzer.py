"""
PyTest Suite for Assignment 2: Sales Data Analysis.

Each test includes comments explaining the functional programming concept
or edge case being validated. Focus areas:
- CSV parsing
- Functional operations (map/filter/reduce)
- Stream transformations
- Analytical correctness in SalesAnalyzer
"""

import csv
import os
import tempfile
from datetime import datetime
from assignment2.sales_analyzer import (
    SalesRecord,
    SalesDataStream,
    SalesAnalyzer
)


# =============================================================================
# SalesRecord Tests
# =============================================================================

def test_sales_record_creation():
    """Test: Basic creation + total_amount correctness."""
    r = SalesRecord(
        order_id=1,
        date=datetime(2024, 1, 1),
        product_category="Electronics",
        product_name="Mouse",
        quantity=2,
        unit_price=50.0,
        customer_region="North",
        customer_segment="Consumer",
        payment_method="Credit"
    )
    assert r.total_amount == 100.0
    assert r.product_category == "Electronics"


def test_sales_record_from_csv_row():
    """Test: CSV row → SalesRecord conversion with correct parsing."""
    row = {
        "order_id": "5",
        "date": "2024-01-10",
        "product_category": "Furniture",
        "product_name": "Chair",
        "quantity": "3",
        "unit_price": "75.0",
        "customer_region": "South",
        "customer_segment": "Business",
        "payment_method": "PayPal"
    }
    r = SalesRecord.from_csv_row(row)
    assert r.order_id == 5
    assert r.total_amount == 225.0
    assert r.date == datetime(2024, 1, 10)


# =============================================================================
# SalesDataStream Tests (Functional Programming)
# =============================================================================

def build_test_stream():
    """Helper: Small standardized dataset for stream tests."""
    return SalesDataStream([
        SalesRecord(1, datetime(2024,1,1), "A", "P1", 1, 10.0, "R1", "S1", "M1"),
        SalesRecord(2, datetime(2024,1,2), "A", "P2", 2, 30.0, "R1", "S2", "M2"),
        SalesRecord(3, datetime(2024,1,3), "B", "P3", 3, 50.0, "R2", "S1", "M1"),
    ])


def test_stream_filter():
    """Test: filter() returns only matching records."""
    stream = build_test_stream()
    result = stream.filter(lambda r: r.product_category == "A")
    assert result.count() == 2


def test_stream_map():
    """Test: map() computes derived values correctly."""
    stream = build_test_stream()
    totals = stream.map(lambda r: r.total_amount)
    assert totals == [10.0, 60.0, 150.0]


def test_stream_reduce():
    """Test: reduce() accumulates values as expected."""
    stream = build_test_stream()
    total = stream.reduce(lambda acc, r: acc + r.total_amount, 0.0)
    assert total == 220.0


def test_stream_sorted_by():
    """Test: sorted_by() sorts correctly via key selector."""
    stream = build_test_stream()
    sorted_stream = stream.sorted_by(lambda r: r.unit_price)
    assert sorted_stream.to_list()[0].product_name == "P1"
    assert sorted_stream.to_list()[-1].product_name == "P3"


def test_stream_distinct_by():
    """Edge Case: distinct_by() should remove duplicate categories."""
    stream = build_test_stream()
    distinct = stream.distinct_by(lambda r: r.product_category)
    assert distinct.count() == 2


def test_stream_take_skip():
    """Test: take(n) and skip(n) return correct subsets."""
    stream = build_test_stream()
    assert stream.take(2).count() == 2
    assert stream.skip(2).count() == 1


def test_stream_find_first():
    """Test: find_first() returns first matching record."""
    stream = build_test_stream()
    first_b = stream.find_first(lambda r: r.product_category == "B")
    assert first_b.product_name == "P3"


# =============================================================================
# SalesAnalyzer Tests (End-to-End)
# =============================================================================

def build_temp_csv():
    """
    Helper: Create a temp CSV on disk with deterministic sample rows.
    Used for all SalesAnalyzer integration tests.
    """
    temp = tempfile.NamedTemporaryFile(mode="w", delete=False, newline="")
    writer = csv.writer(temp)
    writer.writerow([
        "order_id", "date", "product_category", "product_name",
        "quantity", "unit_price", "customer_region",
        "customer_segment", "payment_method"
    ])

    rows = [
        (1, "2024-01-01", "Electronics", "Mouse", 2, 25.0, "North", "Consumer", "Credit Card"),
        (2, "2024-01-01", "Furniture", "Chair", 1, 150.0, "South", "Business", "PayPal"),
        (3, "2024-01-02", "Electronics", "Keyboard", 1, 75.0, "East", "Consumer", "Debit Card"),
        (4, "2024-01-03", "Office Supplies", "Notebook", 5, 10.0, "North", "Consumer", "Cash"),
    ]

    for row in rows:
        writer.writerow(row)

    temp.close()
    return temp.name


def test_analyzer_loading():
    """Test: CSV loads correctly into SalesRecord list."""
    csv_path = build_temp_csv()
    analyzer = SalesAnalyzer(csv_path)
    assert len(analyzer.records) == 4
    os.unlink(csv_path)


def test_total_revenue():
    """Test: total_revenue() performs correct global aggregation."""
    csv_path = build_temp_csv()
    analyzer = SalesAnalyzer(csv_path)
    expected = 50 + 150 + 75 + 50
    assert analyzer.total_revenue() == expected
    os.unlink(csv_path)


def test_revenue_by_category():
    """Test: category grouping aggregates revenue correctly."""
    csv_path = build_temp_csv()
    analyzer = SalesAnalyzer(csv_path)
    result = analyzer.revenue_by_category()
    assert result["Electronics"] == 125.0
    assert "Furniture" in result
    os.unlink(csv_path)


def test_revenue_by_region():
    """Test: region grouping produces valid non-zero results."""
    csv_path = build_temp_csv()
    analyzer = SalesAnalyzer(csv_path)
    result = analyzer.revenue_by_region()
    assert result["North"] > 0
    os.unlink(csv_path)


def test_average_order_by_segment():
    """Test: average revenue per customer segment is computed."""
    csv_path = build_temp_csv()
    analyzer = SalesAnalyzer(csv_path)
    avg = analyzer.average_order_by_segment()
    assert "Consumer" in avg
    os.unlink(csv_path)


def test_top_products_by_revenue():
    """Test: top-N products sorted by descending revenue."""
    csv_path = build_temp_csv()
    analyzer = SalesAnalyzer(csv_path)
    top = analyzer.top_products_by_revenue(2)
    assert len(top) == 2
    assert top[0][1] >= top[1][1]
    os.unlink(csv_path)


def test_sales_count_by_payment_method():
    """Test: payment method counts sum to number of rows."""
    csv_path = build_temp_csv()
    analyzer = SalesAnalyzer(csv_path)
    counts = analyzer.sales_count_by_payment_method()
    assert sum(counts.values()) == 4
    os.unlink(csv_path)


def test_high_value_orders():
    """Test: high-value filtering correctly includes expensive items."""
    csv_path = build_temp_csv()
    analyzer = SalesAnalyzer(csv_path)
    high = analyzer.high_value_orders(100.0)
    assert any(record.product_name == "Chair" for record in high)
    os.unlink(csv_path)


def test_quantity_statistics():
    """Test: min/max/avg/total quantity are computed correctly."""
    csv_path = build_temp_csv()
    analyzer = SalesAnalyzer(csv_path)
    stats = analyzer.quantity_statistics()
    assert stats["min"] == 1
    assert stats["max"] == 5
    os.unlink(csv_path)


def test_expensive_products_analysis():
    """Test: expensive-products summary includes expected fields."""
    csv_path = build_temp_csv()
    analyzer = SalesAnalyzer(csv_path)
    result = analyzer.expensive_products_analysis(price_threshold=100)
    assert result["count"] >= 1
    os.unlink(csv_path)