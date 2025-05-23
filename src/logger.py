import datetime
import enum
import logging
import os
import pathlib
import typing as t

__all__: t.Tuple[str, ...] = (
    "Logger",
    "FileHandler",
    "Formatter",
)


class LogLevelColors(enum.Enum):
    """Colors for the log levels."""

    DEBUG = "\033[96m"
    INFO = "\033[92m"
    WARNING = "\033[93m"
    ERROR = "\033[33m"
    CRITICAL = "\033[91m"
    ENDC = "\033[0m"


class RelativePathFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter the log record."""
        record.pathname = record.pathname.replace(os.getcwd(), "~")
        return True


class Formatter(logging.Formatter):
    """Format the log record."""

    def __init__(self) -> None:
        super().__init__(
            "[%(asctime)s] | %(pathname)s:%(lineno)d | %(levelname)s | %(message)s",
            style="%",
        )

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record."""
        return f"{LogLevelColors[record.levelname].value}{super().format(record)}{LogLevelColors.ENDC.value}"


class FileHandler(logging.FileHandler):
    """Emit a log record.

    Parameters
    ----------
    ext : str
        The file extension.
    folder : pathlib.Path | str
        The folder to save the logs in. Defaults to "logs".
    """

    _last_entry: datetime.datetime = datetime.datetime.today()

    def __init__(self, *, ext: str, folder: t.Union[pathlib.Path, str] = "logs") -> None:
        """Create a new file handler."""
        self.folder = pathlib.Path(folder)
        self.ext = ext
        self.folder.mkdir(exist_ok=True)
        super().__init__(
            self.folder / f"{datetime.datetime.today().strftime('%Y-%m-%d')}-{ext}.log",
            encoding="utf-8",
        )
        self.setFormatter(Formatter())

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record."""
        if self._last_entry.date() != datetime.datetime.today().date():
            self._last_entry = datetime.datetime.today()
            self.close()
            self.baseFilename = (self.folder / f"{self._last_entry.strftime('%Y-%m-%d')}-{self.ext}.log").as_posix()
            self.stream = self._open()
        super().emit(record)


class Logger(logging.Logger):
    """
    The logger used to log information about the client.

    Parameters
    ----------
    name : str
        The name of the logger.
    level : int
        The level of the logger.
    file_logging : bool
        Whether or not to log to a file.

    Attributes
    ----------
    _handler : logging.StreamHandler
        The stream handler used to log to the console.
    _file_handler : t.Optional[logging.FileHandler]
        The file handler used to log to a file.

    Examples
    --------

    >>> logs = Logger(name="application")
    >>> logs.info("Hello, world!")
    [2021-08-29 17:05:32,000] | application/logger.py:95 | INFO | Hello, world!
    """

    _file_handler: FileHandler | None = None

    def __init__(self, *, name: str, level: int = logging.DEBUG, file_logging: bool = False) -> None:
        super().__init__(name, level)
        self._handler = logging.StreamHandler()
        self._handler.addFilter(RelativePathFilter())
        self._handler.setFormatter(Formatter())
        self.addHandler(self._handler)
        if file_logging:
            self._file_handler = FileHandler(ext=name)
            self._file_handler.addFilter(RelativePathFilter())
            self.addHandler(self._file_handler)

    def set_formatter(self, formatter: logging.Formatter) -> None:
        """Set the formatter."""
        self._handler.setFormatter(formatter)
        if self._file_handler is not None:
            self._file_handler.setFormatter(formatter)
