from datetime import datetime

from pydantic import BaseModel


class Car(BaseModel):
    id: str = None
    href: str = None
    price: str = None
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
    address: str = None
    published_date: str = None
    updated_at: str = None
    deleted_at: str = None