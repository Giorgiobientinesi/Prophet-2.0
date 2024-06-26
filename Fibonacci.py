import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import yfinance as yf
from datetime import date,datetime, timedelta, timezone
import numpy as np
import streamlit as st

today_date = date.today()
tickers = pd.read_csv("All-stocks.csv")
tickers = tickers["Symbol"]


def cluster_numbers(numbers, percentage_threshold=0.03):
    clusters = []

    # Sort numbers for easier clustering
    sorted_numbers = sorted(numbers)

    i = 0
    while i < len(sorted_numbers):
        current_number = sorted_numbers[i]
        lower_bound = current_number * (1 - percentage_threshold)
        upper_bound = current_number * (1 + percentage_threshold)
        cluster = [current_number]

        # Check subsequent numbers if they belong to this cluster
        j = i + 1
        while j < len(sorted_numbers):
            if lower_bound <= sorted_numbers[j] <= upper_bound:
                cluster.append(sorted_numbers[j])
                j += 1
            else:
                break

        # Move i to the end of this cluster
        i = j
        clusters.append(cluster)

    return clusters



st.write("Scraper")
genera = st.button("Genera file azioni!")
contatore = 0
if genera:

    in_fibonacci = []
    in_virus = []


    today_date = datetime.today().date()
    for ticker in tickers:
        contatore +=1
        st.write("Ne mancano " + str(len(tickers) - contatore) + " da analizzare")
        data = yf.Ticker(ticker)

        df = pd.DataFrame(data.history(start="2023-01-01", end=today_date, interval="1d"))

        if len(df) > 0:
            df = df.reset_index()
            df["Date"] = df["Date"].dt.tz_localize(None)
            df_test = df

            # FIBONACCI

            i = 15  # minimo locale definito come il minimo dei 30 giorni intorno
            minimi_locali = []
            while i < len(df_test) - 15:
                primo = df_test[i - 15:i + 15]

                if i == primo['Low'].idxmin():
                    minimi_locali.append(i)
                i += 1
            if len(minimi_locali) > 0:
                latest_min_index = minimi_locali[-1]
                latest_max_index = df_test['High'][latest_min_index:].idxmax()

                fibo_38 = df_test["High"][latest_max_index] - (
                            df_test['High'][latest_max_index] - df_test['Low'][latest_min_index]) * 0.38
                fibo_50 = df_test["High"][latest_max_index] - (
                            df_test['High'][latest_max_index] - df_test['Low'][latest_min_index]) * 0.5

                minimum_after = min(df_test["Low"][latest_max_index:])  # trova il minimo dopo il massimo del ritracciamento

                # Questo serve a capire se tra il minimo e il massimo è gia stato in fibonacci

                if (latest_max_index - latest_min_index) > 13:  # I giorni tra il minimo e il massimo sono almeno 13
                    check_prima = df_test.iloc[latest_min_index:latest_max_index + 1]  # isola il segmento
                    tocca_fibo38 = check_prima[check_prima["High"] > fibo_38]["Date"].iloc[
                        0]  # la prima volta che tocca fibo 38
                    check_prima_dopoiltocco = check_prima[
                        check_prima["Date"] > tocca_fibo38]  # isola solo dopo il tocco di fibo 38
                    result = (check_prima_dopoiltocco[
                                  'Low'] < fibo_50).any()  # Se tra il minimo e il massimo già era entrato in fibonacci

                    if result == False:  # Se tra il minimo e il massimo non già era entrato in fibonacci

                        if minimum_after >= fibo_50:  # non è mai sceso sotto fibonacci

                            check_primavolta = []

                            if 1.005 * df_test["Close"].iloc[-1] >= fibo_38 >= 0.995 * df_test["Close"].iloc[-1] or 1.005 * \
                                    df_test["Close"].iloc[-1] >= fibo_50 >= 0.995 * df_test["Close"].iloc[-1] or fibo_38 >= \
                                    df_test["Close"].iloc[-1] >= fibo_50:  # se attualmente rispetta Fibonacci

                                k = latest_max_index  # Questo serve a vedere se dopo fibonacci ci è entrato e uscito

                                while k != df_test.index[-1]:
                                    data = k
                                    if k in df_test.index:
                                        prezzo = df_test["Low"][k]  # aggiungi tutti i minimi dopo il massimo

                                        if fibo_38 >= prezzo >= fibo_50:
                                            check_primavolta.append([data, prezzo])

                                    k += 1

                                if len(check_primavolta) > 0:
                                    if (check_primavolta[-1][0] - check_primavolta[0][0]) <= len(check_primavolta) + 1:
                                        in_fibonacci.append([ticker, df_test["Date"].iloc[latest_min_index],
                                                             df_test["Date"].iloc[latest_max_index]])

                                else:
                                    in_fibonacci.append([ticker, df_test["Date"].iloc[latest_min_index],
                                                         df_test["Date"].iloc[latest_max_index]])

            i = 10  # minimo locale definito come il minimo dei 30 giorni intorno
            minimi_locali = []
            while i < len(df) - 10:
                primo = df[i - 10:i + 10]

                if i == primo['Low'].idxmin():
                    minimi_locali.append(i)
                i += 1

            prezzi = []
            date = []

            for el in minimi_locali:
                prezzi.append(df.iloc[el]["Low"])
                date.append(df.iloc[el]["Date"])

            clusters = cluster_numbers(prezzi, percentage_threshold=0.03)
            resistenze = []
            for el in clusters:
                if len(el) > 2:
                    resistenze.append(min(el))

            oggi = df["Close"].iloc[-1]

            for resistenza in resistenze:
                if resistenza * 1.02 > oggi > resistenza and df["Close"].iloc[-5] > oggi:
                    if ticker not in in_virus:
                        in_virus.append([ticker, resistenza])


    in_fibo = pd.DataFrame(in_fibonacci)
    in_virus = pd.DataFrame(in_virus)

    st.title("Fibonacci")
    st.dataframe(in_fibo)

    st.title("Virus")
    st.dataframe(in_virus)



















