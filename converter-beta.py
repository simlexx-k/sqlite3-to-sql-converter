import sqlite3
import re
import argparse
from datetime import datetime

class SQLiteToSQLConverter:
    def __init__(self, sqlite_file, output_file, target_db='mysql', conversion_type='both'):
        self.sqlite_file = sqlite_file
        self.output_file = output_file
        self.target_db = target_db
        self.conversion_type = conversion_type
        self.conn = None
        self.cursor = None
        self.table_count = 0
        self.row_count = 0

    def connect_to_sqlite(self):
        self.conn = sqlite3.connect(self.sqlite_file)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def get_table_names(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        return [table[0] for table in self.cursor.fetchall()]

    def get_create_table_statement(self, table_name):
        self.cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
        return self.cursor.fetchone()[0]

    def convert_create_table_statement(self, create_statement):
        # Extract table name
        table_name = re.search(r'CREATE TABLE (?:IF NOT EXISTS )?"?([^\s("]+)"?', create_statement).group(1)
        
        # Add IF NOT EXISTS clause
        create_statement = create_statement.replace('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS')
        
        # Remove double quotes around table and column names
        create_statement = create_statement.replace('"', '`')
        
        # Convert SQLite types to MySQL types
        create_statement = create_statement.replace('integer NOT NULL PRIMARY KEY AUTOINCREMENT', 'INT AUTO_INCREMENT PRIMARY KEY')
        create_statement = create_statement.replace('integer', 'INT')
        create_statement = create_statement.replace('DATETIME', 'DATETIME')
        create_statement = create_statement.replace('TEXT', 'TEXT')
        create_statement = create_statement.replace('REAL', 'DOUBLE')
        
        # Remove any remaining AUTOINCREMENT keywords
        create_statement = create_statement.replace('AUTOINCREMENT', '')
        
        # Add MySQL-specific table options
        create_statement = create_statement.rstrip(');')
        create_statement += ') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;'
        
        return create_statement

    def get_insert_statements(self, table_name):
        self.cursor.execute(f"SELECT * FROM `{table_name}`;")
        rows = self.cursor.fetchall()
        columns = [description[0] for description in self.cursor.description]

        insert_statements = []
        for row in rows:
            values = []
            for value in row:
                if value is None:
                    values.append('NULL')
                elif isinstance(value, (int, float)):
                    values.append(str(value))
                elif isinstance(value, str):
                    values.append(f"'{value.replace("'", "''")}'")
                elif isinstance(value, datetime):
                    values.append(f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'")
                else:
                    values.append(f"'{str(value)}'")
            
            insert_statement = f"INSERT IGNORE INTO `{table_name}` ({', '.join(f'`{col}`' for col in columns)}) VALUES ({', '.join(values)});"
            insert_statements.append(insert_statement)

        return insert_statements

    def convert(self):
        self.connect_to_sqlite()
        table_names = self.get_table_names()
        self.table_count = len(table_names)

        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(f"-- Converted from SQLite to {self.target_db.upper()} on {datetime.now()}\n\n")
            f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")

            for table_name in table_names:
                print(f"Processing table: {table_name}")
                
                if self.conversion_type in ['both', 'tables']:
                    create_statement = self.get_create_table_statement(table_name)
                    converted_create_statement = self.convert_create_table_statement(create_statement)
                    f.write(f"{converted_create_statement}\n\n")

                if self.conversion_type in ['both', 'data']:
                    insert_statements = self.get_insert_statements(table_name)
                    for insert_statement in insert_statements:
                        f.write(f"{insert_statement}\n")
                    self.row_count += len(insert_statements)
                f.write("\n")

            f.write("SET FOREIGN_KEY_CHECKS=1;\n")

        self.close_connection()
        self.print_summary()

    def print_summary(self):
        print(f"Conversion completed. Output written to {self.output_file}")
        print(f"Number of tables converted: {self.table_count}")
        if self.conversion_type in ['both', 'data']:
            print(f"Total number of rows inserted: {self.row_count}")

def main():
    parser = argparse.ArgumentParser(description='Convert SQLite database to SQL')
    parser.add_argument('sqlite_file', help='Path to the SQLite database file')
    parser.add_argument('output_file', help='Path to the output SQL file')
    parser.add_argument('--target_db', choices=['mysql', 'postgresql'], default='mysql', help='Target database system (default: mysql)')
    parser.add_argument('--conversion_type', choices=['both', 'tables', 'data'], default='both', help='Type of conversion to perform (default: both)')
    args = parser.parse_args()

    converter = SQLiteToSQLConverter(args.sqlite_file, args.output_file, args.target_db, args.conversion_type)
    converter.convert()

if __name__ == '__main__':
    main()