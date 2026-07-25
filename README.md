# 📊 E-Commerce Cohort & Customer Retention Analytics

An end-to-end analytics project analyzing customer retention across 13 monthly cohorts using **MySQL**, **Python**, and **Streamlit**.

---

## 📌 Project Overview
Understanding customer churn and retention is critical for e-commerce growth. This project ingests transaction records, processes user acquisition cohorts directly inside MySQL using **Common Table Expressions (CTEs)** and date math, and renders an interactive heatmap dashboard in Streamlit.

### Key Metrics Uncovered:
* **Total Cohorts Tracked:** 13 Months
* **Total Customers Processed:** 4,372
* **Average Month-1 Retention Rate:** 24.09%

---

## 🛠️ Tech Stack
* **Database:** MySQL
* **Language:** Python 3.10+
* **Data Manipulation:** Pandas, SQLAlchemy, PyMySQL
* **Data Visualization:** Seaborn, Matplotlib
* **Web App Framework:** Streamlit

---

## ⚙️ How to Run Locally

### 1. Clone Repository & Install Dependencies
```bash
git clone https://github.com/YOUR_USERNAME/e-commerce-cohort-analysis.git
cd e-commerce-cohort-analysis
pip install -r requirements.txt
```

### 2. Ingest Data into MySQL
Ensure MySQL is running, configure database credentials in `load_local_data.py`, and run:

```bash
python load_local_data.py
```

### 3. Launch Dashboard
```bash
streamlit run app.py
```

---
