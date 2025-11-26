# Intuit Build Challenge

A complete solution to the Intuit Build Challenge demonstrating strong skills in concurrent programming and functional data processing.

**Author:** Harsh Modi  
**Email:** harshdee@usc.edu

---

## 📌 Overview

This repository contains solutions for both assignments in the Intuit Build Challenge:

| Assignment | Description | Key Concepts |
|-----------|-------------|--------------|
| **Assignment 1** | Producer–Consumer system with synchronization | Threading, Locks, Blocking Queues, Wait/Notify |
| **Assignment 2** | Sales data analysis built using functional programming | Map, Filter, Reduce, Grouping, Stream-style chaining |

Both solutions are implemented using only the **Python standard library**, with full unit test coverage.

---

## 📁 Project Structure

```text
intuit-build-challenge/
├── README.md
├── requirements.txt
│
├── assignment1/
│   ├── __init__.py
│   ├── producer_consumer.py
│   └── __main__.py
│
├── assignment2/
│   ├── __init__.py
│   ├── sales_analyzer.py
│   └── sales_data.csv
│   └── __main__.py
│
├── tests/
│   ├── __init__.py
│   ├── test_producer_consumer.py
│   └── test_sales_analyzer.py
│
└── outputs/
    ├── assignment1.png
    ├── assignment2.png
    └── assignment_pytests.png
```

---

## ⚙️ Requirements
- Python **3.8+**
- **No external dependencies** (uses only Python standard library)

---

## 🚀 Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/harshmodi15/intuit-build-challenge.git
cd intuit-build-challenge
```

### 2. (Optional) Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
```

---

## ▶️ Running the Solutions

### **Assignment 1 — Producer–Consumer System**
Run the assignment demo:
```bash
python -m assignment1
```

### **Assignment 2 — Sales Data Analysis**
Run the analysis:
```bash
python -m assignment2
```

---

## 🧪 Running Tests

### Run all tests using PyTest
```bash
python -m pytest -v
```

### Or using unittest
```bash
python -m unittest discover tests -v
```

The `outputs/assignment_all_tests.png` file contains the screenshot of all tests passing.

---

## 📸 Sample Output

Screenshots of working console outputs are included in the `/outputs` folder:

| File | Description |
|------|-------------|
| **assignment1.png** | Producer–Consumer system execution |
| **assignment2.png** | High-level sales analysis output |
| **assignment_pytests.png** | All unit tests passing successfully |

---

## 🧠 Design Decisions

### **Assignment 1 (Concurrency)**
- Implemented an entirely custom **BoundedBlockingQueue** using `threading.Condition`.
- Enforced **blocking put/get** behavior with proper signaling.
- Producers and consumers run concurrently and exit gracefully.
- Highly modular and easy to extend for multiple threads.

### **Assignment 2 (Functional Programming)**
- Designed a clean, expressive **SalesDataStream** class inspired by Java Streams.
- All transformations use functional patterns:  
  `map`, `filter`, `reduce`, lambdas, grouping, distinct selection, chaining.
- Implemented multiple analyses combining grouping, aggregation, and sorting.

---

## 📄 License
This project was created for the Intuit Build Challenge.
