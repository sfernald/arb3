from abc import ABC, abstractmethod


class Exchange(ABC):
    """
    The Product interface declares the operations that all concrete products
    must implement.
    """

    @abstractmethod
    def init(self) -> str:
        pass

    @abstractmethod
    def get_price(self, symbol) -> str:
        pass

    @abstractmethod
    def get_exchange_name(self) -> str:
        pass

    @abstractmethod
    def get_balance(self, asset) -> float:
        pass

    @abstractmethod
    def create_limit_buy_order(self, symbol, qty, price) -> any:
        pass

    @abstractmethod
    def create_limit_sell_order(self, symbol, qty, price) -> any:
        pass

    @abstractmethod
    def get_order(self, symbol, order_id) -> str:
        pass

    @abstractmethod
    def cancel_order(self, symbol, order_id) -> str:
        pass

    @abstractmethod
    def get_open_orders(self, symbol) -> str:
        pass

    @abstractmethod
    def check_order(self, symbol, order_id) -> any:
        pass

