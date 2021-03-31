import logging

from metacash.readers.inbank import InBankCSV, InBankPrepaidCSV

config = {

    "logging_level": logging.INFO,

    "accounts": {

        "iban2": {
            "type": "bank",
            "description": "consulting",
            "input": {
                "pathname": "accounts/iban2/orig/01.01.2020-05.01.2020/**/*.csv",
                "reader": InBankCSV.read
            },
            "labeling": {
                "category": "accounts/iban2/patterns/match_category.csv"
            }
        },

        "prepaid1": {
            "type": "prepaid",
            "description": "ecommerce-private",
            "linked-to": "iban1",
            "input": {
                "pathname": "accounts/prepaid1/orig/**/*.csv",
                "reader": InBankPrepaidCSV.read
            },
            "labeling": {
                "category": "accounts/prepaid1/patterns/match_category.csv"
            }
        }

    },

    "meta": {
        "drop": {
            "iban2": ["self"],
            "prepaid1": ["self"]
        }
    }
}
