from Transactions_Window import TransactionsWindow
from dash import Dash

transaction_widget = TransactionsWindow()
app = Dash(__name__)
transaction_widget.make_window_components(app)




if __name__ == '__main__':
    app.run(debug=True)
    