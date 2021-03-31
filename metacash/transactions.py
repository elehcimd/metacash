import glob
import logging
import os
from datetime import timedelta

import pandas as pd
from numpy.testing import assert_almost_equal


class TimestampsGapError(Exception):
    pass


class ConsistencyError(Exception):
    pass


class Transactions:
    columns = ["timestamp", "balance", "amount", "currency", "description", "type"]

    def __init__(self, df=None, meta={}):

        if df is None:
            self.df = pd.DataFrame(columns=Transactions.columns)
        else:
            self.df = df

        self.meta = meta

    def print(self):

        # make sure that we're on a new line
        print("")
        print(f"meta: {self.meta}")

        with pd.option_context('display.max_rows', None,
                               'display.max_columns', None,
                               'display.width', 200):
            print(self.df)

        print("")

    def balance(self, initial=False, final=False):

        # either initial or final
        assert initial ^ final

        idx = 0 if initial else -1

        return self.df.iloc[idx]["balance"]

    def to_csv(self, pathname):
        self.df.to_csv(pathname, index=False)

    def check_consistency(self, config):

        # ensure correct schema
        if list(self.df.columns) != Transactions.columns:
            raise ConsistencyError(f"Schema not correct: {self.df.columns} should be {Transactions.columns}")

        # check column type
        df_invalid = self.df[~self.df["type"].isin(["ib", "fb", "t"])]
        if len(df_invalid) > 0:
            raise Exception(f"Invalid values found in type column: {df_invalid['type'].tolist()}")

        # check that first, last row are initial, final balance, respectively.

        # we must at least have two rows
        if len(self.df) < 2:
            raise ConsistencyError("Transactions table length < 2")

        if self.df["type"].iloc[0] != "ib":
            raise ConsistencyError("First row type must be 'ib' (initial balance)")

        if self.df["type"].iloc[-1] != "fb":
            raise ConsistencyError("First row type must be 'fb' (final balance)")

        # all other rows must be of type 't', provided that there's at least one transaction
        if len(self.df) > 2:
            t = self.df[1:-1]["type"].drop_duplicates().tolist()
            if len(t) != 1 or t[0] != "t":
                raise ConsistencyError(f"Internal rows not always of type 't'. found types: {t}")

        # verify that currency is constant
        if len(self.df["currency"].drop_duplicates()) != 1:
            raise ConsistencyError(f"Rows with multiple currencies: {self.df['currency'].drop_duplicates().tolist()}")

        # verify ordered timestamps
        timestamp_prev = None
        for idx, row in self.df.iterrows():
            if idx == 0:
                timestamp_prev = row["timestamp"]
            else:
                if timestamp_prev > row["timestamp"]:
                    raise ConsistencyError(
                        f"Row at index {idx} has timestamp ({row['timestamp']}) preceding the timestamp \
                        of the previous row ({timestamp_prev})")
                timestamp_prev = row["timestamp"]

        # verify initial, final balance
        expected_end_balance = self.df["balance"].iloc[0] + self.df["amount"].sum()

        try:
            assert_almost_equal(self.df["balance"].iloc[-1], expected_end_balance,
                                decimal=config["float_decimal_precision"])
        except AssertionError:
            raise ConsistencyError(
                f"Expected end balance is {expected_end_balance} but found {self.df['balance'].iloc[-1]}")

        # verify balance column
        # Cumulative sum (balance up to transaction included)

        s_amount = self.df["amount"].copy()
        s_amount.iat[0] = self.df["balance"].iloc[0]
        s_balance = s_amount.cumsum()

        try:
            assert_almost_equal(s_balance.tolist(), self.df["balance"].tolist(),
                                decimal=config["float_decimal_precision"])
        except AssertionError as e:
            raise ConsistencyError(
                f"Balance column contains errors: {e}")

        try:
            assert_almost_equal((s_balance - self.df["balance"]).sum(), 0, decimal=config["float_decimal_precision"])
        except AssertionError as e:
            diff = (s_balance - self.df["balance"]).sum()
            diff = diff[diff != 0]
            logging.debug(f"Unexpected differences in balance column: {diff}")
            raise ConsistencyError(f"Balance column contains errors: {e}")

        # verify that there are no duplicates
        df_duplicates = self.df[self.df.duplicated()]
        if len(df_duplicates) > 0:
            raise ConsistencyError(f"Detected duplicate rows. First: {df_duplicates.iloc[0].tolist()}")

        assert len(self.df.drop_duplicates()) == len(self.df)

    @classmethod
    def read(cls, config, name):

        if type(config["accounts"][name]["input"]) == list:
            config_inputs = config["accounts"][name]["input"]
        else:
            config_inputs = [config["accounts"][name]["input"]]

        transactions_list = []

        for config_input in config_inputs:

            logging.debug(f"Loading config_input: {config_input}")

            reader = config_input["reader"]
            pathname_patterns = config_input["pathname"]

            # pathname_patterns could be a single pattern, or a list of patterns.
            # let's make sure that we do have a list.
            if type(pathname_patterns) != list:
                pathname_patterns = [pathname_patterns]

            pathnames = []

            for pathname_pattern in pathname_patterns:
                pathnames += glob.glob(config.base_dir + os.sep + pathname_pattern, recursive=True)

            logging.debug(f"Loaded pathname patterns: {pathname_patterns}")
            logging.debug(f"Matching pathnames: {pathnames}")

            if len(pathnames) == 0:
                # make sure that there's at least one matching pathname ...
                raise ConsistencyError(f"No matches for pathname patterns {pathname_patterns}")

            transactions_list += [reader(pathname) for pathname in pathnames]

        # check consistency of transactions. it's done here and not inside the constructor
        # of Transactions to avoid the dependency to the `config` parameter.
        for transactions in transactions_list:
            transactions.check_consistency(config)

        for transactions in transactions_list:
            # round floats to desired precision and make sure that -zeros as zeros.
            # transform negative zeros to zeros, if any (adding 0 to -0 results in 0)
            # if it's not just the sign bit, then it will remain rendered as -0.00.
            transactions.df["balance"] = transactions.df["balance"].round(
                decimals=config.data["float_decimal_precision"])
            transactions.df["amount"] = transactions.df["amount"].round(decimals=config.data["float_decimal_precision"])
            transactions.df["balance"] += 0
            transactions.df["amount"] += 0

        return cls.merge(transactions_list)

    @classmethod
    def merge(cls, transactions_list):

        # the merged dataframe is constructed iteratively from the leftmost interval.
        # if gaps are found, an error is raised.

        # sort in place by starting timestamp
        list.sort(transactions_list, key=lambda x: x.df["timestamp"].iloc[0])

        # the first df is always part of the solution
        concat_dfs = []

        for i in range(len(transactions_list)):
            # timestamp interval of transactions under consideration
            ts_begin = transactions_list[i].df["timestamp"].iloc[0]
            ts_end = transactions_list[i].df["timestamp"].iloc[-1]

            if i == 0:
                # the first df is always part of the solution
                concat_dfs.append(transactions_list[i].df)

                logging.debug(
                    f"Initial merge transactions: {[str(ts_begin), str(ts_end)]}")

            else:
                # timestamp interval of transactions selected for merge
                concat_begin = concat_dfs[0]["timestamp"].iloc[0]
                concat_end = concat_dfs[-1]["timestamp"].iloc[-1]

                df = transactions_list[i].df

                logging.debug(
                    f"Merging transactions: {[str(concat_begin), str(concat_end)]} @ {[str(ts_begin), str(ts_end)]}")

                # if timestamp interval already past the latest timestamp interval
                # in transactions selected for merge, ignore
                if ts_end <= concat_end:
                    continue

                # if timestamp interval causing a gap with existing transactions
                # selected for merge, raise error
                if concat_end + timedelta(days=1) < ts_begin:
                    raise TimestampsGapError(
                        f"There is a gap between transactions selected for merge ({[concat_begin, concat_end]}) and the transactions ({[ts_begin, ts_end]} from {transactions_list[i].meta['pathname']}")

                # if we reached this point, we know that there's no gap. therefore,
                # select transactions past the timestamp `concat_end` and append them for concatenation.
                concat_dfs.append(df[df["timestamp"] > concat_end])

        # concatenate transactions

        df = pd.concat(concat_dfs)
        df_begin = df.iloc[:1]
        df_t = df[df["type"] == "t"]
        df_end = df.iloc[-1:]
        df = pd.concat([df_begin, df_t, df_end]).reset_index(drop=True)

        return cls(df)
