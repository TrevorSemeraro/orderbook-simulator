from simulate.simulate import Simulation, generateRandomParticantId
import numpy as np
from enum import IntEnum
from matplotlib import pyplot as plt
from orderbook import OrderBook
import json
import pandas as pd
import seaborn as sns
from decimal import Decimal

lambdas = None
markers = None

VERBOSE = False

def simulate(ask_min : float, bid_min : float):
    participant_id = 0
    
    sim = Simulation(
        lambdas, 
        markers, 
        length=100, 
        initial_bid_quantity=int(bid_min), 
        initial_ask_quantity=int(ask_min),
        participant_id=participant_id,
        verbose= VERBOSE
    )
    
    starting_order = {
        'type' : 'limit', 
        'side' : 'bid', 
        'quantity' : Decimal(1),
        'price' : Decimal(99_99_0), 
        'trade_id' : participant_id
    }
    sim.orderbook.process_order(starting_order, False, False)
    
    def callback():
        if(sim.participant_volume > 0):
            if(VERBOSE):
                print("Ending | Trade Executed")
            return True
        
        did_midprice_change = sim.midprices[-1] != sim.midprice
        if(did_midprice_change):
            if(VERBOSE):
                print("Ending | Midprice Change")
            return True
        
        if(sim.orderbook.get_best_ask() == None or sim.orderbook.get_best_bid() == None):
            if(VERBOSE):
                print("Ending | Empty Orderbook side")
            return True
        
        return False
    
    sim.run(callback)
    
    if(VERBOSE):
        print("Participate Trade Volume:", sim.participant_volume)
    return sim.participant_volume > 0

def main():
    # SETTINGS
    number_of_bins = 30
    trials = 50
    orderbook_min_start_size = 1
    orderbook_max_start_size = 30
    
    # Simulation Start
    z_bin = np.linspace(orderbook_min_start_size, orderbook_max_start_size, number_of_bins)
    print(z_bin)
    probabilities = np.zeros((number_of_bins - 1, number_of_bins - 1))

    for bi, (bid_min, bid_max) in enumerate(zip(z_bin[:-1], z_bin[1:])):
        for ai, (ask_min, ask_max) in enumerate(zip(z_bin[:-1], z_bin[1:])):
            score = 0
            for trial_index in range(0, trials):
                did_order_execute = simulate(ask_min, bid_min)
                if(did_order_execute):
                    score += 1
            probabilities[bi][ai] = score / trials
        print(f'Finished {bi + 1} of {number_of_bins}')

    # The probabilities do not seem to be printing correctly to sns heatmap
    # print(probabilities)

    ax = sns.heatmap(probabilities, linewidth=0.5, cmap='coolwarm')
    ax.invert_yaxis()
    # ax.set_yticks(list(z_bin)[:len(z_bin)-1])

    plt.xlabel('Inital Ask 1 Size')
    plt.ylabel('Inital Bid 1 Size')    
    
    plt.title('Probability of Bid Execution')
    plt.show()
    
    with open('./outputs/probabilities.json', 'w') as f:
        json.dump(probabilities.tolist(), f)

if __name__ == '__main__':
    lambdas = np.load('./outputs/lambdas.npy', allow_pickle=True)

    f = open('./outputs/lambda_markers.json')
    markers = json.load(f)
    f.close()
    
    main()
    
    # # Single Simulation
    # result = simulate(15, 15)
    # print(result)