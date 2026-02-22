import pytest
from unittest.mock import AsyncMock, MagicMock
from scraping.nordstrom_scraper import NordstromScraper

# --- ФІКСТУРИ ---

@pytest.fixture
def scraper():
    """Створює екземпляр скрапера з мокнутими залежностями для всіх тестів."""
    mock_page = MagicMock()
    mock_context = MagicMock()
    
    mock_settings = MagicMock()
    mock_settings.min_default_delay_sec = 1.0
    mock_settings.max_default_delay_sec = 3.0
    mock_settings.start_url = "https://nordstrom.com/fake"
    
    return NordstromScraper(
        settings=mock_settings, 
        page=mock_page, 
        context=mock_context
    )

# --- ТЕСТИ ---

@pytest.mark.asyncio
async def test_get_colors_extracts_correct_names(scraper):
    """Перевіряємо діставання кольорів (старий тест, але тепер використовує фікстуру)."""
    mock_item = MagicMock()
    
    mock_btn1 = AsyncMock()
    mock_btn1.get_attribute.return_value = "Black"
    mock_btn2 = AsyncMock()
    mock_btn2.get_attribute.return_value = "Red"
    
    mock_item.locator.return_value.all = AsyncMock(return_value=[mock_btn1, mock_btn2])

    result_colors = await scraper._get_colors(mock_item)

    assert len(result_colors) == 2
    assert result_colors[0] == "Black"
    assert result_colors[1] == "Red"

@pytest.mark.asyncio
async def test_get_price_with_exact_current_price(scraper):
    """Перевіряємо стандартну ціну зі словом 'Current Price'."""
    mock_item = MagicMock()
    
    # Імітуємо, що знайшли елемент з ціною
    mock_price_element = AsyncMock()
    mock_price_element.count.return_value = 1
    mock_price_element.first.inner_text.return_value = "Current Price $49.99"
    
    # Коли скрапер викличе get_by_text, віддаємо наш фейковий елемент
    mock_item.get_by_text.return_value = mock_price_element
    
    min_p, max_p, valute = await scraper._get_price(mock_item)
    
    assert min_p == 49.99
    assert max_p == 49.99
    assert valute == "$"

@pytest.mark.asyncio
async def test_get_price_with_price_range(scraper):
    """Перевіряємо ситуацію, коли ціна вказана діапазоном (наприклад, для різних розмірів)."""
    mock_item = MagicMock()
    
    mock_price_element = AsyncMock()
    mock_price_element.count.return_value = 1
    mock_price_element.first.inner_text.return_value = "Current Price €40.00 - 50.00"
    
    mock_item.get_by_text.return_value = mock_price_element
    
    min_p, max_p, valute = await scraper._get_price(mock_item)
    
    assert min_p == 40.00
    assert max_p == 50.00
    assert valute == "€"

@pytest.mark.asyncio
async def test_get_price_when_no_price_found(scraper):
    """Перевіряємо Edge Case: ціни взагалі немає на картці товару."""
    mock_item = MagicMock()
    
    # Імітуємо, що основний локатор нічого не знайшов
    mock_price_element = AsyncMock()
    mock_price_element.count.return_value = 0
    mock_item.get_by_text.return_value = mock_price_element
    
    # Імітуємо, що fallback-локатор теж нічого не знайшов
    mock_fallback = AsyncMock()
    mock_fallback.count.return_value = 0
    mock_item.locator.return_value.first = mock_fallback
    
    min_p, max_p, valute = await scraper._get_price(mock_item)
    
    # Скрапер має коректно обробити це і повернути нулі, а не впасти з помилкою
    assert min_p == 0.0
    assert max_p == 0.0
    assert valute == ""