from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
import datetime

"""
NOTE: see setup_database.py before running this script

This script powers the neobank's backend using 2 endpoints: 
GET - fetches user spending insights
POST - records new transactions

Usage:
Run this script to fire up the server 
python app.py
Ensure this server is running when testing API requests. You can test various GET and POST requests using Postman.
"""


# Initialize the Flask application
app = Flask(__name__)
# Connect to SQLite database using SQLAlchemy
engine = create_engine('sqlite:///neobank.db')


"""
    Retrieve spending insights for a specific customer.
    Parameters:
    - customer_id: ID of the customer whose insights are requested
    - top_n (optional): Number of top categories 
    - days_ago (optional): Number of days ago to include transactions from
"""
@app.route('/insights', methods=['GET'])
def get_insights():

    # Retrieve parameters from the GET request
    customer_id = request.args.get('customer_id', type=str)
    top_n = request.args.get('top_n', type=int)
    days_ago = request.args.get('days_ago', type=int)

    # SQL query -- calculates total spending per category for the specified customer
    # SELECT merchants.category to group results by merchant type 
        # It selects the category from the merchants table, which organizes 
        #the data by different types of merchant categories

        #The SUM(transactions.amount_cents) part calculates the total amount 
        #spent in each of these categories. This means it adds up all the money 
        #spent in each category to give a total spending amount for each type of merchant category.


    # SUM(transactions.amount_cents) to calculate total spending per category 
    # FROM transactions specifies transactions as main table 
    # JOIN to link merchants and transactions using merchant_id to access merchant 
        #category into 
    #WHERE clause: filter transactions by customer_id to ensure results are customer
        #specific 
        #include only transactions with a card 
        #ensure transactions are in correct date range
    query = """
    SELECT merchants.category, SUM(transactions.amount_cents) AS total_spent
    FROM transactions
    JOIN merchants ON transactions.merchant_id = merchants.id
    WHERE transactions.customer_id = :customer_id
    AND transactions.is_card = 1
    AND transactions.date <= :today
    """

    # If days_ago is specified, filter transactions from the specified start date
    if days_ago is not None:
        start_date = datetime.date.today() - datetime.timedelta(days=days_ago)
        #only transactions on or after the start_date should be included in results
        query += " AND transactions.date >= :start_date"
    else:
        start_date = None

    # Group by category and order by total spending descending
    query += " GROUP BY merchants.category ORDER BY total_spent DESC"

    # If top_n is specified, limit number of results
    if top_n is not None:
        query += " LIMIT :top_n"

    # Execute query with provided parameters
    with engine.connect() as connection:
        result = connection.execute(text(query), {
            'customer_id': customer_id, #from param 
            'today': datetime.date.today(), #python lib
            'start_date': start_date, #subtract specific num days from todays date
            'top_n': top_n #param, max num of results to return
        }).fetchall()

    # Format the query result into a list of dictionaries
    insights = [{'category': row['category'], 'amount': row['total_spent']} for row in result]
    return jsonify(insights)

BUDGET_LIMIT = 1000 

@app.route('/card_swipe', methods=['POST'])
def card_swipe():
    # Retrieve transaction data from the POST request body
    data = request.json
    customer_id = data.get('customer_id')
    merchant_id = data.get('merchant_id')
    amount_cents = data.get('amount_cents')
    is_card = data.get('is_card')


    #sql query to find the merchants category

    #limit check

    #insert transaction into the database


    #if amount_cent > BUDGET_LIMIT:
   #     return jsonify({'message': 'Unable to complete txn'}), 400
    #else: 

        #SQL query to insert transaction into the database

     #   return  return jsonify({'message': 'Txn completed successfully'}), 200



"""
    Create a new transaction.
"""
@app.route('/transactions', methods=['POST'])
def create_transaction():

    # Retrieve transaction data from the POST request body
    data = request.json
    customer_id = data.get('customer_id')
    merchant_id = data.get('merchant_id')
    amount_cents = data.get('amount_cents')
    is_card = data.get('is_card')

    # SQL query -- inserts a new transaction into the database
    query = """
    INSERT INTO transactions (customer_id, merchant_id, amount_cents, is_card, date)
    VALUES (:customer_id, :merchant_id, :amount_cents, :is_card, :date)
    """

    # Execute the SQL query to insert the data into the database
    with engine.connect() as connection:
        connection.execute(text(query), {
            'customer_id': customer_id,
            'merchant_id': merchant_id,
            'amount_cents': amount_cents,
            'is_card': is_card,
            'date': datetime.date.today() # Set transaction date to today
        })

    return jsonify({'message': 'Transaction created successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)
