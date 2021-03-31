import re
from datetime import datetime

import pandas as pd

from metacash.readers.inbank import InBankCSV


class InBankOperatorCSV:

    @classmethod
    def read(cls, pathname):
        # Read transactions

        df = pd.read_csv(pathname,
                         sep=";",
                         parse_dates=['Data operazione'],
                         date_parser=lambda x: datetime.strptime(x, "%d/%m/%Y") if not x.startswith("0001") else pd.NaT,
                         thousands='.',
                         decimal=",")

        df["description"] = df["Descrizione causale"] + " " + \
                            df["Descrizione movimento 1"] + " " + \
                            df["Descrizione movimento 2"] + " " + \
                            df["Descrizione movimento 3"] + " " + \
                            df["Descrizione movimento 4"] + \
                            df["Descrizione movimento 5"] + \
                            df["Descrizione movimento 6"]

        df.rename(columns={"Data operazione": "timestamp", "Importo": "amount", "Divisa": "currency"}, inplace=True)
        df = df[["timestamp", "amount", "currency", "description"]]

        # Normalize up transaction description
        df["description"] = df["description"].apply(lambda x: re.sub(' +', ' ', x).strip())

        # drop first and last rows containing balance
        df = df[~(df["description"].str.startswith("SALDO CONTABILE"))]

        # Verify that all transactions are in one currency, EUR
        assert df["currency"].drop_duplicates().tolist() == ['EUR']

        return InBankCSV.add_balance(df, pathname)
