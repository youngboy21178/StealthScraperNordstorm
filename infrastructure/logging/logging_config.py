import logging
import sys


class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[90m",      # grey
        "INFO": "\033[92m",       # green
        "WARNING": "\033[93m",    # yellow
        "ERROR": "\033[91m",      # red
        "CRITICAL": "\033[95m",   # magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        message = super().format(record)
        return f"{log_color}{message}{self.RESET}"


def setup_logging(
        format: str,
        level=logging.INFO,
        ):

    handler = logging.StreamHandler(sys.stdout)

    formatter = ColorFormatter(format)

    handler.setFormatter(formatter)

    logging.basicConfig(
        level=level,
        handlers=[handler],
        force=True
    )