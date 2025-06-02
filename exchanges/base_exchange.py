from abc import ABC, abstractmethod

class BaseExchange(ABC):
    @abstractmethod
    def get_balance(self):
        pass

    @abstractmethod
    def open_position(self, coin, size, leverage, order_type="limit"):
        pass

    @abstractmethod
    def close_position(self, position_id):
        pass

    @abstractmethod
    def get_open_positions(self):
        pass

    @abstractmethod
    def get_funding_rate(self, coin):
        pass