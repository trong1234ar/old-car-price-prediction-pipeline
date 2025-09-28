from pydantic import BaseModel


class Car(BaseModel):
    id: str
    href: str
    price: int
    brand: str
    name_car: str
    year: int
    status: str
    kilometers: str
    origin: str
    type_car: str
    gear: str
    engine: str
    color: str
    interior_color: str
    seats: int
    doors: int
    transmission: str
    pulished_date: str
    crawled_date: str
    andress: str