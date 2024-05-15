from flask import Flask, render_template, request, redirect, session,flash,get_flashed_messages,url_for
import psycopg2
import os
import psycopg2.extras
from datetime import datetime,timedelta
import secrets
import string



app = Flask(__name__)
# Set the secret key
app.config['SECRET_KEY'] = '1234'

#folder for Radiologist profiles => images
DOC_IMG_FOLDER = 'static/doctors_images/'
app.config['UPLOAD_DOC_IMG']=DOC_IMG_FOLDER

# Defining database connection parameters  print(Radiologists[0])
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

import psycopg2

def calculate_payments(patient_id, scan_cost):
        # Check if the patient ID exists in the InsurancePolicy table
        cursor.execute("SELECT DeductibleAmount, CopaymentPercentage, CopaymentMax, MaxCoverageAmount FROM InsurancePolicy WHERE PatientID = %s", (patient_id,))
        insurance_record = cursor.fetchone()

        if insurance_record:
            # Patient has insurance, calculate payment after insurance

            deductible_amount, copayment_percentage, copayment_max, max_coverage_amount = insurance_record
            
            # Subtract deductible amount from scan cost
            remaining_cost = scan_cost - deductible_amount
            
            # Apply copayment
            if copayment_percentage > 0:
                copayment_amount = remaining_cost * (copayment_percentage / 100)
                copayment_amount = min(copayment_amount, copayment_max)
                patient_payment = remaining_cost - copayment_amount
            
            # Calculate insurance's payment
            insurance_payment = min(scan_cost - patient_payment, max_coverage_amount)
            
            # Update patient's payment based on insurance payment
            patient_payment = scan_cost - insurance_payment

            return patient_payment

        else:
            # Patient doesn't have insurance, return the scan cost
            return scan_cost
import psycopg2

def get_available_doctor(start_hour, appointment_date):
        # Query to get doctors who don't have appointments at the specified time
        cursor.execute("""
            SELECT RadiologistID 
            FROM Radiologist 
            WHERE RadiologistID NOT IN (
                SELECT PhysicianID 
                FROM Appointments 
                WHERE AppointmentDate = %s 
                AND StartHour = %s
            )
        """, (appointment_date, start_hour))
        available_doctors = cursor.fetchall()

        # Check if there are available doctors
        if len(available_doctors)==0:
            return None

        # Select the doctor with the minimum sum of durations
        min_sum_duration = float('inf')
        selected_doctor = None
        for row in available_doctors:
            row=dict(row)
            print(row)
            cursor.execute("""
                SELECT SUM(Duration) 
                FROM Appointments 
                WHERE AppointmentDate = %s 
                AND PhysicianID = %s
            """, (appointment_date, row["radiologistid"]))
            sum_duration = cursor.fetchone()[0] or 0  # If no appointments, sum_duration will be None
            if sum_duration < min_sum_duration:
                min_sum_duration = sum_duration
                selected_doctor = row["radiologistid"]

        return selected_doctor


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
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
            
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
                        return redirect("/patient")
                    elif userType=="Radiologist":
                        return redirect("/doctor")
                else:
                    Message="Wrong username or password"
                      
    print(Message)
    return render_template('login.html',message=Message)
@app.route('/admin',methods=['GET', 'POST'])
def admin():
    """Admin page"""
    if(session['userType']=="Admins_accounts"):
        Radiologists=find_all("Radiologist")

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






