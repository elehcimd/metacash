from metacash.configuration import Configuration
from metacash.readers.inbank import InBankCSV
import logging


def test_load():
    config = Configuration("fixtures/dataset1/config.py")
    config.describe()

    # verify that we've loaded three accounts
    assert list(config["accounts"].keys()) == ['iban1', 'iban2', 'prepaid1']

    # test that we can define programmtically the importer
    assert config["accounts"]["iban1"]["input"]["reader"] == InBankCSV.read
