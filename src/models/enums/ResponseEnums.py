from enums import Enum

class ResponseSignal(Enum):

   FILE_TYPE_INVALID = "file_type_invalid"
   FILE_SIZE_EXCEEDED = "file_size_exceeded"
   UPLOAD_SUCCESS = "upload_success"
   