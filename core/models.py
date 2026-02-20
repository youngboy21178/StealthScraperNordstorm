from pydantic import BaseModel

class Product(BaseModel):
    title: str
    min_price: float
    max_price: float
    valute: str
    colors: list[str]
    link: str
