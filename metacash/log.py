import logging
import sys
from logging import debug, info, warning, error, critical, _levelToName as level_to_name
from typing import Optional, Dict

from colorama import Fore, Back, Style


class ColoredFormatter(logging.Formatter):
    def __init__(self, *args, colors: Optional[Dict[str, str]] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.colors = colors if colors else {}

    def format(self, record) -> str:
        record.color = self.colors.get(record.levelname, '')
        record.reset = Style.RESET_ALL
        return super().format(record)


class Log:
    level_to_name = level_to_name
    debug = debug
    info = info
    warning = warning
    error = error
    critical = critical

    @classmethod
    def init(cls, level):
        formatter = ColoredFormatter(
            '{color}{levelname:8}{reset}| {message}',
            style='{', datefmt='%Y-%m-%d %H:%M:%S',
            colors={
                'DEBUG': Fore.CYAN,
                'INFO': Fore.GREEN,
                'WARNING': Fore.YELLOW,
                'ERROR': Fore.RED,
                'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT,
            }
        )

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.handlers[:] = []
        logger.addHandler(handler)
        logger.setLevel(level)
