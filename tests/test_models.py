import pytest
from core.models import Product

def test_product_creation_success():
    """We verify that the Product object is successfully created with the correct data."""
    
    product = Product(
        title="Awesome Shoes",
        link="https://nordstrom.com/shoes",
        min_price=49.99,
        max_price=59.99,
        valute="$",
        colors=["Black", "White"]
    )
    
    assert product.title == "Awesome Shoes"
    assert product.min_price == 49.99
    assert product.max_price == 59.99
    assert product.valute == "$"
    assert len(product.colors) == 2
    assert "Black" in product.colors

def test_product_creation_without_colors():
    """We check the creation of products without colours (for example, if it is one size/colour)."""
    
    product = Product(
        title="Simple Hat",
        link="https://nordstrom.com/hat",
        min_price=15.0,
        max_price=15.0,
        valute="€",
        colors=[]
    )
    
    assert product.title == "Simple Hat"
    assert len(product.colors) == 0