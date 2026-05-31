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
# Listen to slider changes: if the number of dice changes, clear the history
new_dice_count = st.slider("Number of dice:", min_value=1, max_value=10, value=st.session_state.dice_count)
if new_dice_count != st.session_state.dice_count:
    st.session_state.dice_count = new_dice_count
    st.session_state.history = []
    st.session_state.current_roll = []
    st.session_state.is_simulating = False

# Button layout
col1, col2, col3, col4 = st.columns(4)

btn_simulate = col1.button("Simulate" if not st.session_state.is_simulating else "Stop")
btn_roll_1 = col2.button("Roll once")
btn_roll_100 = col3.button("Roll 100 times")
btn_reset = col4.button("Reset")

# =========================
# Logic Processing
# =========================
n = st.session_state.dice_count

if btn_reset:
    st.session_state.history = []
    st.session_state.current_roll = []
    st.session_state.is_simulating = False

if btn_roll_1:
    st.session_state.is_simulating = False
    roll = np.random.randint(1, 7, n)
    st.session_state.current_roll = roll
    st.session_state.history.append(np.sum(roll))

if btn_roll_100:
    st.session_state.is_simulating = False
    rolls = np.random.randint(1, 7, size=(100, n))
    st.session_state.current_roll = rolls[-1]  # Display the last roll on the UI
    st.session_state.history.extend(np.sum(rolls, axis=1).tolist())

if btn_simulate:
    # Toggle simulation state
    st.session_state.is_simulating = not st.session_state.is_simulating

# If simulating, add 20 rolls per refresh
if st.session_state.is_simulating:
    rolls = np.random.randint(1, 7, size=(20, n))
    st.session_state.current_roll = rolls[-1]
    st.session_state.history.extend(np.sum(rolls, axis=1).tolist())
    time.sleep(0.05)  # Control animation speed
    st.rerun()        # Rerun script to create animation

# =========================
# UI Rendering: Dice Faces
# =========================
st.markdown("<br>", unsafe_allow_html=True)

# Use Unicode characters to draw realistic dice
dice_faces = {1: '⚀', 2: '⚁', 3: '⚂', 4: '⚃', 5: '⚄', 6: '⚅'}

if len(st.session_state.current_roll) > 0:
    faces_str = " ".join([dice_faces[val] for val in st.session_state.current_roll])
    total_sum = sum(st.session_state.current_roll)
    
    # Use HTML for large font display
    st.markdown(
        f"<div style='font-size: 80px; display: flex; align-items: center;'>"
        f"<span style='color: #333;'>{faces_str}</span> "
        f"<span style='font-size: 50px; margin-left: 20px;'> = <b>{total_sum}</b></span>"
        f"</div>", 
        unsafe_allow_html=True
    )
else:
    st.markdown("<div style='font-size: 80px; color: #ccc;'>🎲 Waiting to roll...</div>", unsafe_allow_html=True)

# =========================
# UI Rendering: Histogram and Normal Curve
# =========================
st.markdown("<hr>", unsafe_allow_html=True)
st.write(f"**TRACKED ROLLS: {len(st.session_state.history)}**")

# Only draw the plot if there is history data
if len(st.session_state.history) > 0:
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Set X-axis range (min = all 1s, max = all 6s)
    min_val = n
    max_val = n * 6
    
    # 1. Plot histogram
    # Use n-0.5 to n*6+0.5 as bin edges so bars are centered on integers
    bins = np.arange(min_val - 0.5, max_val + 1.5, 1)
    ax.hist(st.session_state.history, bins=bins, density=True, color='#1ABC9C', edgecolor='white')
    
    # 2. Plot theoretical normal distribution curve (black line)
    # Theoretical mean for a single die is 3.5, variance is 35/12
    # Sum of n dice: mean = n * 3.5, variance = n * (35/12)
    mu = n * 3.5
    sigma = np.sqrt(n * (35 / 12))
    
    x = np.linspace(min_val, max_val, 200)
    y = norm.pdf(x, mu, sigma)
    ax.plot(x, y, color='black', linewidth=2)
    
    # Beautify chart
    ax.set_xlim(min_val - 1, max_val + 1)
    ax.set_xticks(range(min_val, max_val + 1, max(1, n//2)))
    ax.set_yticks([]) # Hide Y-axis labels
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    st.pyplot(fig)