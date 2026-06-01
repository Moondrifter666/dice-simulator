import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import time

# =========================
# Page Configuration
# =========================
st.set_page_config(page_title="Dice Sum Simulator", layout="centered")

st.title("🎲 Dice Sum Simulator")
st.markdown("""
Choose the number of dice to roll, then watch the simulated throws create a histogram in real time. 
You will notice that even though each die is completely random, their **sum** inevitably forms a perfect bell curve!
""")

# =========================
# Initialize Session State
# =========================
if "dice_count" not in st.session_state:
    st.session_state.dice_count = 5
if "history" not in st.session_state:
    st.session_state.history = []
if "current_roll" not in st.session_state:
    st.session_state.current_roll = []
if "is_simulating" not in st.session_state:
    st.session_state.is_simulating = False

# =========================
# Interactive Controls
# =========================
new_dice_count = st.slider("Number of dice:", min_value=1, max_value=10, value=st.session_state.dice_count)
if new_dice_count != st.session_state.dice_count:
    st.session_state.dice_count = new_dice_count
    st.session_state.history = []
    st.session_state.current_roll = []
    st.session_state.is_simulating = False

# 第一排按钮
col1, col2, col3 = st.columns(3)
btn_simulate = col1.button("Continuous Auto" if not st.session_state.is_simulating else "Stop Auto")
btn_roll_1 = col2.button("Roll once")
btn_roll_100 = col3.button("Roll 100 times")

# 第二排按钮 (新增的动画按钮)
col4, col5, col6 = st.columns(3)
btn_auto_1x100 = col4.button("Auto: 1 roll × 100")
btn_auto_100x20 = col5.button("Auto: 100 rolls × 20")
btn_reset = col6.button("Reset")

# =========================
# 核心：创建一个全局占位符
# =========================
# 这个占位符允许我们只在这个区域内更新画面，而不刷新整个网页
main_display = st.empty()

def render_visuals():
    """将所有骰子和图表的绘制逻辑封装成一个函数，直接在占位符中更新"""
    n = st.session_state.dice_count
    with main_display.container():
        # 1. 渲染骰子
        st.markdown("<br>", unsafe_allow_html=True)
        dice_faces = {1: '⚀', 2: '⚁', 3: '⚂', 4: '⚃', 5: '⚄', 6: '⚅'}
        
        if len(st.session_state.current_roll) > 0:
            faces_str = " ".join([dice_faces[val] for val in st.session_state.current_roll])
            total_sum = sum(st.session_state.current_roll)
            st.markdown(
                f"<div style='font-size: 80px; display: flex; align-items: center;'>"
                f"<span style='color: #333;'>{faces_str}</span> "
                f"<span style='font-size: 50px; margin-left: 20px;'> = <b>{total_sum}</b></span>"
                f"</div>", 
                unsafe_allow_html=True
            )
        else:
            st.markdown("<div style='font-size: 80px; color: #ccc;'>🎲 Waiting to roll...</div>", unsafe_allow_html=True)

        # 2. 渲染图表
        st.markdown("<hr>", unsafe_allow_html=True)
        st.write(f"**TRACKED ROLLS: {len(st.session_state.history)}**")

        if len(st.session_state.history) > 0:
            fig, ax = plt.subplots(figsize=(10, 4))
            min_val = n
            max_val = n * 6
            bins = np.arange(min_val - 0.5, max_val + 1.5, 1)
            ax.hist(st.session_state.history, bins=bins, density=True, color='#1ABC9C', edgecolor='white')
            
            mu = n * 3.5
            sigma = np.sqrt(n * (35 / 12))
            x = np.linspace(min_val, max_val, 200)
            y = norm.pdf(x, mu, sigma)
            ax.plot(x, y, color='black', linewidth=2)
            
            ax.set_xlim(min_val - 1, max_val + 1)
            ax.set_xticks(range(min_val, max_val + 1, max(1, n//2)))
            ax.set_yticks([]) 
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            
            st.pyplot(fig)
            plt.close(fig) # 关键：防止连续画图导致内存溢出

# =========================
# 按钮行为逻辑
# =========================
n = st.session_state.dice_count

if btn_reset:
    st.session_state.history = []
    st.session_state.current_roll = []
    st.session_state.is_simulating = False
    render_visuals()

elif btn_roll_1:
    st.session_state.is_simulating = False
    roll = np.random.randint(1, 7, n)
    st.session_state.current_roll = roll
    st.session_state.history.append(np.sum(roll))
    render_visuals()

elif btn_roll_100:
    st.session_state.is_simulating = False
    rolls = np.random.randint(1, 7, size=(100, n))
    st.session_state.current_roll = rolls[-1]
    st.session_state.history.extend(np.sum(rolls, axis=1).tolist())
    render_visuals()

# --- 核心动画逻辑：使用局部刷新 ---

elif btn_auto_1x100:
    st.session_state.is_simulating = False
    for _ in range(100):
        roll = np.random.randint(1, 7, n)
        st.session_state.current_roll = roll
        st.session_state.history.append(np.sum(roll))
        render_visuals()  # 仅重新绘制图表区域
        time.sleep(0.05)  # 动画间隔

elif btn_auto_100x20:
    st.session_state.is_simulating = False
    for _ in range(20):
        rolls = np.random.randint(1, 7, size=(100, n))
        st.session_state.current_roll = rolls[-1]
        st.session_state.history.extend(np.sum(rolls, axis=1).tolist())
        render_visuals()  # 仅重新绘制图表区域
        time.sleep(0.1)   # 数据增加多，稍微停顿长一点让你看清变化

elif btn_simulate:
    st.session_state.is_simulating = not st.session_state.is_simulating
    if not st.session_state.is_simulating:
        render_visuals()

# 连续不断播放的逻辑 (需要用 rerun)
if st.session_state.is_simulating:
    rolls = np.random.randint(1, 7, size=(10, n))
    st.session_state.current_roll = rolls[-1]
    st.session_state.history.extend(np.sum(rolls, axis=1).tolist())
    render_visuals()
    time.sleep(0.1)
    st.rerun()

# 如果没有按任何按钮，就静态展示当前画面
if not any([btn_roll_1, btn_roll_100, btn_auto_1x100, btn_auto_100x20, btn_reset]) and not st.session_state.is_simulating:
    render_visuals()
