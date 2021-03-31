import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd


def barplot_amount(config, s_amount, title, x_label=None, show_cumulative=False):
    plt.figure(figsize=(20, 5))
    ax = plt.gca()

    s_color = (s_amount >= 0).map({True: "forestgreen", False: "orangered"})
    s_cumulative = s_amount.cumsum()

    if show_cumulative:
        s_cumulative.plot(kind="bar", ax=ax, color='lightgray')

    s_amount.plot(kind="bar", ax=ax, color=s_color)

    ax.set_axisbelow(True)
    plt.grid(axis="y", which='major', color='gray', alpha=1, linestyle='dotted', linewidth=1)
    # plt.grid(axis="y", which='minor', color='gray', alpha=.5, linestyle='dotted', linewidth=1)

    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(4))

    # plt.legend()

    # ax.yaxis.set_major_locator(ticker.MultipleLocator(100))
    # ax.yaxis.set_minor_locator(ticker.MultipleLocator(20))

    amount_mean = config["float_format"].format(s_amount.mean())
    amount_min = config["float_format"].format(s_amount.min())
    amount_max = config["float_format"].format(s_amount.max())
    amount_cum = config["float_format"].format(s_cumulative.iloc[-1])

    # Draw y=zero line, and make sure that the Y interval is mirrored [-x,+x] in the Y limits.
    ax.hlines(0, ax.get_xlim()[0], ax.get_xlim()[1])
    mid_range = max(-ax.get_ylim()[0], ax.get_ylim()[1])
    ax.set_ylim([-mid_range, +mid_range])

    ax.set_ylabel("Amount")
    ax.set_xlabel(x_label)
    plt.title(
        f"{title}\nmean={amount_mean} highest={amount_min} lowest={amount_max}")

    #    if len(s_amount.index) >10:
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: config["float_format"].format(x)))

    if type(s_amount.index) == pd.core.indexes.datetimes.DatetimeIndex:
        ax.xaxis.set_major_formatter(plt.FixedFormatter(s_amount.index.to_series().dt.strftime("%b\n%Y")))

    plt.show()


def get_ms(df, max_rows=30):
    df = df.set_index("timestamp")
    ms = 1
    while True:
        if len(df.groupby(pd.Grouper(level='timestamp', freq=f"{ms}MS"))) <= max_rows:
            return ms
        else:
            ms += 1


def barplot_monthly(config, df, colname, title, category_name=None, show_cumulative=False):
    if category_name:
        # we should keep also the first and last rows (ibfb), to maintain the overall timestamp interval.
        df = df[(df["type"] == "ib") | (df["type"] == "fb") | (df["label.category"] == category_name)]

    if colname == "amount":
        agg_func = "sum"
    elif colname == "balance":
        agg_func = "last"
    else:
        raise Exception("Unknown column name")

    ms = get_ms(df, 30)
    df = df.set_index("timestamp"). \
        groupby(pd.Grouper(level='timestamp', freq=f"{ms}MS")). \
        agg({colname: agg_func}). \
        fillna(method="backfill")

    barplot_amount(config, df[colname], title, "Month", show_cumulative=show_cumulative)


def barplot_categories(config, df, title, limit_abs_n=10):
    # group by category and aggregate amount
    df = df.groupby("label.category").agg({"amount": sum}).reset_index()

    # select top-n categories by absolute amount, and aggregate the others
    df["amount_abs"] = df["amount"].abs()
    df_sorted = df.sort_values(by=["amount_abs"], ascending=False)
    df_sorted_selected = df_sorted[:limit_abs_n]
    df_sorted_excluded = df_sorted[limit_abs_n:]
    df_sorted_excluded_agg = pd.DataFrame([{"label.category": f"others({len(df_sorted_excluded)})",
                                            "amount": df_sorted_excluded["amount"].sum()}])

    s_amount = pd.concat([df_sorted_selected, df_sorted_excluded_agg], ignore_index=True). \
        set_index("label.category", drop=True)["amount"]

    barplot_amount(config, s_amount, title, "Category", show_cumulative=True)


def barplot_categories_percentage(config, df, title, limit_abs_n=10):
    categories = df.groupby("label.category").agg({"amount": "sum"})["amount"].abs().sort_values(
        ascending=False).index.tolist()
    categories = categories[:limit_abs_n]
    df = df[df["label.category"].isin(categories)]

    ms = get_ms(df, 30)
    df = df.set_index("timestamp").groupby([pd.Grouper(level='timestamp', freq=f"{ms}MS"), "label.category"]).agg(
        {"amount": sum}).unstack().fillna(0)

    # s = df["amount"].sum(axis=1).abs().copy().max()
    # for category in categories:
    #    df["amount"][category] /= -s / 100

    plt.figure(figsize=(20, 5))
    ax = plt.gca()
    df["amount"][categories].plot(kind="bar", stacked=True, ax=ax, edgecolor="white", linewidth=1)
    # ax.set_ylim([0, 100])

    ax.set_axisbelow(True)
    plt.grid(axis="y", which='major', color='gray', alpha=1, linestyle='dotted', linewidth=1)
    # plt.grid(axis="y", which='minor', color='gray', alpha=.5, linestyle='dotted', linewidth=1)
    # Draw y=zero line, and make sure that the Y interval is mirrored [-x,+x] in the Y limits.
    ax.hlines(0, ax.get_xlim()[0], ax.get_xlim()[1])
    mid_range = max(-ax.get_ylim()[0], ax.get_ylim()[1])
    ax.set_ylim([-mid_range, +mid_range])

    ax.set_ylabel("Month")
    ax.set_ylabel("Amount")

    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(4))

    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2),
              fancybox=True, shadow=True, ncol=10)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: config["float_format"].format(x)))

    plt.title(f"{title}\n")

    plt.xticks(rotation=0)
    plt.yticks(rotation=0)

    ax.xaxis.set_major_formatter(plt.FixedFormatter(df.index.to_series().dt.strftime("%b\n%Y")))

    plt.show()
