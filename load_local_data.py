from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

# 1. Define file path using Path to handle spaces and backslashes smoothly
folder_path = Path(
    r'C:\Users\TANMOY DAS\OneDrive\Documents\Projects\E-Commerce Customer Cohort & Churn Analysis'
)

# Look for the .csv or .xlsx file in your directory
csv_files = list(folder_path.glob('*.csv')) + list(folder_path.glob('*.xlsx'))

if not csv_files:
  raise FileNotFoundError(
      f'No CSV or Excel file found in {folder_path}. Please check the file name/extension.'
  )

data_file = csv_files[0]
print(f'Found file: {data_file.name}')

# 2. Read local file
print('Loading local dataset into Pandas...')
if data_file.suffix == '.csv':
  df = pd.read_csv(data_file, encoding='latin1')
else:
  df = pd.read_excel(data_file)

# 3. Clean column names & data types
print('Cleaning data...')
# Map common variations of column names in Online Retail dataset
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# Handle missing Customer IDs
if 'customerid' in df.columns:
  df.rename(columns={'customerid': 'customer_id'}, inplace=True)
if 'invoiceno' in df.columns:
  df.rename(columns={'invoiceno': 'invoice_no'}, inplace=True)
if 'stockcode' in df.columns:
  df.rename(columns={'stockcode': 'stock_code'}, inplace=True)
if 'invoicedate' in df.columns:
  df.rename(columns={'invoicedate': 'invoice_date'}, inplace=True)
if 'unitprice' in df.columns:
  df.rename(columns={'unitprice': 'unit_price'}, inplace=True)

df = df.dropna(subset=['customer_id'])
df['customer_id'] = df['customer_id'].astype(int).astype(str)
df['invoice_date'] = pd.to_datetime(df['invoice_date'])

# Select required standard columns
cols_to_keep = [
    'invoice_no',
    'stock_code',
    'description',
    'quantity',
    'invoice_date',
    'unit_price',
    'customer_id',
    'country',
]
df = df[[col for col in cols_to_keep if col in df.columns]]

# 4. Connect to MySQL & Push Data
# REPLACE 'YOUR_MYSQL_PASSWORD' WITH YOUR ACTUAL WORKBENCH PASSWORD
DB_USER = 'root'
DB_PASSWORD = 'YourNewPassword'  # <--- Update this!
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'ecommerce_analytics'

engine = create_engine(
    f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

print('Uploading data to MySQL table `raw_transactions`...')
df.to_sql(
    name='raw_transactions', con=engine, if_exists='replace', index=False
)

print(
    '🚀 Done! Dataset loaded successfully into MySQL database `ecommerce_analytics`.'
)