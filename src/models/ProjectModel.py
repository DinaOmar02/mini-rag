from .BaseDataModel import BaseDataModel
from .db_schemes import Project

class ProjectModel(BaseDataModel):

    def __init__(self):
        super().__init__()
        