from abc import ABC, abstractmethod
from Db import *
import time
from Sms import *
import math
import random


class ExchangeCreator(ABC):
    """
    The Creator class declares the factory method that is supposed to return an
    object of a Product class. The Creator's subclasses usually provide the
    implementation of this method.
    """

    db = None
    exchange = None
    strategy_name = None
    total_phases = None

    @abstractmethod
    def factory_method(self):
        """
        Note that the Creator may also provide some default implementation of
        the factory method.
        """
        pass

    def get_base_asset(self, symbol):
        if len(symbol) <= 7:
            return symbol[0:3]
        else:
            return symbol[0:4]

    def get_quote_asset(self, symbol):
        if len(symbol) == 6:
            return symbol[-3:]
        else:
            return symbol[-4:]

    def buy_at_discount(self, run_id, symbol_buy, min_buy, discount):
        # get pricing
        price_buy = self.exchange.get_price(symbol_buy)
        print(price_buy)

        price = round(float(price_buy['bidPrice']) - (float(price_buy['bidPrice']) * discount), 2)
        print(price)

        # calculate amount to buy
        bal = float(math.trunc(self.exchange.get_balance(self.get_quote_asset(symbol_buy))))
        print(bal)

        if bal < min_buy:
            result = "7001 Error. Strategy aborted: Source token below minimum buy threshold"
            self.db.log_action(self.strategy_name, self.exchange.get_exchange_name(), "STRATEGY ABORTED", "7001", result, run_id)
            return None, 1

        qty = round((bal-1) / price, 6)
        print(qty)

        order = self.exchange.create_limit_buy_order(symbol_buy, qty, price)
        print(order)

        if order:
            self.db.log_action(self.strategy_name, self.exchange.get_exchange_name(), "ORDER PLACED", order['orderId'], order, run_id)
            last_phase_completed = self.db.set_next_phase(run_id)
            return order, last_phase_completed
        else:
            result = "7004 Error. Strategy aborted: Order failed"
            self.db.log_action(self.strategy_name, self.exchange.get_exchange_name(), "STRATEGY ABORTED", "7004", result, run_id)
            return None, 1

    def sell_at_premium(self, run_id, symbol_sell, min_sell, premium):
        # get pricing
        price_sell = self.exchange.get_price(symbol_sell)
        print(price_sell)

        price = float(price_sell['askPrice']) + float(price_sell['askPrice']) * premium
        print(price)

        # calculate amount to buy
        bal = self.exchange.get_balance(self.get_base_asset(symbol_sell))
        print(bal)

        if bal < min_sell:
            result = "7002 Error. Strategy aborted: Source token below minimum sell threshold"
            self.db.log_action(self.strategy_name, self.exchange.get_exchange_name(), "STRATEGY ABORTED", "7002", result, run_id)
            return None, 3

        amt_to_sell = bal
        print(amt_to_sell)

        order = self.exchange.create_limit_sell_order(symbol_sell, amt_to_sell, price)
        print(order)

        if order:
            self.db.log_action(self.strategy_name, self.exchange.get_exchange_name(), "ORDER PLACED", order['orderId'], order, run_id)
            last_phase_completed = self.db.set_next_phase(run_id)
            return order, last_phase_completed
        else:
            result = "7004 Error. Strategy aborted: Order failed"
            self.db.log_action(self.strategy_name, self.exchange.get_exchange_name(), "STRATEGY ABORTED", "7004", result, run_id)
            return None, 3

    # obsolete
    def wait_for_order_completion(self, run_id, order, max_wait, check_wait, symbol):
        times_to_check = max_wait / check_wait
        times_checked = 0
        print(order)

        # if order id not in hand go get it from db
        if not order:
            # go fetch the order id using the run_id
            order_id = self.db.get_action_id(run_id)
        else:
            order_id = str(order['orderId'])

        # if order hasn't completed after max_wait minutes
        # break out and cancel order
        while not self.exchange.check_order(symbol=symbol, order_id=order_id):
            # get pricing
            price = self.exchange.get_price(symbol)
            print("Price Info:")
            print(price)

            print("waiting for order to complete")
            times_checked += 1
            if times_checked >= times_to_check:
                # max time to wait to execute the order, so cancel
                self.exchange.cancel_order(symbol=symbol, order_id=order_id)
                result = "7003 Error. Strategy aborted: Order time exceeded threshold"
                self.db.log_action(self.strategy_name, self.exchange.get_exchange_name(), "STRATEGY ABORTED", "7003", result, run_id)

                # need to fetch max phases and return that instead of hard coded value
                return self.total_phases
            time.sleep(check_wait*60)

        order = self.exchange.check_order(symbol=symbol, order_id=order_id)
        self.db.log_action(self.strategy_name, self.exchange.get_exchange_name(), "ORDER FILLED", order_id, order, run_id)

        Sms().send("+12058437892", "+17148784500", "Order filled: " + str(order))
        last_phase_completed = self.db.set_next_phase(run_id)
        return last_phase_completed

    def wait_for_order(self, run_id, order, max_wait, check_wait):
        times_to_check = max_wait / check_wait
        times_checked = 0
        print(order)

        # if order id not in hand go get it from db
        if not order:
            return self.total_phases
        else:
            order_id = str(order['orderId'])
            symbol = str(order['symbol'])

        # if order hasn't completed after max_wait minutes
        # break out and cancel order
        order = self.exchange.get_order(symbol=symbol, order_id=order_id)
        while not self.exchange.check_order(symbol=symbol, order_id=order_id):
            # get pricing
            price = self.exchange.get_price(symbol)
            print("Price Info:")
            print(price)

            print("Waiting for " + str(order['side']) + " order to complete: " + str(order['symbol']))
            times_checked += 1
            if times_checked >= times_to_check:
                # max time to wait to execute the order, so cancel
                self.exchange.cancel_order(symbol=symbol, order_id=order_id)
                result = "7003 Error. Strategy aborted: Order time exceeded threshold"
                self.db.log_action(self.strategy_name, self.exchange.get_exchange_name(), "STRATEGY ABORTED", "7003", result, run_id)

                # need to fetch max phases and return that instead of hard coded value
                return self.total_phases
            time.sleep(check_wait*60)

        order = self.exchange.check_order(symbol=symbol, order_id=order_id)
        self.db.log_action(self.strategy_name, self.exchange.get_exchange_name(), "ORDER FILLED", order_id, order, run_id)

        Sms().send("+12058437892", "+17148784500", "Order filled: " + str(order))
        last_phase_completed = self.db.set_next_phase(run_id)
        return last_phase_completed

    # obsolete
    def execute_strategy_001(self, symbol_buy, symbol_sell, min_buy, max_wait, discount, premium) -> str:
        """
        strategy 001 is buy symbol_buy and sell symbol_sell on same exchange
        use source token balance, but min_buy required
        after min_wait minutes, if an order execution has not completed, strategy is aborted
        """
        self.strategy_name = "STRATEGY_001"
        self.total_phases = 4
        buy_order = None
        sell_order = None

        # Call the factory method to create an exchange object.
        self.exchange = self.factory_method()
        self.exchange.init()

        #init db
        self.db = Db()
        run_id, last_phase_completed = self.db.init(self.strategy_name, self.exchange.get_exchange_name(), self.total_phases)


        # check if there's any open orders
        # if there is, then wait for them to finish
        # if the order completes to non stable
        # then put in an order to sell at symbol_buy
        # then continue with process below

        orders = self.exchange.get_open_orders()
        print(orders)
        #result = self.exchange.cancel_order('BTCUSDC', 218241745)
        #print(result)

        bal = self.exchange.get_balance('USDC')
        print(bal)
        bal = self.exchange.get_balance('USDT')
        print(bal)
        bal = self.exchange.get_balance('BTC')
        print(bal)


        #sell_order, last_phase_completed = self.sell_at_premium(run_id, symbol_buy, self.exchange.get_balance('BTC'), premium)
        #last_phase_completed = self.wait_for_order_completion(run_id, sell_order, max_wait, 2, symbol_buy)
        #exit()

        if last_phase_completed < 1:
            buy_order, last_phase_completed = self.buy_at_discount(run_id, symbol_buy, min_buy, discount)

        if last_phase_completed < 2:
            last_phase_completed = self.wait_for_order_completion(run_id, buy_order, max_wait, 2, symbol_buy)

        time.sleep(300)

        if last_phase_completed < 3:
            sell_order, last_phase_completed = self.sell_at_premium(run_id, symbol_sell, self.exchange.get_balance(self.get_base_asset(symbol_sell)), premium)

        if last_phase_completed < 4:
            last_phase_completed = self.wait_for_order_completion(run_id, sell_order, max_wait, 2, symbol_sell)

        self.db.set_specific_phase(run_id, last_phase_completed)
        self.db.close(self.strategy_name, self.exchange.get_exchange_name(), run_id)

        result = "Completed"
        return result

    def execute_strategy_002(self, min_buy, max_wait, discount, premium, asset) -> str:
        """
        strategy 002 is buy symbol_buy and sell symbol_sell on same exchange
        this strategy is based on current tokens held and what orders are currently open
        """
        self.strategy_name = "STRATEGY_002"
        self.total_phases = 4
        buy_order = None
        sell_order = None
        symbol_buy = asset + "USDC"
        symbol_sell = asset + "USDT"
        symbol_usd = asset + "USD"
        orders = None

        # Call the factory method to create an exchange object.
        self.exchange = self.factory_method()
        self.exchange.init()

        #init db
        self.db = Db()
        run_id, last_phase_completed = self.db.init(self.strategy_name, self.exchange.get_exchange_name(), self.total_phases)


        # check if there's any open orders
        # if there is, then wait for them to finish
        # if the order completes to btc
        # then put in an order to sell at random stable
        # then continue with process below

        bal_usdc = self.exchange.get_balance('USDC')
        print(bal_usdc)
        bal_usdt = self.exchange.get_balance('USDT')
        print(bal_usdt)
        bal_usd = self.exchange.get_balance('USD')
        print(bal_usd)
        bal_asset = self.exchange.get_balance(asset)
        print(bal_asset)

        asset_price = self.exchange.get_price(symbol_sell)
        print(asset_price)

        orders = self.exchange.get_open_orders(symbol_sell)
        print(orders)

        if orders is None or orders == []:
            # pick the token you have the most in dollars
            if bal_usdc > bal_usdt and bal_usdc > bal_usd and bal_usdc > bal_asset * float(asset_price['bidPrice']):
                print("Buying BTC: " + symbol_buy)
                order, last_phase_completed = self.buy_at_discount(run_id, symbol_buy, min_buy, discount)
                last_phase_completed = 1
            elif  bal_usdt > bal_usdc and bal_usdt > bal_usd and bal_usdt > bal_asset * float(asset_price['bidPrice']):
                print("Buying BTC: " + symbol_sell)
                order, last_phase_completed = self.buy_at_discount(run_id, symbol_sell, min_buy, discount)
                last_phase_completed = 1
            elif  bal_usd > bal_usdc and bal_usd > bal_usdt and bal_usd > bal_asset * float(asset_price['bidPrice']):
                print("Buying BTC: " + symbol_usd)
                order, last_phase_completed = self.buy_at_discount(run_id, symbol_usd, min_buy, discount)
                last_phase_completed = 1
            elif bal_asset * float(asset_price['bidPrice']) > bal_usdc and bal_asset * float(asset_price['bidPrice']) > bal_usdt:
                #if random.choice([True, False]):
                order, last_phase_completed = self.sell_at_premium(run_id, symbol_sell, self.exchange.get_balance(self.get_base_asset(symbol_sell)), premium)
                #else:
                #    if random.choice([True, False]):
                #        order, last_phase_completed = self.sell_at_premium(run_id, symbol_usd, self.exchange.get_balance(self.get_base_asset(symbol_usd)), premium)
                #    else:
                #        order, last_phase_completed = self.sell_at_premium(run_id, symbol_buy, self.exchange.get_balance(self.get_base_asset(symbol_buy)), premium)

                # last_phase_completed should not complete until the end of this script run
                last_phase_completed = 3
        else:
            # wait for current order to finish
            last_phase_completed = self.wait_for_order(run_id, orders[0], max_wait, 2)

        self.db.set_specific_phase(run_id, last_phase_completed)
        self.db.close(self.strategy_name, self.exchange.get_exchange_name(), run_id)

        result = "Completed Strategy"
        return result
