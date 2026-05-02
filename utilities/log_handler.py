import logging


def setToolName(toolname):
    return toolname


class RedFormatter(logging.Formatter):
    RED = "\033[31m"
    RESET = "\033[0m"

    def format(self, record):
        # Ensure Tool_Name exists
        record.Tool_Name = getattr(record, "Tool_Name", "N/A")

        # Full formatted log
        formatted = super().format(record)

        # Extract actual message
        message = record.getMessage()

        # Split prefix and message safely
        prefix, sep, _ = formatted.partition(message)

        if sep:  # message found
            return f"{self.RED}{prefix}{self.RESET}{message}"

        return formatted


# Common log format
log_format = (
    "%(asctime)s | %(levelname)-8s | %(Tool_Name)s | "
    "%(filename)s:%(lineno)d :%(message)s"
)

# Console formatter (RED prefix only)
console_formatter = RedFormatter(log_format)

# File formatter (NO COLOR)
file_formatter = logging.Formatter(log_format)


# -------------------------------
# Console Handler
# -------------------------------
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(console_formatter)


# -------------------------------
# File Handler
# -------------------------------
file_handler = logging.FileHandler(
    "logs\\tool.log",
    mode="a",
    encoding="utf-8"
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)


# -------------------------------
# Logger Setup
# -------------------------------
logger = logging.getLogger("AppiumLogger")
logger.setLevel(logging.DEBUG)

# IMPORTANT → Prevent duplicate logs
logger.propagate = False

# Remove old handlers if already attached
if logger.hasHandlers():
    logger.handlers.clear()

# Add handlers only once
logger.addHandler(console_handler)
logger.addHandler(file_handler)


# -------------------------------
# Main Logging Function
# -------------------------------
def nowLogs(*args):
    name = setToolName("Appium")

    if not args:
        logger.warning(
            "Empty log message",
            stacklevel=2,
            extra={"Tool_Name": name}
        )
        return

    # Join all arguments into single message
    message = " ".join(str(arg) for arg in args)

    logger.info(
        message,
        stacklevel=2,
        extra={"Tool_Name": name}
    )