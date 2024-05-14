from flask import Flask, render_template, request, redirect, session,flash,get_flashed_messages,url_for
import psycopg2
import os
import psycopg2.extras
from datetime import datetime
import secrets
import string

app = Flask(__name__)
# Set the secret key
app.config['SECRET_KEY'] = '1234'

#folder for Radiologist profiles => images
DOC_IMG_FOLDER = 'static/doctors_images/'
app.config['UPLOAD_DOC_IMG']=DOC_IMG_FOLDER

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

def find_all(table_name):
    "Returns all rows in specified table."
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    result=cursor.fetchall()
    data = [dict(row) for row in result]
    return data

def get_var_name(var):
    for name, value in locals().items():
        if value is var:
            return name

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    Message=''
    if request.method == 'POST':
        check_create = 'create' in request.form
        check_sign = 'sign' in request.form
        if (not (check_create or check_sign)  or (check_create and check_sign)):
            Message = 'Please select Sign In or Sign Up'
        elif check_create:
            username = request.form['username1']
            ssn=request.form['ssn']
            name=request.form['fullname']
            email=request.form['email']
            password=request.form['password1']
            birthdate_str=request.form['birthdate']
            # Convert date string to datetime object
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')
            if username:
                query_check_username_uniqueness ="SELECT UserName FROM Patients WHERE UserName=%s"
                cursor.execute(query_check_username_uniqueness, (username,))
                if cursor.fetchone():
                    Message = 'Change the username because it is already used'
                else:
                    query_insert_patient='''
                    INSERT INTO Patients(FullName,SSN,DateOfBirth,email,UserName,Password) VALUES(%s,%s,%s,%s,%s,%s)
                                                                                                                    '''
                    cursor.execute(query_insert_patient,(name,ssn,birthdate,email,username,password))
                    connection.commit()
                    Message="Account successfully created"
        elif check_sign:
            username=request.form["username2"]
            password=request.form["password2"]
            userType=request.form["userType"]
            if userType == "null":
                Message="Please select the account type"
            elif username and password and userType:
                cursor.execute('SELECT * FROM ' + userType+ ' WHERE UserName=%s AND Password=%s', (username, password))
                if cursor.fetchone():
                    session['username']=username
                    session['userType']=userType
                    if userType=="Admins_accounts":
                        return redirect("/admin")
                    elif userType=="Patients":
                        return redirect("//patient")
                    elif userType=="Radiologist":
                        return "HEllO IN DOCTOR PAGE"
                else:
                    Message="Wrong username or password"
                      
    print(Message)
    return render_template('login.html',message=Message)
@app.route('/admin',methods=['GET', 'POST'])
def admin():
    """Admin page"""
    if(session['userType']=="Admins_accounts"):
        Radiologists=find_all("Radiologist")
        print(Radiologists[0])
        return render_template("admin2.html",doctors=Radiologists)
    else:
        return redirect("/")  #if not logged in as an Admin go to home page
    


@app.route('/add_doctor',methods=['POST'])
def add_doctor():
    Message=""
    """Admin page"""
    if(session['userType']=="Admins_accounts"):
        if request.method == "POST":
            username = request.form['user_name']
            print(username)
            ssn=request.form['ssn']
            print(ssn)
            name=request.form['full_name']
            print(name)
            email=request.form['email']
            print(email)
            password=request.form['password']
            print(password)
            gender=request.form['Gender']
            print(gender)
            
            if username:
                query_check_username_uniqueness ="SELECT UserName FROM Radiologist WHERE UserName=%s"
                cursor.execute(query_check_username_uniqueness, (username,))
                if cursor.fetchone():
                    Message = 'username is already used'
                    
                else:
                    if ssn:
                        query_check_ssn_uniqueness ="SELECT SSN FROM Radiologist WHERE SSN=%s"
                        cursor.execute(query_check_ssn_uniqueness, (ssn,))
                        if cursor.fetchone():
                            Message = 'SSN is already used'
                        else:
                            #SSN  => ENTERED,UNIQUE   AND USERNAME => ENTERED,UNIQUE 
                            query_insert_doctor="INSERT INTO Radiologist(FullName,SSN,email,UserName,Password,Gender) VALUES(%s,%s,%s,%s,%s,%s)"                                                                                                  
                            cursor.execute(query_insert_doctor,(name,ssn,email,username,password,gender))
                            connection.commit()
                            Message="Account successfully created"
                            #That part is for the profile picture
                            if 'profile_image' in request.files:
                                radiologist_image=request.files['profile_image']
                                if radiologist_image.filename:
                                    file_data=radiologist_image.filename.split(".")
                                    filename=username+"."+file_data[1]
                                    file_path=os.path.join(app.config['UPLOAD_DOC_IMG'],filename)
                                    radiologist_image.save( os.path.join(app.config['UPLOAD_DOC_IMG'] ,filename) )
                                    #save file path in database
                                    update_img_query="UPDATE Radiologist SET RadiologistImage=%s where UserName=%s "
                                    cursor.execute(update_img_query,(file_path,username))
                                    connection.commit()
                    else: Message="ENTER SSN"
            else: Message="ENTER Username"
            Radiologists=find_all("Radiologist")
            return render_template('admin2.html',message=Message,doctors=Radiologists)
    else:
        return redirect("/")  #if not logged in as an Admin go to home page


