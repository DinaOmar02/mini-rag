from helpers import get_app_settings
class BaseController:
    
    def __init__(self):
        self.app_settings = get_app_settings()