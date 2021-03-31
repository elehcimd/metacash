import os

import metacash
from metacash.configuration import Configuration
from metacash.readers.paypal import PayPalCSV

# chdir to project directory
os.chdir(os.path.dirname(metacash.__file__) + "/../")


def test_paypal_csv():
    config = Configuration("fixtures/dataset2/config.py")
    pathnames = config.account_input_pathnames("paypal1")
    print(pathnames)
    transactions = PayPalCSV.read(pathnames[0])
    transactions.print()
