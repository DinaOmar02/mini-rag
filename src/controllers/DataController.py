from fastapi import UploadFile
from models import ResponseSignal
from controllers import BaseController

class DataController(BaseController):

    def __init__(self):
        super().__init__()

    def validate_file_type(self,file: UploadFile):
        
        self.response_signal = ResponseSignal()
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, self.response_signal.FILE_TYPE_INVALID
        
        if file.size > self.app_settings.FILE_MAX_SIZE:
            return False, self.response_signal.FILE_SIZE_EXCEEDED
        
        return True, self.response_signal.UPLOAD_SUCCESS