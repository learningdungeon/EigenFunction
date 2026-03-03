import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- PAGE CONFIG ---
st.set_page_config(page_title="Eigen-Hunt: Research Edition", layout="wide")

# --- SESSION STATE INITIALIZATION ---
if 'score' not in st.session_state:
    st.session_state.score = 0
    st.session_state.history = []
    st.session_state.matrix = np.array([[0, 1], [1, 0]]) # Start with Pauli-X
    st.session_state.vector = np.array([1, 1])
    st.session_state.is_eigen = True

# --- LOGIC: GENERATE NEW ROUND ---
def next_round():
    # 50% chance for a true Eigen-pair
    st.session_state.is_eigen = np.random.choice([True, False])
    
    if st.session_state.is_eigen:
        # Common Quantum Gates
        gates = [
            np.array([[0, 1], [1, 0]]),   # Pauli-X
            np.array([[1, 0], [0, -1]]),  # Pauli-Z
            np.array([[2, 0], [0, 2]]),   # Scaling Identity
            np.array([[1, 1], [1, 1]])    # Projection
        ]
        st.session_state.matrix = gates[np.random.randint(0, len(gates))]
        
        # Test common directional vectors
        vecs = [np.array([1, 1]), np.array([1, -1]), np.array([1, 0]), np.array([0, 1])]
        # Cross-product check to ensure alignment
        valid = [v for v in vecs if np.allclose(np.cross(st.session_state.matrix @ v, v), 0)]
        
        if valid:
            st.session_state.vector = valid[np.random.randint(0, len(valid))]
        else:
            # Fallback if no specific vector matches
            st.session_state.vector = np.array([1, 1])
    else:
        # Random non-eigen scenario
        st.session_state.matrix = np.random.randint(-2, 3, size=(2, 2))
        st.session_state.vector = np.array([1, 2])
    
    st.rerun()

# --- HEADER ---
st.title("🎯 Eigen-Hunt: Research Edition")
st.write("Find the **Stable Directions** where the Matrix preserves the Vector's Identity.")

# --- UI LAYOUT ---
col1, col2 = st.columns([1.5, 2])

with col1:
    st.subheader("1. The Math & Ratio Check")
    m = st.session_state.matrix
    v = st.session_state.vector
    Av = m @ v
    
    # Calculation String Formatting
    calc_text = r"\begin{pmatrix} %s & %s \\ %s & %s \end{pmatrix} \begin{pmatrix} %s \\ %s \end{pmatrix} = \begin{pmatrix} %s \\ %s \end{pmatrix}" % (
        m[0,0], m[0,1], m[1,0], m[1,1], v[0], v[1], Av[0], Av[1]
    )
    st.latex(calc_text)

    # Ratio Check (Handling zeros)
    rx = Av[0]/v[0] if v[0] != 0 else (0.0 if Av[0] == 0 else None)
    ry = Av[1]/v[1] if v[1] != 0 else (0.0 if Av[1] == 0 else None)

    c_a, c_b = st.columns(2)
    c_a.metric("X-Factor ($\lambda_x$)", f"{rx:.2f}" if rx is not None else "Div/0")
    c_b.metric("Y-Factor ($\lambda_y$)", f"{ry:.2f}" if ry is not None else "Div/0")

    # Determine match
    is_match = False
    if rx is not None and ry is not None and np.isclose(rx, ry):
        is_match = True
    elif rx is None and ry is not None and np.isclose(Av[0], 0):
        is_match = True # Case for vectors on Y-axis
    elif ry is None and rx is not None and np.isclose(Av[1], 0):
        is_match = True # Case for vectors on X-axis

    st.write("---")
    
    # Buttons for User Interaction
    b1, b2 = st.columns(2)
    if b1.button("✅ YES (Eigenvector)"):
        if st.session_state.is_eigen:
            st.success("Correct! The character is preserved.")
            st.session_state.score += 10
        else:
            st.error("Wrong! The vector was tilted.")
            
    if b2.button("❌ NO (Not Eigenvector)"):
        if not st.session_state.is_eigen:
            st.success("Correct! Identity was changed.")
            st.session_state.score += 10
        else:
            st.error("Actually, it stayed on the same line!")

    st.metric("Total Score", st.session_state.score)
    
    if st.button("Generate Next Challenge ➡️", use_container_width=True):
        next_round()

    if st.button("💾 Save to Research Log", use_container_width=True):
        if is_match:
            eigenval = rx if rx is not None else ry
            entry = {"Matrix": str(m.tolist()), "Vector": str(v.tolist()), "Eigenvalue": eigenval}
            st.session_state.history.append(entry)
            st.toast("Saved to Research Log!")
        else:
            st.warning("Only Eigenvectors can be saved to the log.")

with col2:
    st.subheader("2. Visual Proof")
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Setting dynamic camera view
    limit = max(np.abs([*v, *Av, 2])) + 0.5
    ax.set_xlim(-limit, limit); ax.set_ylim(-limit, limit)
    ax.axhline(0, color='black', lw=1); ax.axvline(0, color='black', lw=1)
    ax.grid(True, linestyle=':', alpha=0.6)

    # Blue = Input, Red = Output
    ax.quiver(0, 0, v[0], v[1], color='blue', angles='xy', scale_units='xy', scale=1, 
              label=f'Input v ({v[0]}, {v[1]})', width=0.015)
    
    if not np.allclose(Av, 0):
        ax.quiver(0, 0, Av[0], Av[1], color='red', alpha=0.7, angles='xy', scale_units='xy', scale=1, 
                  label=f'Output Av ({Av[0]:.1f}, {Av[1]:.1f})', width=0.01)
    else:
        ax.plot(0, 0, 'ro', label='Output Collapsed to 0')

    ax.set_aspect('equal')
    ax.legend(loc='upper right')
    st.pyplot(fig)

# --- RESEARCH LOG SECTION ---
st.write("---")
st.subheader("📚 Your Quantum Research Log")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.table(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Research as CSV", data=csv, file_name="quantum_research_log.csv")
else:
    st.info("Find an Eigenvector and click 'Save' to start your log.")