from pydantic import BaseModel, Field
from core.utils import PyObjectId, ObjectId


class UserResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    family: str
    email: str
    type: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "gpa": "3.0",
            }
        }


class User(BaseModel):
    name: str
    family: str
    email: str
    type: str
    password: str


class Login(BaseModel):
    email: str
    password: str
