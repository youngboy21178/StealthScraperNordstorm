import logging
from core.models import Product

class ProductRepository:
    def __init__(self, connection):
        self.connection = connection 
        self.logger = logging.getLogger(__name__)

    def add_product(self, product: Product) -> None:
        try:
            # 1. Зберігаємо товар і одразу отримуємо його ID (RETURNING id)
            result = self.connection.execute(
                """
                INSERT INTO products (title, min_price, max_price, link, valute) 
                VALUES (?, ?, ?, ?, ?) 
                RETURNING id
                """,
                (product.title, product.min_price, product.max_price, product.link, product.valute)
            ).fetchone()
            
            if not result:
                return
            product_id = result[0]

            # 2. Зберігаємо кольори
            for color_name in product.colors:
                # Перевіряємо, чи є вже такий колір у базі
                color_row = self.connection.execute(
                    "SELECT id FROM colors WHERE name = ?", 
                    (color_name,)
                ).fetchone()

                if color_row:
                    color_id = color_row[0] # Колір вже є, беремо його ID
                else:
                    # Якщо немає, додаємо і отримуємо новий ID
                    color_id = self.connection.execute(
                        "INSERT INTO colors (name) VALUES (?) RETURNING id", 
                        (color_name,)
                    ).fetchone()[0]

                # 3. Зв'язуємо товар і колір у третій таблиці
                self.connection.execute(
                    "INSERT INTO product_colors_link (product_id, color_id) VALUES (?, ?)",
                    (product_id, color_id)
                )

            self.logger.debug(f"New product '{product.title}' added with ID {product_id} and {len(product.colors)} colors")

        except Exception as e:
            self.logger.error(f"Database error while adding product '{product.title}': {e}")
    
    def save_all(self, products: list[Product]) -> None:
        """Stores the list of goods in the database."""
        if not products:
            self.logger.warning("No products to save.")
            return

        for item in products: 
            self.add_product(item)
            
        self.logger.info(f"Successfully added {len(products)} products to the database.")