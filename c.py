import psycopg2

def execute_d_command(table_name, dbname, user, password, host, port):
    try:
        # Connect to your PostgreSQL database
        connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )

        # Create a cursor to perform database operations
        cursor = connection.cursor()

        # Execute queries to fetch table information
        cursor.execute(f"SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';")
        columns = cursor.fetchall()

        cursor.execute(f"SELECT indexname, indexdef FROM pg_indexes WHERE tablename = '{table_name}';")
        indexes = cursor.fetchall()

        cursor.execute(f"SELECT constraint_name, constraint_type FROM information_schema.table_constraints WHERE table_name = '{table_name}';")
        constraints = cursor.fetchall()

        # Print the table name, columns, indexes, and constraints
        print(f"Table: {table_name}")
        print("Columns:")
        for column in columns:
            print(f"\t{column[1]}: {column[2]}")
        
        print("Indexes:")
        for index in indexes:
            print(f"\t{index[0]}: {index[1]}")
        
        print("Constraints:")
        for constraint in constraints:
            print(f"\t{constraint[0]}: {constraint[1]}")

        # Close the cursor and connection
        cursor.close()
        connection.close()

    except psycopg2.Error as e:
        print(f"Error executing \d command for table {table_name}:", e)

def execute_dt_command(dbname, user, password, host, port):
    try:
        # Connect to your PostgreSQL database
        connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
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
            table_name = table[0]
            execute_d_command(table_name, dbname, user, password, host, port)

        # Close the cursor and connection
        cursor.close()
        connection.close()

    except psycopg2.Error as e:
        print("Error executing \dt command:", e)

if __name__ == "__main__":
    dbname = "postgres"
    user = "postgres"
    password = "root"
    host = "localhost"
    port = "5432"
    execute_dt_command(dbname, user, password, host, port)
