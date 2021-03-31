from metacash.readers.paypal import PayPalCSV

config = {

    "accounts": {
        "paypal1": {
            "type": "paypal",
            "description": "ecommerce-private",
            "linked-to": "iban1",
            "input": {
                "pathname": "accounts/paypal1/orig/**/*.CSV",
                "reader": PayPalCSV.read
            },
        },
    }
}
