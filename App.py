import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="PK Expert Simulator", layout="wide")

st.title("🎓 Професионален Фармакокинетичен Симулатор")
st.markdown("Моделиране на **многократно дозиране** и **терапевтичен прозорец**.")

# --- СТРАНИЧНА ЛЕНТА ---
with st.sidebar:
    st.header("⚙️ Параметри на режима")
    dose = st.slider("Единична доза (mg)", 50, 1000, 500, 50)
    interval = st.slider("Интервал между дозите (h)", 4, 24, 8, 2)
    num_doses = st.slider("Брой дози", 1, 10, 5)
    
    st.divider()
    st.header("🧬 Физиология")
    Vd = st.slider("Обем на разпределение (L)", 5, 100, 25)
    ka = st.slider("Абсорбция (ka) [за перорален прием]", 0.1, 2.0, 0.5, 0.1)
    
    st.divider()
    st.header("⚠️ Терапевтичен прозорец")
    msc = st.number_input("Макс. безопасна конц. (MSC) [mg/L]", value=40.0)
    mec = st.number_input("Мин. ефективна конц. (MEC) [mg/L]", value=10.0)

    st.divider()
    kel_A = st.slider("kel: Пациент А (Здрав)", 0.05, 0.5, 0.2)
    kel_B = st.slider("kel: Пациент Б (Патология)", 0.01, 0.5, 0.05)

# --- ЛОГИКА НА СИМУЛАЦИЯТА ---
t = np.linspace(0, num_doses * interval + 24, 1000)

def calculate_pk(t_array, d, v, k_el, k_a, tau, n):
    c_total = np.zeros_like(t_array)
    for i in range(n):
        t_dose = i * tau
        mask = t_array >= t_dose
        t_rel = t_array[mask] - t_dose
        # Формула за перорална абсорбция (Bateman function)
        c_total[mask] += (d/v) * (k_a / (k_a - k_el)) * (np.exp(-k_el * t_rel) - np.exp(-k_a * t_rel))
    return c_total

conc_A = calculate_pk(t, dose, Vd, kel_A, ka, interval, num_doses)
conc_B = calculate_pk(t, dose, Vd, kel_B, ka, interval, num_doses)

# --- ГРАФИКА ---
fig, ax = plt.subplots(figsize=(12, 6))

# Рисуване на кривите
ax.plot(t, conc_A, label="Пациент А", color="#0083B8", lw=2)
ax.plot(t, conc_B, label="Пациент Б", color="#FF4B4B", lw=2, linestyle="--")

# Терапевтичен прозорец
ax.axhline(msc, color="red", alpha=0.3, linestyle=":", label="Токсична граница (MSC)")
ax.axhline(mec, color="green", alpha=0.3, linestyle=":", label="Ефективна граница (MEC)")
ax.fill_between(t, mec, msc, color="green", alpha=0.05, label="Терапевтичен прозорец")

ax.set_xlabel("Време (часове)")
ax.set_ylabel("Концентрация (mg/L)")
ax.legend(loc='upper right', fontsize='small')
ax.grid(True, alpha=0.3)

st.pyplot(fig)

# --- АНАЛИЗ ---
col1, col2 = st.columns(2)

with col1:
    max_A = np.max(conc_A)
    st.metric("Пик Пациент А", f"{max_A:.2f} mg/L")
    if max_A > msc: st.error("🚨 РИСК ОТ ТОКСИЧНОСТ (А)")
    elif max_A < mec: st.warning("📉 ПОДТЕРАПЕВТИЧНИ НИВА (А)")

with col2:
    max_B = np.max(conc_B)
    st.metric("Пик Пациент Б", f"{max_B:.2f} mg/L")
    if max_B > msc: st.error("🚨 РИСК ОТ ТОКСИЧНОСТ (Б)")
    elif max_B < mec: st.warning("📉 ПОДТЕРАПЕВТИЧНИ НИВА (Б)")
