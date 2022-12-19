from Exchanges.Binance.BinanceCreator import *
from Exchanges.Mexc.MexcCreator import *


def client_code(creator: ExchangeCreator) -> None:
    """
    The client code works with an instance of a concrete creator, albeit through
    its base interface. As long as the client keeps working with the creator via
    the base interface, you can pass it any creator's subclass.
    """
    #creator.execute_strategy_002(10.0, 2400, 0.0035, 0.0035, "BTC")
    creator.execute_strategy_002(10.0, 2400, 0.0035, 0.0035, "ETH")


    #creator.execute_strategy_001("BTCUSDT", "BTCUSDC", 10.0, 240, 0.0025, 0.0025)
    #creator.execute_strategy_001("BTCUSDC", "BTCUSDT", 10.0, 240, 0.0025, 0.0025)
    print("waiting to restart")
    time.sleep(300)

if __name__ == "__main__":

    while True:
        print("App: Launched with the BinanceCreator.")
        client_code(BinanceCreator())

        print("App: Launched with the MexcCreator.")
        client_code(MexcCreator())

        print("\n")

