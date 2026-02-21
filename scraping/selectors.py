import re

class NordstromSelectors:

    BTN_SALE = "Sale"
    LINK_UNDER_50 = "Under $50"
    BTN_FILTER = "Filter"
    BTN_GENDER = "Gender"
    BTN_BOYS = "Boys"
    BTN_PRODUCT_TYPE = "Product Type"
    LBL_PRODUCT_TYPE = "Product Type"
    BTN_SHOES = "Shoes"
    BTN_ALL_SHOES = "All Shoes"
    BTN_VIEW_RESULTS = "View Results"
    BTN_TOP = "Top"

    PRODUCT_GRID_ARTICLE = 'div[data-container-type="product-grid"] article'
    PRODUCT_TITLE_LINK = "h3 a"
    COLOR_BUTTONS = "ul li button[aria-label]"

    PRICE_CURRENT_TEXT = "Current Price"
    PRICE_FALLBACK_TAG = "span"
    PRICE_FALLBACK_REGEX = re.compile(r"\d+[,.]\d{2}")