from io import StringIO

import pandas as pd
from numpy.testing import assert_almost_equal

from metacash.labels import Labels
from metacash.metacash import MetaCash
from metacash.simulation.sim_transactions import SimulateAccount
from metacash.simulation.sim_transactions import SimulateTransactions, TimestampSampler, TransactionsSampler, \
    AmountSampler


def test_sampler_range1():
    tss = TimestampSampler.date_range(start="2018-01-01 00:17:00", end="2018-01-08 00:06:00")
    print(tss.index)
    assert str(tss.index[0]) == "2018-01-01 00:00:00"
    assert str(tss.index[-1]) == "2018-01-07 00:00:00"


def test_sampler_range_monthly():
    tss = TimestampSampler.date_range(start="2020-01-01", periods=6, freq='MS')
    print(tss.index)


def test_sampler_range_weekly():
    tss = TimestampSampler.date_range(start="2020-01-01", periods=4, freq='W-WED')
    print(tss.index)


def test_income():
    sim = SimulateTransactions()

    ts_sampler = TimestampSampler.date_range(start="2020-01-01", periods=12, freq='MS')
    amount_sampler = AmountSampler(3000.00)
    income_sampler = TransactionsSampler(ts_sampler, amount_sampler, "income")
    print()
    print(income_sampler.sample().df)


def test_housing():
    ts_sampler = TimestampSampler.date_range(start="2020-01-01", periods=12, freq='MS')
    amount_sampler = AmountSampler(-1400.00)
    housing_sampler = TransactionsSampler(ts_sampler, amount_sampler, "income")
    print()
    print(housing_sampler.sample().df)


def test_typical_month():
    ts_sampler = TimestampSampler.date_range(start="2020-01-01", periods=12, freq='MS')
    sim = SimulateTransactions()
    sim += TransactionsSampler(ts_sampler, AmountSampler(-1400.00), description="housing")
    sim += TransactionsSampler(ts_sampler, AmountSampler(-850.00), description="health")
    sim += TransactionsSampler(ts_sampler, AmountSampler(-200.00), description="food")
    sim += TransactionsSampler(ts_sampler, AmountSampler(-100.00), description="income")
    sim += TransactionsSampler(ts_sampler, AmountSampler(2600.00), description="income")
    transactions = sim.sample()
    print()
    print(transactions.df)

    assert_almost_equal(transactions.df.iloc[-1]["balance"], 600.0)


def test_account():
    myf = MetaCash("fixtures/dataset1/config-no-errors.py")
    print(myf.accounts["iban2"].df())
    assert_almost_equal(myf.accounts["iban2"].balance(), 60000.0)

    ts_sampler = TimestampSampler.date_range(start="2020-01-01", periods=12, freq='MS')
    sim = SimulateTransactions()
    sim += TransactionsSampler(ts_sampler, AmountSampler(-1400.00), description="housing")
    transactions = sim.sample()

    df_patterns = pd.read_csv(StringIO("""pattern;label
        housing;housing 
        """), sep=";")

    patterns_dfs = {"category.label": df_patterns}
    labels = Labels.load_df(transactions, patterns_dfs)
    account = SimulateAccount(myf.config, "simulation", transactions, labels).account
    print(account.df())

# print()
# account.overview()
