from flask import Flask, render_template, request, url_for
import pyodbc
import os
from flask import jsonify

app = Flask(__name__)

serverName = "localhost\\SQLEXPRESS"
databaseName = "reviews"

# Connection string with Trusted_Connection=yes for Windows Authentication
conn_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={serverName};DATABASE={databaseName};Trusted_Connection=yes"

try:
    conn = pyodbc.connect(conn_string)
    print("Connected to database successfully!")
except pyodbc.Error as ex:
    print("Database connection error:", ex)
    exit()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/search')
def search():
    return render_template("search.html")

@app.route('/review')
def review():
    return render_template("review.html")

@app.route('/submit_review', methods=['POST'])
def submit_review():
    if request.method == 'POST':
        movie_name = request.form['movie_name']
        rating = request.form['rate']
        comment = request.form['message']
        
        print(movie_name,rating,comment)
        
        cursor = conn.cursor()
        cursor.execute("INSERT INTO html_reviews (Movie_Name, Review, Score) VALUES (?, ?, ?)", (movie_name, comment, rating))
        conn.commit()
        
        os.system("python E:\\SE-2024\\server\\model\\Roberta.py")
        os.system("python E:\\SE-2024\\server\\database\\python_sql.py")
        
        return render_template("success.html")  # Render success template after storing in database

    return render_template("invalid.html")  # Render invalid template for invalid request method

@app.route('/display')
def display():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM python_reviews")  # Assuming review_table is your SQL table name
    data = cursor.fetchall()
    return render_template("display.html", data=data, url_for=url_for)


if __name__ == '__main__':
    app.run(debug=True) 