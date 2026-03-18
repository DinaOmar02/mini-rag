from enum import Enum

class ResponseSignal(Enum):

   FILE_VALIDATED_SUCCESS = "file_validated_success"
   FILE_TYPE_INVALID = "file_type_invalid"
   FILE_SIZE_EXCEEDED = "file_size_exceeded"
   FILE_UPLOAD_SUCCESS = "upload_success"
   FILE_UPLOAD_FAILED = "file_upload_failed"
   FILE_CHUNK_SIZE = 512000
   
   FILE_PROCESSING_FAILED = "file_processing_failed"
   FILE_PROCEESED_SUCCESS = "file_processed_success"

   NO_FILES_ERROR = " no_files_error"
   FILE_ID_ERROR = "no_file_found_with_this_id"