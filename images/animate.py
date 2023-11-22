import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.animation as animation

# prefix = "AMZN_2012-06-21_34200000_57600000"
prefix = "INTC_2012-06-21_34200000_57600000"

trades_data_file = f"./data/{prefix}_message_5.csv"
orderbook_data_file = f"./data/{prefix}_orderbook_5.csv"

trade_df = pd.read_csv(trades_data_file, names=(
    'time',
    'type',
    'orderId',
    'size',
    'price',
    'direction'
))

orderbook_df = pd.read_csv(orderbook_data_file, names=(
    'ask1_price',
    'ask1_size',
    'bid1_price',
    'bid1_size',

    'ask2_price',
    'ask2_size',
    'bid2_price',
    'bid2_size',

    'ask3_price',
    'ask3_size',
    'bid3_price',
    'bid3_size',

    'ask4_price',
    'ask4_size',
    'bid4_price',
    'bid4_size',

    'ask5_price',
    'ask5_size',
    'bid5_price',
    'bid5_size',
))

df = pd.concat([trade_df, orderbook_df], axis=1)
df['event_lapse'] = df['time'].diff().fillna(0)

fig, ax = plt.subplots()
rng = np.random.default_rng(19680801)
data = np.array([20, 20, 20, 20])
x = np.array([1, 2, 3, 4])

artists = []

def analyzeFrame(frame: int):
    row = df.iloc[frame]
    bid_prices = [
        row['bid1_price'],
        row['bid2_price'],
        row['bid3_price']
    ]
    bid_sizes = [
        row['bid1_size'],
        row['bid2_size'],
        row['bid3_size']
    ]
    ask_prices = [
        row['ask1_price'],
        row['ask2_price'],
        row['ask3_price']
    ]
    ask_sizes = [
        row['ask1_size'],
        row['ask2_size'],
        row['ask3_size']
    ]
    # container = ax.bar(np.concatenate(np.divide(bid_prices, 10000), np.divide(ask_prices, 10000)), np.concatenate(bid_sizes, ask_sizes), 0.01)    
    # print(np.concatenate((bid_prices, ask_prices)))
    # print(np.concatenate((bid_sizes, ask_sizes)))
    
    prices = np.concatenate((np.divide(bid_prices, 10000), np.divide(ask_prices, 10000)))
    sizes = np.concatenate((bid_sizes, ask_sizes))

    container = ax.bar(prices, sizes, 0.01, color=[*['green']*3, *['red']*3])

    artists.append(container)

frames = 1000
step_size = 25
for i in range(0, frames):
    analyzeFrame(i * step_size)

ani = animation.ArtistAnimation(fig=fig, artists=artists, interval=1000)
ani.save('animation.mp4', fps=30)
# plt.show()