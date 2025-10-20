from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Car(BaseModel):
    id: Optional[str] = None
    href: Optional[str] = None
    price: Optional[int] = None
    brand: Optional[str] = None
    name_car: Optional[str] = None
    year: Optional[int] = None
    status: Optional[str] = None
    kilometers: Optional[str] = None
    origin: Optional[str] = None
    type_car: Optional[str] = None
    gear: Optional[str] = None
    engine: Optional[str] = None
    color: Optional[str] = None
    interior_color: Optional[str] = None
    seats: Optional[int] = None
    doors: Optional[int] = None
    transmission: Optional[str] = None
    address: Optional[str] = None
    published_date: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None