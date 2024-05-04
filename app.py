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
    if request.method == 'POST':
        check_create = 'create' in request.form
        check_sign = 'sign' in request.form
        if check_create:
            username = request.form['username1']
            print(username)
            ssn=request.form['ssn']
            print(ssn)
            name=request.form['fullname']
            print(name)
            email=request.form['email']
            print(email)
            password=request.form['password1']
            print(password)
            birthdate_str=request.form['birthdate']
            print(birthdate_str)
            # Convert date string to datetime object
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')
            print(birthdate)
            if username:
                query_check_username_uniqueness ="SELECT UserName FROM Patients WHERE UserName=%s"
                cursor.execute(query_check_username_uniqueness, (username,))
                if cursor.fetchone():
                    message = 'Change the username because it is already used'
                else:
                    query_insert_patient='''
                    INSERT INTO Patients(FullName,SSN,DateOfBirth,email,UserName,Password) VALUES(%s,%s,%s,%s,%s,%s)
                                                                                                                    '''
                    cursor.execute(query_insert_patient,(name,ssn,birthdate,email,username,password))
                    connection.commit()
                    message="Account successfully created"
    
    return render_template('login.html')