import pandas as pd
from sqlalchemy import create_engine

"""
This script sets up the SQLite database using the CSV files given in the problem statement. 

Usage:
Run this script first before launching the app to ensure the database is set up.
python setup_database.py
"""

# Load CSV files
merchants_df = pd.read_csv('merchants_2024_06_20.csv')
transactions_df = pd.read_csv('transactions_2024_06_20.csv')

# Create SQLite database
engine = create_engine('sqlite:///neobank.db')

# Save dataframes to SQL tables
merchants_df.to_sql('merchants', engine, index=False, if_exists='replace')
transactions_df.to_sql('transactions', engine, index=False, if_exists='replace')

print("Database setup complete.")

