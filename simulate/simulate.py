from enum import IntEnum
import numpy as np
import math
import sys
from typing import Callable
from decimal import Decimal
import random

from orderbook.order import Order

sys.path.append('..')

# relative imports
from orderbook import OrderBook

class OrderbookIndexes(IntEnum):
    Bid=0
    Ask=1

class OrderbookTypes(IntEnum):
    Limit=0
    Market=1
    Cancel=2

modifier = 0.1
lambda_length = 50

def generateRandomParticantId():
    return np.random.randint(0, 1E3)

class Simulation:
    """
    Simulations Birth Death Process of orderbook
    """
    orderbook: OrderBook
    def __init__(
            self, 
            process_rates,
            lambda_markers=None, 
            orderbook=None, 
            depth:int=1, 
            tick_size:int= 10, 
            midprice:int=99_995, 
            length:int=100, 
            participant_id=0,
            initial_bid_quantity:int=5,
            initial_ask_quantity:int=5,
            verbose= False
        ):
        self.process_rates = process_rates
        self.lambda_markers = lambda_markers
        self.tick_size = tick_size
        self.midprice = midprice
        self.spread = 0
        self.verbose = verbose
        
        self.bid_orders = []
        self.ask_orders = []

        if(orderbook is None):
            orderbook = OrderBook()
            
            limit_orders = []
            
            for _ in range(0, initial_bid_quantity):
                bid_order_id = generateRandomParticantId()
                self.bid_orders.append(bid_order_id)
                limit_orders.append({
                    'type' : 'limit', 
                    'side' : 'bid', 
                    'quantity' : Decimal(1), 
                    'price' : Decimal(midprice - (tick_size / 2)),
                    'trade_id' : bid_order_id
                })
            for _ in range(0, initial_ask_quantity):
                ask_order_id = generateRandomParticantId()
                self.ask_orders.append(ask_order_id)
                limit_orders.append({
                    'type' : 'limit', 
                    'side' : 'ask', 
                    'quantity' : Decimal(1), 
                    'price' : Decimal(midprice + (tick_size / 2)),
                    'trade_id' : ask_order_id
                })

            # Add orders to order book
            for order in limit_orders:
                trades, order_id = orderbook.process_order(order, False, self.verbose)
                self.process_trade(trades)
        
        self.orderbook = orderbook
        self.midprices = [self.midprice]
        self.time = 0.
        self.time_history = [0.]
        self.depth = depth
        self.length = length
        
        self.participant_id = participant_id
        self.participant_volume = 0
        self.should_stop = False
    
    def calculate_lambda_markers(self, queue_size, percentile_33, percentile_66):
        if(queue_size == 0):
            return 0
        elif(queue_size < percentile_33):
            return 1
        elif(queue_size < percentile_66):
            return 2
        else:
            return 3

    
    def next_event(self) -> bool:
        """
        generate the waiting time and identity of the next event.
        outputs:
        """
        
        best_ask_price = self.orderbook.get_best_ask()
        best_bid_price = self.orderbook.get_best_bid()
        if(self.verbose):
            print("Best Prices | Ask:", best_ask_price, "Bid:", best_bid_price)
        
        ask_size = self.orderbook.get_volume_at_price('ask', best_ask_price)
        ask_size = min(math.ceil(ask_size), lambda_length - 1) 
               
        bid_size = self.orderbook.get_volume_at_price('bid', best_bid_price)
        bid_size = min(math.ceil(bid_size), lambda_length - 1)

        self.midprice = (best_ask_price + best_bid_price) / Decimal(2)
        self.spread = best_ask_price - best_bid_price

        bid_reference_price, ask_reference_price = 0, 0
        self.midprices.append(self.midprice)
        # print(f"Midprice {self.midprice}, Spread {self.spread}")
        # print(f"Ask {ask_size}, Bid {bid_size}")
        
        if(self.spread % self.tick_size == 0):
            # if the midprice is between two ticks that are enxt to each other
            # i.e. midprice = 100.050, tick_size = 0.01, bid = 100.00, ask = 100.01, spread = 0.01
            bid_reference_price = self.midprice - self.tick_size / Decimal(2)
            ask_reference_price = self.midprice + self.tick_size / Decimal(2)
        else:
            # If the midprice is between two ticks that are NOT next to each other
            # i.e. midprice = 100.01, tick_size = 0.01, bid = 100.00, ask = 100.02, spread = 0.02
            bid_reference_price = self.midprice
            ask_reference_price = self.midprice
        
        for depth_index in range(0, self.depth):
            ask_queue_size = min(math.ceil(ask_size), lambda_length - 1)
            bid_queue_size = min(math.ceil(bid_size), lambda_length - 1)
            
            ask_queue_group = self.calculate_lambda_markers(ask_queue_size, self.lambda_markers['ask_queue_size_33_percentile'], self.lambda_markers['ask_queue_size_66_percentile'])
            bid_queue_group = self.calculate_lambda_markers(bid_queue_size, self.lambda_markers['bid_queue_size_33_percentile'], self.lambda_markers['bid_queue_size_66_percentile'])
            
            # Limit, Market, Cancel
            bid_intensities = [0, 0, 0]
            ask_intensities = [0, 0, 0]
            
            for order_type in OrderbookTypes:
                bid_intensities[order_type] = self.process_rates[OrderbookIndexes.Ask][ask_queue_group][OrderbookIndexes.Bid][order_type][bid_size]
                ask_intensities[order_type] = self.process_rates[OrderbookIndexes.Bid][bid_queue_group][OrderbookIndexes.Ask][order_type][ask_size]
            
            # if(self.verbose):
                # print(bid_size, bid_queue_size, bid_queue_group)
                # print(ask_size, ask_queue_size, ask_queue_group)
                # print("bid intensities:", bid_intensities)
                # print("ask intensities:", ask_intensities)
            
            bid_order_amounts = [np.random.exponential(x) * modifier for x in bid_intensities]
            ask_order_amounts = [np.random.exponential(x) * modifier for x in ask_intensities]
            
            bid_order_id = generateRandomParticantId()
            ask_order_id = generateRandomParticantId()
            
            self.bid_orders.append(bid_order_id)
            self.ask_orders.append(ask_order_id)
            
            orders = [
                {
                    'type' : 'limit', 
                    'side' : 'bid', 
                    'quantity' : Decimal(bid_order_amounts[0]), 
                    'price' : bid_reference_price - 10 * depth_index,
                    'trade_id' : bid_order_id
                },
                {
                    'type' : 'limit', 
                    'side' : 'ask', 
                    'quantity' : Decimal(ask_order_amounts[0]), 
                    'price' : ask_reference_price + 10 * depth_index,
                    'trade_id' : ask_order_id
                },
                # our ask intensity is the amount that we want to market order on the buy side, therefore it is a market bid, and vice versa.
                {
                    'type' : 'market', 
                    'side' : 'bid', 
                    'quantity' : Decimal(ask_order_amounts[1]), 
                    'trade_id' : generateRandomParticantId()
                },
                {
                    'type' : 'market', 
                    'side' : 'ask', 
                    'quantity' : Decimal(bid_order_amounts[1]), 
                    'trade_id' : generateRandomParticantId()
                },
            ]
            
            # Process orders
            for order in orders:
                if(order['quantity'] <= 0):
                    continue
                
                trades, order_in_book = self.orderbook.process_order(order, False, self.verbose)
                self.process_trade(trades)
            
            bid_amount_to_cancel = Decimal(bid_order_amounts[2])
            bid_price = bid_reference_price - 10 * depth_index
            self.cancelOrderbookQuantity('bid', bid_amount_to_cancel, bid_price)
            
            ask_amount_to_cancel = Decimal(ask_order_amounts[2])
            ask_price = ask_reference_price + 10 * depth_index
            self.cancelOrderbookQuantity('ask', ask_amount_to_cancel, ask_price)


        return False
    
    def cancelOrderbookQuantity(self, side: str, quantity: Decimal, price: Decimal):
        """Cancels specified amount sitting on top of orderbook at random.
        Returns true is there is enough volume to cancel
        Returns false if there is not enough volume to process the request"""    
        
        if(self.verbose):
            print("Processing Order Cancellation:", side, quantity)
            
        while(quantity > 0):
            orders : list[Order] = []
        
            if(side == 'ask'):
                orders = self.orderbook.asks.get_orders_at_price(price)
            else:
                orders = self.orderbook.bids.get_orders_at_price(price)
                
            if(len(orders) == 0):
                return False
        
            random_order : Order = random.choice(orders)  
            order_id = random_order.order_id 
            order_size = random_order.quantity
            
            if(order_size > quantity):
                new_size = order_size - quantity
                quantity = 0
                
                order_size = new_size
                
                self.orderbook.modify_order(order_id, {
                    'type' : 'limit', 
                    'side' : 'ask', 
                    'quantity' : new_size, 
                    'price' : random_order.price,
                    'trade_id' : random_order.trade_id
                })
            else:
                self.orderbook.cancel_order(side, order_id)
                quantity -= order_size
        return True
    
    def loop(self, callback: Callable[['Simulation'], bool]):
        self.should_stop = callback(self)
                
        if(self.verbose):
            print(f"Simulation Round {self.time} | Ending?={self.should_stop}")
        
        if(self.should_stop):
            return
        
        self.next_event()
        
        self.time += 1
        self.time_history.append(self.time)
        
        print(f"*** ORDERBOOK {self.time} ***")
        print(self.orderbook)
    
    def run(self, callback: Callable[['Simulation'], bool]):
        """ Run the simulation
        callback: function to call after each event, return True to stop the simulation, takes in the simulation object
        """
        if(self.verbose):
            print(f"Running Simulation. Real Tick Size={self.tick_size}. Midprice={self.midprice}. Spread={self.spread}")
        
        if(self.length == -1):
            while not self.should_stop:
                self.loop(callback=callback)
            
        for _ in range(0, self.length):
            if(self.should_stop):
                break
            
            self.loop(callback=callback)
            
    def process_trade(self, trades):
        for trade in trades:
            if trade['party1'][0] == self.participant_id or trade['party2'][0] == self.participant_id:
                # TODO: check if there is any volume left for the participant, call callbacks, run scripts, etc...
                self.participant_volume += trade['quantity']
                continue