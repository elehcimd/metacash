class DashboardWidget:

    @classmethod
    def init(cls, dw, skip=[]):

        dw.reg = {}

        # register all widgets, i.e., methods starting with "w_".
        for w_name in list(filter(lambda x: x.startswith("w_"), dir(dw))):
            w_func = getattr(dw, w_name)

            if w_func in skip:
                continue

            dw.reg[w_func] = w_func()
