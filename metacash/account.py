import logging

import pandas as pd

from metacash.labels import Labels
from metacash.transactions import Transactions


class Account:

    @classmethod
    def load_regular(cls, config, name):
        logging.debug(f"Loading account {name}")
        transactions = Transactions.read(config, name)
        labels = Labels.loadRegular(config, name, transactions)
        account = cls(config, name, transactions, labels)
        account.description = config['accounts'][name]['description']
        return account

    def __init__(self, config, name, transactions, labels):
        self.name = name
        self.config = config
        self.transactions = transactions
        self.labels = labels

    def balance(self):
        # return balance
        return self.transactions.balance(final=True)

    def df(self, ts_begin=None, ts_end=None):

        df = self.transactions.df

        # make sure that the requested time interval is within the transactions bounds.

        if ts_begin and ts_begin < self.transactions.df.iloc[0].timestamp:
            raise Exception(f"requested ts_begin={ts_begin} is invalid")

        if ts_end and ts_end > self.transactions.df.iloc[-1].timestamp:
            raise Exception(f"requested ts_end={ts_end} is invalid")

        # consolidate dataframe including transaction labels, if present.
        if len(self.labels.df) > 0:
            df = df.merge(self.labels.df, left_index=True, right_index=True)

        if ts_begin:
            df = df[df.timestamp >= ts_begin]
            if df.iloc[0]["type"] != "ib":
                # initial balance record removed, add it
                first = self.transactions.df.iloc[0].copy()
                first.timestamp = ts_begin
                first.balance = df.iloc[0].balance - df.iloc[0].amount
                first["label.category"] = "ignore"
                first["label.type"] = "ignore"
                df_first = pd.DataFrame([first.to_dict()])
                df = pd.concat([df_first, df], ignore_index=True)

        if ts_end:
            df = df[df.timestamp <= ts_end]
            if df.iloc[-1]["type"] != "fb":
                # final balance record removed, add it
                last = self.transactions.df.iloc[-1].copy()
                last.timestamp = ts_end
                last.balance = df.iloc[-1].balance
                last["label.category"] = "ignore"
                last["label.type"] = "ignore"
                df_last = pd.DataFrame([last.to_dict()])
                df = pd.concat([df, df_last], ignore_index=True)

        df = df.reset_index(drop=True)

        return df

    def overview(self):
        ts_begin = self.df()["timestamp"].iloc[0].date().strftime('%Y-%m-%d')
        ts_end = self.df()["timestamp"].iloc[-1].date().strftime('%Y-%m-%d')
        balance = self.config["float_format"].format(self.balance())
        n_transactions = len(self.transactions.df)
        logging.info(f"{self.name:40}: [{ts_begin},{ts_end}] ({n_transactions}) {balance}")
