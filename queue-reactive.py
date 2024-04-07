import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from lib.data import loadData, normalizeData
from lib.intensity import calculateLambdas, plotLambdas
from lib.distribution import InvariantDistribution

from simulate.simulate import Simulation

pd.options.mode.chained_assignment = None  # default='warn'

# prefix = "AMZN_2012-06-21_34200000_57600000"
prefix = "INTC_2012-06-21_34200000_57600000"

trades_data_file = f"./data/{prefix}_message_5.csv"
orderbook_data_file = f"./data/{prefix}_orderbook_5.csv"

DEPTH = 3
ORDER_TYPES = 3
PRICE_TICK = 100
NORMALIZED_QUEUE_MAX = 50

df = loadData(trades_data_file, orderbook_data_file)
normalizeData(df, DEPTH, PRICE_TICK)

lambdas = calculateLambdas(df, DEPTH, NORMALIZED_QUEUE_MAX, ORDER_TYPES)
plotLambdas(lambdas, ORDER_TYPES)

# Monte Carlo Simulation
prob_of_exec = Simulation()
