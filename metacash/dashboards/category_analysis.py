import ipywidgets as widgets
from IPython.display import display, clear_output

from metacash.dashboards.dashboard_widget import DashboardWidget
from metacash.dashboards.plots import barplot_monthly
from metacash.dashboards.utils import display_df


class Widgets:

    def __init__(self, category_analysis):
        self.category_analysis = category_analysis

        # w_tab requires the other widgets to be already registered,
        # so skip it and register it explicitly.
        self.reg = {}
        DashboardWidget.init(self, skip=[self.w_tab])
        self.reg[self.w_tab] = self.w_tab()

    def w_select_category(self):
        df = self.category_analysis.select_transactions.get_transactions().copy()
        df = df.groupby("label.category").agg({"amount": "sum"})
        df["amount_abs"] = df["amount"].abs()
        df = df.sort_values(by="amount_abs", ascending=False)
        categories = df.index.tolist()

        w = widgets.ToggleButtons(
            options=categories,
            description='Category:',
            disabled=False,
            button_style=''
        )

        def onchange(change):
            if change["type"] == "change" and change["name"] == "value":
                self.category_analysis.run_overview()

        w.observe(onchange)

        return w

    def w_tab(self):
        w = widgets.Tab(children=[
            self.reg[self.w_plot_category],
            self.reg[self.w_tabular],
        ],
            layout=widgets.Layout(overflow_y='auto'))

        w.set_title(0, "Plot")
        w.set_title(1, "Tabular")
        return w

    def w_plot_category(self):
        w = widgets.Output()
        return w

    def w_tabular(self):
        w = widgets.Output(layout=widgets.Layout(height='400px', overflow_y='auto'))
        return w

    def get_category_name(self):
        return self.reg[self.w_select_category].value

    def display(self):
        display(self.reg[self.w_select_category])
        display(self.reg[self.w_tab])
        self.category_analysis.run_overview()


class CategoryAnalysis:
    def __init__(self, select_transactions):
        self.select_transactions = select_transactions
        self.widgets = Widgets(self)
        self.myf = select_transactions.myf

    def display(self):
        self.widgets.display()

    def run_overview(self):
        df = self.select_transactions.get_transactions()
        category_name = self.widgets.get_category_name()

        with self.widgets.reg[self.widgets.w_plot_category]:
            clear_output()
            barplot_monthly(self.myf.config, df, "amount", "Monthly amount", category_name=category_name,
                            show_cumulative=True)

        with self.widgets.reg[self.widgets.w_tabular]:
            clear_output()
            df = df[df["label.category"] == category_name]
            display_df(self.myf.config, df)
