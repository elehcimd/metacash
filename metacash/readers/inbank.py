import json
import os
import re
from datetime import datetime

import pandas as pd

from metacash.transactions import Transactions


class InBankCSV:

    @staticmethod
    def add_balance(df, pathname):
        json_pathname = os.path.splitext(pathname)[0] + ".json"

        with open(json_pathname) as f:
            data = json.load(f)

        assert "initial_balance" in data or "final_balance" in data
        assert not ("initial_balance" in data and "final_balance" in data)

        initial_balance = data.get("initial_balance", None)
        final_balance = data.get("final_balance", None)

        timestamp_begin = datetime.strptime(data["timestamp_begin"], "%d/%m/%Y")
        timestamp_end = datetime.strptime(data["timestamp_end"], "%d/%m/%Y")

        # todo: this seems to break tests. investigate.
        # consider only transactions within the specified timestamp interval
        # df = df[(df.timestamp >= timestamp_begin) & (df.timestamp <= timestamp_begin)]

        # Normalize up transaction description
        df["description"] = df["description"].apply(lambda x: re.sub(' +', ' ', x).strip())

        # create first, last rows for balance
        df_balance_initial = pd.DataFrame([{"timestamp": timestamp_begin,
                                            "amount": 0,
                                            "currency": "EUR",
                                            "description": "Initial balance"
                                            }], columns=Transactions.columns)

        df_balance_final = pd.DataFrame([{"timestamp": timestamp_end,
                                          "amount": 0,
                                          "currency": "EUR",
                                          "description": "Final balance"
                                          }], columns=Transactions.columns)

        df = pd.concat([df_balance_initial, df, df_balance_final])

        df["type"] = "t"
        df["type"].iat[0] = "ib"
        df["type"].iat[-1] = "fb"
        df["description"].iat[0] = "Initial balance"
        df["description"].iat[-1] = "Final balance"

        if final_balance is not None:
            # Cumulative sum (balance up to transaction included)
            # operations are reversed, so we need to change the sign and eval the cumulative sum from the bottom
            s_amount = df["amount"] * -1
            s_amount.iat[-1] = final_balance
            s_balance = s_amount.loc[::-1].cumsum()[::-1]
            initial_balance = s_balance.iat[0]

        # Cumulative sum (balance up to transaction included)
        df["amount"].iat[0] = initial_balance
        df["balance"] = df["amount"].cumsum()
        df["amount"].iat[0] = 0

        # Reorder and select columns
        df = df[Transactions.columns]

        # reset index
        df.reset_index(inplace=True, drop=True)

        meta = {"pathname": pathname}

        return Transactions(df, meta)

    @classmethod
    def read(cls, pathname):
        # Read transactions

        df = pd.read_csv(pathname,
                         sep=";",
                         parse_dates=['DATA'],
                         date_parser=lambda x: datetime.strptime(x, "%d/%m/%Y"),
                         thousands='.',
                         decimal=",")

        df.rename(columns={"DATA": "timestamp", "DARE": "withdrawals", "AVERE": "deposits", "Unnamed: 4": "currency",
                           "DESCRIZIONE OPERAZIONE": "description"}, inplace=True)
        df = df[["timestamp", "withdrawals", "deposits", "currency", "description"]]
        df["withdrawals"].fillna(0, inplace=True)
        df["deposits"].fillna(0, inplace=True)

        # Money moved, either in (positive) or out (negative)
        df["amount"] = df["deposits"] - df["withdrawals"]

        # Normalize up transaction description
        df["description"] = df["description"].apply(lambda x: re.sub(' +', ' ', x).strip())

        # drop rows with saldo iniziale, liquido, contabile
        df = df[~df["description"].isin(["Saldo iniziale", "Saldo liquido", "Saldo contabile"])]

        # Verify that all transactions are in one currency, EUR
        assert df["currency"].drop_duplicates().tolist() == ['EUR']

        return cls.add_balance(df, pathname)


class InBankPrepaidCSV:

    @classmethod
    def read(cls, pathname):
        # Read transactions

        df = pd.read_csv(pathname,
                         sep=";",
                         parse_dates=['DATA'],
                         date_parser=lambda x: datetime.strptime(x, "%d/%m/%Y - %H:%M"),
                         thousands='.',
                         decimal=",")

        df.rename(
            columns={"DATA": "timestamp", "DARE": "withdrawals", "AVERE": "deposits", "DESCRIZIONE": "description"},
            inplace=True)

        def is_eur(row):

            s_withdrawals = str(row["withdrawals"])
            s_deposits = str(row["deposits"])

            if "€" in s_withdrawals or "€" in s_deposits:
                return "EUR"
            else:
                return None

        df["currency"] = df.apply(lambda row: is_eur(row), axis=1)

        def extract_amount(row):
            """
            Example for withdrawals: "- 25,00 €"
            Example for deposits: "+ 1.000,00 €"
            """

            # one of these two is nan, the other contains the value with sign
            if row["withdrawals"] == row["withdrawals"]:
                v = row["withdrawals"]
            else:
                v = row["deposits"]

            # extract amount as float
            v = float(v[:-1].replace("- ", "-").replace("+ ", "+").replace(".", "").replace(",", "."))
            return v

        df["amount"] = df.apply(lambda row: extract_amount(row), axis=1)

        return InBankCSV.add_balance(df, pathname)
