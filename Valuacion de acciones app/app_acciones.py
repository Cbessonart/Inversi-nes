import streamlit as st
import yfinance as yf
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Valuación de Acciones", layout="centered")
st.title("📊 Evaluador de Valuación de Acciones")

# Entrada de usuario
ticker_input = st.text_input("🧾 Ingresa el símbolo de la acción (ej. AAPL, MSFT, TSLA):", value="AAPL")

# Función para obtener los datos de la acción
@st.cache_data  # Asegúrate de tener Streamlit >= 1.18.0, si no, usa @st.cache
def obtener_datos(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info
    except Exception as e:
        st.error(f"No se pudo obtener la información: {e}")
        return None

# Función para evaluar la valuación de la acción
def evaluar_valuacion(info):
    pe = info.get("trailingPE", None)
    pb = info.get("priceToBook", None)
    roe = info.get("returnOnEquity", None)
    debt = info.get("debtToEquity", None)

    evaluaciones = []
    puntaje = 0

    if pe is not None:
        if pe < 15:
            evaluaciones.append("✅ *P/E bajo*: El precio es bajo respecto a las ganancias. Históricamente puede indicar una oportunidad de compra.")
            puntaje += 1
        elif pe < 25:
            evaluaciones.append("🟡 *P/E razonable*: El precio es coherente con sus ganancias.")
        else:
            evaluaciones.append("🔴 *P/E alto*: Podría estar sobrevaluada respecto a sus ganancias actuales.")
            puntaje -= 1
    else:
        evaluaciones.append("⚠️ No se encontró información sobre el P/E ratio.")

    if pb is not None:
        if pb < 1:
            evaluaciones.append("✅ *P/B bajo*: El mercado valora esta acción por debajo de su valor contable. Puede indicar subvaluación.")
            puntaje += 1
        elif pb < 3:
            evaluaciones.append("🟡 *P/B razonable*: Está dentro de rangos normales.")
        else:
            evaluaciones.append("🔴 *P/B alto*: Puede estar sobrevaluada en relación a su valor contable.")
            puntaje -= 1
    else:
        evaluaciones.append("⚠️ No se encontró información sobre el P/B ratio.")

    if roe is not None:
        roe_pct = roe * 100
        if roe_pct > 15:
            evaluaciones.append(f"✅ *ROE alto ({roe_pct:.2f}%)*: La empresa tiene alta rentabilidad sobre su capital.")
            puntaje += 1
        elif roe_pct > 10:
            evaluaciones.append(f"🟡 *ROE razonable ({roe_pct:.2f}%)*: Muestra un rendimiento aceptable.")
        else:
            evaluaciones.append(f"🔴 *ROE bajo ({roe_pct:.2f}%)*: La empresa tiene baja rentabilidad sobre su capital.")
            puntaje -= 1
    else:
        evaluaciones.append("⚠️ No se encontró información sobre el ROE.")

    if debt is not None:
        if debt < 1:
            evaluaciones.append("✅ *Bajo endeudamiento*: Tiene una estructura financiera saludable.")
            puntaje += 1
        elif debt < 2:
            evaluaciones.append("🟡 *Endeudamiento medio*: Podría sostenerse pero requiere seguimiento.")
        else:
            evaluaciones.append("🔴 *Alto endeudamiento*: La empresa depende mucho de deuda, puede ser riesgosa.")
            puntaje -= 1
    else:
        evaluaciones.append("⚠️ No se encontró información sobre deuda/capital.")

    # Evaluación final basada en puntaje
    if puntaje >= 2:
        conclusion = "✅ La acción parece **subvaluada**. Puede representar una oportunidad de inversión."
    elif puntaje <= -2:
        conclusion = "🔴 La acción parece **sobrevaluada**. Hay que tener precaución al invertir."
    else:
        conclusion = "🟡 La acción parece **razonablemente valuada** según los indicadores analizados."

    return evaluaciones, conclusion

# Mostrar resultados si hay un ticker ingresado
if ticker_input:
    datos = obtener_datos(ticker_input)

    if datos:
        st.header(f"📈 Información Financiera: {datos.get('longName', ticker_input)}")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Precio Actual", f"${datos.get('currentPrice', 'N/A')}")
            st.metric("P/E Ratio", datos.get("trailingPE", "N/A"))
            st.metric("P/B Ratio", datos.get("priceToBook", "N/A"))

        with col2:
            roe = datos.get("returnOnEquity", None)
            roe_text = f"{roe*100:.2f}%" if roe is not None else "N/A"
            st.metric("ROE", roe_text)
            st.metric("Deuda/Capital", datos.get("debtToEquity", "N/A"))

        st.subheader("📌 Evaluación de la Valuación")
        evaluacion, conclusion = evaluar_valuacion(datos)

        for punto in evaluacion:
            st.markdown(f"- {punto}")

        st.subheader("📊 Conclusión Final")
        if "subvaluada" in conclusion:
            st.success(conclusion)
        elif "razonablemente" in conclusion:
            st.warning(conclusion)
        else:
            st.error(conclusion)

        st.caption("Fuente: Yahoo Finance a través de yfinance")
    else:
        st.error("No se pudo obtener la información del ticker.")


