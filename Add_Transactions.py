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
    
    def save_formated_csv():
        df = get_formatted_df()
        config.read('Configurations/csv_config.ini')
        csv_processed_path = config['csv_files']['processed_path']
        # Save the modified DataFrame to a new CSV file
        df.to_csv(csv_processed_path, index=False, header=False)

    def get_csv_data():
        csv_data: StringIO
        config.read('Configurations/csv_config.ini')
        csv_processed_path = config['csv_files']['processed_path']
        with open(csv_processed_path, 'r') as f:
            csv_data = f.read()
        return StringIO(csv_data)

    def get_formatted_df():
        df = get_df_from_csv()
        df = format_columns(df)
        return df

    def save_csv_file():
        pass


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

    def make_temp_table(cur):
        create_temp_table_script = f"CREATE TABLE IF NOT EXISTS temp_table (id SERIAL PRIMARY KEY," \
                                                                     "transaction_date DATE," \
                                                                     "to_or_from TEXT," \
                                                                     "withdrawl NUMERIC(15, 2)," \
                                                                     "deposit NUMERIC(15, 2)," \
                                                                     "balance NUMERIC(15, 2));"

        cur.execute(create_temp_table_script)

    def copy_csv_to_temp(cur):
        csv_data = get_csv_data()
        cur.copy_from(csv_data, "temp_table", sep=',', columns=('transaction_date', 'to_or_from', 'withdrawl', 'deposit','balance'))

    def copy_temp_to_transactions(cur):
        insert_script = f"INSERT INTO {app_table_name} (transaction_date, to_or_from, withdrawl, deposit, balance) " \
                    "SELECT transaction_date, to_or_from, withdrawl, deposit, balance " \
                    "FROM temp_table " \
                    "ON CONFLICT (transaction_date, to_or_from, withdrawl, deposit, balance) DO NOTHING "
        cur.execute(insert_script)

    def delete_temp(cur):
        delete_temp_table_script = "DROP TABLE IF EXISTS temp_table;"
        cur.execute(delete_temp_table_script)

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
    
    save_formated_csv()
    make_temp_table(cur)
    copy_csv_to_temp(cur)
    copy_temp_to_transactions(cur)
    delete_temp(cur)

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