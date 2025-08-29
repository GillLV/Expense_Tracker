from time import strftime
from dash import Dash, html, dcc, callback, ctx, Output, Input
from dash import dash_table
import dash_bootstrap_components as dbc
from datetime import date
from flask import app
import pandas as pd
import datetime
import configparser
import psycopg2


class TransactionsWindow:

    year_month_str : str
    day : int

    transaction_table_id = 'transaction_table'
    transaction_date_picker_id = 'transaction_date_range_picker'
    delete_button_id = 'delete_button' 

    app_host : str
    app_database_name : str
    app_username : str
    app_password : str
    app_port : str
    app_table_name : str

    def __init__(self):
        self.init_dates()
        self.init_connection()

    def init_dates(self):
        self.date = datetime.datetime.now()
        self.month = self.date.month
        self.year = self.date.year
        self.day = self.get_num_days_in_month()
        self.year_month_str = f'{self.year}-{self.month:02d}'

    def init_connection(self):
        config = configparser.ConfigParser()
        config.read('Configurations/database_config.ini')
        self.app_host = config['app_connection']['app_hostname']
        self.app_database_name = config['app_connection']['app_database']
        self.app_username = config['app_connection']['app_username']
        self.app_password = config['app_connection']['app_pwd']
        self.app_port = config['app_connection']['app_port']
        self.app_table_name = config['app_connection']['app_table']

    def get_num_days_in_month(self):
        days = 31
        months_with_30_days = [4, 6, 9, 11]
        if (self.month in months_with_30_days):
            days = 30
        elif (self.month == 2):
            days = 28
        return days

    def read_from_database(self, script, params):
        
        df = pd.DataFrame()

        try:

            # Open a connection to the PostgreSQL database
            conn = psycopg2.connect(host=self.app_host,
                                    dbname=self.app_database_name,
                                    user=self.app_username,
                                    password=self.app_password,
                                    port=self.app_port)

            cur = conn.cursor()

            df = pd.read_sql_query(script, conn, params=params)
           


        # Catch errors and close connection
        except Exception as error:
            print("Error creating table:", error)
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()
                print("Database connection closed.")

        return df

    def execute_on_database(self, script, params):
        
        df = pd.DataFrame()

        try:

            # Open a connection to the PostgreSQL database
            conn = psycopg2.connect(host=self.app_host,
                                    dbname=self.app_database_name,
                                    user=self.app_username,
                                    password=self.app_password,
                                    port=self.app_port)

            cur = conn.cursor()

            cur.execute(script, params)

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
        return df

    def get_df_of_current_month(self):
        select_script = f"SELECT * FROM {self.app_table_name} WHERE transaction_date::text LIKE %s"
        params = (self.year_month_str + '%',)
        df = self.read_from_database(select_script, params)
        df = df.drop('id', axis=1)
        return df

    # make table of uploaded transactions matching the current month and year 
    def make_transaction_table(self):

        df = self.get_df_of_current_month()

        def get_column_type(col):
            type : str
            if (col == "transaction_date"):
               type ="datetime"
            elif (col == "to_or_from"):
               type = "text"
            else:
               type = "numeric"
            
            return type

        return dbc.Container([dash_table.DataTable(
                                df.to_dict('records'), 
                                [{"name": i, "id": i, "type": get_column_type(i)} for i in df.columns],
                                id=self.transaction_table_id,
                                style_header={'fontWeight': 'bold'},
                                row_selectable="multi"
                                ), dbc.Alert(id="table_out")
                            ])


    def make_date_range_picker(self):
        return dcc.DatePickerRange(
            id=self.transaction_date_picker_id,
            start_date=date(self.year, self.month, 1),
            end_date=date(self.year, self.month, self.get_num_days_in_month()),
        )


    def make_delete_button(self):
        return html.Button('remove', id=self.delete_button_id, n_clicks=0)

    def delete_selected_rows(self, select_df):
        # create a list of ids of the rows to delete and delete from database
        # There should only be one single entry that matches the selected row, but check for all just in case
        ids = select_df['id'].tolist()
        placeholders = ','.join(['%s'] * len(ids))
        delete_script = f"DELETE FROM {self.app_table_name} WHERE id IN ({placeholders})"
        self.execute_on_database(delete_script, ids)

    def get_all_rows_df(self):
        select_script = f"SELECT * FROM {self.app_table_name}"
        df = self.read_from_database(select_script, None)
        return df
    
    def get_selected_date_range_df(self, start_date, end_date):
        params = (strftime(start_date), strftime(end_date))
        select_script = f"SELECT * FROM {self.app_table_name} WHERE transaction_date BETWEEN %s AND %s"
        df = self.read_from_database(select_script, params)
        df = df.drop('id', axis=1)
        return df   

    # defines the layout using the defined components and handles callbacks
    def make_window_components (self, app):
        app.layout = [html.Div(children=[ html.H1( children="Transaction History",
                                                    style={
                                                            'textAlign': 'center',
                                                            'font-family': 'Arial, sans-serif'
                                                          }
                                                 ),
                                          html.Div(children=[self.make_date_range_picker(), self.make_delete_button()],
                                                    style={
                                                            'display': 'flex'
                                                          }
                                                  )
                                         ],
                              ), 
                     html.Div(children=self.make_transaction_table())]

        # When the row selection changes, highlight selected rows
        @callback(
            Output('transaction_table', 'style_data_conditional'), 
            Input('transaction_table', 'selected_rows')
        )
        def update_selected_rows_theming(selected_rows):
            if selected_rows:
                return[
                        {
                            "if": {"row_index": i},
                            "backgroundColor": "rgb(69, 245, 66)",
                            "color": "black"
                        }
                        for i in selected_rows
                      ]
            else:
                return []
    
        # Catch all callback for when the table's data changes
        @callback(
            Output(self.transaction_table_id, 'data'), 
            Input(self.delete_button_id, 'n_clicks'),
            Input(self.transaction_table_id, 'selected_rows'),
            Input(self.transaction_table_id, 'data'),
            Input(component_id=self.transaction_date_picker_id, component_property='start_date'),
            Input(component_id=self.transaction_date_picker_id, component_property='end_date')
        )
        def update_transaction_table(n_clicks, selected_rows, data, start_date, end_date):
            
            df = pd.DataFrame(data)
            triggered_id = ctx.triggered_id

            # Delete button has been pressed. Handle deletion of selected rows.
            if triggered_id == self.delete_button_id:
                if n_clicks is not None:
                    if selected_rows:
                        for row_index in selected_rows:

                            # identify the rows to delete
                            row = df.iloc[row_index]
                            params = (
                                      row['transaction_date'],
                                      row['to_or_from'],
                                      float(row['withdrawl']),
                                      float(row['deposit']),
                                      float(row['balance'])
                                     )

                            select_df = self.get_selected_rows_df(params)
                            self.delete_selected_rows(select_df)
                            df = self.get_selected_date_range_df(start_date, end_date)

            # Date range selection changed, filter table entries to match.
            elif triggered_id == self.transaction_date_picker_id:
                df = self.get_selected_date_range_df(start_date, end_date)

            return df.to_dict('records')
