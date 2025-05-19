import streamlit as st
import yfinance as yf
from yfinance.exceptions import YFRateLimitError

st.set_page_config(page_title="Analizador de Inversiones", page_icon="📊")

st.title("📈 Analizador de Acciones y Momento de Inversión")
st.markdown("Ingresa un ticker para ver si es **buen momento de invertir** con base en fundamentos.")

ticker = st.text_input("Ticker de la acción (ej. AAPL, BAC, VOO):", value="BAC")

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info  # Este acceso puede lanzar una excepción

        nombre = info.get("longName", "Desconocido")
        pb_ratio = info.get("priceToBook", None)
        book_value = info.get("bookValue", None)
        pe_ratio = info.get("trailingPE", None)
        roe = info.get("returnOnEquity", None)
        sector = info.get("sector", "N/A")
        summary = info.get("longBusinessSummary", "No disponible.")
        price = info.get("currentPrice", None)
        avg_volume = info.get("averageVolume", None)

        # Obtener volumen diario más reciente
        hist = stock.history(period="5d")
        if not hist.empty:
            last_volume = hist['Volume'][-1]
            last_date = hist.index[-1].strftime('%Y-%m-%d')
        else:
            last_volume = None
            last_date = None

        st.subheader(f"📄 Información general de {nombre} ({ticker.upper()})")
        st.write(summary)

        st.markdown("### 🧾 Indicadores Financieros")
        col1, col2 = st.columns(2)
        col1.metric("Precio Actual", f"${price:.2f}" if price else "N/A")
        col2.metric("Book Value", f"${book_value:.2f}" if book_value else "N/A")

        col1.metric("P/B Ratio", f"{pb_ratio:.2f}" if pb_ratio else "N/A")
        col2.metric("P/E Ratio", f"{pe_ratio:.2f}" if pe_ratio else "N/A")

        col1.metric("ROE", f"{roe:.2%}" if roe else "N/A")
        col2.metric("Sector", sector)

        st.markdown("---")
        st.markdown("### 📊 Volumen de negociación")
        if last_volume is not None and last_date is not None:
            st.write(f"**Volumen negociado el día {last_date}:** {last_volume:,} acciones")
        else:
            st.write("No se pudo obtener el volumen diario más reciente.")

        if avg_volume:
            st.write(f"**Volumen promedio diario:** {avg_volume:,} acciones")
        else:
            st.write("No se pudo obtener el volumen promedio diario.")

        st.markdown("---")
        st.markdown("### 💡 Evaluación de Inversión")

        if pb_ratio and pb_ratio < 1:
            st.success("📉 La acción parece **infravalorada** (P/B < 1)")
        elif pb_ratio and 1 <= pb_ratio <= 3:
            st.info("📊 La acción parece **razonablemente valuada**")
        elif pb_ratio and pb_ratio > 3:
            st.warning("📈 La acción podría estar **sobrevalorada** (P/B > 3)")

        if pe_ratio and pe_ratio > 25:
            st.warning("🔴 P/E muy alto: podría estar cara respecto a sus ganancias.")
        elif pe_ratio and pe_ratio < 10:
            st.success("🟢 P/E bajo: potencial valor oculto.")

        if roe and roe > 0.15:
            st.success("💪 Alto ROE: la empresa genera buen rendimiento sobre su capital.")
        elif roe and roe < 0.05:
            st.warning("⚠️ Bajo ROE: poco eficiente con su capital.")

        if pb_ratio and pb_ratio < 1 and roe and roe > 0.15 and pe_ratio and pe_ratio < 15:
            st.success("✅ Evaluación final: **Buen momento para considerar invertir.**")
        else:
            st.info("🔍 Evaluación final: **Analiza más antes de invertir.**")

    except YFRateLimitError:
        st.error("⚠️ Has hecho demasiadas peticiones a Yahoo Finance. Espera unos minutos antes de intentar de nuevo.")
    except Exception as e:
        st.error(f"Ocurrió un error al obtener los datos: {e}")




