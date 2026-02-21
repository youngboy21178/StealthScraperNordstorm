import logging
from core.models import Product

class ProductRepository:
    def __init__(self, connection):
        self.conn = connection 
        self.logger = logging.getLogger(__name__)

    def add_product(self, product: Product) -> None:
        try:
            result = self.conn.execute("""
                INSERT INTO products (title, min_price, max_price, link, valute) 
                VALUES (?, ?, ?, ?, ?)
                RETURNING id
            """, (product.title, product.min_price, product.max_price, product.link, product.valute)).fetchone()
            
            product_id = result[0]
            self.logger.debug(f"New product '{product.title}' was added with ID {product_id}")

            if product.colors:
                for color in product.colors:
                    self.conn.execute("""
                        INSERT INTO product_colors (product_id, color_name) 
                        VALUES (?, ?)
                    """, (product_id, color))
                self.logger.debug(f"Added {len(product.colors)} colors for product {product_id}")
                
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