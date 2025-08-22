# About
A soon to be dashboard project that tracks and plot expenses from uploaded csv files. The goal is to allow users to upload expenses from a csv file and allow for custom transaction categorization. Once transactions are categorized by type, the app will provide a break down on monthly spending. <br>

# Current Features
The expense tracker currently provides the following features
* Upload expenses via the `Add_Transactions.py` script
* Display uploaded transactions in the transactions table. Transactions can be filtered by date
* Allow for multi row selection to remove transactions

# Setup
The configurations folder contains two template configuration files used to run the expense tracker application: the database configuration and the csv confiuration. Fill in the configuation files with your settings to run the application. 

## Database Seup
*This application uses PostgreSQL to store transaction data. PostgreSQL can be downloaded [here](https://www.postgresql.org/). Enter the port and password selected during istallation into `csv_config.ini`.
*For ease of effort, add the PosgreSQL bin directory (on windows, the default path is `C:\Program Files\PostgreSQL\<version>\bin`) to PATH. 
*To make a new database on the command line in Windows, open a new instance of the command prompt enter 
```
  psql -U postgres
```
you will be prompted to enter your password.
*Create a new database with the command 
```
    CREATE DATABASE your_database_name;
```