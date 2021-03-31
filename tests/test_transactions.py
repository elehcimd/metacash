from metacash.readers.inbank import InBankCSV
from metacash.readers.metacash import MetaCashCSV
from metacash.configuration import Configuration
import glob
from metacash.transactions import Transactions, TimestampsGapError

import metacash
import tempfile
import os

# chdir to project directory
os.chdir(os.path.dirname(metacash.__file__) + "/../")


def test_to_csv():
    config = Configuration("fixtures/dataset1/config.py")
    pathnames = config.account_input_pathnames("iban1")

    transactions = InBankCSV.read(pathnames[0])
    transactions.print()

    tmp_pathname = tempfile.mkstemp()[1]

    transactions.to_csv(tmp_pathname)

    transactions = MetaCashCSV.read(tmp_pathname)
    transactions.print()

    os.unlink(tmp_pathname)


def test_merge_fail_timestamps_gap():
    config = Configuration("fixtures/dataset1/config.py")
    pathnames = config.account_input_pathnames("iban1")

    transactions1 = InBankCSV.read(pathnames[0])
    transactions2 = InBankCSV.read(pathnames[1])

    try:
        transactions12 = Transactions.merge([transactions1, transactions2])
    except TimestampsGapError:
        return
    else:
        raise Exception("Exception not raised")


def test_merge_timestamps_no_gap():
    config = Configuration("fixtures/dataset1/config.py")
    pathnames = config.account_input_pathnames("iban2")

    transactions1 = InBankCSV.read(pathnames[0])
    transactions2 = InBankCSV.read(pathnames[1])

    transactions12 = Transactions.merge([transactions1, transactions2])

    transactions12.print()
