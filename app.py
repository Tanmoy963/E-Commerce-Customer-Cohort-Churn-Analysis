import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sqlalchemy import create_engine
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title='E-Commerce Cohort Analysis',
    page_icon='📊',
    layout='wide',
)

st.title('📊 E-Commerce Cohort & Retention Analysis')
st.markdown(
    'This dashboard uses **SQL (MySQL)** for data aggregations and'
    ' **Python** for visualization to measure customer retention over time.'
)


# Database Connection Setup
@st.cache_data
def load_cohort_data():
  DB_USER = 'root'
  DB_PASSWORD = 'YourNewPassword'  # <--- YOUR MYSQL PASSWORD
  DB_HOST = 'localhost'
  DB_PORT = '3306'
  DB_NAME = 'ecommerce_analytics'

  engine = create_engine(
      f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
  )

  # Escaped % with %% so Python doesn't throw a format error
  query = """
    WITH customer_cohorts AS (
        SELECT 
            customer_id,
            DATE_FORMAT(MIN(invoice_date), '%%Y-%%m-01') AS cohort_month
        FROM raw_transactions
        WHERE customer_id IS NOT NULL AND customer_id != ''
        GROUP BY customer_id
    ),
    monthly_activity AS (
        SELECT DISTINCT
            customer_id,
            DATE_FORMAT(invoice_date, '%%Y-%%m-01') AS activity_month
        FROM raw_transactions
        WHERE customer_id IS NOT NULL AND customer_id != ''
    )
    SELECT 
        c.cohort_month,
        PERIOD_DIFF(
            DATE_FORMAT(a.activity_month, '%%Y%%m'), 
            DATE_FORMAT(c.cohort_month, '%%Y%%m')
        ) AS cohort_index,
        COUNT(DISTINCT c.customer_id) AS active_customers
    FROM customer_cohorts c
    JOIN monthly_activity a ON c.customer_id = a.customer_id
    GROUP BY c.cohort_month, cohort_index
    ORDER BY c.cohort_month, cohort_index;
    """
  df = pd.read_sql(query, engine)
  return df

try:
  df = load_cohort_data()

  # Reshape data into a Pivot Table (Cohort Matrix)
  cohort_matrix = df.pivot(
      index='cohort_month', columns='cohort_index', values='active_customers'
  )

  # Calculate Retention Percentage
  cohort_size = cohort_matrix.iloc[:, 0]
  retention_matrix = cohort_matrix.divide(cohort_size, axis=0) * 100

  # High-level Metrics
  col1, col2, col3 = st.columns(3)
  col1.metric('Total Cohorts', len(cohort_matrix))
  col2.metric('Initial Total Customers', int(cohort_size.sum()))
  col3.metric(
      'Average Month-1 Retention',
      f"{retention_matrix.iloc[:, 1].mean():.2f}%",
  )

  st.divider()

  # Plotting the Retention Heatmap
  st.subheader('🔥 Cohort Retention Rates (%)')

  fig, ax = plt.subplots(figsize=(14, 8))
  sns.heatmap(
      retention_matrix,
      annot=True,
      fmt='.1f',
      cmap='YlGnBu',
      cbar_kws={'label': 'Retention Rate (%)'},
      ax=ax,
  )
  plt.title('Customer Retention Rate by Monthly Cohort', fontsize=14)
  plt.xlabel('Months Since First Purchase (Cohort Index)', fontsize=12)
  plt.ylabel('Cohort Month', fontsize=12)

  st.pyplot(fig)

except Exception as e:
  st.error(
      f'Error connecting to database or fetching data: {e}\nCheck your MySQL'
      ' password in `app.py`.'
  )