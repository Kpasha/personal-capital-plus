from personalcapital import (
    Connector,
    Database
)
from personalcapital.etl import get_expenses, get_accounts
from datetime import datetime, date
from .log import logger


def current_expense_margin(month=None):
    df = get_expenses(month)
    non_staple = df.loc[(~df.is_staple) & (df.isSpending)]
    return 3200 - non_staple['amount'].sum()


def get_report():
    monthly_expense_margin = current_expense_margin()
    accounts = get_accounts()
    group_sums = accounts.groupby('accountTypeGroup').sum()['balance']
    net_worth = accounts['balance'].sum()
    loan_debt = group_sums.loc['LOAN']
    car_loan_debt = accounts.loc[accounts['firmName'].str.contains('Toyota'), 'balance'].sum()
    student_loan_debt = accounts.loc[accounts['firmName'].str.contains('Navient'), 'balance'].sum()
    credit_debt = group_sums.loc['CREDIT_CARD']
    retirement = group_sums.loc['RETIREMENT']
    investments = group_sums.loc['INVESTMENT']
    bank = group_sums.loc['BANK']

    return {
        "1) Net Worth": "{:.2f}".format(net_worth),
        "2) Loans (All)": "{:.2f}".format(loan_debt),
        "3) Loans (Auto)": "{:.2f}".format(car_loan_debt),
        "4) Loans (Student)": "{:.2f}".format(student_loan_debt),
        "5) Credit Cards": "{:.2f}".format(credit_debt),
        "6) Bank": "{:.2f}".format(bank),
        "7) Retirement": "{:.2f}".format(retirement),
        "8) Monthly Margin": "{:.2f}".format(monthly_expense_margin),
        "9) Last Update": datetime.now().strftime("%m/%d %H:%M")
    }
