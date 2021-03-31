from metacash.metacash import MetaCash
from numpy.testing import assert_almost_equal


def test_load_iban2():
    myf = MetaCash("fixtures/dataset1/config-no-errors.py")
    print(myf.accounts["iban2"].df())
    assert_almost_equal(myf.accounts["iban2"].balance(), 60000.0)


def test_load_prepaid1():
    myf = MetaCash("fixtures/dataset1/config-no-errors.py")
    print(myf.accounts["prepaid1"].df())
    assert_almost_equal(myf.accounts["prepaid1"].balance(), 3000.0)

