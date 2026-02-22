import os
import duckdb

# Вкажи тут правильне ім'я твого файлу бази даних!
# Наприклад: "nordstrom.duckdb" або "nordstrom.db" (як ти назвав його в репозиторії)
DB_NAME = "scraper_data.duckdb" 

def main():
    # Будуємо правильний шлях до БД (вона лежить у корені або в infrastructure/database)
    # Зміни шлях, якщо твоя БД лежить в іншому місці
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(os.path.dirname(current_dir), "infrastructure/database", DB_NAME)
    
    if not os.path.exists(db_path):
        print(f"❌ Базу даних не знайдено за шляхом: {db_path}")
        return

    print(f"✅ Підключаюсь до бази: {db_path}\n")
    conn = duckdb.connect(db_path)

    try:
        print("\n🎨 ВСІ УНІКАЛЬНІ КОЛЬОРИ (Таблиця colors):")
        conn.sql("SELECT * FROM colors LIMIT 10").show()

        print("\n🔗 ЗВ'ЯЗКИ: ЯКИЙ ТОВАР МАЄ ЯКІ КОЛЬОРИ (JOIN 3-х таблиць):")
        conn.sql("""
            SELECT p.id as product_id, p.title, c.name as color_name
            FROM products p
            JOIN product_colors_link pcl ON p.id = pcl.product_id
            JOIN colors c ON pcl.color_id = c.id
            ORDER BY p.id
            LIMIT 15
        """).show()
        
    except duckdb.CatalogException as e:
        print(f"❌ Помилка: Таблиці ще не створені або БД порожня. Деталі: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()