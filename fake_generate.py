import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from faker import Faker
import random
import itertools
from functools import partial

# Initialize Faker
fake = Faker()

# Function to connect to MySQL and fetch table metadata
def fetch_table_metadata(host, user, password, database, table):
    query = f"""
    SELECT 
        COLUMN_NAME,
        COLUMN_TYPE,
        CHARACTER_MAXIMUM_LENGTH,
        IS_NULLABLE,
        COLUMN_KEY,
        COLUMN_DEFAULT,
        EXTRA
    FROM 
        INFORMATION_SCHEMA.COLUMNS
    WHERE 
        TABLE_SCHEMA = '{database}' 
        AND TABLE_NAME = '{table}';
    """
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        schema = cursor.fetchall()
        return schema
    except Error as e:
        st.error(f"Failed to fetch table metadata: {e}")
        return None
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

# Function to select Faker generators based on column semantics and metadata
from faker import Faker
import random

fake = Faker()

# Function to select Faker generators based on column semantics and metadata
def select_faker_generator(column_name, column_type, max_length, is_nullable):
    column_name_lower = column_name.lower()

    # Mapping column names to realistic data generators
    if 'name' in column_name_lower:
        if 'first' in column_name_lower:
            return fake.first_name
        elif 'last' in column_name_lower:
            return fake.last_name
        else:
            return fake.name
    elif 'email' in column_name_lower:
        return fake.email
    elif 'phone' in column_name_lower or 'mobile' in column_name_lower:
        return fake.phone_number
    elif 'address' in column_name_lower:
        return fake.address
    elif 'city' in column_name_lower:
        return fake.city
    elif 'state' in column_name_lower:
        return fake.state
    elif 'country' in column_name_lower:
        return fake.country
    elif 'zip' in column_name_lower or 'postal' in column_name_lower:
        return fake.zipcode
    elif 'birth' in column_name_lower or 'birthday' in column_name_lower:
        if 'date' in column_type:
            return lambda: fake.date_of_birth().strftime('%Y-%m-%d')  # Explicit handling for birthdays
    elif 'date' in column_name_lower and 'time' not in column_name_lower:
        return lambda: fake.date().strftime('%Y-%m-%d')  # General date handling
    elif 'time' in column_name_lower and 'stamp' not in column_name_lower:
        return fake.time
    elif 'timestamp' in column_type or 'datetime' in column_type:
        return lambda: fake.date_time().strftime('%Y-%m-%d %H:%M:%S')  # Format for datetime
    elif 'username' in column_name_lower:
        return fake.user_name
    elif 'password' in column_name_lower:
        return fake.password
    elif 'company' in column_name_lower:
        return fake.company
    elif 'job' in column_name_lower or 'position' in column_name_lower:
        return fake.job
    elif 'price' in column_name_lower or 'cost' in column_name_lower:
        return lambda: round(random.uniform(1.0, 1000.0), 2)
    elif 'int' in column_type:
        return lambda: random.randint(0, 100)  # Adjust range as needed
    elif 'float' in column_type or 'double' in column_type:
        return lambda: round(random.uniform(0.0, 100.0), 2)
    elif 'char' in column_type or 'text' in column_type:
        # Use max_length to limit text length if available, with a fallback length
        max_len = max_length if max_length else 20
        return lambda: fake.text(max_nb_chars=min(max_len, 20))
    else:
        # If a column is nullable, randomly assign None some of the time
        return lambda: None if is_nullable == 'YES' and random.random() > 0.9 else fake.word()

# Function to generate fake data rows based on metadata
def generate_fake_data(schema, num_rows):
    data_generators = {
        col['COLUMN_NAME']: select_faker_generator(
            col['COLUMN_NAME'],
            col['COLUMN_TYPE'],
            col['CHARACTER_MAXIMUM_LENGTH'],
            col['IS_NULLABLE']
        ) for col in schema if col['COLUMN_KEY'] != 'PRI'
    }
    
    # Use itertools to generate rows of fake data
    data = [
        {col: gen() for col, gen in data_generators.items()} 
        for _ in itertools.repeat(None, num_rows)
    ]
    
    return pd.DataFrame(data)

# Function to escape single quotes in SQL values
def escape_sql_value(value):
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"  # Properly escape single quotes in strings for SQL
    elif value is None:
        return 'NULL'
    else:
        return str(value)

# Function to generate SQL INSERT statements
def generate_insert_statements(table, data):
    columns = ", ".join(data.columns)
    insert_statements = []

    for _, row in data.iterrows():
        # Use the helper function to properly format values
        values = ", ".join(escape_sql_value(val) for val in row)
        insert_statement = f"INSERT INTO {table} ({columns}) VALUES ({values});"
        insert_statements.append(insert_statement)

    return "\n".join(insert_statements)

# Main function for the Streamlit app
def main():
    st.set_page_config(page_title='MySQL Fake Data Generator', layout='centered')
    st.title('MySQL Fake Data Generator')

    st.sidebar.header('MySQL Connection')
    host = st.sidebar.text_input('Host', 'localhost')
    user = st.sidebar.text_input('User', 'root')
    password = st.sidebar.text_input('Password', type='password')
    database = st.sidebar.text_input('Database')
    table = st.sidebar.text_input('Table Name')

    num_rows = st.sidebar.slider('Number of Rows', min_value=1, max_value=30000, value=10, step=1)

    if st.sidebar.button('Generate Fake Data'):
        schema = fetch_table_metadata(host, user, password, database, table)
        if schema:
            fake_data = generate_fake_data(schema, num_rows)
            st.dataframe(fake_data)

            # Generate and provide SQL insert statements download
            insert_statements = generate_insert_statements(table, fake_data)
            st.download_button(
                label="Download data as SQL",
                data=insert_statements,
                file_name=f'{table}_fake_data.sql',
                mime='text/plain'
            )

if __name__ == '__main__':
    main()