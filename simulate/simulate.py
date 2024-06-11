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
lambda_length = 100

def generateRandomParticantId():
    return np.random.randint(0, 1000000)

class Simulation:
    """
    Simulations Birth Death Process of orderbook
    """
    def __init__(self, process_rates, orderbook=None, depth=1, tick_size = 10, midprice = 99_995, length=100):
        self.process_rates = process_rates
        
        self.tick_size = tick_size
        
        self.midprice = midprice
        self.spread = 0

        if(orderbook is None):
            orderbook = OrderBook()
        
        self.orderbook = orderbook
        self.orderbook.submit_order('lmt', 'ask', 5, 100_000, generateRandomParticantId())
        self.orderbook.submit_order('lmt', 'bid', 5, 99_990, generateRandomParticantId())
        self.orderbook_history = [self.orderbook.get_mkt_depth(3)]
        
        self.midprices = [self.midprice]
        
        self.time = 0.
        self.time_history = [0.]
        
        self.depth = depth
        self.length = length
        
    def next_event(self):
        """
        generate the waiting time and identity of the next event.
        outputs:
        tau: float, waiting time before next event.
        event: int, 0 means birth and 1 means death.
        """

        best_bid_array = self.orderbook.get_mkt_depth(1)[1]
        best_ask_array = self.orderbook.get_mkt_depth(1)[0]
        
        
        if len(best_ask_array) == 0 or len(best_bid_array) == 0:
            print("Error: No best bid or best ask")
            return ValueError("No best bid or best ask")
        
        [best_ask_price, ask_size] = best_ask_array[0]
        ask_size = min(math.ceil(ask_size), lambda_length - 1) 
               
        [best_bid_price, bid_size] = best_bid_array[0]
        bid_size = min(math.ceil(bid_size), lambda_length - 1)

        self.midprice = (best_ask_price + best_bid_price) / 2
        self.spread = best_ask_price - best_bid_price

        bid_reference_price, ask_reference_price = 0, 0
        self.midprices.append(self.midprice)
        # print(f"Midprice {self.midprice}, Spread {self.spread}")
        # print(f"Ask {ask_size}, Bid {bid_size}")
        
        if(self.spread % self.tick_size == 0):
            # if the midprice is between two ticks that are enxt to each other
            # i.e. midprice = 100.050, tick_size = 0.01, bid = 100.00, ask = 100.01, spread = 0.01
            bid_reference_price = self.midprice - self.tick_size / 2
            ask_reference_price = self.midprice + self.tick_size / 2
        else:
            # If the midprice is between two ticks that are NOT next to each other
            # i.e. midprice = 100.01, tick_size = 0.01, bid = 100.00, ask = 100.02, spread = 0.02
            bid_reference_price = self.midprice
            ask_reference_price = self.midprice
        
        # Gets the b/d rates at depth = 0
        for depth_index in range(0, self.depth):
            bid_limit_intensity = self.process_rates[depth_index][OrderbookIndexes.Bid][OrderbookTypes.Limit][bid_size]
            bid_market_intensity = self.process_rates[depth_index][OrderbookIndexes.Bid][OrderbookTypes.Market][bid_size]
            bid_cancel_intensity = self.process_rates[depth_index][OrderbookIndexes.Bid][OrderbookTypes.Cancel][bid_size]
            ask_limit_intensity = self.process_rates[depth_index][OrderbookIndexes.Ask][OrderbookTypes.Limit][ask_size]
            ask_market_intensity = self.process_rates[depth_index][OrderbookIndexes.Ask][OrderbookTypes.Market][ask_size]
            ask_cancel_intensity = self.process_rates[depth_index][OrderbookIndexes.Ask][OrderbookTypes.Cancel][ask_size]

            print(f"Depth: {depth_index}, Bid: {bid_limit_intensity}, {bid_market_intensity}, {bid_cancel_intensity}")

            tb_limit = np.random.exponential(bid_limit_intensity)* modifier
            tb_market = np.random.exponential(bid_market_intensity)* modifier
            tb_cancel = np.random.exponential(bid_cancel_intensity)* modifier
            
            ta_limit = np.random.exponential(ask_limit_intensity)* modifier
            ta_market = np.random.exponential(ask_market_intensity)* modifier
            ta_cancel = np.random.exponential(ask_cancel_intensity)* modifier
                        
            # use time delays rather than sizes (1/k_bid_cancel)
            
            if best_bid_array[0][1] + tb_limit < tb_market + tb_cancel:
                print(f"{self.time}: tb_limit + bid_size: {tb_limit + best_bid_array[0][1]} < tb_market + tb_cancel {tb_market + tb_cancel}. ")
            
            self.orderbook.submit_order('lmt', 'bid', tb_limit, bid_reference_price - 10 * depth_index, generateRandomParticantId())
            self.orderbook.submit_order('mkt', 'bid', tb_market, bid_reference_price - 10 * depth_index, generateRandomParticantId())
            self.orderbook.submit_order('mkt', 'bid', tb_cancel, bid_reference_price - 10 * depth_index, generateRandomParticantId())
        
            self.orderbook.submit_order('lmt', 'ask', ta_limit, ask_reference_price + 10 * depth_index, generateRandomParticantId())
            self.orderbook.submit_order('mkt', 'ask', ta_market, ask_reference_price + 10 * depth_index, generateRandomParticantId())
            self.orderbook.submit_order('mkt', 'ask', ta_cancel, ask_reference_price + 10 * depth_index, generateRandomParticantId())

    def run(self):
        print(f"Running Simulation. Real Tick Size={self.tick_size}. Midprice={self.midprice}. Spread={self.spread}")
        for i in range(0, self.length):
            self.next_event()
            
            self.orderbook_history.append(self.orderbook.get_mkt_depth(3))    # record population size after event
            
            self.time += 1
            self.time_history.append(self.time)    # record time of event