import os
import logging
from datetime import datetime

class CustomLogger:
    def __init__(self , log_dir = "logs"):
        self.log_dir = os.path.join(os.getcwd() , log_dir) 
        os.makedirs(self.log_dir , exist_ok= True)
        log_file = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        log_file_path = os.path.join(self.log_dir , log_file)
        logging.basicConfig(
            filename=log_file_path,
            level= logging.INFO,
            format="[ %(asctime)s ] %(levelname)s %(name)s (lin_no:%(lineno)d) - %(message)s"
        )

    def get_logger(self , name = __file__):
        return logging.getLogger(os.path.basename(name))

# if __name__ == "__main__":
#     obj = CustomLogger()
#     log = obj.get_logger()
#     log.info("Working fine")
#     log.critical("Check the Critical")

