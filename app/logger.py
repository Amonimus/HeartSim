"""system logger"""
import logging
import os
from logging import Logger as LoggingLogger, Filter, StreamHandler, LogRecord


class Logger(LoggingLogger):
	"""logging.Logger class extension"""

	def __init__(self, name: str = "Logger", *args, **kwargs):
		super().__init__(name, *args, **kwargs)
		fmt: str = "[%(asctime)s] [\"%(RELPATH)s:%(lineno)s\":%(funcName)s] [%(levelname)s] %(message)s"

		class ColorFormatter(logging.Formatter):
			"""Applies custom colors to log format"""
			purple = "\x1b[35;20m"
			blue = "\x1b[34;20m"
			yellow = "\x1b[33;20m"
			red = "\x1b[31;20m"
			bold_red = "\x1b[31;1m"
			reset = "\x1b[0m"
			FORMATS: dict = {
				logging.DEBUG: blue + fmt + reset,
				logging.INFO: purple + fmt + reset,
				logging.WARNING: yellow + fmt + reset,
				logging.ERROR: red + fmt + reset,
				logging.CRITICAL: bold_red + fmt + reset
			}

			def format(self, record: logging.LogRecord):
				"""Formatter"""
				log_fmt = self.FORMATS.get(record.levelno)
				formatter = logging.Formatter(log_fmt)
				return formatter.format(record)

		class ContextFilter(Filter):
			"""Applies custom variables to log format"""

			def filter(self, record: LogRecord) -> bool:
				"""Allows relative path in log format"""
				record.RELPATH = os.path.relpath(record.pathname)
				record.FULLPATH = record.pathname.replace('\\', '/')
				return True

		self.addFilter(ContextFilter())
		console_handler: StreamHandler = StreamHandler()
		console_handler.setFormatter(ColorFormatter())
		self.addHandler(console_handler)


logger: Logger = Logger()
