class OpenSalePageException(Exception):
    """
    An exception is thrown when the number of attempts
    to navigate to the discounts page has been exhausted.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ProductsNotFound(Exception):
    """
    Exception: no products were found on any page.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)