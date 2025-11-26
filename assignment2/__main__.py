"""
Assignment 2: Sales Analysis Demo

Executed when running:
    python -m assignment2
"""

import os
from .sales_analyzer import SalesAnalyzer


def main():
    print("\n=== Sales Data Analysis (Assignment 2) ===\n")

    # Load the CSV file in the same package folder
    csv_path = os.path.join(os.path.dirname(__file__), "sales_data.csv")

    analyzer = SalesAnalyzer(csv_path)

    print(f"Total revenue: {analyzer.total_revenue():,.2f}")
    print("\nTop 5 Products by Revenue:")
    for product, revenue in analyzer.top_products_by_revenue(5):
        print(f" - {product}: {revenue:,.2f}")

    print("\nHigh-value Orders (>= 200):")
    for record in analyzer.high_value_orders(200.0):
        print(f" - Order #{record.order_id}: {record.total_amount:,.2f}")

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()