from pymongo import MongoClient
from .log import logger


class Database(object):
    def __init__(self):
        self.client = MongoClient('localhost', port=27017)
        self.db = self.client.personalcapital
        self.txns = self.db.transactions
        # self.accounts = self.db.accounts

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def add_transactions(self, txns):
        existing_ids = set([
            e['userTransactionId']
            for e in self.txns.find({}, ["userTransactionId"])
        ])
        passed_ids = set([
            e['userTransactionId']
            for e in txns
        ])
        new_ids = passed_ids - existing_ids

        new_txns = [
            txn
            for txn in txns
            if txn['userTransactionId'] in new_ids
        ]

        if len(new_txns) > 0:
            logger.info("Adding {} new transactions.".format(len(new_txns)))
            self.txns.insert_many(new_txns)
        else:
            logger.info("No new transactions to add to the database.")

    def get_transactions(self):
        return list(self.txns.find())

    def clear_transactions(self):
        self.txns.remove({})
