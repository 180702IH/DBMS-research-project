
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
        cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';")
        columns = cursor.fetchall()

        cursor.execute(f"SELECT indexname, indexdef FROM pg_indexes WHERE tablename = '{table_name}';")
        indexes = cursor.fetchall()

        cursor.execute(f"SELECT constraint_name, constraint_type FROM information_schema.table_constraints WHERE table_name = '{table_name}';")
        constraints = cursor.fetchall()

        # Fetch foreign keys and their references
        cursor.execute(f"""
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM
                information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
            WHERE
                constraint_type = 'FOREIGN KEY' AND tc.table_name = '{table_name}';
        """)
        foreign_keys = cursor.fetchall()

        # Print the table name, columns, indexes, constraints, and foreign keys
        print(f"Table: {table_name}")
        print("Columns:")
        for column in columns:
            print(f"\t{column[0]}: {column[1]}")
        
        print("Indexes:")
        for index in indexes:
            print(f"\t{index[0]}: {index[1]}")
        
        print("Constraints:")
        for constraint in constraints:
            print(f"\t{constraint[0]}: {constraint[1]}")

        print("Foreign Keys:")
        for fk in foreign_keys:
            print(f"\t{fk[0]}: {fk[1]} -> {fk[2]}({fk[3]})")

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
