import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. ЗАГЛАВИЕ И ОПИСАНИЕ ---
st.title("Фармакокинетична Симулация")
st.markdown("""
Тази интерактивна графика демонстрира промяната в плазмената концентрация 
след **IV болус** приложение в еднокомпартментен модел.
""")

# --- 2. СТРАНИЧНА ЛЕНТА С ПЛЪЗГАЧИ (INPUT) ---
st.sidebar.header("Параметри")

dose = st.sidebar.slider("Доза (mg)", min_value=100, max_value=5000, value=1000, step=100)
Vd = st.sidebar.slider("Обем на разпределение (L)", min_value=5, max_value=100, value=20, step=1)
kel = st.sidebar.slider("Константа на елиминиране (kel)", min_value=0.01, max_value=1.0, value=0.2, step=0.01)

# --- 3. ИЗЧИСЛЕНИЯ (ENGINE) ---
# Генерираме времето: от 0 до 24 часа, 150 точки за гладка крива
t = np.linspace(0, 24, 150)

# Формулата за IV болус
Ct = (dose / Vd) * np.exp(-kel * t)

# Изчисляваме и полуживота за информация
t_half = 0.693 / kel

# --- 4. ВИЗУАЛИЗАЦИЯ (PLOT) ---
st.subheader("Графика на концентрация-време")

# Създаваме фигурата
fig, ax = plt.subplots(figsize=(10, 6))

# Основната линия
ax.plot(t, Ct, color='#0083B8', linewidth=3, label='Концентрация')

# Защриховане под кривата (AUC)
ax.fill_between(t, Ct, color='#0083B8', alpha=0.1)

# Стилове
ax.set_xlabel("Време (часове)", fontsize=12)
ax.set_ylabel("Концентрация (mg/L)", fontsize=12)
ax.set_title(f"IV Болус (t½ = {t_half:.2f} ч.)", fontsize=14)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend()

# Премахваме горната и дясната рамка за по-чист вид
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Показваме в Streamlit
st.pyplot(fig)

# --- 5. ДОПЪЛНИТЕЛНИ ДАННИ ---
st.info(f"При тези параметри, началната концентрация (C0) е **{dose/Vd:.2f} mg/L**.")
