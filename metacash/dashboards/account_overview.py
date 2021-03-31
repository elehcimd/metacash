from logging import info

import ipywidgets as widgets
from IPython.display import display, clear_output

from metacash.dashboards.category_analysis import CategoryAnalysis
from metacash.dashboards.dashboard_widget import DashboardWidget
from metacash.dashboards.plots import barplot_categories
from metacash.dashboards.plots import barplot_monthly, barplot_categories_percentage
from metacash.dashboards.select_transactions import SelectTransactions
from metacash.dashboards.utils import display_df


class Widgets:

    def __init__(self, account_overview):
        self.account_overview = account_overview
        self.myf = account_overview.myf

        # w_tab requires the other widgets to be already registered,
        # so skip it and register it explicitly.
        self.reg = {}
        DashboardWidget.init(self, skip=[self.w_tab])
        self.reg[self.w_tab] = self.w_tab()

    def w_run_overview(self):
        w = widgets.Button(
            description="Overview",
            layout=widgets.Layout(width='auto', height="auto"))

        def onclick(_):
            self.account_overview.run_overview()

        w.on_click(onclick)

        return w

    def w_tab(self):
        w = widgets.Tab(children=[
            self.reg[self.w_log],
            self.reg[self.w_transactions],
            self.reg[self.w_plot_inout],
            self.reg[self.w_plot_balance],
            self.reg[self.w_plot_categories],
            self.reg[self.w_plot_agg_category]
        ],
            layout=widgets.Layout(overflow_y='auto'))  # height='500px',

        w.set_title(0, "Messages")
        w.set_title(1, "Transactions")
        w.set_title(2, "Monthly amount")
        w.set_title(3, "Monthly balance")
        w.set_title(4, "Monthly categories")
        w.set_title(5, "Categories")

        return w

    def w_log(self):
        w = widgets.Output()
        return w

    def w_transactions(self):
        w = widgets.Output(layout=widgets.Layout(height='400px', overflow_y='auto'))

        return w

    def w_plot_agg_category(self):
        w = widgets.Output()
        return w

    def w_plot_categories(self):
        w = widgets.Output()
        return w

    def w_plot_inout(self):
        w = widgets.Output()
        return w

    def w_plot_balance(self):
        w = widgets.Output()
        return w

    def w_category_analysis(self):
        w = widgets.Output()
        return w

    def display(self):
        grid = widgets.GridspecLayout(1, 1)
        grid[0, 0] = self.reg[self.w_run_overview]
        display(grid)
        display(self.reg[self.w_tab])
        display(self.reg[self.w_category_analysis])


class AccountOverview:

    def __init__(self, myf):
        self.myf = myf
        self.select_transactions = SelectTransactions(myf)
        self.widgets = Widgets(self)

    def display(self):
        self.select_transactions.display()
        self.widgets.display()
        self.run_overview()

    def run_overview(self):
        # update selection parameters
        self.select_transactions.update_selection()

        account_name = self.select_transactions.account_name
        account = self.myf.accounts[account_name]
        ts_min = account.transactions.df.iloc[0].timestamp
        ts_max = account.transactions.df.iloc[-1].timestamp
        ts_begin = self.select_transactions.ts_begin
        ts_end = self.select_transactions.ts_end
        df_transactions = self.select_transactions.get_transactions()

        with self.widgets.reg[self.widgets.w_log]:
            clear_output()
            info(f"Name.................: {account_name}")
            info(f"Description..........: {account.description}")
            info(f"Balance..............: {account.config['float_format'].format(account.balance())}")
            info(f"Available period.....: {str(ts_min.date())}, {str(ts_max.date())}")
            info(f"Selected period......: {str(ts_begin.date())}, {str(ts_end.date())}")
            info(f"Transactions count...: {len(df_transactions)}")
        with self.widgets.reg[self.widgets.w_transactions]:
            clear_output()
            display_df(self.myf.config, df_transactions)

        with self.widgets.reg[self.widgets.w_plot_inout]:
            clear_output()
            barplot_monthly(self.myf.config, df_transactions, "amount", "Monthly amount",
                            show_cumulative=True)

        with self.widgets.reg[self.widgets.w_plot_balance]:
            clear_output()
            barplot_monthly(self.myf.config, df_transactions, "balance", "Monthly balance")

        with self.widgets.reg[self.widgets.w_plot_categories]:
            clear_output()
            barplot_categories_percentage(self.myf.config, df_transactions, "Monthly amount by category")

        with self.widgets.reg[self.widgets.w_plot_agg_category]:
            clear_output()
            barplot_categories(self.myf.config, df_transactions,
                               "Top-10 categories ordred by by absolute monthly amount")
            CategoryAnalysis(self.select_transactions).display()

        with self.widgets.reg[self.widgets.w_category_analysis]:
            clear_output()
