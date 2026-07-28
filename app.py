import duckdb
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title='Live Cohort & Retention Analysis',
    page_icon='📊',
    layout='wide',
)

st.title('📊 E-Commerce Cohort & Retention Analytics')
st.markdown(
    '**Live Interactive Dashboard** | Built with **SQL (DuckDB/MySQL)**,'
    ' **Python**, & **Streamlit**'
)


# Load Data and Execute SQL Query directly
@st.cache_data
def load_cohort_data():
  # URL to raw CSV on GitHub (allows the live app to run independently)
  data_url = 'https://raw.githubusercontent.com/guipsamora/pandas_exercises/master/07_Visualization/Online_Retail/Online_Retail.csv'

  # Connect to in-memory SQL database
  con = duckdb.connect(database=':memory:')

  # SQL Query using CTEs and SQL Date Functions
  query = f"""
    WITH cleaned_data AS (
        SELECT 
            CAST(CustomerID AS INT) AS customer_id,
            strptime(InvoiceDate, '%m/%d/%Y %H:%M') AS invoice_date
        FROM read_csv_auto('{data_url}')
        WHERE CustomerID IS NOT NULL
    ),
    customer_cohorts AS (
        SELECT 
            customer_id,
            date_trunc('month', MIN(invoice_date)) AS cohort_month
        FROM cleaned_data
        GROUP BY customer_id
    ),
    monthly_activity AS (
        SELECT DISTINCT
            customer_id,
            date_trunc('month', invoice_date) AS activity_month
        FROM cleaned_data
    )
    SELECT 
        strftime(c.cohort_month, '%Y-%m-01') AS cohort_month,
        (date_part('year', a.activity_month) - date_part('year', c.cohort_month)) * 12 + 
        (date_part('month', a.activity_month) - date_part('month', c.cohort_month)) AS cohort_index,
        COUNT(DISTINCT c.customer_id) AS active_customers
    FROM customer_cohorts c
    JOIN monthly_activity a ON c.customer_id = a.customer_id
    GROUP BY c.cohort_month, cohort_index
    ORDER BY c.cohort_month, cohort_index;
    """

  df = con.execute(query).df()
  return df


try:
  df = load_cohort_data()

  # Reshape data into a Pivot Table Matrix
  cohort_matrix = df.pivot(
      index='cohort_month', columns='cohort_index', values='active_customers'
  )

  # Calculate Retention Percentage
  cohort_size = cohort_matrix.iloc[:, 0]
  retention_matrix = cohort_matrix.divide(cohort_size, axis=0) * 100

  # High-level Metrics
  col1, col2, col3 = st.columns(3)
  col1.metric('Total Cohorts Tracked', len(cohort_matrix))
  col2.metric('Total Unique Customers', f'{int(cohort_size.sum()):,}')
  col3.metric(
      'Average Month-1 Retention',
      f'{retention_matrix.iloc[:, 1].mean():.2f}%',
  )

  st.divider()

  # Plotting the Retention Heatmap
  st.subheader('🔥 Customer Retention Rate Heatmap (%)')

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
  st.error(f'Error executing live dashboard: {e}')