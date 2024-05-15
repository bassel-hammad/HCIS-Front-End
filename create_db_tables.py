
import psycopg2
from psycopg2 import Error
import psycopg2.extras
creation_query='''CREATE TABLE  IF NOT EXISTS Admins_accounts (
    UserName VARCHAR(50) PRIMARY KEY,
    Password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Patients (
    PatientID SERIAL PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
    SSN VARCHAR(30),
    DateOfBirth DATE NOT NULL,
    PatientImage VARCHAR(100),
    email VARCHAR(100) NOT NULL,
    UserName VARCHAR(50) UNIQUE,
    Password VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS Radiologist (
    RadiologistID SERIAL PRIMARY KEY,
    SSN VARCHAR(30),
    FullName VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    Bio TEXT,
    RadiologistImage VARCHAR(100),
    UserName VARCHAR(50) UNIQUE,
    Gender VARCHAR(6),
    Password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS ScanTypes (
    ScanTypeID SERIAL PRIMARY KEY,
    ScanTypeName VARCHAR(100) NOT NULL,
    Cost INT NOT NULL
);
CREATE TABLE IF NOT EXISTS InsuranceCompany (
    CompanyID SERIAL PRIMARY KEY,
    CompanyName VARCHAR(100),
    PhoneNumber VARCHAR(50) UNIQUE,
    Address VARCHAR(255),
    Website VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS InsurancePolicy (
    PolicyID SERIAL PRIMARY KEY,
    PolicyNumber VARCHAR(50),
    CompanyID INT REFERENCES InsuranceCompany(CompanyID),
    PatientID INT REFERENCES Patients(PatientID),
    PolicyStartDate DATE,
    PolicyEndDate DATE,
    DeductibleAmount INT,
    CopaymentAmount INT,
    MaxCoverageAmount INT,
    CopaymentMax INT,
    CONSTRAINT fk_patient FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);

CREATE TABLE IF NOT EXISTS ImagingReport (
    ReportID SERIAL PRIMARY KEY,
    PatientID INT REFERENCES Patients(PatientID),
    StudyType VARCHAR(50),
    StudyDate DATE,
    OrderingPhysician VARCHAR(150),
    RadiologistID INT,
    Image VARCHAR(100),
    ReportText TEXT,
    Impressions TEXT,
    Recommendations TEXT,
    CONSTRAINT fk_patient_report FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
    CONSTRAINT fk_radiologist_report FOREIGN KEY (RadiologistID) REFERENCES Radiologist(RadiologistID)
);


CREATE TABLE IF NOT EXISTS Appointments (
    AppointmentID SERIAL PRIMARY KEY,
    AppointmentDate DATE NOT NULL,
    PatientID INT REFERENCES Patients(PatientID),
    PhysicianID INT,
    Duration INTEGER,
    StartHour TIME NOT NULL,
    EndHour TIME NOT NULL,
    Purpose TEXT,
    Cost INT,
    CostAfterInsurance INT,
    ScanTypeID INT REFERENCES ScanTypes(ScanTypeID), -- Add ScanTypeID column
    CONSTRAINT fk_patient_appointment FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
    CONSTRAINT fk_physician FOREIGN KEY (PhysicianID) REFERENCES Radiologist(RadiologistID)
);

CREATE TABLE IF NOT EXISTS Prescription (
    PrescriptionID SERIAL PRIMARY KEY,
    PatientID INT REFERENCES Patients(PatientID),
    RadiologistID INT REFERENCES Radiologist(RadiologistID),
    MedicationName VARCHAR(100),
    Dosage VARCHAR(50),
    Frequency VARCHAR(50),
    Duration VARCHAR(50),
    Notes TEXT,
    CONSTRAINT fk_patient_prescription FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
    CONSTRAINT fk_radiologist_prescription FOREIGN KEY (RadiologistID) REFERENCES Radiologist(RadiologistID)
);

CREATE TABLE IF NOT EXISTS PatientCost (
    CostID SERIAL PRIMARY KEY,
    PatientID INT REFERENCES Patients(PatientID),
    Description VARCHAR(255),
    Amount INT,
    Date DATE,
    CONSTRAINT fk_patient_cost FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);

'''
# Defining database connection parameters
# Please replace the values with your own credentials.
db_params = {
    "host": "localhost",
    "database": "department", # The name of the database you want to use, it  should be already created in PostgreSQL
    "user": "postgres",#"your-username",
    "password": "root",#"your-password",
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
        cursor.execute(creation_query)
        connection.commit()


        try:
            cursor.execute("INSERT INTO Admins_accounts (UserName, Password) VALUES (%s, %s)", ('admin1', '1234'))
            connection.commit()
            print("Record inserted successfully.")
        except psycopg2.Error as e:
            connection.rollback()
            print("Error:", e)

        cursor.close()
        connection.close()
        print("Database connection closed.")