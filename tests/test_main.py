import contextlib
import io
import logging

from logger import Logger


@contextlib.contextmanager
def with_captured_output():
    with contextlib.redirect_stdout(io.StringIO()) as stdout, contextlib.redirect_stderr(io.StringIO()) as stderr:
        yield stdout, stderr


def test_logger_initialization() -> None:
    logger = Logger(name="test_logger", file_logging=False)
    assert logger.name == "test_logger"
    assert logger.level == logging.DEBUG
    assert logger._file_handler is None


def test_logger_info() -> None:
    with with_captured_output() as (_, stderr):
        logger = Logger(name="test_logger", file_logging=False)
        logger.info("Test info message")
        output = stderr.getvalue().strip()
        assert "Test info message" in output
        assert "INFO" in output
