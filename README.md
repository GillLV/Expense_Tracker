# About
A soon to be dashboard project that tracks and plots expenses from uploaded csv files. The goal is to allow for custom transaction categorization. Once transactions are categorized, the app will provide a break down on monthly spending. <br>

# Current Features
The expense tracker currently provides the following features
* Upload expenses via the `Add_Transactions.py` script.
* Display uploaded transactions in the transactions table. Transactions can be filtered by date.
* Allow for multi row selection to remove transactions.

# Setup
The configurations folder contains two template configuration files used to run the expense tracker application: the database configuration file and the csv configuration file. Fill in the configuation files with your desired settings to run the application. 

## Database Setup
This application uses PostgreSQL to store transaction data. PostgreSQL can be downloaded [here](https://www.postgresql.org/). To configure the database, fill in the settings in `csv_config.ini`. `csv_config.ini` already contains recommended settings for the hostname and port, aswell as the superuser username and database. Changing these settings is not supported. Set `super_pwd` to the password selected during PostgreSQL installation. Select a desired username (`app_username`), database name (`app_database`), and table name (`app_table`), as well as a strong password (`app_pwd`) for the application connection. Once settings are configured, run the command 
```
  python setup_db.py
```
in the project directory. 

## CSV Setup
This application does not yet support adding transaction data via the user interface. To add transaction data to the database, configure the `csv_config.ini` file. Set `input_path` to the path of the CSV you wish to add. Set `output_path` to file path you wish to save the processed CSV file to. Once settings are configured, run
```
  python Add_Transactions.py`
```
in the project directory.