import logging

logger = logging.getLogger("shiny_shim")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("shiny_shim.log")
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

logger.debug("shiny_shim.log logger initialized")
