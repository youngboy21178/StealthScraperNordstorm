-- Генератори ID
CREATE SEQUENCE IF NOT EXISTS seq_product_id;
CREATE SEQUENCE IF NOT EXISTS seq_color_id;

-- 1. Таблиця Товарів
CREATE TABLE IF NOT EXISTS products (
    id INTEGER DEFAULT nextval('seq_product_id') PRIMARY KEY,
    title VARCHAR,
    min_price DOUBLE,
    max_price DOUBLE,
    link VARCHAR,
    valute VARCHAR
);

-- 2. Таблиця Кольорів (унікальні назви)
CREATE TABLE IF NOT EXISTS colors (
    id INTEGER DEFAULT nextval('seq_color_id') PRIMARY KEY,
    name VARCHAR UNIQUE
);

-- 3. Проміжна таблиця (Зв'язок Товари <-> Кольори)
CREATE TABLE IF NOT EXISTS product_colors_link (
    product_id INTEGER,
    color_id INTEGER,
    PRIMARY KEY (product_id, color_id)
);