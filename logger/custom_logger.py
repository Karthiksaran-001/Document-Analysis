import os
import logging
from datetime import datetime
import structlog

class CustomLogger:
    def __init__(self , log_dir = "logs"):
        self.log_dir = os.path.join(os.getcwd() , log_dir) 
        os.makedirs(self.log_dir , exist_ok= True)
        log_file = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.log_file_path = os.path.join(self.log_dir , log_file)
        

    def get_logger(self , name = __file__):
        logger_name = os.path.basename(name)
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(filename= self.log_file_path)
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        ## Add StructLOG for JSON format
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt ="iso" , utc = True , key = "Timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer(to = "event"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory= structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use= True)
        return structlog.get_logger(logger_name)
    

# if __name__ == "__main__":
#     obj = CustomLogger()
#     log = obj.get_logger()
#     log.info("Working fine")
#     log.critical("Check the Critical")

