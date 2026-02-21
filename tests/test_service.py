import pytest
from unittest.mock import AsyncMock, MagicMock

# Підстав правильний шлях імпорту до твого ScrapingService!
from services.scraping_service import ScrapingService

@pytest.mark.asyncio
async def test_scraping_service_run_flow():
    """
    Перевіряємо, чи Сервіс правильно оркеструє (керує) всіма процесами:
    відкриває браузер -> парсить -> зберігає в БД -> зберігає куки -> закриває браузер.
    """
    
    # 1. ARRANGE (Готуємо наші моки-замінники)
    
    # Мокаємо репозиторій (БД)
    mock_repository = MagicMock()
    
    # Мокаємо Фабрику браузерів та сторінку
    mock_factory = AsyncMock()
    mock_page = MagicMock()
    mock_context = AsyncMock()
    
    # Кажемо фабриці: "коли в тебе попросять сторінку, поверни ці два фейки"
    mock_factory.get_page.return_value = (mock_page, mock_context)
    
    # Кажемо контексту: "коли попросять куки, поверни фейковий словник"
    mock_context.cookies.return_value = [{"name": "session", "value": "12345"}]
    mock_factory.cookies_manager = AsyncMock() # Менеджер кук
    
    # Мокаємо сам Скрапер
    mock_scraper_instance = AsyncMock()
    # Імітуємо, що скрапер успішно зібрав 2 товари
    mock_scraper_instance.scrape.return_value = ["Fake Product 1", "Fake Product 2"]
    
    # Створюємо фейковий КЛАС скрапера, який при створенні повертає наш фейковий інстанс
    mock_scraper_class = MagicMock(return_value=mock_scraper_instance)
    
    # Мокаємо налаштування скрапера
    mock_settings = MagicMock()
    
    # Ініціалізуємо наш сервіс із усіма цими фейками
    service = ScrapingService(
        repository=mock_repository,
        browser_factory=mock_factory,
        scraper_class=mock_scraper_class,
        scraper_settings=mock_settings
    )
    
    # 2. ACT (Запускаємо головний метод)
    await service.run()
    
    # 3. ASSERT (Перевіряємо, чи Сервіс відпрацював як хороший менеджер)
    
    # Чи створив він браузер і чи взяв сторінку?
    mock_factory.create.assert_awaited_once()
    mock_factory.get_page.assert_awaited_once()
    
    # Чи створив він скрапер і чи викликав метод scrape()?
    mock_scraper_class.assert_called_once()
    mock_scraper_instance.scrape.assert_awaited_once()
    
    # Чи зберіг він наші "2 товари" у базу даних?
    mock_repository.save_all.assert_called_once_with(["Fake Product 1", "Fake Product 2"])
    
    # Чи дістав він куки і чи відправив їх на збереження?
    mock_context.cookies.assert_awaited_once()
    mock_factory.cookies_manager.save.assert_awaited_once_with([{"name": "session", "value": "12345"}])
    
    # НАЙГОЛОВНІШЕ: чи зупинив він браузер у кінці (блок finally)?
    mock_factory.stop.assert_awaited_once()