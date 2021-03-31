import os
import re
from logging import info

import numpy as np
import pandas as pd


class ConsistencyError(Exception):
    pass


class Labeling:
    columns = ["pattern", "label"]

    def check_consistency(self):
        if list(self.df_patterns.columns) != Labeling.columns:
            raise ConsistencyError(f"Expected columns {Labeling.columns} but found {list(self.df_patterns.columns)}")

    @classmethod
    def loadPathname(cls, patterns_pathname):
        df = pd.read_csv(patterns_pathname)
        return cls(df)

    def __init__(self, df):
        self.df_patterns = df
        self.check_consistency()

    def label(self, transactions_df):
        s_labels = pd.Series([np.nan] * len(transactions_df), index=transactions_df.index)

        for idx, row in self.df_patterns.iterrows():
            s_labels.loc[transactions_df["description"].str.match(
                row["pattern"].strip(), flags=re.IGNORECASE)] = row["label"].strip()

        # label "unknown" forced to remaining unlabeled transactions
        s_labels.fillna("unknown", inplace=True
                        )
        return s_labels


class Labels:

    @classmethod
    def loadRegular(cls, config, account_name, transactions):

        labels = {}

        if "labeling" in config["accounts"][account_name]:
            for name, pathname in config["accounts"][account_name]["labeling"].items():
                labels[f"label.{name}"] = Labeling.loadPathname(config.base_dir + os.sep + pathname).label(
                    transactions.df)

        df_labels = pd.DataFrame(labels)

        return cls(transactions, df_labels)

    @classmethod
    def load_df(cls, transactions, labels_patterns):

        labels = {}
        for name, patterns in labels_patterns.items():
            labels[f"label.{name}"] = Labeling(patterns).label(transactions.df)

        df_labels = pd.DataFrame(labels)
        return cls(transactions, df_labels)

    def __init__(self, transactions, df_labels):
        self.transactions = transactions
        self.df = df_labels

    def debug_missing(self):
        df = self.transactions.df.merge(self.df, left_index=True, right_index=True)
        df = df[(df["label.category"] == "unknown") | (df["label.type"] == "unknown")].reset_index(drop=True)

        info(f"Found {len(df)} unknown transactions")
        return df
