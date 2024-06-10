from enum import IntEnum
import numpy as np
import math

from simulate.orderbook.order_book import OrderBook

class OrderbookIndexes(IntEnum):
    Bid=0
    Ask=1

class OrderbookTypes:
    Limit=0
    Market=1
    Cancel=2

modifier = 0.1

def generateRandomParticantId():
    return np.random.randint(0, 1000000)

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
        self.spread = 0

    def round_to_tick_size(self, price, tick_size):
        return round(price / tick_size) * tick_size

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

        if len(best_ask) != 0 and len(best_bid) != 0:
            print("Best Ask:", best_ask[0][0], "Best Bid:", best_bid[0][0])
            self.midprice = self.round_to_tick_size((best_ask[0][0] + best_bid[0][0]) / 2, self.tick_size * 0.1)
            self.spread = self.round_to_tick_size(best_ask[0][0] - best_bid[0][0], self.tick_size)
            print("Midprice:", self.midprice, "Spread:", self.spread)

        bid_reference_price, ask_reference_price = 0, 0
        if(self.spread == self.tick_size):
            # if the midprice is between two ticks that are enxt to each other
            # i.e. midprice = 100.005, tick_size = 0.01, bid = 100.00, ask = 100.01, spread = 0.01
            bid_reference_price = self.midprice - self.tick_size / 2
            ask_reference_price = self.midprice + self.tick_size / 2
        else:
            # If the midprice is between two ticks that are NOT next to each other
            # i.e. midprice = 100.01, tick_size = 0.01, bid = 100.00, ask = 100.02, spread = 0.02
            bid_reference_price = self.midprice
            ask_reference_price = self.midprice
        
        print("BRP:", bid_reference_price, "ARP:", ask_reference_price)

        # Gets the b/d rates at depth = 0
        for depth_index in range(0, self.depth):
            bid_limit = self.process_rates[depth_index][OrderbookIndexes.Bid][OrderbookTypes.Limit][bid_size]
            bid_market = self.process_rates[depth_index][OrderbookIndexes.Bid][OrderbookTypes.Market][bid_size]
            bid_cancel = self.process_rates[depth_index][OrderbookIndexes.Bid][OrderbookTypes.Cancel][bid_size]
            ask_limit = self.process_rates[depth_index][OrderbookIndexes.Ask][OrderbookTypes.Limit][ask_size]
            ask_market = self.process_rates[depth_index][OrderbookIndexes.Ask][OrderbookTypes.Market][ask_size]
            ask_cancel = self.process_rates[depth_index][OrderbookIndexes.Ask][OrderbookTypes.Cancel][ask_size]


            tb_limit = np.random.exponential(bid_limit)    # draw a random number from exponential dist as putative birth time        
            tb_market = np.random.exponential(bid_market)    # draw a random number from exponential dist as putative death time
            tb_cancel = np.random.exponential(bid_cancel)    # draw a random number from exponential dist as putative death time
            ta_limit = np.random.exponential(ask_limit)    # draw a random number from exponential dist as putative birth time        
            ta_market = np.random.exponential(ask_market)    # draw a random number from exponential dist as putative death time
            ta_cancel = np.random.exponential(ask_cancel)    # draw a random number from exponential dist as putative death time
            
            # print("Intensities:", k_bid_limit, k_bid_market, k_bid_cancel)
            # print("Values:", tb_limit, tb_market, tb_cancel )
            
            # Test if 1/k works for the time interval
            # t_cancel = np.random.exponential(1/k_bid_cancel)    # draw a random number from exponential dist as putative death time
            
            self.orderbook.submit_order('lmt', 'bid', tb_limit * modifier, bid_reference_price - self.tick_size * depth_index, generateRandomParticantId())
            self.orderbook.submit_order('mkt', 'bid', tb_market * modifier, bid_reference_price - self.tick_size * depth_index, generateRandomParticantId())
            self.orderbook.submit_order('mkt', 'bid', tb_cancel * modifier, bid_reference_price - self.tick_size * depth_index, generateRandomParticantId())
        
            self.orderbook.submit_order('lmt', 'ask', ta_limit * modifier, ask_reference_price + self.tick_size * depth_index, generateRandomParticantId())
            self.orderbook.submit_order('mkt', 'ask', ta_market * modifier, ask_reference_price + self.tick_size * depth_index, generateRandomParticantId())
            self.orderbook.submit_order('mkt', 'ask', ta_cancel * modifier, ask_reference_price + self.tick_size * depth_index, generateRandomParticantId())

    def run(self):
        for i in range(0, self.length):
            self.next_event()
            self.time_history.append(self.time)    # record time of event
            self.orderbook_history.append(self.orderbook.get_mkt_depth(3))    # record population size after event