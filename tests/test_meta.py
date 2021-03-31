from metacash.metacash import MetaCash
from metacash.meta import Meta, ConsistencyError
from numpy.testing import assert_almost_equal
from metacash.account import Account

def test_meta_build_exception():
    myf = MetaCash("fixtures/dataset1/config-no-errors.py")
    try:
        Meta.build(myf.config, myf.accounts)
    except ConsistencyError:
        return
    else:
        raise Exception("Exception not raised")


def test_meta_build():
    myf = MetaCash("fixtures/dataset1/config-meta-simple.py")
    account = Meta.build(myf.config, myf.accounts)

    # check that initial,final balance matches what's in the accounts
    initial_balance = sum([account.transactions.balance(initial=True) for account in myf.accounts.values()])
    final_balance = sum([account.transactions.balance(final=True) for account in myf.accounts.values()])

    assert_almost_equal(account.transactions.balance(initial=True), initial_balance)
    assert_almost_equal(account.balance(), final_balance)

    print(account.df())
