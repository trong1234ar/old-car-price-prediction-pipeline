from pydantic import BaseModel


class Car(BaseModel):
    id: str
    href: str
    price: int