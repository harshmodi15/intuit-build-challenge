
# Assignment 2 — Design & Architecture Document  
### Sales Data Analysis Using Functional Programming (Python)

This document describes the architecture, functional programming techniques, dataset assumptions, and design rationale behind the Sales Analyzer module.

---

# 1. Architecture Overview

The system is built around a clean functional data-processing pipeline, inspired by Java Streams and implemented using Python’s standard library.

```
┌───────────────────────────────────────────────┐
│                Sales Analyzer System           │
├───────────────────────────────────────────────┤
│  SalesRecord                                   │
│    • Typed representation of one CSV row       │
│    • Performs field parsing + validation       │
│                                                │
│  SalesDataStream                               │
│    • Functional operations                     │
│       - filter(), map(), reduce()              │
│       - sorted_by(), distinct_by()             │
│       - group_by(), take(), skip()             │
│    • Stream-style method chaining              │
│                                                │
│  SalesAnalyzer                                 │
│    • Loads CSV → SalesRecord list              │
│    • Performs all analytical queries           │
│    • Uses pure functional transformations      │
└───────────────────────────────────────────────┘
```

The design intentionally avoids external libraries like pandas to demonstrate functional programming fundamentals.

---

# 2. Component Responsibilities

## **SalesRecord**
- Dataclass representation of a transaction.  
- Strict parsing of:
  - `order_id`
  - `date`
  - `product_category`
  - `product_name`
  - `quantity`
  - `unit_price`
  - `customer_region`
  - `customer_segment`
  - `payment_method`  
- Provides computed property `total_amount`.

---

## **SalesDataStream**
A reusable functional pipeline class supporting:

### **Core Transformations**
- `filter(predicate)`
- `map(mapper)`
- `reduce(reducer, initial)`
- `sorted_by(key, reverse=False)`
- `distinct_by(key)`

### **Sequence Operations**
- `take(n)`
- `skip(n)`

### **Finding / Matching**
- `find_first(predicate)`
- `any_match(predicate)`
- `all_match(predicate)`
- `max_by(key)`
- `min_by(key)`

### **Grouping**
- `group_by(key)` → returns dictionary of key → list of records  

This creates a declarative, chainable, predictable workflow.

---

## **SalesAnalyzer**
Handles all analytics:

### **Implemented Analyses**
1. Total revenue  
2. Revenue by product category  
3. Revenue by region  
4. Average revenue by customer segment  
5. Top N products by revenue  
6. Sales count by payment method  
7. Monthly revenue grouping  
8. High-value orders (threshold filter)  
9. Quantity statistics (min/max/avg)  
10. Expensive product analysis (price threshold)

Each method is built using functional primitives (map/filter/reduce/group).

---

# 3. Key Design Decisions

## **1. Pure Functional Programming**
All analytics follow:

- No mutation  
- No global state  
- No side effects  
- Return new immutable structures  

**Why:**  
Functional code is easier to reason about, test, and maintain.

---

## **2. Custom Stream Abstraction Instead of pandas**
**Why not use pandas?**
- Assignment objective was to demonstrate functional programming concepts  
- pandas hides functional transformations behind a DataFrame abstraction  
- pandas would reduce the demonstration value  

**Advantages of custom pipeline:**
- Explicit map/filter/reduce usage  
- Chaining resembles Java Streams  
- Transparent data flow  

---

## **3. In-Memory Record Model**
SalesRecord objects are:

- Type-safe  
- Easy to validate  
- IDE-friendly  
- Provide computed fields (e.g., revenue)

Better than stringly-typed dictionaries.

---

## **4. Dictionary-Based Aggregations**
All group-based analytics use:

```python
from collections import defaultdict
```

**Why:**  
- Avoids repeated key checks  
- Clean accumulation patterns  
- Efficient grouping  
- Converts to normal dicts before returning (clean API)

---

## **5. Deterministic CSV Loading**
`csv.DictReader` ensures:

- Safe parsing  
- Field-level control  
- No unexpected type coercions (as pandas might do)

---

## **6. Stream Chaining for Readability**
Example:

```python
(self.stream
    .filter(lambda r: r.total_amount > 200)
    .sorted_by(lambda r: r.total_amount, reverse=True)
    .take(5)
)
```

This style is:

- Extremely readable  
- Declarative  
- Eliminates need for for-loops  
- Aligns with assignment goals  

---

# 4. Dataset Design Assumptions

The `sales_data.csv` file is designed to:

- Represent realistic sales transactions  
- Cover multiple categories & products  
- Enable meaningful analytics  
- Spread data across multiple months  
- Include variation in regions and customer segments  
- Support all test cases and edge conditions

Includes:
- 9 fields  
- Mixed product categories  
- Multiple payment methods  
- Multiple customer segments  
- Varying quantities and unit prices  
- Properly structured dates for time-series grouping  

---

# 5. Functional Programming Techniques Used

### **map()**
- Extracting numerical values  
- Transforming object → attribute  
- Uniform projections across records  

### **filter()**
- High-value orders  
- Expensive products  
- Category/region selection  

### **reduce()**
- Calculating total revenue  
- Aggregations requiring a single result  

### **group_by()**
- Category revenue  
- Region revenue  
- Monthly revenue  

### **Composition**
Many methods combine several of these:

```python
self.stream     .filter(...)     .map(...)     .reduce(...)
```

---

# 6. Testing Strategy

Tests verify:

### **SalesRecord**
- Field parsing  
- Type conversions  
- total_amount correctness  

### **SalesDataStream**
- map/filter/reduce correctness  
- sorting & distinct correctness  
- grouping  
- take/skip  
- finding methods  

### **SalesAnalyzer**
- Every analysis method  
- Edge cases:
  - empty datasets  
  - top-N values  
  - threshold filters  
  - monthly grouping  
  - aggregated values  

This ensures correctness, determinism, and functional purity.

---

# 7. Potential Enhancements

- Add caching for repeated analytics  
- Add visualization layer (matplotlib)  
- Accept JSON or Parquet as input formats  
- Introduce parallelized map/reduce  
- Compute rolling monthly averages  
- Add user-defined analytics plugins  

---

# 8. Summary

The Sales Analyzer demonstrates:

### ✔ Clean functional programming design  
### ✔ Effective use of map/filter/reduce  
### ✔ Lightweight stream abstraction  
### ✔ Correct functional behaviors  
### ✔ Clear separation of parsing, transformation, analytics  
### ✔ Thorough testing of all components  

The implementation prioritizes **readability**, **functional purity**, and **extensibility**, while fitting naturally into the assignment requirements.

---

# End of Assignment 2 DESIGN.md
