import psycopg2
from io import StringIO
import pandas as pd
import configparser

success = True

try:        
    
    config = configparser.ConfigParser()
    config.read('Configurations/database_config.ini')

    host = config['connection']['hostname']
    dbname = "postgres"
    user = config['connection']['username']
    password = config['connection']['pwd']
    port = config['connection']['port']
    table_name = config['connection']['table_name']

    # Open a connection to the PostgreSQL database
    conn = psycopg2.connect(host=host,
                            dbname=dbname,
                            user=user,
                            password=password,
                            port=port)
    conn.autocommit = True 

    new_db_name = config['connection']['database']
    create_db_script = f"CREATE DATABASE {new_db_name}"

    cur = conn.cursor()
    cur.execute(create_db_script)

    conn.commit()

# Catch errors and close connection
except Exception as error:
    print("Error creating table:", error)
    success = False
finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()
        print("Database connection closed.")


if success:
    try:

        config = configparser.ConfigParser()
        config.read('Configurations/database_config.ini')

        host = config['connection']['hostname']
        dbname = config['connection']['database']
        user = config['connection']['username']
        password = config['connection']['pwd']
        port = config['connection']['port']
        table_name = config['connection']['table_name']

        # Open a connection to the PostgreSQL database
        conn = psycopg2.connect(host=host,
                            dbname=dbname,
                            user=user,
                            password=password,
                            port=port)
        create_table_script = f"CREATE TABLE IF NOT EXISTS {table_name} (id SERIAL PRIMARY KEY," \
                                                                     "transaction_date DATE," \
                                                                     "to_or_from TEXT," \
                                                                     "withdrawl NUMERIC(15, 2)," \
                                                                     "deposit NUMERIC(15, 2)," \
                                                                     "balance NUMERIC(15, 2));"
        cur = conn.cursor()
        cur.execute(create_table_script)

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