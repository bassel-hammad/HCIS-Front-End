import psycopg2
from psycopg2 import extras

# Defining database connection parameters
db_params = {
    "host": "localhost",
    "database": "department",  # Replace with your database name
    "user": "postgres",        # Replace with your username
    "password": "2929",        # Replace with your password
    "port": 5432               # Replace with your database port
}

# List of insurance companies to insert
insurance_companies = [
    ('Allianz Egypt Insurance Company', '0100 155 8505', 'Nile City Towers, North Tower, 25th Floor, Corniche El Nile, Ramlet Beaulac, Cairo, Egypt', 'www.allianz.com.eg'),
    ('MetLife Alico Egypt', '19999', '3 El-Sarayat St., 1st District, New Cairo, Cairo, Egypt', 'www.metlife.com.eg'),
    ('Suez Canal Insurance Company', '16060', '1 El Batal Ahmed Abdel Aziz St., Gameat Al Dowal Al Arabia St., Mohandessin, Giza, Egypt', 'www.suezcanalinsurance.com'),
    ('Arab Misr Insurance Group (GIG)', '19460', '16 Dr. Kamal El Tawil St., Mohandessin, Giza, Egypt', 'www.gig-egypt.com')
]

try:
    # Establishing a connection to the database
    connection = psycopg2.connect(**db_params)
    # Creating a cursor object to interact with the database
    cursor = connection.cursor()

    # Iterating over the list of insurance companies and inserting them into the database
    for company in insurance_companies:
        cursor.execute("""
            INSERT INTO InsuranceCompany (CompanyName, PhoneNumber, Address, Website)
            VALUES (%s, %s, %s, %s)
        """, company)
    
    # Committing the transaction
    connection.commit()
    print("Insurance companies inserted successfully.")

except (Exception, psycopg2.Error) as error:
    print(f"Error inserting insurance companies: {error}")

finally:
    # Closing the cursor and connection
    if connection:
        cursor.close()
        connection.close()
        print("Database connection closed.")
