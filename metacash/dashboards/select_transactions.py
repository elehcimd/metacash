import datetime

import ipywidgets as widgets
from IPython.display import display
from dateutil.relativedelta import relativedelta

from metacash.dashboards.dashboard_widget import DashboardWidget


class Widgets:

    def __init__(self, select_transactions):
        self.select_transactions = select_transactions
        self.myf = select_transactions.myf
        DashboardWidget.init(self)

    def w_select_account(self):
        account_names = list(self.myf.accounts.keys())

        w = widgets.Dropdown(
            options=account_names,
            value=account_names[0],
            description='Account:',
            disabled=False,
        )

        def onchange(change):
            if change["type"] == "change" and change["name"] == "value":
                self.update_dates()

        w.observe(onchange)

        return w

    def w_select_dates(self):
        options = ["Last month", "Last 2 months", "Last 3 months", "Last 6 months", "Last 12 months",
                   "Last 24 months", "Widest", "Custom"]

        w = widgets.Dropdown(
            options=options,
            value=options[0],
            description='Interval:',
            disabled=False,

        )

        def onchange(change):
            if change["type"] == "change" and change["name"] == "value":
                if w.value == "Custom":
                    self.reg[self.w_select_date_begin].disabled = False
                    self.reg[self.w_select_date_end].disabled = False
                else:
                    self.reg[self.w_select_date_begin].disabled = True
                    self.reg[self.w_select_date_end].disabled = True
                self.update_dates()

        w.observe(onchange)

        return w

    def w_select_date_begin(self):
        w = widgets.DatePicker(
            description='Begin:',
            disabled=True,
            layout=widgets.Layout(height="auto")
        )

        def onchange(change):
            if change["type"] == "change" and change["name"] == "value":
                self.reg[self.w_select_date_begin].value = datetime.datetime.combine(
                    self.reg[self.w_select_date_begin].value,
                    datetime.datetime.min.time())

        w.observe(onchange)

        return w

    def w_select_date_end(self):
        w = widgets.DatePicker(
            description='End:',
            disabled=True,
            layout=widgets.Layout(height="auto")
        )

        def onchange(change):
            if change["type"] == "change" and change["name"] == "value":
                self.reg[self.w_select_date_end].value = datetime.datetime.combine(
                    self.reg[self.w_select_date_end].value,
                    datetime.datetime.min.time())

        w.observe(onchange)

        return w

    def update_dates(self):

        account_name = self.reg[self.w_select_account].value
        begin_timestamp = self.myf.accounts[account_name].transactions.df.iloc[0]["timestamp"]
        end_timestamp = self.myf.accounts[account_name].transactions.df.iloc[-1]["timestamp"]

        if self.reg[self.w_select_dates].value == "Custom":
            if self.reg[self.w_select_date_end].value is None:
                self.reg[self.w_select_date_end].value = end_timestamp
            if self.reg[self.w_select_date_begin].value is None:
                self.reg[self.w_select_date_begin].value = begin_timestamp
        elif self.reg[self.w_select_dates].value == "Widest":
            self.reg[self.w_select_date_end].value = end_timestamp
            self.reg[self.w_select_date_begin].value = begin_timestamp
        elif self.reg[self.w_select_dates].value == "Last month":
            self.reg[self.w_select_date_end].value = end_timestamp
            self.reg[self.w_select_date_begin].value = end_timestamp - relativedelta(months=1)
        elif self.reg[self.w_select_dates].value == "Last 2 months":
            self.reg[self.w_select_date_end].value = end_timestamp
            self.reg[self.w_select_date_begin].value = end_timestamp - relativedelta(months=2)
        elif self.reg[self.w_select_dates].value == "Last 3 months":
            self.reg[self.w_select_date_end].value = end_timestamp
            self.reg[self.w_select_date_begin].value = end_timestamp - relativedelta(months=3)
        elif self.reg[self.w_select_dates].value == "Last 6 months":
            self.reg[self.w_select_date_end].value = end_timestamp
            self.reg[self.w_select_date_begin].value = end_timestamp - relativedelta(months=6)
        elif self.reg[self.w_select_dates].value == "Last 12 months":
            self.reg[self.w_select_date_end].value = end_timestamp
            self.reg[self.w_select_date_begin].value = end_timestamp - relativedelta(months=12)
        elif self.reg[self.w_select_dates].value == "Last 24 months":
            self.reg[self.w_select_date_end].value = end_timestamp
            self.reg[self.w_select_date_begin].value = end_timestamp - relativedelta(months=24)

        # make sure that we're within the bounds of the transactions table for the selected account
        self.reg[self.w_select_date_begin].value = max(self.reg[self.w_select_date_begin].value, begin_timestamp)
        self.reg[self.w_select_date_end].value = min(self.reg[self.w_select_date_end].value, end_timestamp)

    def display(self):
        grid = widgets.GridspecLayout(5, 1)
        grid[0, 0] = self.reg[self.w_select_account]
        grid[1, 0] = self.reg[self.w_select_dates]
        grid[2, 0] = self.reg[self.w_select_date_begin]
        grid[3, 0] = self.reg[self.w_select_date_end]
        display(grid)
        self.update_dates()

    def get_dates(self):
        return (self.reg[self.w_select_date_begin].value, self.reg[self.w_select_date_end].value)

    def get_account_name(self):
        return self.reg[self.w_select_account].value


class SelectTransactions:

    def __init__(self, myf):
        self.myf = myf
        self.ts_begin = None
        self.ts_end = None
        self.account_name = None
        self.widgets = Widgets(self)

    def display(self):
        self.widgets.display()

    def update_selection(self):
        self.widgets.update_dates()
        self.ts_begin, self.ts_end = self.widgets.get_dates()
        self.account_name = self.widgets.get_account_name()

        if self.ts_begin is None:
            return False
        if self.ts_end is None:
            return False
        if self.account_name is None:
            return False

        return True

    def get_transactions(self):
        if not self.update_selection():
            return None
        else:
            account = self.myf.accounts[self.account_name]
            return account.df(ts_begin=self.ts_begin, ts_end=self.ts_end).copy()
