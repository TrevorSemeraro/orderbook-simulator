from enum import IntEnum
import numpy as np

from orderbook.order_book import OrderBook

class OrderEvents:
    Limit=1
    Market=2
    Cancel=3

class Simulation:
    """
    Simulations Birth Death Process of orderbook
    """
    def __init__(self, process_rates, starting_condititons = None):
        self.process_rates = process_rates

        self.orderbook = OrderBook()

        # TODO: Add starting conditiions to orderbook if specified
        if(starting_condititons != None):
            print("Starting Conditions not yet implemented")
    
        self.time = 0.
        self.orderbook_history = [self.orderbook.get_mkt_depth(3)]
        self.time_history = [0.]

    def next_event(self):
        """
        generate the waiting time and identity of the next event.
        outputs:
        tau: float, waiting time before next event.
        event: int, 0 means birth and 1 means death.
        """


        # Gets the b/d rates at depth = 0
        k_bid_limit = self.process_rates[0][0]
        k_bid_market = self.process_rates[0][1]
        k_bid_cancel = self.process_rates[0][2]
        
        t_limit = np.random.exponential(1/k_bid_limit)    # draw a random number from exponential dist as putative birth time
        
        t_market = np.random.exponential(1/k_bid_market)    # draw a random number from exponential dist as putative death time
        # t_cancel = np.random.exponential(1/k_bid_cancel)    # draw a random number from exponential dist as putative death time

        if t_limit < t_market:    # birth happens first
            return t_limit, OrderEvents.Limit
        else:    # death happens first
            return t_market, OrderEvents.Market
        
    def run(self, midprice=100, length=100, tick_size = 0.01):

        while self.time < length:
            tau, event = self.next_event()    # draw next event
            self.time += tau    # update time

            if event == OrderEvents.Limit:    # birth happens
                self.orderbook.submit_order('lmt', 'bid', 1, midprice - tick_size, 0)
                self.orderbook.submit_order('lmt', 'ask', 1, midprice - tick_size, 0)
            elif event == OrderEvents.Market:    # death happens
                self.orderbook.submit_order('mkt', 'bid', 0.5, midprice - tick_size, 0)
                self.orderbook.submit_order('mkt', 'ask', 0.5, midprice - tick_size, 0)
            
            self.time_hist.append(self.time)    # record time of event
            self.pop_hist.append(self.orderbook.get_mkt_depth(3))    # record population size after event