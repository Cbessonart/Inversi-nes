import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from scipy.optimize import minimize
import io

st.set_page_config(layout="wide", page_title="Frontera Eficiente Pro")
st.title("📈 Frontera Eficiente - Análisis Avanzado de Portafolios")

# Inputs del usuario
tickers_input = st.text_input("Ingrese tickers separados por coma (ej: AAPL, MSFT, GOOG):", "AAPL, MSFT, GOOG")
start_date = st.date_input("Fecha de inicio", datetime.today() - timedelta(days=3*365))
end_date = st.date_input("Fecha de fin", datetime.today())
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

# Validar tickers
def validate_tickers(tickers):
    valid = []
    for t in tickers:
        try:
            data = yf.download(t, period="1y", progress=False)
            if not data.empty:
                valid.append(t)
        except:
            continue
    return valid

valid_tickers = validate_tickers(tickers)
if not valid_tickers:
    st.error("❌ No se encontraron tickers válidos. Verifica los símbolos ingresados.")
    st.stop()

# Cargar precios ajustados
@st.cache_data
def load_data(tickers, start, end):
    raw = yf.download(tickers, start=start, end=end, group_by='ticker', auto_adjust=True, progress=False)
    return pd.DataFrame({t: raw[t]["Close"] for t in tickers if t in raw}).dropna()

df = load_data(valid_tickers, start_date, end_date)
st.subheader("📊 Precios ajustados (promedios móviles 30 días)")
ma = df.rolling(window=30).mean()
st.line_chart(ma)

# Calcular retornos
returns = df.pct_change().dropna()
mean_returns = returns.mean() * 252
cov_matrix = returns.cov() * 252

# Métricas individuales
stats = pd.DataFrame({
    "Rendimiento (%)": mean_returns * 100,
    "Desviación Std (%)": returns.std() * np.sqrt(252) * 100
})
st.subheader("📈 Métricas por activo")
st.dataframe(stats.style.format({"Rendimiento (%)": "{:.2f}", "Desviación Std (%)": "{:.2f}"}))

# Tabla de correlación
st.subheader("📘 Matriz de correlación")
st.dataframe(returns.corr())

# Optimización
def portfolio_performance(weights, mean_returns, cov_matrix):
    ret = np.dot(weights, mean_returns)
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    sharpe = ret / std
    return std, ret, sharpe

def negative_sharpe(weights, mean_returns, cov_matrix):
    return -portfolio_performance(weights, mean_returns, cov_matrix)[2]

def check_sum(weights):
    return np.sum(weights) - 1

# NUEVOS LÍMITES: 5% mínimo, 20% máximo por activo
bounds = tuple((0.05, 0.20) for _ in range(len(valid_tickers)))
constraints = {'type': 'eq', 'fun': check_sum}
initial_weights = np.array([1/len(valid_tickers)] * len(valid_tickers))

optimized = minimize(negative_sharpe, initial_weights,
                     args=(mean_returns, cov_matrix),
                     method='SLSQP', bounds=bounds,
                     constraints=constraints)

opt_weights = optimized.x
opt_std, opt_ret, opt_sharpe = portfolio_performance(opt_weights, mean_returns, cov_matrix)

if np.isnan(opt_ret) or np.isnan(opt_std):
    st.error("❌ Error en el cálculo de los retornos y/o desviación estándar del portafolio. Verifica los datos de entrada.")
    st.stop()

# Asset Allocation
st.subheader("📉 Asset Allocation (límites 5%–20%)")
alloc_df = pd.DataFrame({'Ticker': valid_tickers, 'Peso (%)': opt_weights * 100})
fig1, ax1 = plt.subplots()
ax1.pie(opt_weights, labels=valid_tickers, autopct='%1.1f%%')
ax1.axis('equal')
st.pyplot(fig1)
st.dataframe(alloc_df.style.format({"Peso (%)": "{:.2f}"}))

# Wilshire 5000
wilshire = yf.download("^W5000", start=start_date, end=end_date, auto_adjust=True)["Close"].pct_change().dropna()
wilshire_ret = wilshire.mean() * 252
wilshire_std = wilshire.std() * np.sqrt(252)
wilshire_sharpe = wilshire_ret / wilshire_std

st.subheader("📊 Comparativa con Wilshire 5000")
st.write(f"📌 Portafolio - Rendimiento: {float(opt_ret):.2%}, Volatilidad: {float(opt_std):.2%}, Sharpe: {float(opt_sharpe):.2f}")
st.write(f"📌 Wilshire 5000 - Rendimiento: {float(wilshire_ret):.2%}, Volatilidad: {float(wilshire_std):.2%}, Sharpe: {float(wilshire_sharpe):.2f}")

# Frontera eficiente
st.subheader("📐 Frontera Eficiente")
num_ports = 20000
all_weights = []
ret_arr = []
vol_arr = []
sharpe_arr = []

for _ in range(num_ports):
    weights = np.random.dirichlet(np.ones(len(valid_tickers)), size=1)[0]
    port_ret = np.dot(weights, mean_returns)
    port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    sharpe = port_ret / port_vol
    ret_arr.append(port_ret)
    vol_arr.append(port_vol)
    sharpe_arr.append(sharpe)

frontier_df = pd.DataFrame({
    'Rendimiento': ret_arr,
    'Volatilidad': vol_arr,
    'Sharpe': sharpe_arr
})

fig2, ax2 = plt.subplots()
scatter = ax2.scatter(frontier_df['Volatilidad'], frontier_df['Rendimiento'], c=frontier_df['Sharpe'], cmap='viridis', alpha=0.5)
ax2.scatter(opt_std, opt_ret, color='red', marker='*', s=200, label='Portafolio Óptimo')
ax2.set_xlabel('Volatilidad (Desviación Estándar)')
ax2.set_ylabel('Rendimiento Esperado')
ax2.set_title('Frontera Eficiente')
ax2.legend()
fig2.colorbar(scatter, label='Sharpe Ratio')
st.pyplot(fig2)

# Exportar gráfica como PNG
buf = io.BytesIO()
fig2.savefig(buf, format='png')
st.download_button("📥 Descargar Frontera (PNG)", data=buf.getvalue(), file_name="frontera_eficiente.png", mime="image/png")

# Exportar datos CSV
csv_data = frontier_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Descargar datos (CSV)", data=csv_data, file_name='frontera_eficiente.csv', mime='text/csv')

# Proyecciones
st.subheader("📉 Proyecciones a 7–10 años (Regresión Lineal)")
future_years = [7, 8, 9, 10]
X = np.arange(len(df)).reshape(-1, 1)
reg_df = pd.DataFrame()

for ticker in valid_tickers:
    model = LinearRegression().fit(X, df[ticker].values.reshape(-1, 1))
    predictions = [model.predict([[len(df) + 252 * y]])[0][0] for y in future_years]
    reg_df[ticker] = predictions

reg_df.index = [f"{y} años" for y in future_years]
st.dataframe(reg_df.style.format("{:.2f}"))

# Escenarios
st.subheader("🔮 Escenarios del portafolio")
scenario_df = pd.DataFrame({
    "Escenario": ["Optimista", "Regular", "Pesimista"],
    "Rendimiento Estimado (%)": [opt_ret*1.25*100, opt_ret*100, opt_ret*0.75*100],
    "Desviación Std (%)": [opt_std*0.9*100, opt_std*100, opt_std*1.2*100]
})
st.dataframe(scenario_df.style.format({"Rendimiento Estimado (%)": "{:.2f}", "Desviación Std (%)": "{:.2f}"}))