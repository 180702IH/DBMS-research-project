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

        # Initialize a dictionary to store table information
        table_info = {
            "Table": table_name,
            "Columns": [],
            "Indexes": [],
            "Constraints": [],
            "Foreign_Keys": []
        }

        # Execute queries to fetch table information
        cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';")
        columns = cursor.fetchall()
        for column in columns:
            table_info["Columns"].append({"Column": column[0], "Data_Type": column[1]})
        
        cursor.execute(f"SELECT indexname, indexdef FROM pg_indexes WHERE tablename = '{table_name}';")
        indexes = cursor.fetchall()
        for index in indexes:
            table_info["Indexes"].append({"Index": index[0], "Definition": index[1]})
        
        cursor.execute(f"SELECT constraint_name, constraint_type FROM information_schema.table_constraints WHERE table_name = '{table_name}';")
        constraints = cursor.fetchall()
        for constraint in constraints:
            table_info["Constraints"].append({"Constraint": constraint[0], "Type": constraint[1]})

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
        for fk in foreign_keys:
            table_info["Foreign_Keys"].append({"Constraint": fk[0], "Column": fk[1], "Foreign_Table": fk[2], "Foreign_Column": fk[3]})

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return table_info

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
        
        # Initialize a list to store table information dictionaries
        table_info_list = []

        # Print the tables
        print("Tables in the public schema:")
        for table in tables:
            table_name = table[0]
            table_info = execute_d_command(table_name, dbname, user, password, host, port)
            table_info_list.append(table_info)

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return table_info_list

    except psycopg2.Error as e:
        print("Error executing \dt command:", e)

if __name__ == "__main__":
    dbname = "postgres"
    user = "postgres"
    password = "root"
    host = "localhost"
    port = "5432"
    tables_info = execute_dt_command(dbname, user, password, host, port)
    print(tables_info)
