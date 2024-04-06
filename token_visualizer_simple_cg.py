import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

current_epoch = int(datetime.now().timestamp())

def fetch_historical_data(network_id, pool_address, days_back=30):
    # Adjust the URL to include the network_id
    url = f"https://api.geckoterminal.com/api/v2/networks/{network_id}/pools/{pool_address}/ohlcv/{resolution}"
    
    # Calculate the start and end dates for the historical data fetch
    start_date = int((datetime.now() - timedelta(days=days_back)).timestamp())
    end_date = int(datetime.now().timestamp())
    
    # Parameters for daily data over the specified period
    params = {
        'from': start_date,
        'to': end_date,
    }
    
    response = requests.get(url, params=params).json()
    data = response['data']
    
    # Transforming the data into a pandas DataFrame
    ohlcv_list = response['data']['attributes']['ohlcv_list']
    df = pd.DataFrame(ohlcv_list, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')


    return df

# Network and Pool addresses for two tokens
network_id = 'base'
pool_address_tokenA = '0x87cadde19468283af8d610474ecbd19ed285f698' # $higher
tokenAlabel = 'HIGHER'
pool_address_tokenB = '0xc9034c3e7f58003e6ae0c8438e7c8f4598d5acaa' # $degen
tokenBlabel = 'DEGEN'

resolution = 'day' #hour or day

df_tokenA = fetch_historical_data(network_id, pool_address_tokenA)
df_tokenB = fetch_historical_data(network_id, pool_address_tokenB)



# Relative graph
# Merge the dataframes on the 'timestamp' column
df = pd.merge(df_tokenA, df_tokenB, on='timestamp', how='outer', suffixes=('_tokenA', '_tokenB'))

# Calculate the relative price of TokenA vs TokenB
df['relative_price'] = df['close_tokenA'] / df['close_tokenB']

# Create a figure with 2 subplots
fig, axs = plt.subplots(2, figsize=(8, 8))

# --- CHART 1 ---
# Plot the relative price in the first subplot
axs[0].plot(df['timestamp'], df['relative_price'], label=f'{tokenAlabel}/{tokenBlabel}')
axs[0].plot(df['timestamp'], 1/df['relative_price'], label=f'{tokenBlabel}/{tokenAlabel}', color='grey')
axs[0].set_xlabel('Date')
axs[0].set_ylabel('Relative Price')
axs[0].set_title(f'Historical Relative Price: {tokenAlabel} vs {tokenBlabel}')
axs[0].legend()

# Add current relative price value to the first subplot
current_relative_price = round(df['relative_price'].iloc[-1], 2)
current_relative_price_ba = round(1/df['relative_price'].iloc[-1], 2)
axs[0].text(df['timestamp'].iloc[-1], current_relative_price, f'Current Relative Price: {current_relative_price}', ha='right', va='bottom')
axs[0].text(df['timestamp'].iloc[-1], current_relative_price_ba, f'Current Relative Price: {current_relative_price_ba}', ha='right', va='top', color='grey')

# --- CHART 2 ---
# Plot the closing prices in the second subplot
axs[1].plot(df_tokenA['timestamp'], df_tokenA['close'], label=tokenAlabel, color='green')
axs[1].plot(df_tokenB['timestamp'], df_tokenB['close'], label=tokenBlabel, color='purple')
axs[1].set_xlabel('Date')
axs[1].set_ylabel('Closing Price')
axs[1].set_title(f'Historical Closing Prices: {tokenAlabel} vs {tokenBlabel}')
axs[1].legend()

# Add current token prices to the second subplot
current_price_tokenA = df_tokenA['close'].iloc[0]
current_price_tokenB = df_tokenB['close'].iloc[0]
axs[1].text(df_tokenA['timestamp'].iloc[0], current_price_tokenA, f'Current Price {tokenAlabel}: {current_price_tokenA:.4f}', ha='right', va='bottom')
axs[1].text(df_tokenB['timestamp'].iloc[0], current_price_tokenB, f'Current Price {tokenBlabel}: {current_price_tokenB:.4f}', ha='right', va='bottom')

# Display the figure
plt.tight_layout()
plt.show()