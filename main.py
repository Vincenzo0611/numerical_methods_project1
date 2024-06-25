import matplotlib.pyplot as plt
import pandas as pd
from data import *

def EMA(data, day, n):
    alpha = 2 / (n + 1)
    numerator = 0
    denominator = 0
    for i in range(n):
        if day - i >= 0:
            numerator += (1 - alpha) ** i * data[day - i]
            denominator += (1 - alpha) ** i
    ema = numerator / denominator
    return ema

def make_decision(macd, signal, opening):
    capital = 1000
    capital_delay = 1000
    capital_s = 1000
    num_shares = 0
    num_shares_delay = 0
    num_shares_s = 0
    capital_history = [capital]
    capital_history_delay = [capital]
    capital_simple = [capital_s]
    last_capital = 1000
    number_buy = 0
    number_sell = 0
    profit = 0
    buy_dates = []
    sell_dates = []
    profitable_sell_dates = []
    unprofitable_sell_dates = []
    delay = 1

    num_shares_s += capital_s / opening[26 + 1]
    capital_s -= opening[26 + 1] * num_shares_s

    for day in range(26, len(macd) - 1):
        capital_simple.append(capital_s + num_shares_s * opening[day + 1])
        if macd[day] > signal[day] and macd[day - 1] <= signal[day - 1] and capital != 0:
            num_shares += capital / opening[day+1]
            capital -= opening[day+1] * num_shares
            number_buy += 1
            buy_dates.append(day)
            num_shares_delay += capital_delay / opening[day+1]
            capital_delay -= opening[day + 1 - delay] * num_shares_delay
        elif macd[day] < signal[day] and macd[day - 1] >= signal[day - 1] and num_shares != 0:
            capital += opening[day+1] * num_shares
            num_shares = 0
            capital_delay += opening[day + 1 - delay] * num_shares_delay
            num_shares_delay = 0
            number_sell += 1
            if(last_capital < capital):
                profit += 1
                profitable_sell_dates.append(day)
            else:
                unprofitable_sell_dates.append(day)
            last_capital = capital
            sell_dates.append(day)

        capital_history.append(capital + num_shares * opening[day+1])
        capital_history_delay.append(capital_delay + num_shares_delay * opening[day+ 1 - delay])
    print("Liczba transakcji:", number_sell)
    print("Liczba zyskownych transakcji:", profit)
    capital_history.append(capital + num_shares * opening[len(opening) - 1])
    capital_history_delay.append(capital_delay + num_shares_delay * opening[len(opening) - 8])
    capital_simple.append(capital_s + num_shares_s * opening[len(opening) - 1])
    return capital_history, buy_dates, sell_dates, profitable_sell_dates, unprofitable_sell_dates, capital_simple, capital_history_delay

data = get_tesla()
macd = []
signal = []
for i in range(0, 26):
    macd.append(0)
for i in range(26, len(data["Zamkniecie"])):
    macd.append(EMA(data["Zamkniecie"], i, 12) - EMA(data["Zamkniecie"], i, 26))
for i in range(len(macd)):
    signal.append(EMA(macd, i, 9))

capital_history, buy_dates, sell_dates, profitable_sell_dates, unprofitable_sell_dates, simple_capital, capital_delay = make_decision(macd, signal, data["Otwarcie"])

dates = pd.to_datetime(data["Data"])

plt.figure(figsize=(10, 6))
plt.plot(dates[25:], data["Zamkniecie"][25:], linestyle='-', color='green')
plt.title('Wykres notowań analizowanego instrumentu finansowego')
plt.xlabel('Data')
plt.ylabel('Cena Zamkniecie')
plt.grid(True)
plt.tight_layout()

plt.figure(figsize=(18, 8))
plt.plot(dates, macd, label='MACD', color='blue')
plt.plot(dates, signal, label='Signal Line', color='red')

sp = True
kp = True
for i in range(1, len(macd)):
    if macd[i] > signal[i - 1] and macd[i - 1] <= signal[i - 2]:
        plt.plot(dates[i], macd[i], '^', markersize=10, color='green', label='Kupno' if kp else "")
        kp = False
    elif macd[i] < signal[i - 1] and macd[i - 1] >= signal[i - 2]:
        plt.plot(dates[i], macd[i], 'v', markersize=10, color='red', label='Sprzedaż' if sp else "")
        sp = False

plt.title('MACD and Signal Line')
plt.xlabel('Days')
plt.ylabel('MACD Value')
plt.legend()
plt.grid(True)

plt.figure(figsize=(10, 6))
plt.plot(dates[25:], capital_history, label='Capital', color='green')
plt.plot(dates[25:], simple_capital, label='Capital without MACD', color='blue')
plt.title('Zmiana kapitału w czasie')
plt.xlabel('Dzień')
plt.ylabel('Kapitał')
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.scatter([dates[i] for i in buy_dates], [capital_history[i-25] for i in buy_dates], color='yellow', label='Kupno')
plt.scatter([dates[i] for i in profitable_sell_dates], [capital_history[i-25] for i in profitable_sell_dates], color='green', label='Zyskowna sprzedaż')
plt.scatter([dates[i] for i in unprofitable_sell_dates], [capital_history[i-25] for i in unprofitable_sell_dates], color='red', label='Niezyskowna sprzedaż')
plt.legend()

plt.figure(figsize=(10, 6))
plt.plot(dates[25:], capital_delay, label='Capital MACD with 1 days earlier', color='yellow')
plt.title('Zmiana kapitału w czasie')
plt.xlabel('Dzień')
plt.ylabel('Kapitał')
plt.legend()
plt.grid(True)
plt.tight_layout()


plt.show()
