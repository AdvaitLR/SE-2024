import pandas as pd
from sqlalchemy import create_engine

df = pd.read_pickle(r"E:\SE-2024\server\model\dataframe.pkl")
df = df.rename(columns={'Rating': 'Analysed_Rating', 'Comment': 'Analysed_Review', 'Score': 'User_Rating', 'Review': 'User_Review', 'Time': 'Review_Time'})
df = df.iloc[[-1]]  # Select the last row and keep it as a DataFrame

# Establish a connection to your SQL database using Windows authentication
server_name = 'localhost\\SQLEXPRESS'
database_name = 'reviews'
table_name = 'python_reviews'

engine = create_engine(f'mssql+pyodbc://{server_name}/{database_name}?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes')

# Write the DataFrame to the SQL database table
df.to_sql(table_name, con=engine, if_exists='append', index=False)
