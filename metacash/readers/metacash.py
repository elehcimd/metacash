import pandas as pd

from metacash.transactions import Transactions


class MetaCashCSV:

    @staticmethod
    def read(pathname):
        # Read transactions

        df = pd.read_csv(pathname)

        df.description.fillna("", inplace=True)

        meta = {
            "pathname": pathname
        }

        return Transactions(df, meta)
