import logging

from metacash.readers.inbank import InBankCSV, InBankPrepaidCSV

config = {

    "logging_level": logging.INFO,

    "accounts": {

        "iban1": {
            # there's a gap between two sub-directories. tests pass for each sub-directory separately,
            # but will then fail if the entire directory is used as input.
            "type": "bank",
            "description": "private",
            "input": {
                "pathname": "accounts/iban1/orig/**/*.csv",
                "reader": InBankCSV.read
            },
        },

        "iban2": {
            # clean transactions, no errors.
            "type": "bank",
            "description": "consulting",
            "input": {
                "pathname": "accounts/iban2/orig/**/*.csv",
                "reader": InBankCSV.read
            },
        },

        "prepaid1": {
            # no errors, everything can be loaded with no consistency issues.
            "type": "prepaid",
            "description": "ecommerce-private",
            "linked-to": "iban1",
            "input": {
                "pathname": "accounts/prepaid1/orig/**/*.csv",
                "reader": InBankPrepaidCSV.read
            },
        }

    }

}
