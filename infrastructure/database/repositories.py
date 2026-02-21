from core.models import Product


class ProductRepository:

    def __init__(self, connection):
        self.connection = connection

    def save_all(self, products: list[Product]):

        self.connection.execute("BEGIN")

        for p in products:
            self.connection.execute(
                "INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)",
                [
                    p.title,
                    p.brand,
                    p.price,
                    p.currency,
                    ",".join(p.colors),
                    p.scraped_at
                ]
            )

        self.connection.execute("COMMIT")