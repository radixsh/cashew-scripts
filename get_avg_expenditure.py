import sys
import sqlite3
import csv
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from pprint import pprint

TOLERANCE_HOURS = 36
DATE_FORMAT = '%B %d, %Y %I:%M %p PT'

def print_all_from_today(day=datetime, conn=sqlite3.Connection):
    start_time = int((day - timedelta(hours=TOLERANCE_HOURS)).timestamp())
    formatted_start_time = datetime.fromtimestamp(start_time).strftime(DATE_FORMAT)
    end_time = int((day + timedelta(hours=TOLERANCE_HOURS)).timestamp())
    query = f"SELECT * FROM transactions \
            WHERE date_created > '{start_time}' \
            AND date_created < '{end_time}'"
    from_this_day = conn.execute(query).fetchall()

    print(f"All transactions within {TOLERANCE_HOURS} hours of {day}:")
    # https://stackoverflow.com/questions/3420122/filter-dict-to-contain-only-certain-keys
    mykeys = ['amount', 'date_created', 'income', 'name', 'note']
    for entry in from_this_day:
        newdict = {key: entry[key] for key in mykeys}
        newdict['date_created'] = datetime.fromtimestamp(newdict['date_created']).strftime(DATE_FORMAT)
        print(newdict)

def show_all_tables(conn):
    LIMIT = 10
    tables = [##'wallets',
              #'categories',
              ##'objectives',
              'transactions',
              #'budgets',
              ##'category_budget_limits',
              #'associated_titles',
              ##'app_settings',
              ##'scanner_templates',
              ##'delete_logs'
              ]
    for table in tables:
        print(table)
        count = 0
        cmd = f"SELECT * FROM {table} ORDER BY 'date_created' DESC"
        for row in conn.execute(cmd):
            count += 1
            if count >= LIMIT:
                break
            pprint(row)
        print()
    print('\n')

def dict_factory(cursor, row):
    # https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
    # https://docs.python.org/3/library/sqlite3.html#sqlite3-howto-row-factory
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

# Goal: Find average monthly expenditure (not counting income)
def main():

    try:
        # https://docs.python.org/3/library/sqlite3.html#tutorial
        conn = sqlite3.connect(sys.argv[1])
        conn.row_factory = dict_factory
    except:
        print('Usage: ./get_avgs.py cashew.sql')
        sys.exit(0)

    # For debugging
    # show_all_tables(conn)

    # The SQL query and datetime conversions were done via ChatGPT
    query = 'SELECT MIN(date_created), MAX(date_created) FROM transactions'
    min_timestamp, max_timestamp = conn.execute(query).fetchone().values()

    # Convert from Unix timestamp to datetime object
    start_date = datetime.fromtimestamp(min_timestamp)
    start_date = start_date + relativedelta(months=1)
    end_date = datetime.fromtimestamp(max_timestamp)
    print(f"Date range to analyze: {start_date} to {end_date}")

    running_total = 0.0
    months = 0
    # The loop is from ChatGPT
    while start_date < end_date:
        months += 1

        # First day of next month
        next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)

        query = (f"SELECT * FROM transactions "
                 "WHERE date_created >= ? AND "
                 "date_created < ?")
        results = conn.execute(query, (start_date.strftime('%s'),
                                       next_month.strftime('%s'))).fetchall()
        print(f"{start_date.strftime('%B %Y')}: {len(results)} purchases")

        monthly_expenses = 0.0
        monthly_income = 0.0
        for item in results:
            if item["income"] == 0:
                monthly_expenses += item["amount"]
            elif item["income"] == 1:
                monthly_income += item["amount"]

            # print(datetime.fromtimestamp(item["date_created"]).strftime(DATE_FORMAT),
            #       item["name"],
            #       item["amount"],
            #       item["note"])

        print(f"\tExpenses: {monthly_expenses:>7.2f} USD"
                f"\tIncome: {monthly_income:>7.2f} USD")
        running_total += monthly_expenses

        start_date = next_month

    print(f"Average monthly expenditure: {running_total / months:>7.2f} USD")

if __name__ == "__main__":
    main()
