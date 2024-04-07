from enum import IntEnum
import numpy as np
import math

from simulate.orderbook.order_book import OrderBook

class OrderEvents:
    Limit=1
    Market=2
    Cancel=3

class Simulation:
    """
    Simulations Birth Death Process of orderbook
    """
    def __init__(self, process_rates, depth=3, tick_size = 0.01, midprice = 100, length=100):
        self.process_rates = process_rates

        self.orderbook = OrderBook()
    
        self.time = 0.
        self.orderbook_history = [self.orderbook.get_mkt_depth(3)]
        self.time_history = [0.]
        self.depth = depth
        self.tick_size = tick_size
        self.midprice = midprice
        self.length = length

    def next_event(self):
        """
        generate the waiting time and identity of the next event.
        outputs:
        tau: float, waiting time before next event.
        event: int, 0 means birth and 1 means death.
        """

        depth = 0

        best_ask = self.orderbook.get_mkt_depth(1)[0]

        lambda_length = 100

        if len(best_ask) == 0:
            ask_size = 0
        else:
            ask_size = min(math.ceil(best_ask[0][1]), lambda_length - 1)
        
        best_bid = self.orderbook.get_mkt_depth(1)[1]

        if len(best_bid) == 0:
            bid_size = 0
        else:
            bid_size = min(math.ceil(best_ask[0][1]), lambda_length - 1)

        # Gets the b/d rates at depth = 0
        k_bid_limit = self.process_rates[depth][0][0][bid_size]
        k_bid_market = self.process_rates[depth][0][1][bid_size]
        k_bid_cancel = self.process_rates[depth][0][2][bid_size]

        # lambdas[depth_level][OrderbookIndexes.Ask][OrderbookTypes.Limit][queue_length]
        k_ask_limit = self.process_rates[depth][0][0][ask_size]
        k_ask_market = self.process_rates[depth][0][1][ask_size]
        k_ask_cancel = self.process_rates[depth][0][2][ask_size]

        tb_limit = np.random.exponential(k_bid_limit)    # draw a random number from exponential dist as putative birth time        
        tb_market = np.random.exponential(k_bid_market)    # draw a random number from exponential dist as putative death time
        tb_cancel = np.random.exponential(k_bid_cancel)    # draw a random number from exponential dist as putative death time
        # Test if 1/k works for the time interval
        # t_cancel = np.random.exponential(1/k_bid_cancel)    # draw a random number from exponential dist as putative death time

        ta_limit = np.random.exponential(k_ask_limit)    # draw a random number from exponential dist as putative birth time        
        ta_market = np.random.exponential(k_ask_market)    # draw a random number from exponential dist as putative death time
        ta_cancel = np.random.exponential(k_ask_cancel)    # draw a random number from exponential dist as putative death time
        # Test if 1/k works for the time interval
        # t_cancel = np.random.exponential(1/k_bid_cancel)    # draw a random number from exponential dist as putative death time

        self.orderbook.submit_order('lmt', 'bid', tb_limit, self.midprice - self.tick_size, 0)
        self.orderbook.submit_order('mkt', 'bid', tb_market, self.midprice - self.tick_size, 0)
        self.orderbook.submit_order('mkt', 'bid', tb_cancel, self.midprice - self.tick_size, 0)
        
        self.orderbook.submit_order('lmt', 'ask', ta_limit, self.midprice + self.tick_size, 0)
        self.orderbook.submit_order('mkt', 'ask', ta_market, self.midprice + self.tick_size, 0)
        self.orderbook.submit_order('mkt', 'ask', ta_cancel, self.midprice + self.tick_size, 0)

    def run(self):
        for i in range(0, self.length):
            self.next_event()
            self.time_history.append(self.time)    # record time of event
            self.orderbook_history.append(self.orderbook.get_mkt_depth(3))    # record population size after event