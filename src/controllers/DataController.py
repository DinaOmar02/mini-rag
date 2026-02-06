from fastapi import UploadFile
from models import ResponseSignal
from controllers import BaseController

class DataController(BaseController):

    def __init__(self):
        super().__init__()

    def validate_uploaded_file(self,file: UploadFile):
        
        scale = 1024 * 1024  # Convert bytes to megabytes

        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_INVALID.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE * scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value
        
        return True, ResponseSignal.FILE_UPLOAD_SUCCESS.value