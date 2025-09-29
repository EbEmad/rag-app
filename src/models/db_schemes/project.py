from pydantic import BaseModel,Field,validator
from typing import Optional
from bson.objectid import ObjectId
class Project(BaseModel):
    _id:Optional[ObjectId]
    project_id:str=Field(...,min_length=1)

    @validator("Project_id")
    def validate_project_id(cls,value):
        if not value.isalnum():
            raise ValueError("Project_id Must be alphanumeric")
        return value
    
    class Config:
        arbitrary_types_allowed=True