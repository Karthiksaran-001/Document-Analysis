import os
import sys
from logger.custom_logger import CustomLogger
import traceback
import warnings
warnings.filterwarnings("ignore")



class DocumentException(Exception):
    def __init__(self, error_message ,error_details:sys = sys):
        _,_,exc_tb = error_details.exc_info()
        self.file_name = exc_tb.tb_frame.f_code.co_filename
        self.lineno = exc_tb.tb_frame.f_lineno
        self.error_message = str(error_message)
        self.traceback_str = ''.join(traceback.format_exception(*error_details.exc_info()))
    def __str__(self):
        return f"""
        Error in {self.file_name} at lin_no : {self.lineno}
        Message : {self.error_message}
        Traceback:
        {self.traceback_str}
        """

# if __name__ == "__main__":
#     log  = CustomLogger().get_logger(__file__)
#     try:
#         a = 10/0
#         log.info(f"Result is {a}")
#     except Exception as e:
#         app_exc = DocumentException(e)
#         log.error(app_exc)
#         raise app_exc