# SQLite to SQL Converter

This Python tool converts SQLite databases to SQL scripts compatible with MySQL or PostgreSQL. It offers flexible options for converting table structures, data, or both.

## Features

- Converts SQLite database schema to MySQL or PostgreSQL compatible SQL
- Generates INSERT statements for data migration
- Options to convert only table structures, only data, or both
- Handles data type conversions
- Escapes special characters in data
- Provides a summary of the conversion process

## Requirements

- Python 3.6+
- sqlite3 module (usually comes pre-installed with Python)

## Installation

1. Clone this repository or download the `sqlite_to_sql_converter.py` file.
2. Ensure you have Python 3.6 or higher installed on your system.

## Usage

Run the script from the command line with the following syntax:

### Arguments

- `sqlite_file`: Path to the input SQLite database file
- `output_file`: Path where the output SQL file will be saved

### Options

- `--target_db {mysql,postgresql}`: Specify the target database system (default: mysql)
- `--conversion_type {both,tables,data}`: Specify the type of conversion to perform (default: both)

### Examples

1. Convert both tables and data to MySQL (default):
   ```
   python sqlite_to_sql_converter.py input.db output.sql
   ```

2. Convert only table structures to MySQL:
   ```
   python sqlite_to_sql_converter.py input.db output.sql --conversion_type tables
   ```

3. Convert only data to MySQL:
   ```
   python sqlite_to_sql_converter.py input.db output.sql --conversion_type data
   ```

4. Convert to PostgreSQL:
   ```
   python sqlite_to_sql_converter.py input.db output.sql --target_db postgresql
   ```

## Output

The script will generate an SQL file containing:
- CREATE TABLE statements (if table conversion is selected)
- INSERT statements (if data conversion is selected)
- MySQL/PostgreSQL specific syntax and data type adjustments

After conversion, the tool will display a summary including:
- Number of tables converted
- Total number of rows inserted (if data conversion was performed)

## Notes

- The tool uses 'INSERT IGNORE' for MySQL to handle potential duplicate key errors during import.
- Foreign key checks are disabled during the import process to prevent constraint violations.
- Always review the generated SQL script and test it in a safe environment before using it on a production database.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](issues) if you want to contribute.

## License

[MIT](https://choosealicense.com/licenses/mit/)