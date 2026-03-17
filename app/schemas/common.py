from pydantic import BaseModel

class Pagination(BaseModel):
    skip : int = 0
    limit : int = 10

class MessageResponseDTO(BaseModel):
    message: str