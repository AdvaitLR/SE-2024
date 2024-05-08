#Importing various Python Libraries

import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from tqdm import tqdm
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from scipy.special import softmax
from tqdm.notebook import tqdm
import pyodbc
import pickle
from sqlalchemy import create_engine

#Connecting to local database

serverName = "localhost\\SQLEXPRESS"
databaseName = "reviews"
conn_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={serverName};DATABASE={databaseName};Trusted_Connection=yes"
engine = create_engine(f'mssql+pyodbc://{serverName}/{databaseName}?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes')

try:
    conn = pyodbc.connect(conn_string)
    print("Connected to database successfully!")
except pyodbc.Error as ex:
    print("Database connection error:", ex)
    exit()

# Query to select data from the Reviews table
query = "SELECT * FROM html_reviews"

# Read data from the database into a pandas DataFrame
df = pd.read_sql(query, con=engine)
df=df.iloc[[-1]]

# Load the tokenizer and model from the local cache
tokenizer = AutoTokenizer.from_pretrained("E:\\SE-2024\\server\\model\\tokenizer_cache")
model = AutoModelForSequenceClassification.from_pretrained("E:\\SE-2024\\server\\model\\model_cache")

#Function to calculate the model parameters

def polarity_scores_roberta(example):
    encoded_text = tokenizer(example, return_tensors='pt')
    output = model(**encoded_text)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    scores = scores
    scores_dict = {
        'roberta_neg': scores[0],
        'roberta_neu': scores[1],
        'roberta_pos': scores[2]
    }
    return scores_dict

#Dictionary to store the values returned by the function

res={}
for i, row in tqdm(df.iterrows(), total=len(df)):
    try:
        text = row['Review']
        myid = row['Review_Id']
        roberta_result = polarity_scores_roberta(text)        
        res[myid] = roberta_result
    except RuntimeError:
        print(f'Broke for id {myid}')

#Reforming the DataFrame

roberta_df = pd.DataFrame(res).T
roberta_df = roberta_df.reset_index().rename(columns={'index':'Review_Id'})
roberta_df = roberta_df.merge(df, how='left')

#Enhancing the model parameters to a simpler class 

# Initialize lists to store data
data = {'Review_Id': [], 'r_neg': [], 'r_pos': [], 'r_neu': [], 'Rating': [], 'Comment': []}

for i, row in tqdm(roberta_df.iterrows(), total=len(roberta_df)):
    r_neg = roberta_df['roberta_neg'][i]
    r_pos = roberta_df['roberta_pos'][i]
    r_neu = roberta_df['roberta_neu'][i]
    
    if r_neg >= 0.85:
        rating = 1
        com='Horrible'
    elif r_pos >= 0.85:
        rating = 5
        com='Fantastic'
    elif 0.65 <= r_pos < 0.85:
        rating = 4
        com='Good'
    elif 0.65 <= r_neg < 0.85:
        rating = 2
        com='Bad'
    else:
        rating = 3
        com='Average'
    
    my_id = row['Review_Id']  # Extract 'Id' from the current row
    
    # Append data to lists
    data['Review_Id'].append(my_id)
    data['r_neg'].append(r_neg)
    data['r_pos'].append(r_pos)
    data['r_neu'].append(r_neu)
    data['Rating'].append(rating)  
    data['Comment'].append(com)
# Create a DataFrame from the collected data
max_df = pd.DataFrame(data)

#Making a single DataFrame 

# Merge DataFrames on index
display_df = pd.merge(max_df, roberta_df, left_index=False, right_index=False, how='inner')


# List of unwanted columns in df1
unwanted_columns_merged = ['r_neg', 'r_pos', 'r_neu',
                            'roberta_neg', 'roberta_pos', 'roberta_neu',]

# Drop unwanted columns from df1
display_df = display_df.drop(unwanted_columns_merged, axis=1)

column_order = ['Review_Id', 'Movie_Name', 'Rating', 'Comment', 'Score', 'Review', 'Review_Time']

display_df=display_df[column_order]

#Converting DataFrame to pickle file for database updation

display_df.to_pickle(r"E:\SE-2024\server\model\dataframe.pkl")