@app.route("/add_insurance", methods=["POST","GET"])
def add_insurance():
    msg=""
    if request.method == "POST":
        # Retrieve data from the form
        insurance_company = request.form["insuranceCompany"]
        policy_number = int(request.form["policyNumber"])
        policy_start_date_str = request.form["policyStartDate"]
        policy_end_date_str = request.form["policyEndDate"]
        deductible_amount = int(request.form["deductibleAmount"])
        copayment_amount = int(request.form["copaymentAmount"])
        max_coverage_amount = int(request.form["maxCoverageAmount"])
        copayment_max = int(request.form["copaymentMax"])
        
        # Convert date strings to datetime objects
        try:
            policy_start_date = datetime.datetime.strptime(policy_start_date_str, "%Y-%m-%d").date()
            policy_end_date = datetime.datetime.strptime(policy_end_date_str, "%Y-%m-%d").date()
        except ValueError:
            msg += "Invalid date format. Please use YYYY-MM-DD format for dates.\n"
        
        # Check if the policy end date is after the policy start date
        if policy_start_date >= policy_end_date:
            msg += "Policy end date must be after the policy start date.\n"
        
        # Validate other fields for negativity
        if deductible_amount < 0:
            msg += "Deductible amount cannot be negative.\n"
        if copayment_amount < 0:
            msg += "Copayment amount cannot be negative.\n"
        if max_coverage_amount < 0:
            msg += "Max coverage amount cannot be negative.\n"
        if copayment_max < 0:
            msg += "Copayment max amount cannot be negative.\n"
        
        if msg=="":
            
            query_to_get_patient_id = "SELECT PatientID FROM Patients WHERE UserName = %s"
            cursor.execute(query_to_get_patient_id, (session['username'],))
            patient_id = cursor.fetchone()
            if patient_id:
                patient_id = patient_id[0]
                # Save the data to the database
                insert_query = '''INSERT INTO InsurancePolicy (PolicyNumber, CompanyID, PatientID, PolicyStartDate, PolicyEndDate, DeductibleAmount, CopaymentAmount, MaxCoverageAmount, CopaymentMax)
                                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                cursor.execute(insert_query, (policy_number, insurance_company, patient_id, policy_start_date, policy_end_date, deductible_amount, copayment_amount, max_coverage_amount, copayment_max))
                # Commit the transaction
                connection.commit()
                msg = "Data added successfully"
    
    companies_data = find_all("InsuranceCompany")
    return render_template('add_insurance.html', message=msg, insurance_companies=companies_data)


@app.route('/patient')
def patient():
    # Retrieve patient data
    patient_query = "SELECT * FROM Patients WHERE UserName = %s"
    cursor.execute(patient_query, (session['username'],))
    patient =dict(cursor.fetchone())

    # Retrieve patient scans
    #scans_query = "SELECT * FROM Scans WHERE patient_id = %s"
    #cursor.execute(scans_query, (patient_id,))
    #scans = cursor.fetchall()

    return render_template('view_patient_info.html', patient=patient)



@app.route('/book_scan', methods=['POST','GET'])
def book_scan():
    msg=""
    _continue_=True
    if request.method == 'POST':
        # Retrieve form data
        scan_type = request.form['scanType']
        appointment_date = request.form['appointmentDate']
        start_hour = request.form['startHour']
        purpose = request.form['purpose']
        end_hour = int(start_hour) + 1
        duration = 1
        
        query_to_get_patient_id = "SELECT PatientID FROM Patients WHERE UserName = %s"
        cursor.execute(query_to_get_patient_id, (session['username'],))
        patient_id = cursor.fetchone()
        if patient_id:
            patient_id = patient_id[0]
        else:
            _continue_=False

        if scan_type != 'null':
            cursor.execute("SELECT Cost FROM ScanTypes WHERE ScanTypeID = %s", (scan_type,))
            # Fetch the result
            cost_row = cursor.fetchone()
        else:
            msg = msg+"Please select a scan type \n"
            _continue_=False

        # Check if the result exists
        if _continue_ and cost_row:
            # Extract the cost from the result
            cost = int(cost_row[0])
            cost_after_insurance = calculate_payments(patient_id, cost)

            doctor_id = get_available_doctor(start_hour, appointment_date)
            if doctor_id == None:
                msg = "No doctor available for this time"
                _continue_ = False

            if _continue_:
                end_hour = int(start_hour) + duration

                # Insert data into the Appointments table
                query = '''
                    INSERT INTO Appointments (ScanTypeID, AppointmentDate, PatientID, PhysicianID, Duration, StartHour, EndHour, Purpose, Cost, CostAfterInsurance) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''
                cursor.execute(query, (scan_type, appointment_date, patient_id, doctor_id, duration, start_hour, end_hour, purpose, cost, cost_after_insurance))

                # Commit the transaction
                connection.commit()
                msg = "Appointment created successfully"

    query = "SELECT * FROM Appointments WHERE PatientID = %s;"

    # Execute the SQL query with the patient ID as parameter
    cursor.execute(query, (patient_id,))

    # Fetch all the results
    appointments = cursor.fetchall()
    patient_appointments = [dict(row) for row in appointments]
    # Render a success or confirmation page
    return render_template('patient_appointments.html', patient=patient,msg=msg,appointments=patient_appointments)


@app.route('/doctor')
def doctor():
    patient_query = "SELECT * FROM Radiologist WHERE UserName = %s"
    cursor.execute(patient_query, (session['username'],))
    radiologist =dict(cursor.fetchone())
    print(radiologist)
    # Render the HTML template for the doctor's dashboard
    return render_template('Radiologydoctor.html',doctor=radiologist)



@app.route('/my_calendar', methods=['GET', 'POST'])
def my_calendar():
    if request.method == 'POST':
        date = request.form['appointment_date']
        if  date:
            pass
        else:
            return render_template('calendar.html')

        doctor_query = "SELECT * FROM Radiologist WHERE UserName = %s"
        cursor.execute(doctor_query, (session['username'],))
        radiologist =dict(cursor.fetchone())
        date = request.form['appointment_date']
        query = '''
            SELECT a.Purpose, a.AppointmentDate, a.StartHour, a.EndHour, p.FullName
            FROM Appointments a
            INNER JOIN Patients p ON a.PatientID = p.PatientID
            WHERE a.AppointmentDate = %s AND a.PhysicianID = %s
        '''
        cursor.execute(query, (date,radiologist['radiologistid']))
        appointments = cursor.fetchall()
        data = [dict(row) for row in appointments]
        print(len(data))
        print(data)
        return render_template('appointments.html', appointments=data, date=date)
    return render_template('calendar.html')

@app.route('/my_patients', methods=['GET', 'POST'])
def my_patients():
    return render_template("my_patinents.html",doctor={1,2,3,4,5})

if __name__ == "__main__":
    app.run()