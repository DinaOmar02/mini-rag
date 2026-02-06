from enum import Enum

class ResponseSignal(Enum):

   FILE_VALIDATED_SUCCESS = "file_validated_success"
   FILE_TYPE_INVALID = "file_type_invalid"
   FILE_SIZE_EXCEEDED = "file_size_exceeded"
   FILE_UPLOAD_SUCCESS = "upload_success"
   FILE_UPLOAD_FAILED = "file_upload_failed"
   
   