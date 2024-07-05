import psycopg2

class TableColumn:
    def __init__(self, name, data_type, not_null):
        self.name = name
        self.data_type = data_type
        self.not_null = not_null

class TableInfo:
    def __init__(self, name):
        self.name = name
        self.columns = []  # List to store TableColumn objects
        self.primary_keys = []  # List to store primary key column names
        self.foreign_keys = {}  # Dictionary to store foreign key column names and referenced table
        self.uniques = {}  # Dictionary to store unique constraint column names
        self.not_nulls = []  # List to store not null constraint column names

    def add_column(self, name, data_type, not_null):
        column = TableColumn(name, data_type, not_null)
        self.columns.append(column)
        if not_null:
            self.not_nulls.append(name)

    def add_primary_key(self, column_name):
        self.primary_keys.append(column_name)

    def add_foreign_key(self, column_name, referenced_table, referenced_column):
        self.foreign_keys[column_name] = {"referenced_table": referenced_table, "referenced_column": referenced_column}

    def add_unique(self, constraint_name, column_name):
        if constraint_name in self.uniques:
            self.uniques[constraint_name].append(column_name)
        else:
            self.uniques[constraint_name] = [column_name]

    # No need to change add_not_null method

def get_table_info(table_name, dbname, user, password, host, port):
    table_info = TableInfo(table_name)

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
        cursor.execute(f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{table_name}';")
        columns = cursor.fetchall()

        cursor.execute(f"SELECT constraint_name, constraint_type FROM information_schema.table_constraints WHERE table_name = '{table_name}';")
        constraints = cursor.fetchall()

        # Fetch foreign keys and their references
        cursor.execute(f"""
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS referenced_table,
                ccu.column_name AS referenced_column
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

        # Populate table_info with fetched data
        for column in columns:
            not_null = True if column[2] == 'NO' else False
            table_info.add_column(column[0], column[1], not_null)

        for constraint in constraints:
            if constraint[1] == 'PRIMARY KEY':
                # Fetch primary key column names
                cursor.execute(f"SELECT column_name FROM information_schema.key_column_usage WHERE constraint_name = '{constraint[0]}';")
                primary_key_columns = cursor.fetchall()
                for pk_column in primary_key_columns:
                    table_info.add_primary_key(pk_column[0])
            elif constraint[1] == 'UNIQUE':
                # Fetch unique constraint column names
                cursor.execute(f"SELECT column_name FROM information_schema.constraint_column_usage WHERE constraint_name = '{constraint[0]}';")
                unique_columns = cursor.fetchall()
                for uc_column in unique_columns:
                    table_info.add_unique(constraint[0], uc_column[0])

        for fk in foreign_keys:
            table_info.add_foreign_key(fk[1], fk[2], fk[3])

        # Close the cursor and connection
        cursor.close()
        connection.close()

    except psycopg2.Error as e:
        print(f"Error fetching table info for {table_name}:", e)

    return table_info

def main():
    dbname = "postgres"
    user = "postgres"
    password = "root"
    host = "localhost"
    port = "5432"

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
        
        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Print the tables
        print("Tables in the public schema:")
        for table in tables:
            table_name = table[0]
            table_info = get_table_info(table_name, dbname, user, password, host, port)
            print(f"\nTable Name: {table_info.name}")
            print("Columns:")
            for column in table_info.columns:
                print(f"\tName: {column.name}, Type: {column.data_type}, Not Null: {column.not_null}")
            print("Primary Keys:", table_info.primary_keys)
            print("Foreign Keys:")
            for column_name, fk_info in table_info.foreign_keys.items():
                print(f"\t{column_name} -> {fk_info['referenced_table']}({fk_info['referenced_column']})")
            print("Unique Constraints:")
            for constraint_name, columns in table_info.uniques.items():
                print(f"\t{constraint_name}: {', '.join(columns)}")
            print("Not Null Constraints:", table_info.not_nulls)

    except psycopg2.Error as e:
        print("Error executing \dt command:", e)

if __name__ == "__main__":
    main()
