from metacash.labels import Labeling
from metacash.configuration import Configuration
from metacash.readers.inbank import InBankCSV
from metacash.metacash import MetaCash
import os

import metacash

# chdir to project directory
os.chdir(os.path.dirname(metacash.__file__) + "/../")


def test_labeling():
    config = Configuration("fixtures/dataset1/config.py")
    pathnames = config.account_input_pathnames("iban2")
    transactions = InBankCSV.read(pathnames[0])

    labeling = Labeling.loadPathname("fixtures/dataset1/accounts/iban2/patterns/match_category.csv")

    s_labels = labeling.label(transactions.df)

    # let's get the location of the first match
    idx = s_labels[(~s_labels.isnull()) & (s_labels.str.contains("bank-fee"))].index[0]

    # ...and check it against the transactions dataframe
    assert transactions.df.loc[idx]["description"] == "Imposte e tasse"


def test_labeling_config():

    myf = MetaCash("fixtures/dataset1/config-no-errors.py")
#    print(myf.accounts["iban2"].config) #describe() #transactions.print()
