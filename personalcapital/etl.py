import json
import pandas as pd
from datetime import datetime, date, timedelta

from .log import logger
from personalcapital import (
    Connector,
    Database
)
from personalcapital.constants import (
    STAPLE_CATEGORIES
)


def get_category_map():
    with Connector.connect() as session:
        category_map = {
            item['transactionCategoryId']: item['name']
            for item in session.make_request("/transactioncategory/getCategories")
        }
    return category_map


def get_transactions():
    with Database() as db:
        txns = db.get_transactions()
    return txns


def update_transactions():
    def _update_transactions(session):
        now = datetime.now()
        date_format = '%Y-%m-%d'
        days = 365 * 2
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

        return transactions['transactions']

    with Connector.connect() as session, Database() as db:
        txns = _update_transactions(session)
        db.clear_transactions()
        db.add_transactions(txns)


def get_expenses(month=None):
    if month is None:
        month = date.today().strftime("%Y-%m")
    df = pd.DataFrame(get_transactions())

    # filter by the month of interest
    df['year_month'] = df['transactionDate'].map(lambda d: '-'.join(d.split('-')[:2]))
    df = df.loc[df['year_month'] == month]

    cmap = get_category_map()
    df['category'] = df['categoryId'].map(cmap)
    df['is_staple'] = df['category'].map(lambda cat: cat in STAPLE_CATEGORIES)
    df['transactionDate'] = pd.to_datetime(df['transactionDate'])
    return df


def get_accounts():
    with Connector.connect() as session:
        accounts = pd.DataFrame(session.make_request('/newaccount/getAccounts')['accounts'])
    accounts.loc[accounts.isLiability, 'balance'] = -1 * accounts.loc[accounts.isLiability, 'balance']
    return accounts
