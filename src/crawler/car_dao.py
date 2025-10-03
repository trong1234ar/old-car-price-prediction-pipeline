from pydantic import BaseModel
from datetime import datetime

class Car(BaseModel):
    id: str = None
    href: str = None
    price: int = None
    updated_at: datetime = None
    deleted_at: datetime = None
    brand: str = None
    name_car: str = None
    year: int = None
    status: str = None
    kilometers: str = None
    origin: str = None
    type_car: str = None
    gear: str = None
    engine: str = None
    color: str = None
    interior_color: str = None
    seats: int = None
    doors: int = None
    transmission: str = None
    pulished_date: datetime = None
    address: str = None