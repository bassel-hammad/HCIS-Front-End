import psycopg2

# Database connection parameters
db_params = {
    "host": "localhost",
    "database": "department",
    "user": "postgres",
    "password": "bassel2003",
    "port": 5432
}

try:
    # Establishing a connection to the database
    connection = psycopg2.connect(**db_params)
    # Creating a cursor object to interact with the database
    cursor = connection.cursor()

    # SQL statement to insert initial data into the ScanTypes table
    sql_insert = """
    INSERT INTO ScanTypes (ScanTypeName, Cost) 
    VALUES 
        ('MRI', 400),
        ('CT Scan', 300),
        ('PET Scan', 500),
        ('UltraSound Scan', 200);
    """

    # Execute the SQL statement
    cursor.execute(sql_insert)

    # Commit the transaction
    connection.commit()

    print("Data inserted successfully!")

except (Exception, psycopg2.Error) as error:
    print(f"Error inserting data: {error}")

finally:
    # Close the cursor and connection
    if connection:
        cursor.close()
        connection.close()
