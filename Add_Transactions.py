import psycopg2
from io import StringIO
import pandas as pd
import configparser


try:        
    
    config = configparser.ConfigParser()
    config.read('Configurations/database_config.ini')

    host = config['app_connection']['app_hostname']
    dbname = config['app_connection']['app_database']
    user = config['app_connection']['app_username']
    password = config['app_connection']['app_pwd']
    port = config['app_connection']['app_port']
    table_name = config['app_connection']['app_table']

    # Open a connection to the PostgreSQL database
    conn = psycopg2.connect(host=host,
                            dbname=dbname,
                            user=user,
                            password=password,
                            port=port)

    cur = conn.cursor()

    config.read('Configurations/csv_config.ini')
    input_path = config['csv_files']['input_path']
    processed_path = config['csv_files']['processed_directory']

    # Open the csv in pandas
    df = pd.read_csv(input_path, header=None)

    print(df)

    # Vectorized functions to format table to make it compatible of PostgresSql
    def format_date(x):
        dates = x.split('/')
        if len(dates) != 3:
            dates = x.split('-')
            if len(dates) != 3:
                raise ValueError("Date format not accepted")
            else:
                return x
        return f"{dates[2]}-{dates[0]}-{dates[1]}"
    

    def replace_empty_with_zeros(x):
        if pd.isna(x):
            return 0
        return x

    df.iloc[:,0] = df.iloc[:,0].apply(format_date)
    df.iloc[:,2] = df.iloc[:,2].apply(replace_empty_with_zeros)
    df.iloc[:,3] = df.iloc[:,3].apply(replace_empty_with_zeros)

    # Save the modified DataFrame to the original CSV file
    df.to_csv(processed_path, index=False, header=False)

    csv_data: StringIO

    csv_path = processed_path
    with open(csv_path, 'r') as f:
        csv_data = f.read()

    csv = StringIO(csv_data)

    config.read('Configurations/database_config.ini')

    # Copy the csv file to our PostgreSQL table
    cur.copy_from(csv, table_name, sep=',', columns=('transaction_date', 'to_or_from', 'withdrawl', 'deposit','balance'))

    conn.commit()

# Catch errors and close connection
except Exception as error:
    print("Error creating table:", error)
finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()
        print("Database connection closed.")