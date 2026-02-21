import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Настройка на страницата
st.set_page_config(page_title="PK Expert Simulator", layout="wide")

st.title("🎓 Фармакокинетичен Симулатор")
st.markdown("Интерактивен модел за обучение по клинична фармакология.")

# --- СТРАНИЧНА ЛЕНТА: ИЗБОР НА МОДЕЛ (PRESETS) ---
with st.sidebar:
    st.header("📋 Избор на лекарство")
    drug_type = st.selectbox(
        "Изберете сценарий:",
        ["Стандартно лекарство", "Дигоксин (Тесен индекс)", "Фенобарбитал (Дълъг t½)", "Алкохол (0-ред елиминиране)"]
    )
    
    st.divider()
    st.header("⚙️ Параметри на режима")
    
    # Настройки по подразбиране спрямо избраното лекарство
    if drug_type == "Дигоксин (Тесен индекс)":
        def_dose, def_msc, def_mec, def_kel, def_vd = 0.25, 2.0, 0.8, 0.02, 500
    elif drug_type == "Фенобарбитал (Дълъг t½)":
        def_dose, def_msc, def_mec, def_kel, def_vd = 100.0, 40.0, 15.0, 0.007, 40
    elif drug_type == "Алкохол (0-ред елиминиране)":
        def_dose, def_msc, def_mec, def_kel, def_vd = 20000.0, 500.0, 200.0, 0.1, 40
    else:
        def_dose, def_msc, def_mec, def_kel, def_vd = 500.0, 40.0, 10.0, 0.2, 25

    dose = st.slider("Единична доза (mg)", 0.1, 30000.0, float(def_dose))
    interval = st.slider("Интервал между дозите (h)", 2, 48, 12)
    num_doses = st.slider("Брой дози", 1, 15, 5)
    
    st.divider()
    Vd = st.slider("Обем на разпределение (Vd) [L]", 5, 600, int(def_vd))
    ka = st.slider("Скорост на абсорбция (ka)", 0.1, 2.0, 0.5)
    
    st.divider()
    st.header("🧬 Индивидуални параметри (kel)")
    kel_A = st.slider("Пациент А (Норма)", 0.001, 1.0, float(def_kel), format="%.3f")
    kel_B = st.slider("Пациент Б (Патология)", 0.001, 1.0, float(def_kel/2), format="%.3f")

    msc = def_msc
    mec = def_mec

# --- ЛОГИКА НА ИЗЧИСЛЕНИЯТА ---
t = np.linspace(0, max(num_doses * interval + 24, 72), 1000)

def calculate_pk(t_array, d, v, k_el, k_a, tau, n, drug_mode):
    c_total = np.zeros_like(t_array)
    is_alcohol = (drug_mode == "Алкохол (0-ред елиминиране)")
    
    for i in range(n):
        t_dose = i * tau
        mask = t_array >= t_dose
        t_rel = t_array[mask] - t_dose
        
        if is_alcohol:
            # Модел на нулев ред (линейно изчистване)
            c0 = d / v
            v_max = 150 # mg/L на час (средно за алкохол)
            c_calc = c0 - (v_max * t_rel)
            c_calc[c_calc < 0] = 0
            c_total[mask] += c_calc
        else:
            # Модел на първи ред (експоненциално изчистване)
            # Използваме формула за перорален прием (Bateman)
            c_total[mask] += (d/v) * (k_a / (k_a - k_el)) * (np.exp(-k_el * t_rel) - np.exp(-k_a * t_rel))
    return c_total

conc_A = calculate_pk(t, dose, Vd, kel_A, ka, interval, num_doses, drug_type)
conc_B = calculate_pk(t, dose, Vd, kel_B, ka, interval, num_doses, drug_type)

# --- ГРАФИКА ---
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(t, conc_A, label="Пациент А", color="#0083B8", lw=2.5)
ax.plot(t, conc_B, label="Пациент Б", color="#FF4B4B", lw=2.5, linestyle="--")

# Терапевтичен прозорец
ax.axhline(msc, color="red", alpha=0.3, linestyle=":", label="Токсична граница (MSC)")
ax.axhline(mec, color="green", alpha=0.3, linestyle=":", label="Мин. ефективна (MEC)")
ax.fill_between(t, mec, msc, color="green", alpha=0.05)

ax.set_xlabel("Време (часове)")
ax.set_ylabel("Концентрация (mg/L)")
ax.legend(loc='upper right')
ax.grid(True, alpha=0.2)
st.pyplot(fig)

# --- АНАЛИЗ И ИНТЕРПРЕТАЦИЯ ---
st.subheader("📝 Клиничен анализ")
if drug_type == "Алкохол (0-ред елиминиране)":
    st.info("**Обяснение:** Алкохолът показва кинетика от **нулев ред**. Ензимите са наситени и тялото чисти фиксирано количество за час, независимо от концентрацията. Графиката е линейна.")
else:
    col1, col2 = st.columns(2)
    with col1:
        if np.max(conc_A) > msc: st.error("⚠️ Пациент А: Риск от токсичност!")
        elif np.max(conc_A) < mec: st.warning("📉 Пациент А: Подтерапевтични нива.")
        else: st.success("✅ Пациент А: В прозореца.")
    with col2:
        if np.max(conc_B) > msc: st.error("⚠️ Пациент Б: Критичен риск от токсичност!")
        elif np.max(conc_B) < mec: st.warning("📉 Пациент Б: Ниска ефикасност.")
        else: st.success("✅ Пациент Б: В прозореца.")

# --- ЕКСПОРТ ---
st.divider()
export_df = pd.DataFrame({"Време (h)": t, "Пациент А (mg/L)": conc_A, "Пациент Б (mg/L)": conc_B})
csv = export_df.to_csv(index=False).encode('utf-8-sig')
st.download_button("📥 Свали данните за упражнение (CSV)", data=csv, file_name='pk_data.csv', mime='text/csv')
