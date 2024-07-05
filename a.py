import psycopg2

def execute_dt_command():
    try:
        # Connect to your PostgreSQL database
        connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="root",
            host="localhost",
            port="5432"
        )

        # Create a cursor to perform database operations
        cursor = connection.cursor()

        # Execute the \dt command as a SQL query
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        
        # Fetch all the tables
        tables = cursor.fetchall()
        
        # Print the tables
        print("Tables in the public schema:")
        for table in tables:
            print(table[0])

        # Close the cursor and connection
        cursor.close()
        connection.close()

    except psycopg2.Error as e:
        print("Error executing \dt command:", e)

if __name__ == "__main__":
    execute_dt_command()
