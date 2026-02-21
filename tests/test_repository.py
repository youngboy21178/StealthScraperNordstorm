import pytest
import duckdb
from core.models import Product

# Увага: перевір, чи правильний шлях імпорту для твого проєкту!
from infrastructure.database.repositories import ProductRepository 

import os
import pytest
import duckdb

@pytest.fixture
def db_connection():
    """
    Creates a temporary database in RAM (:memory:) 
    and deploys the REAL schema from our file there.
    """
    conn = duckdb.connect(':memory:')

    current_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(current_dir, "..", "infrastructure", "database", "schema.sql")
    
    # Читаємо файл схеми
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    # Виконуємо справжні запити для створення таблиць
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


# --- САМІ ТЕСТИ (Аналог @Test у Java) ---

def test_add_product_saves_to_db(repository, db_connection, sample_product):
    """Перевіряємо, чи один товар успішно зберігається у БД разом з кольорами."""
    
    # 1. Викликаємо метод (Act)
    repository.add_product(sample_product)
    
    # 2. Перевіряємо таблицю products (Assert)
    saved_product = db_connection.execute("SELECT title, min_price FROM products").fetchone()
    assert saved_product is not None, "Товар не зберігся в базу!"
    assert saved_product[0] == "Nike Air Max" # title
    assert saved_product[1] == 99.99          # min_price
    
    # 3. Перевіряємо зв'язану таблицю кольорів (Assert)
    saved_colors = db_connection.execute("SELECT color_name FROM product_colors").fetchall()
    assert len(saved_colors) == 3, "Збереглися не всі кольори!"
    
    # Перетворюємо список кортежів [('Black',), ('White',), ('Red',)] у звичайний список
    color_names = [row[0] for row in saved_colors]
    assert "Black" in color_names
    assert "Red" in color_names

def test_save_all_inserts_multiple_products(repository, db_connection):
    """Перевіряємо пакетне збереження товарів."""
    
    products_list = [
        Product(title="Shoe 1", link="link1", min_price=10, max_price=10, valute="$", colors=[]),
        Product(title="Shoe 2", link="link2", min_price=20, max_price=20, valute="$", colors=["Blue"]),
    ]
    
    # 1. Викликаємо метод збереження списку
    repository.save_all(products_list)
    
    # 2. Перевіряємо кількість записів
    count_result = db_connection.execute("SELECT COUNT(*) FROM products").fetchone()
    assert count_result[0] == 2, "Мало бути збережено 2 товари!"

def test_save_all_with_empty_list_does_not_fail(repository, db_connection):
    """Перевіряємо, що пустий список не викликає помилок (Edge Case)."""
    
    # Метод не повинен викидати Exception
    repository.save_all([]) 
    
    # Перевіряємо, що база залишилась пустою
    count_result = db_connection.execute("SELECT COUNT(*) FROM products").fetchone()
    assert count_result[0] == 0