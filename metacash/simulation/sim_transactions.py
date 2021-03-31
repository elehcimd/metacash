import pandas as pd

from metacash.account import Account
from metacash.transactions import Transactions


class TimestampSampler:
    def __init__(self, ts_index):
        self.index = ts_index

    def add_noise_uniform(self, d):
        # sample from [0,s] uniformly
        return self

    def add_noise_normal(self, d):
        # sample from [0,s] uniformly
        return self

    @classmethod
    def date_range(cls, *args, **kwargs):
        # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.date_range.html
        return cls(pd.date_range(*args, **kwargs).round("D"))

    def sample(self):
        return self.index.copy()


class AmountSampler:
    def __init__(self, amount, noise=None):
        self.amount = amount
        self.noise = noise

    def sample(self):
        # normal distrib mu=0 stddev=1/2: 95% values within -1,1
        if self.noise is not None:
            noise_sample = self.noise(self.amount)
        else:
            noise_sample = 0
        return self.amount + noise_sample


class TransactionsSampler:
    def __init__(self, ts_sampler, amount_sampler, description):
        self.ts_sampler = ts_sampler
        self.amount_sampler = amount_sampler
        self.description = description

    def sample(self):
        index = self.ts_sampler.sample()
        df = pd.DataFrame(columns=Transactions.columns)
        df = df.drop(columns=["timestamp"])

        for ts in index:
            df.at[ts, "amount"] = self.amount_sampler.sample()
            df.at[ts, "currency"] = "EUR"
            df.at[ts, "currency"] = "EUR"
            df.at[ts, "description"] = self.description
            df.at[ts, "type"] = "t"

        df["balance"] = df["amount"].cumsum()

        # add ibfb records

        ib = df.iloc[:1].copy()
        ib["balance"] = 0
        ib["amount"] = 0
        ib["type"] = "ib"
        fb = df.iloc[-1:].copy()
        fb["amount"] = 0
        fb["type"] = "fb"

        df = pd.concat([ib, df, fb])

        df.index.name = "timestamp"
        df.reset_index(inplace=True)

        transactions = Transactions(df)
        return transactions
    # transactions.check_consistency()


class SimulateTransactions:
    def __init__(self):
        self.transactions__samplers = []

    def add(self, transactions_sampler):
        self.transactions__samplers.append(transactions_sampler)
        return self

    # adding two objects
    def __add__(self, sampler):
        return self.add(sampler)

    def sample(self):
        dfs = []
        for sampler in self.transactions__samplers:
            dfs.append(sampler.sample().df)

        # merge, making union and not skipping overlapping
        # timestamp intervals as in Transactions.merge

        df = pd.concat(dfs)

        ib = df.iloc[:1].copy()
        ib["timestamp"] = df[df.type == "ib"]["timestamp"].min()
        ib["balance"] = df[df.type == "ib"]["balance"].sum()
        ib["description"] = ""
        fb = df.iloc[-1:].copy()
        fb["timestamp"] = df[df.type == "fb"]["timestamp"].min()
        fb["description"] = ""

        df = df[df.type == "t"].sort_values(by="timestamp", ascending=True)

        df = pd.concat([ib, df, fb]).reset_index(drop=True)

        df["balance"] = df.iloc[0]["balance"] + df["amount"].cumsum()

        return Transactions(df)


class SimulateAccount:

    def __init__(self, config, name, transactions, labels):
        self.account = Account(config, name, transactions, labels)
        self.account.description = "Simulation"
