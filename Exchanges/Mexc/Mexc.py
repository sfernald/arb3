from mexc_sdk import Spot
from Exchange import *

"""Concrete Products provide various implementations of the Product interface.
"""


class Mexc(Exchange):
    EXCHANGE_NAME = "MEXC"
    API_KEY = "put api key here"
    API_SECRET = "put api secret here"
    TLD = None
    client = None
    exchange_info = None

    def init(self) -> str:
        # gets client
        self.client = Spot(api_key=self.API_KEY,api_secret=self.API_SECRET)

        result = "Initialized"
        return result

    def get_price(self, symbol) -> str:
        price = self.client.book_ticker(symbol)

        return price

    def get_exchange_name(self) -> str:
        return self.EXCHANGE_NAME

    def get_balance(self, asset) -> float:
        asset_info = self.client.account_info()

        for balance in asset_info['balances']:
            if balance['asset'] == asset:
                return float(balance['free'])

        return 0.0

    def create_limit_buy_order(self, symbol, qty, price) -> any:
        try:
            formatted_qty = '{0:.6f}'.format(qty)
            order = self.client.new_order(
                symbol=symbol,
                side="BUY",
                order_type="LIMIT",
                options={ "quantity": formatted_qty, "price": str(price) })
            return order
        except Exception as e:
            print(e)
            return str(e)

    def create_limit_sell_order(self, symbol, qty, price) -> any:
        try:
            order = self.client.new_order(
                symbol=symbol,
                side="SELL",
                order_type="LIMIT",
                options={ "quantity": '{0:.6f}'.format(qty), "price": str(price) })
            return order
        except Exception as e:
            print(e)
            return str(e)

    def get_order(self, symbol, order_id) -> str:
        try:
            order = self.client.query_order(symbol=symbol,
                options={ "orderId": order_id })
            return order
        except Exception as e:
            print(e)
            return None

    def cancel_order(self, symbol, order_id) -> str:
        try:
            orders = self.client.cancel_order(symbol=symbol, orderId=order_id)
            return orders
        except Exception as e:
            print(e)
            return None

    def get_open_orders(self, symbol) -> str:
        try:
            orders = self.client.open_orders(symbol=symbol)
            return orders
        except Exception as e:
            print(e)
            return None

    def check_order(self, symbol, order_id) -> any:
        try:
            order = self.client.query_order(symbol=symbol,
                options={ "orderId": order_id })
            print("Order Info:")
            print(order)

            if order['status'] == 'FILLED':
                return order
            else:
                return None
        except Exception as e:
            print(e)
            return None
