from simulate.simulate import Simulation, generateRandomParticantId
import numpy as np
from enum import IntEnum
from matplotlib import pyplot as plt
from orderbook import OrderBook
import json
import pandas as pd
import seaborn as sns
from decimal import Decimal
import time

lambdas = None
markers = None

VERBOSE = False
participant_id = 0

def callback(sim: Simulation):
    trade_executed = sim.participant_volume > 0
    # bid_trade_executed = sim.bid_participant_volume > 0
    # ask_trade_executed = sim.ask_participant_volume > 0

    did_midprice_change = sim.midprices[-1] != sim.midprice

    if(trade_executed or did_midprice_change):
        return True
    
    empty_orderbook = sim.orderbook.get_best_ask() == None or sim.orderbook.get_best_bid() == None    
    if(empty_orderbook):
        print("ERROR | Empty Orderbook side")
        return True
    
    return False

def main():
    start_time = time.time()
    
    orderbook = OrderBook()
    starting_orders = [
        {
        'type' : 'limit', 
        'side' : 'bid', 
        'quantity' : Decimal(15),
        'price' : Decimal(99_99_0), 
        'trade_id' : 1
        },
        {
        'type' : 'limit', 
        'side' : 'ask', 
        'quantity' : Decimal(15),
        'price' : Decimal(100_00_0), 
        'trade_id' : 1
        },
        {
        'type' : 'limit', 
        'side' : 'bid', 
        'quantity' : Decimal(1),
        'price' : Decimal(99_99_0), 
        'trade_id' : participant_id
        },
        {
        'type' : 'limit', 
        'side' : 'ask', 
        'quantity' : Decimal(1),
        'price' : Decimal(100_00_0), 
        'trade_id' : participant_id
        },
    ]
    
    for order in starting_orders:
        orderbook.process_order(order, False, False)
    
    simulation = Simulation(
        lambdas, 
        markers,
        
        length=-1, 
        orderbook=orderbook,

        participant_id=participant_id,
        verbose= VERBOSE,
    )
    
    trials = 1
    depth = 30
    
    for i in range(trials):    
        simulation.run(callback=callback)
    
    print("--- %s seconds ---" % (time.time() - start_time))        
    
if __name__ == '__main__':
    lambdas = np.load('./outputs/lambdas.npy', allow_pickle=True)

    f = open('./outputs/lambda_markers.json')
    markers = json.load(f)
    f.close()
    
    main()