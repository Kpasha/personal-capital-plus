from personalcapital import (
    Connector,
    Database
)
import json
import logging
from datetime import datetime, timedelta

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Python 2 and 3 compatibility
if hasattr(__builtins__, 'raw_input'):
    input = raw_input


def get_transactions(session):
    now = datetime.now()
    date_format = '%Y-%m-%d'
    days = 365 * 2
    # log.warning("Only querying for 2 days worth of data.")
    # days = 20
    start_date = (now - (timedelta(days=days+1))).strftime(date_format)
    end_date = (now - (timedelta(days=1))).strftime(date_format)
    txn_response = session.fetch('/transaction/getUserTransactions', {
        'sort_cols': 'transactionTime',
        'sort_rev': 'true',
        'page': '0',
        'rows_per_page': '100',
        'startDate': start_date,
        'endDate': end_date,
        'component': 'DATAGRID'
    })

    # throw error if bad, parse json if good
    if txn_response.status_code != 200:
        raise ValueError("Fetching transactions failed with code {}.".format(txn_response.status_code))
    txn_response = txn_response.json()

    # parse the data out and return
    transactions = txn_response['spData']
    print('Number of transactions between {0} and {1}: {2}'.format(transactions['startDate'], transactions['endDate'],
                                                                   len(transactions['transactions'])))

    return transactions


def main():
    with Connector.connect() as session:
        accts_response = get_accounts(session)
        txn_response = get_transactions(session)
        category_map = {
            item['transactionCategoryId']: item['name']
            for item in session.make_request("/transactioncategory/getCategories")
        }

    with Database() as db:
        db.add_transactions(txn_response['transactions'])


if __name__ == '__main__':
    main()
