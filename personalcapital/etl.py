import json
import pandas as pd
from datetime import date

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
