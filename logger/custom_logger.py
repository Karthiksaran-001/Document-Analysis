import os
import logging
from datetime import datetime

class CustomLogger:
    def __init__(self , log_dir = "logs"):
        self.log_dir = os.path.join(os.getcwd() , log_dir) 
        os.makedirs(self.log_dir , exist_ok= True)
        log_file = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.log_file_path = os.path.join(self.log_dir , log_file)
        

    def get_logger(self , name = __file__):
        logger_name = os.path.basename(__name__)
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        file_formatter = logging.Formatter("[ %(asctime)s ] %(levelname)s %(name)s (lin_no:%(lineno)d) - %(message)s")
        stream_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        file_handler = logging.FileHandler(filename= self.log_file_path)
        file_handler.setFormatter(file_formatter)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(stream_formatter)
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        return logger
    

if __name__ == "__main__":
    obj = CustomLogger()
    log = obj.get_logger()
    log.info("Working fine")
    log.critical("Check the Critical")

