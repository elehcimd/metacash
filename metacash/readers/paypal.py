from datetime import datetime

import pandas as pd

from metacash.readers.inbank import InBankCSV


class PayPalCSV:

    @staticmethod
    def read(pathname):
        # Read transactions

        df = pd.read_csv(pathname,
                         parse_dates=['Date'],
                         date_parser=lambda x: datetime.strptime(x, "%d/%m/%Y"),
                         thousands=',',
                         decimal="."
                         )

        df.rename(columns={"Date": "timestamp", "Currency": "currency", "Net": "amount"}, inplace=True)
        df["type"] = "t"

        df = df[df["Status"] == "Completed"]

        # TODO handle currencies
        df["currency"] = "EUR"

        def extract_description(row):
            description = ""
            columns = ["Transaction ID", "Name", "Type", "From Email Address", "Item Title", "Invoice Number",
                       "Subject", "Note"]

            for column in columns:
                if str(row[column]) != "nan":
                    description += f"{column}:{row[column]} "

            return description.strip()

        df["description"] = df.apply(lambda row: extract_description(row), axis=1)

        # currency conversions

        return InBankCSV.add_balance(df, pathname)
