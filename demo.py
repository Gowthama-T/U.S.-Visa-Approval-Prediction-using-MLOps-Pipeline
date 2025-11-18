from us_visa.logger import logger
from us_visa.exception import USvisaException
  

logger.info("Logging works!")


try:
    a =2/0
except Exception as e:
    raise UsvisaException(e, sys)