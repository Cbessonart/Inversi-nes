import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ta

def obtener_datos(ticker):
    stock = yf.Ticker(ticker)
    historial = stock.history(period="6mo", interval="1d")
    info = stock.info
    return historial, info

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

    # Precio y medias móviles
    plt.subplot(3, 1, 1)
    plt.plot(historial["Close"], label="Close")
    plt.plot(historial["SMA_20"], label="SMA 20")
    plt.plot(historial["EMA_20"], label="EMA 20")
    plt.title(f"{ticker} - Precio con SMA/EMA")
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
    plt.plot(historial["MACD_signal"], label="Signal", color='orange')
    plt.title("MACD")
    plt.legend()

    plt.tight_layout()
    plt.show()

def evaluar_valuacion(info):
    pe_ratio = info.get("trailingPE", None)
    peg_ratio = info.get("pegRatio", None)
    roe = info.get("returnOnEquity", None)

    print("\n--- Indicadores Financieros Clave ---")
    print(f"P/E Ratio: {pe_ratio}")
    print(f"PEG Ratio: {peg_ratio}")
    print(f"ROE: {roe}")

    print("\n--- Evaluación Básica ---")
    if pe_ratio and pe_ratio < 15 and peg_ratio and peg_ratio < 1:
        print("📈 La acción parece infravalorada.")
    elif pe_ratio and pe_ratio > 25 and peg_ratio and peg_ratio > 2:
        print("📉 La acción podría estar sobrevalorada.")
    else:
        print("🔍 La valuación parece razonable o requiere más análisis.")

def main():
    ticker = input("Ingresa el ticker de la acción (ej. AAPL, TSLA): ").upper()
    historial, info = obtener_datos(ticker)
    
    if historial.empty:
        print("❌ No se pudieron obtener datos. Verifica el ticker.")
        return

    historial = calcular_indicadores(historial)
    mostrar_graficas(historial, ticker)
    evaluar_valuacion(info)

if __name__ == "__main__":
    main()
