import streamlit as pd
import pandas as pd
from datetime import datetime, date

# ... (CSS ve diğer kısımlar aynı kalacak) ...

# ----- PORT ROTATION DÜZENLEME FONKSİYONU -----
def update_rotation():
    st.session_state.port_rotation_df = st.session_state.rotation_editor

# ----- TABLO 1: PORT ROTATION -----
st.markdown("**Port Rotation**")
if 'port_rotation_df' not in st.session_state:
    st.session_state.port_rotation_df = pd.DataFrame({
        "Port Type": ["Ballast Port"],
        "Port Name": [""],
        "Distance": [0.0]
    })

# Key'i 'rotation_editor' olarak değiştirdik ve on_change parametresini ekledik
edited_rotation = st.data_editor(
    st.session_state.port_rotation_df,
    column_config={
        "Port Type": st.column_config.SelectboxColumn("**Port Type**", options=["Ballast Port", "Load Port", "Discharge Port", "Bunker Port", "Return Ballast"], required=True),
        "Port Name": st.column_config.TextColumn("**Port Name**"),
        "Distance": st.column_config.NumberColumn("**Distance**", format="%.2f")
    },
    hide_index=True, 
    num_rows="dynamic", 
    use_container_width=True, 
    key="rotation_editor",
    on_change=update_rotation
)

# Eğer kullanıcı doğrudan 'edited_rotation' üzerinden işlem yapıyorsa bunu state'e eşitle
if not edited_rotation.equals(st.session_state.port_rotation_df):
    st.session_state.port_rotation_df = edited_rotation
