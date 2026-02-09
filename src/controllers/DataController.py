from fastapi import UploadFile
from models import ResponseSignal
from .BaseController import BaseController
from .ProjectController import ProjectController
import re
import os

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
    

    def generate_filepath(self, original_filename: str, project_id: str):

        random_key = self.generate_random_string(length=12)
        proj_path = ProjectController().get_project_path(project_id=project_id)

        cleaned_filename = self.get_clean_file_name(original_filename)

        new_filepath = os.path.join(
            proj_path,
              random_key + "_" + cleaned_filename
              )

        while os.path.exists(new_filepath):
            random_key = self.generate_random_string(length=12)
            new_filepath = os.path.join(
                proj_path,
                random_key + "_" + cleaned_filename
            )

        return new_filepath, random_key

    def get_clean_file_name(self, filename: str):

        # Remove special characters using regex
        cleaned_name = re.sub(r'[^\w]', '', filename)
       
        # Replace spaces with underscores
        cleaned_name = cleaned_name.replace(" ", "_")
    
        return cleaned_name