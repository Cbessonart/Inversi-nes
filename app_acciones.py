import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ta
import time

def obtener_datos(ticker, intentos=3, espera=5):
    for i in range(intentos):
        try:
            print(f"Intento {i+1} para obtener datos de {ticker}...")
            stock = yf.Ticker(ticker)
            historial = stock.history(period="6mo", interval="1d")
            info = stock.info
            if not historial.empty and info:
                return historial, info
        except Exception as e:
            print(f"Error en intento {i+1}: {e}")
        print("Esperando para reintentar...")
        time.sleep(espera)
    raise Exception("❌ No se pudo obtener la información del ticker luego de varios intentos.")

def calcular_indicadores(historial):
    historial["SMA_20"] = historial["Close"].rolling(window=20).mean()
    historial["EMA_20"] = historial["Close"].ewm(span=20, adjust=False).mean()

    rsi = ta.momentum.RSIIndicator(historial["Close"], window=14)
    historial["RSI"] = rsi.rsi()

    macd = ta.trend.MACD(historial["Close"])
    historial["MACD"] = macd.macd()
    historial["MACD_signal"] = macd.macd_signal()

    return historial

def mostrar_graficas(historial, ticker):
    plt.figure(figsize=(14, 8))

    # Precio + Medias móviles
    plt.subplot(3, 1, 1)
    plt.plot(historial["Close"], label="Cierre", color="black")
    plt.plot(historial["SMA_20"], label="SMA 20", color="blue")
    plt.plot(historial["EMA_20"], label="EMA 20", color="green")
    plt.title(f"{ticker} - Precio con Medias Móviles")
    plt.legend()

    # RSI
    plt.subplot(3, 1, 2)
    plt.plot(historial["RSI"], label="RSI", color='purple')
    plt.axhline(70, color='red', linestyle='--')
    plt.axhline(30, color='green', linestyle='--')
    plt.title("RSI")
    plt.legend()

    # MACD
    plt.subplot(3, 1, 3)
    plt.plot(historial["MACD"], label="MACD", color='blue')
    plt.plot(historial["MACD_signal"], label="Señal", color='orange')
    plt.title("MACD")
    plt.legend()

    plt.tight_layout()
    plt.show()

def evaluar_valuacion(info):
    pe_ratio = info.get("trailingPE")
    peg_ratio = info.get("pegRatio")
    roe = info.get("returnOnEquity")

    print("\n📊 Indicadores Financieros:")
    print(f"P/E Ratio: {pe_ratio}")
    print(f"PEG Ratio: {peg_ratio}")
    print(f"ROE: {roe}")

    print("\n📌 Evaluación de valuación:")
    if pe_ratio and peg_ratio:
        if pe_ratio < 15 and peg_ratio < 1:
            print("✅ La acción parece infravalorada.")
        elif pe_ratio > 25 and peg_ratio > 2:
            print("⚠️ La acción podría estar sobrevalorada.")
        else:
            print("🧐 La valuación parece razonable o requiere más análisis.")
    else:
        print("❓ No hay suficiente información para evaluar la valuación.")

def main():
    ticker = input("🔎 Ingresa el ticker de la acción (ej. AAPL, BAC, TSLA): ").upper()
    try:
        historial, info = obtener_datos(ticker)
        historial = calcular_indicadores(historial)
        mostrar_graficas(historial, ticker)
        evaluar_valuacion(info)
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    main()
