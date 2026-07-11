from pydantic import BaseModel

class Prod(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int