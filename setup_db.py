import psycopg2
from io import StringIO
import pandas as pd
import configparser
from psycopg2 import sql


success = True

try:        
    
    config = configparser.ConfigParser()
    config.read('Configurations/database_config.ini')

    super_host = config['super_connection']['super_hostname']
    super_dbname = config['super_connection']['super_database']
    super_user = config['super_connection']['super_username']
    super_password = config['super_connection']['super_pwd']
    super_port = config['super_connection']['super_port']

    # Open a connection to the PostgreSQL database
    conn = psycopg2.connect(host=super_host,
                            dbname=super_dbname,
                            user=super_user,
                            password=super_password,
                            port=super_port)
    conn.autocommit = True 

    cur = conn.cursor()

    app_user = config['app_connection']['app_username']
    app_password = config['app_connection']['app_pwd']

    user_query = sql.SQL("CREATE USER {username} WITH PASSWORD {password}").format(
            username=sql.Identifier(app_user),
            password=sql.Literal(app_password)
        )

    new_db_name = config['app_connection']['app_database']
    create_db_script = f"CREATE DATABASE {new_db_name} OWNER {app_user}"

    cur.execute(user_query)
    print(f"User '{app_user}' created successfully.")
    cur.execute(create_db_script)
    print(f"Database '{new_db_name}' created successfully.")

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

        app_host = config['app_connection']['app_hostname']
        app_dbname = config['app_connection']['app_database']
        app_user = config['app_connection']['app_username']
        app_password = config['app_connection']['app_pwd']
        app_port = config['app_connection']['app_port']
        app_table_name = config['app_connection']['app_table']

        # Open a connection to the PostgreSQL database
        conn = psycopg2.connect(host=app_host,
                            dbname=app_dbname,
                            user=app_user,
                            password=app_password,
                            port=app_port)
        create_table_script = f"CREATE TABLE IF NOT EXISTS {app_table_name} (id SERIAL PRIMARY KEY," \
                                                                     "transaction_date DATE," \
                                                                     "to_or_from TEXT," \
                                                                     "withdrawl NUMERIC(15, 2)," \
                                                                     "deposit NUMERIC(15, 2)," \
                                                                     "balance NUMERIC(15, 2));"
        cur = conn.cursor()
        cur.execute(create_table_script)
        print(f"Table '{app_table_name}' created successfully.")

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