import sys
from loguru import logger

logger.remove(handler_id=None)
logger.add(sys.stdout, format="{time} - {level} - {message}", level="INFO")
error_trace = logger.add(sys.stderr, format="{time} {level} {message}", level="WARNING")
log_trace = logger.add("logs/export.log", level="INFO", rotation="100 MB", encoding="utf8")

logger.trace("Show something...")
