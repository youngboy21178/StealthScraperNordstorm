import pytest
import duckdb
import os
from core.models import Product

from infrastructure.database.repositories import ProductRepository 

@pytest.fixture
def db_connection():
    """
    Creates a temporary database in RAM (:memory:) 
    and deploys the REAL schema from our file there.
    """
    conn = duckdb.connect(':memory:')

    current_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(current_dir, "..", "infrastructure", "database", "schema.sql")
    
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    conn.execute(schema_sql)
    
    yield conn  
    
    conn.close()

@pytest.fixture
def repository(db_connection):
    """Створює екземпляр нашого репозиторію з тестовою базою."""
    return ProductRepository(connection=db_connection)

@pytest.fixture
def sample_product():
    """Генерує тестовий товар для перевірок."""
    return Product(
        title="Nike Air Max",
        link="https://nordstrom.com/nike",
        min_price=99.99,
        max_price=120.00,
        valute="$",
        colors=["Black", "White", "Red"]
    )

def test_add_product_saves_to_db(repository, db_connection, sample_product):
    """We check whether one product is successfully stored in the database along with colours."""
    
    repository.add_product(sample_product)
    
    saved_product = db_connection.execute("SELECT title, min_price FROM products").fetchone()
    assert saved_product is not None
    assert saved_product[0] == "Nike Air Max"
    assert saved_product[1] == 99.99          
    
    # НОВИЙ ЗАПИТ: З'єднуємо 3 таблиці через JOIN, щоб дістати назви кольорів
    saved_colors = db_connection.execute("""
        SELECT c.name 
        FROM product_colors_link pcl
        JOIN colors c ON pcl.color_id = c.id
    """).fetchall()
    
    assert len(saved_colors) == 3
    color_names = [row[0] for row in saved_colors]
    assert "Black" in color_names
    assert "Red" in color_names

def test_save_all_inserts_multiple_products(repository, db_connection):
    """We check batch storage of goods."""
    
    products_list = [
        Product(title="Shoe 1", link="link1", min_price=10, max_price=10, valute="$", colors=[]),
        Product(title="Shoe 2", link="link2", min_price=20, max_price=20, valute="$", colors=["Blue"]),
    ]
    
    repository.save_all(products_list)
    
    count_result = db_connection.execute("SELECT COUNT(*) FROM products").fetchone()
    assert count_result[0] == 2, "Мало бути збережено 2 товари!"

def test_save_all_with_empty_list_does_not_fail(repository, db_connection):
    """We verify that an empty list does not cause errors (Edge Case)."""
    
    repository.save_all([]) 
    
    count_result = db_connection.execute("SELECT COUNT(*) FROM products").fetchone()
    assert count_result[0] == 0

