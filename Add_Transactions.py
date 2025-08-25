import psycopg2
from io import StringIO
import pandas as pd
import configparser


try:           
    config = configparser.ConfigParser()

    def get_df_from_csv():
        config.read('Configurations/csv_config.ini')
        csv_input_path = config['csv_files']['input_path']

        # Open the csv in pandas
        return pd.read_csv(csv_input_path, header=None)  
    
    def save_df_to_csv(df):
        config.read('Configurations/csv_config.ini')
        csv_processed_path = config['csv_files']['processed_path']
        # Save the modified DataFrame to the original CSV file
        df.to_csv(csv_processed_path, index=False, header=False)

    def get_csv_data():
        csv_data: StringIO
        config.read('Configurations/csv_config.ini')
        csv_processed_path = config['csv_files']['processed_path']
        with open(csv_processed_path, 'r') as f:
            csv_data = f.read()
        return StringIO(csv_data)

    def get_formatted_df_from_csv():
        df = get_df_from_csv()
        df = format_columns(df)
        return df

    def copy_csv_to_table():
        df = get_formatted_df_from_csv()
        save_df_to_csv(df)
        csv_data = get_csv_data()
        # Copy the csv file to our PostgreSQL table
        cur.copy_from(csv_data, app_table_name, sep=',', columns=('transaction_date', 'to_or_from', 'withdrawl', 'deposit','balance'))   

    def is_US_format(split_list):
        if len(split_list) != 3:
            return False
        elif len(split_list[0]) != 2 or len(split_list[1]) != 2 or len(split_list[2]) != 4:
            return False
        elif int(split_list[0]) > 12:
            return False
        return True

    def is_ISO_format(split_list):
        if len(split_list) != 3:
            return False
        elif len(split_list[0]) != 4 or len(split_list[1]) != 2 or len(split_list[2]) != 2:
            return False
        elif int(split_list[1]) > 12:
            return False
        return True

    # Vectorized functions to format table to make it compatible of PostgresSql
    def format_date_US_to_ISO(date_str):
        dates = date_str.split('/')
        if is_US_format(dates):
             return f"{dates[2]}-{dates[0]}-{dates[1]}"
        dates = date_str.split('-')
        if is_ISO_format(dates):
            return date_str
        raise ValueError("Date format not accepted")

    def replace_empty_col_with_zeros(x):
        if pd.isna(x):
            return 0.0
        else:
            return x

    def format_columns(df):
        df.iloc[:,0] = df.iloc[:,0].apply(format_date_US_to_ISO)
        df.iloc[:,2] = df.iloc[:,2].apply(replace_empty_col_with_zeros)
        df.iloc[:,3] = df.iloc[:,3].apply(replace_empty_col_with_zeros)
        return df

    config.read('Configurations/database_config.ini')

    app_host_name = config['app_connection']['app_hostname']
    app_database_name = config['app_connection']['app_database']
    app_username = config['app_connection']['app_username']
    app_password = config['app_connection']['app_pwd']
    app_port = config['app_connection']['app_port']
    app_table_name = config['app_connection']['app_table']

    # Open a connection to the PostgreSQL database
    conn = psycopg2.connect(host=app_host_name,
                            dbname=app_database_name,
                            user=app_username,
                            password=app_password,
                            port=app_port)

    cur = conn.cursor()
    copy_csv_to_table()
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