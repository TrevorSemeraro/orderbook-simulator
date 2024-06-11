# Monte Carlo Simulation
from simulate.simulate import Simulation
import numpy as np
from enum import IntEnum
from matplotlib import pyplot as plt

lambdas = np.load('lambdas.npy')

class OrderbookEventTypes(IntEnum):
    Limit=1
    PartialCancel=2
    Deletion=3
    ExecutionOfVisibleOrder=4
    ExecutionOfHiddenOrder=5
    TradingHalt=7

class OrderbookIndexes(IntEnum):
    Bid=0
    Ask=1

DEPTH = 3
ORDER_TYPES = 3
PRICE_TICK = 100
NORMALIZED_QUEUE_MAX = 50

prob_of_exec = Simulation(lambdas, length=20)
prob_of_exec.run()

# Orderbook dataframe
import pandas as pd

orderbook_history = []

for orderbook in prob_of_exec.orderbook_history:
    orderbook_history.append(orderbook)
    
orderbook_df = pd.DataFrame(orderbook_history, columns=['Ask', 'Bid'])

print(orderbook_df)