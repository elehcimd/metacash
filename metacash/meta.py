import pandas as pd

from metacash.account import Account
from metacash.labels import Labels
from metacash.transactions import Transactions


class ConsistencyError(Exception):
    pass


class Meta:

    @classmethod
    def build(cls, config, accounts):

        # make sure that all accounts have the same set of label columns.
        colnames_labels = set(next(iter(accounts.values())).labels.df.columns)
        for name, account in accounts.items():
            if set(account.labels.df.columns) != colnames_labels:
                raise ConsistencyError(
                    f"Account {name} has different set of columns label.*: {colnames_labels} != {set(account.labels.df.columns)}")

        # collect transactions and labels from the accounts
        dfs_transactions = []
        dfs_labels = []

        for name, account in accounts.items():
            if name == "meta":
                # self! skip it
                continue

            # we make copies of transactions and labels to not alter them.
            # e.g., not adding account_name column.
            df_transactions = account.transactions.df.copy()
            df_transactions["account_name"] = name
            dfs_transactions.append(df_transactions)

            df_labels = account.labels.df.copy()
            dfs_labels.append(df_labels)

        # concatenate transactions and reset index, so that it is consistent for both transactions and labels
        df_transactions = pd.concat(dfs_transactions, ignore_index=True).reset_index(drop=True)
        df_labels = pd.concat(dfs_labels, ignore_index=True).reset_index(drop=True)

        # the initial balance is the sum of all records representing initial balances, one for each aggregated account
        initial_balance = df_transactions[df_transactions["type"] == "ib"]["balance"].sum()

        # let's create the ibfb records (dataframes of one row)
        row_ib_transactions = df_transactions.iloc[:1].copy()
        row_fb_transactions = df_transactions.iloc[-1:].copy()
        row_ib_transactions["timestamp"] = df_transactions.timestamp.min()
        row_ib_transactions["account_name"] = "meta"
        row_fb_transactions["timestamp"] = df_transactions.timestamp.max()
        row_fb_transactions["account_name"] = "meta"

        # ...we do this also for the labels, they're all nans but easier here then later
        row_ib_labels = df_labels.iloc[:1].copy()
        row_fb_labels = df_labels.iloc[-1:].copy()

        # we drop all ibfb records from both dataframes. we do this by index
        index_drop = df_transactions[df_transactions.type != "t"].index
        df_transactions.drop(index=index_drop, inplace=True)
        df_labels.drop(index=index_drop, inplace=True)

        # sort transactions by timestamp, and update also the ordering of labels to make it consistent
        df_transactions.sort_values(by=["timestamp", "account_name"], inplace=True)
        df_labels = df_labels.loc[df_transactions.index]

        # now, let's add back the ibfb records
        df_transactions = pd.concat([row_ib_transactions, df_transactions, row_fb_transactions],
                                    ignore_index=True).reset_index(drop=True)
        df_labels = pd.concat([row_ib_labels, df_labels, row_fb_labels], ignore_index=True).reset_index(
            drop=True).reset_index(drop=True)

        df_transactions["amount"].iat[0] = initial_balance
        df_transactions["balance"] = df_transactions["amount"].cumsum()
        df_transactions["amount"].iat[0] = 0

        transactions = Transactions(df_transactions)
        labels = Labels(transactions, df_labels)

        account = Account(config, "meta", transactions, labels)
        account.description = "Meta"
        return account