@app.route("/edit_doctor",methods=['POST','GET'])
def edit_doctor():
    if request.method=='GET':
        # Get the value of the 'doctor_id' parameter from the URL
        doctor_id = request.args.get('doctor_id')
        msg=request.args.get('msg')
        if msg is None:
            msg=''
        cursor.execute('SELECT * FROM  Radiologist WHERE RadiologistID=%s' , (doctor_id, ))
        data = cursor.fetchone()
        doctor = dict(data)
        return render_template('edit_doctor.html',doctor=doctor,message=msg)
    if request.method=='POST':
        doctor_id=request.form['doctor_id']
        username = request.form['user_name']
        ssn=request.form['ssn']
        name=request.form['full_name']
        email=request.form['email']
        password=request.form['password']
        query_update_doctor = """
        UPDATE Radiologist 
        SET FullName = %s, SSN = %s, email = %s, UserName = %s, Password = %s
        WHERE RadiologistID = %s"""
        cursor.execute(query_update_doctor, (name, ssn, email, username, password, doctor_id))
        connection.commit()
        msg="The data has been updated successfully"
        return redirect(url_for('edit_doctor', doctor_id=doctor_id, msg=msg))
        
   


#delete_doctor_route
@app.route("/delete_doctor_route")
def delete_doctor_route():
    # Get the value of the 'doctor_id' parameter from the URL
    doctor_id = request.args.get('doctor_id')
    # Delete the doctor from the database
    cursor.execute('DELETE FROM Radiologist WHERE RadiologistID = %s', (doctor_id,))
    connection.commit()
    return redirect(url_for('admin'))



@app.route("/patient")
def patient():
    return render_template('add_insurance.html')
    return render_template('patient.html',patient=[1,2,3,4,5,6,7])


@app.route("/add_insurance", methods=["POST","GET"])
def add_insurance():
    msg=""
    if request.method == "POST":
        # Retrieve data from the form
        insurance_company = request.form["insuranceCompany"]
        policy_number = request.form["policyNumber"]
        policy_start_date = request.form["policyStartDate"]
        policy_end_date = request.form["policyEndDate"]
        deductible_amount = request.form["deductibleAmount"]
        copayment_amount = request.form["copaymentAmount"]
        max_coverage_amount = request.form["maxCoverageAmount"]
        copayment_max = request.form["copaymentMax"]
        if (deductible_amount<0):
            msg+='Deductible amount cannot be negative \n '
        if (copayment_amount<0):
            msg+="copayment amount cannot  be negative \n"
        if (max_coverage_amount<0):
            msg+="max covrage  cannot  be negative \n"
        if (copayment_max<0):
            msg+="max copayment  cannot  be negative \n"
        if msg == "":      
            query_to_get_patient_id="SELECT PatientID FROM Patients WHERER  UserName=%s"
            cursor.execute(query_to_get_patient_id, (session['username'],))
            patient_id=cursor.fetchone()
            if patient_id:
                patient_id=patient_id[0]
            # Save the data to the database (you need to implement this part)
                insert_query = '''INSERT INTO InsurancePolicy ( PolicyNumber, CompanyID, PatientID, PolicyStartDate, PolicyEndDate, DeductibleAmount, CopaymentAmount, MaxCoverageAmount, CopaymentMax)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            '''
                cursor.execute(insert_query, (policy_number, insurance_company, patient_id, policy_start_date, policy_end_date, deductible_amount, copayment_amount, max_coverage_amount, copayment_max))

                # Commit the transaction
                connection.commit()
                msg="Data added successfully"
    companies_data=find_all("InsuranceCompany")
    print(companies_data)
    return render_template('add_insurance.html',message=msg,insurance_companies=companies_data)
if __name__ == "__main__":
    app.run()