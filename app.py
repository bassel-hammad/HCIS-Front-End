from flask import Flask, render_template, request, redirect, session,flash,get_flashed_messages
import psycopg2
import os
import psycopg2.extras
from datetime import datetime
import secrets
import string

app = Flask(__name__)

# Defining database connection parameters
# Please replace the values with your own credentials.
db_params = {
    "host": "localhost",
    "database": "department", # The name of the database you want to use, it  should be already created in PostgreSQL
    "user": "postgres",#"your-username",
    "password": "2929",#"your-password",
    "port":5432
}
try:
    # Establishing a connection to the database
    connection = psycopg2.connect(**db_params)
    # Creating a cursor object to interact with the database
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Performing database operations here...
except (Exception, psycopg2.Error) as error:
    print(f"Error connecting to the database: {error}")

finally:
    if connection:
        print("Database")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    message=''
    return render_template('sign_in.html', msg=message)