from binance.client import Client
from binance.enums import *
from binance.helpers import round_step_size
from Exchange import *

"""Concrete Products provide various implementations of the Product interface.
"""


class Binance(Exchange):
    EXCHANGE_NAME = "BINANCE.US"
    API_KEY = "put api key here"
    API_SECRET = "put api secret here"
    TLD = 'us'
    client = None
    exchange_info = None

    def init(self) -> str:
        # gets binance client
        self.client = Client(api_key=self.API_KEY, api_secret=self.API_SECRET, tld=self.TLD)

        #self.exchange_info = self.client.get_exchange_info("BTCUSDT")
        #print(self.exchange_info)

        result = "Initialized"
        return result

    def get_price(self, symbol) -> str:
        price = self.client.get_ticker(symbol=symbol)
        return price

    def get_exchange_name(self) -> str:
        return self.EXCHANGE_NAME

    def get_balance(self, asset) -> float:
        balance = self.client.get_asset_balance(asset=asset)

        return float(balance['free'])

    def create_limit_buy_order(self, symbol, qty, price) -> any:
        try:
            order = self.client.order_limit_buy(
                symbol=symbol,
                quantity='{0:.4f}'.format(qty),
                price='{0:.2f}'.format(price))
            return order
        except Exception as e:
            print(e)
            return None

    def create_limit_sell_order(self, symbol, qty, price) -> any:
        try:
            order = self.client.order_limit_sell(
                symbol=symbol,
                quantity='{0:.6f}'.format(qty),
                price='{0:.2f}'.format(price))
            return order
        except Exception as e:
            print(e)
            return None

    def get_order(self, symbol, order_id) -> str:
        try:
            order = self.client.get_order(symbol=symbol, orderId=order_id)
            return order
        except Exception as e:
            print(e)
            return None

    def cancel_order(self, symbol, order_id) -> str:
        try:
            order = self.client.cancel_order(symbol=symbol, orderId=order_id)
            return order
        except Exception as e:
            print(e)
            return None

    def get_open_orders(self, symbol) -> str:
        try:
            orders = self.client.get_open_orders()
            return orders
        except Exception as e:
            print(e)
            return None

    def check_order(self, symbol, order_id) -> any:
        try:
            order = self.client.get_order(symbol=symbol, orderId=order_id)
            print("Order Info:")
            print(order)

            if order['status'] == 'FILLED':
                return order
            else:
                return None
        except Exception as e:
            print(e)
            return None
