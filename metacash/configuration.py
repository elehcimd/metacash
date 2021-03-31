import glob
import logging
import os


class Configuration:

    def __init__(self, pathname):
        with open(pathname) as f:
            data = f.read()

        g = {}
        exec(data, g)
        self.data = g["config"]

        if "logging_level" not in self.data:
            logging.debug("Preference logging_level missing, defaulting to INFO")
            self.data["logging_level"] = logging.INFO

        if "float_format" not in self.data:
            logging.debug("Preference float_format missing, defaulting to '{:.2f}'")
            self.data["float_format"] = "{:.2f}"

        if "float_decimal_precision" not in self.data:
            logging.debug(f"Preference float_decimal_precision missing, defaulting to 4")
            self.data["float_decimal_precision"] = 4

        self.base_dir = os.path.dirname(pathname)

    def describe(self):
        accounts = list(self.data["accounts"])
        logging.info(f"There are {len(accounts)} registered accounts: {accounts}")

    def account_input_pathnames(self, name):
        """
        Return pathnames of files matching the glob pattern in sorted order
        """

        # todo: this method does not work with multi readers.
        assert (type(self.data["accounts"][name]["input"]) != list)

        pathname_pattern = self.base_dir + os.sep + self.data["accounts"][name]["input"]["pathname"]
        pathnames = sorted(glob.glob(f"{pathname_pattern}", recursive=True))
        return pathnames

    def __getitem__(self, key):
        return self.data.get(key, None)
