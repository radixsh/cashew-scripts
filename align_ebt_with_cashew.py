import sys
import sqlite3
import csv
from datetime import datetime
from datetime import timedelta
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

def generate_insertion_string(row=dict, store_name=str) -> str:
    new_entry = {
            'amount': row['Transaction Amount'],
            # 'budget_fks_exclude': None,
            'category_fk': '3',
            # 'created_another_future_transaction': 0,
            'date_created': datetime.now().timestamp(),
            # 'date_time_modified': datetime.now().timestamp(),
            # 'end_date': None,
            'income': 0,
            # 'method_added': None,
            'name': store_name,
            'note': 'Inserted via script',
            # 'objective_fk': None,
            # 'objective_loan_fk': None,
            # 'original_date_due': 1705506262,
            'paid': 1,
            # 'paired_transaction_fk': None,
            # 'period_length': 1,
            # 'reoccurrence': 3,
            # 'shared_date_updated': None,
            # 'shared_key': None,
            # 'shared_old_key': None,
            # 'shared_reference_budget_pk': None,
            # 'shared_status': None,
            # 'skip_paid': 1,
            # 'sub_category_fk': None,
            # 'transaction_original_owner_email': None,
            # 'transaction_owner_email': None,
            'transaction_pk': '3a7c5659-98e8-49e4-97a2-f15fb64586b5',
            # 'type': None,
            # 'upcoming_transaction_notification': 1,
            # 'wallet_fk': '0'
            }
    # Desired format: (:amount, :date_created, :income, :name, :note, :paid)
    # string = "("
    # for key in new_entry.keys():
    #     string += f":{key}, "
    # string = string.rstrip(", ")
    # string += ")"
    # print(string)
    # return string
    return new_entry

# https://softhints.com/python-3-convert-dictionary-to-sql-insert/
def insert(row=dict, store_name=str, conn=sqlite3.Connection) -> None:
    mydict = generate_insertion_string(row, store_name)
    keys = ','.join(f"{x}" for x in mydict.keys())
    values = ','.join(f"\"{x}\"" for x in mydict.values())
    insertion = f"INSERT INTO transactions ({keys}) VALUES ({values})"
    print(f'Command: {insertion}')
    conn.execute(insertion)
    conn.commit()
    print_all_from_today()

def normalize(store_name=str) -> str:
    # I entered Trader Joe's purchases in Cashew as "trader joe's"
    if store_name == "Trader Joes 182":
        return "trader joe's"
    elif store_name == "Ucd Stores Mbs-marketp":
        return "MU food"
    elif store_name == "Kim`s Mart":
        return "kim's mart"
    elif store_name == "Davis Farmers Market":
        return "farmer's market"
    else:
        return f'{store_name} NOT FOUND!!!!!!!!! elephant'

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

# Goal: If there is some EBT transaction that is not in the Cashew data, then
# insert that transaction into Cashew data
def main():
    try:
        # https://docs.python.org/3/library/sqlite3.html#tutorial
        conn = sqlite3.connect(sys.argv[1])
        conn.row_factory = dict_factory
        ebt_csv = open(sys.argv[2], newline='')
        ebt_reader = csv.DictReader(ebt_csv)
    except:
        print('Usage: ./analyze.py cashew.sql ebt.csv')
        sys.exit(0)

    # For debugging
    # show_all_tables(conn)

    # For each EBT purchase
    for row in ebt_reader:

        if row['Transaction Type'] != 'Food Purchase':
            continue
        print()

        # Format: row['Store Name & Address'] = "Trader Joes 182, Trader Joes 182885 Russdavis        Ca Us,"
        store_name = row['Store Name & Address'].split(',')[0]
        store_name = normalize(store_name)

        # Format: row['Transaction Date & Time'] = "August 26, 2024 06:58 PM PT"
        day = datetime.strptime(row['Transaction Date & Time'], DATE_FORMAT)
        print_all_from_today(day, conn)

        # Strip "-$ 58.93" to -58.93
        amount = row['Transaction Amount']
        amount = float(amount[amount.index(" "):]) * -1

        start_time = int((day - timedelta(hours=TOLERANCE_HOURS)).timestamp())
        end_time = int((day + timedelta(hours=TOLERANCE_HOURS)).timestamp())
        query = f'SELECT * FROM transactions \
                WHERE name == "{store_name}" \
                AND amount == "{amount}" \
                AND date_created > "{start_time}" \
                AND date_created < "{end_time}"'
        result = conn.execute(query).fetchone()

        # If there's no matching transaction (amount/date) in Cashew already
        if result is None:
            print(f"EBT transaction: {day}, {store_name}, {amount}")
            print("No matching transaction found in Cashew data :(")

            # If user assents, then insert this transaction into Cashew SQL database
            # (Insert only if user actively says to)
            if input("Insert this transaction? (y/N) ") == 'y':
                print("doing it!")
                insert(row, store_name, conn)
            else:
                print("not doing it!")

        else:
            print(f"A matching transaction ({store_name}, "
                  f"{amount}) was found in cashew data :D")

if __name__ == "__main__":
    main()
