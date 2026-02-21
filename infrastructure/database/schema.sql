CREATE SEQUENCE IF NOT EXISTS seq_product_id;

CREATE TABLE IF NOT EXISTS products (
    id INTEGER DEFAULT nextval('seq_product_id') PRIMARY KEY,
    title VARCHAR,
    min_price DOUBLE,
    max_price DOUBLE,
    link VARCHAR,
    valute VARCHAR,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_colors (
    product_id INTEGER,
    color_name VARCHAR,
    FOREIGN KEY (product_id) REFERENCES products(id)
);