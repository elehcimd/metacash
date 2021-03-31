from logging import debug

import pandas as pd

from metacash.account import Account
from metacash.configuration import Configuration
from metacash.log import Log
from metacash.meta import Meta
from metacash.transactions import Transactions


class MetaCash:
    def __init__(self, config_pathname):
        self.config_pathname = config_pathname
        self.reload()

    def reload(self):
        self.config = Configuration(self.config_pathname)
        self.accounts = {}

        Log.init(self.config["logging_level"])
        debug(f"Logging level set to {Log.level_to_name[self.config['logging_level']]}")

        #        pd.options.display.float_format = self.config["float_format"].format
        #        debug(f"Float format set to {self.config['float_format']}")

        # load accounts
        for name in self.config["accounts"].keys():
            self.accounts[name] = Account.load_regular(self.config, name)

    def overview(self):
        for account in self.accounts.values():
            account.overview()

    def drop(self, account_name):
        del self.accounts[account_name]
        return self

    def retain(self, account_name):
        self.accounts = {account_name: self.accounts[account_name]}
        return self

    def get_transactions_agg(self):
        dfs = []
        for name in self.config["accounts"].keys():
            df = self.accounts[name].df()
            df["account"] = name
            dfs.append(df)
        df = pd.concat(dfs).sort_values(by="timestamp", ascending=True)
        return Transactions(df)

    def meta(self):
        return Meta.build(self.config, self.accounts)

    def add_meta(self):
        self.accounts["meta"] = self.meta()
        return self

    def format_float(self, x):
        x = round(x, self.config["float_decimal_precision"])
        return self.config["float_format"].format(x)
