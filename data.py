import pandas as pd

def get_apple():
    apple = pd.read_csv('aapl_us_d.csv')
    return apple

def get_tesla():
    tesla = pd.read_csv('tsla_us_d.csv')
    return tesla

def get_eth_big():
    eth = pd.read_csv('eth_v_d.csv')
    return eth

def get_eth_small():
    eth = pd.read_csv('eth_v_d2.csv')
    return eth