from ExchangeCreator import *
from Exchanges.Mexc.Mexc import *


"""
Concrete Creators override the factory method in order to change the resulting
product's type.
"""


class MexcCreator(ExchangeCreator):

    def factory_method(self) -> Exchange:
        return Mexc()
