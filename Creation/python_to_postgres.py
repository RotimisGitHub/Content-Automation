import logging
from pprint import pprint
import psycopg2


host = "localhost"
database = "reddit"
username = "postgres"
pwd = "U24tuc9r"
port_no = 5432


class PostgresClass:
    def __init__(self):
        # Establish Connection to Database using correct credentials.
        self.db_connection = psycopg2.connect(
            host=host,
            dbname=database,
            user=username,
            password=pwd,
            port=port_no
        )
        # open a cursor which allows you to query your database (Kind of like a tool a
        # librarian would give you to look for
        # books in a library)
        self.cursor = self.db_connection.cursor()

    @staticmethod
    def postgres_decorator(enable_commit=False):
        def decorator(func):
            def wrapper(*args, **kwargs):
                self = args[0]
                try:

                    result = func(*args, **kwargs)

                    # Commit changes if needed
                    if enable_commit:
                        self.db_connection.commit()

                    return result

                except Exception as e:
                    logging.exception(e)

                finally:
                    if not kwargs.get("keep_connection", False):
                        if self.cursor and not self.cursor.closed:
                            self.cursor.close()
                        if self.db_connection and not self.db_connection.closed:
                            self.db_connection.close()

            return wrapper

        return decorator


class PGHandler(PostgresClass):
    def __init__(self, table_name):
        super().__init__()
        self.table_name = table_name

    @PostgresClass.postgres_decorator(enable_commit=False)
    def retrieve_tables_from_database(self, **kwargs):
        self.cursor.execute("""
                SELECT table_name, column_name, data_type, character_maximum_length, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public';
            """)
        # Fetch all the rows from the query result
        table_info = self.cursor.fetchall()

        column_counter = 0

        database_dict = []
        while column_counter != len(table_info):
            table_name = table_info[column_counter][0]

            matches = None
            column_list = []
            table = {
                "Table Name": table_name,

            }
            for row in table_info:
                if row[0] == table_name:
                    table_columns = {

                        "Name": row[1],
                        "Datatype": row[2],
                        "Character Limit": row[3],
                        "Nullable": row[4]

                    }

                    column_list.append(table_columns)
                    matches = len([row[0] for row in table_info if row[0] == table_name])

            table["Columns"] = column_list
            column_counter += matches
            database_dict.append(table)

        pprint(database_dict)

        return database_dict

    @PostgresClass.postgres_decorator(enable_commit=False)
    def retrieve_table_info(self, **kwargs):

        self.cursor.execute(f"""
                SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = '{self.table_name}';
            """)

        # Fetch all the rows from the query result
        table_info = self.cursor.fetchall()

        table_dictionary = {
            "Table Name": self.table_name,
        }
        list_of_row_properties = []
        for column in table_info:
            list_of_row_properties.append({
                "Column Name": column[0],
                "Datatype": column[1],
                "Character Max": column[2],
                "Nullable": column[3]
            })
        table_dictionary["Column Information"] = list_of_row_properties
        pprint(table_dictionary)

        return table_dictionary

    @PostgresClass.postgres_decorator(enable_commit=True)
    def insert_to_table(self, *data, **kwargs):

        table_info = self.retrieve_table_info(keep_connection=True)
        table_columns = [i['Column Name'] for i in table_info['Column Information']]

        #  This insert script enables me to insert data into my desired columns,
        #  without being constrained to a certain amount of columns

        placeholders = ', '.join(['%s'] * len(table_columns))

        insert_script = (f"""
                INSERT INTO {self.table_name} ({
        ', '.join(table_columns)
        }) VALUES ({placeholders});
                """)

        self.cursor.execute(insert_script, data)
        result = self.cursor.rowcount
        if result == 1:

            print(f"Successfully applied data into {self.table_name}")
            return result


    @PostgresClass.postgres_decorator(enable_commit=False)
    def field_checker(self, column=None, desired_field=None, **kwargs):

        if column is not None:

            insert_script = f"SELECT {column} FROM {self.table_name}"
        else:
            insert_script = f"SELECT * FROM {self.table_name}"

        if desired_field:
            insert_script = insert_script + f"WHERE {column} = '{desired_field}'"

        self.cursor.execute(insert_script)
        result = [i[0] for i in self.cursor.fetchall()]
        none_calculator = []
        for output in result:
            if output is None:
                none_calculator.append(0)
            else:
                none_calculator.append(1)

        if sum(none_calculator) == 0:
            result = None

        return result

