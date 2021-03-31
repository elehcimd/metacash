import pandas as pd
from IPython.core.display import display, HTML


def display_h1(msg):
    return display(HTML(f"<h1>{msg}</h1>"))


def display_h2(msg):
    return display(HTML(f"<h2>{msg}</h2>"))


def display_h3(msg):
    return display(HTML(f"<h3>{msg}</h3>"))


def display_p(msg):
    return display(HTML(f"<p>{msg}</p>"))


def display_df(config, df):
    with pd.option_context(
            'display.max_rows', None,
            'display.max_columns', None,
            'display.max_colwidth', None,
            'display.chop_threshold', (10 ** -config["float_decimal_precision"]),
            'display.float_format', lambda x: config["float_format"].format(x),
            'display.precision', config["float_decimal_precision"]

    ):
        display(df)


def register_widgets(w, skip=[]):
    w.reg = {}

    # register all widgets, i.e., methods starting with "w_".
    for w_name in list(filter(lambda x: x.startswith("w_"), dir(w))):
        w_func = getattr(w, w_name)

        if w_func in skip:
            continue

        w.reg[w_func] = w_func()
