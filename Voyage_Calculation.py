import streamlit as st
import pandas as pd
from datetime import datetime

# Sayfa Yapılandırması
st.set_page_config(page_title="Chartering Bridge", layout="wide")

st.markdown("""
    <style>
    .stNumberInput label { font-size: 12px !important; color: #888 !important; }
    .stTextInput label { font-size: 12px !important; color: #888 !important; }
    .main-header { font-size: 24px; font-weight: bold; margin-bottom: 20px; border-bottom: 2px solid #f0f2f6; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">1 - General Information</p>', unsafe_allow_html=True)

# ----------------- ANA DÜZEN -----------------
col_left, col_right, col_button = st.columns([1.2, 3, 0.8])

with col_left:
    st.write("") 
    
    v_id_col1, v_id_col2 = st.columns([1, 1.5])
    with v_id_col1: st.info("Voyage ID No")
    with v_id_col2: voyage_id = st.text_input("", value="2026-001", label_visibility="collapsed")
    
    date_col1, date_col2 = st.columns([1, 1.5])
    with date_col1: st.info("Date")
    with date_col2: voyage_date = st.date_input("", value=datetime(2026, 7, 14), label_visibility="collapsed")
    
    curr_col1, curr_col2 = st.columns([1, 1.5])
    with curr_col1: st.info("Currency Rate")
    with curr_col2: currency_rate = st.number_input("", value=1.050, format="%.3f", label_visibility="collapsed")

with col_right:
    st.markdown("**Bunker Prices (Interactive Table)**")
    
    # Gerçek bir Excel tablosu altyapısı (Dataframe) kuruyoruz
    if 'bunker_df' not in st.session_state:
        st.session_state.bunker_df = pd.DataFrame({
            "Seç": [True, False, False, False],
            "Liman": ["Istanbul", "Gibraltar", "3rd Port", "4th Port"],
            "MGO %0,10": [1050.0, 1020.0, 0.0, 0.0],
            "ULSFO %0,10": [820.0, 790.0, 0.0, 0.0],
            "VLSFO %0,50": [640.0, 610.0, 0.0, 0.0],
            "IFO 380 %3,50": [580.0, 550.0, 0.0, 0.0]
        })

    # Tabloyu ekranda düzenlenebilir (Excel gibi) gösteriyoruz
    edited_df = st.data_editor(
        st.session_state.bunker_df,
        column_config={
            "Seç": st.column_config.CheckboxColumn("Seç", default=False, width="small"),
            "Liman": st.column_config.TextColumn("Liman", width="medium"),
            "MGO %0,10": st.column_config.NumberColumn(format="$ %.2f"),
            "ULSFO %0,10": st.column_config.NumberColumn(format="$ %.2f"),
            "VLSFO %0,50": st.column_config.NumberColumn(format="$ %.2f"),
            "IFO 380 %3,50": st.column_config.NumberColumn(format="$ %.2f"),
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Kullanıcının tabloda yaptığı anlık değişiklikleri hafızaya kaydediyoruz
    st.session_state.bunker_df = edited_df

with col_button:
    st.write("") 
    st.write("")
    # Buton sağ tarafta yerini aldı
    if st.button("Get Bunker Prices", type="primary", use_container_width=True):
        st.toast("Güncel fiyatlar çekiliyor...", icon="⛽")
        # 2. Adımda burayı API'ye bağlayacağız, şimdilik test amaçlı fiyatları güncelliyor
        st.session_state.bunker_df.loc[st.session_state.bunker_df["Liman"] == "Istanbul", ["MGO %0,10", "ULSFO %0,10", "VLSFO %0,50", "IFO 380 %3,50"]] = [1090.0, 850.0, 680.0, 610.0]
        st.rerun()

# ----------------- HESAPLAMA MANTIĞI -----------------
st.divider()

# Seçili limanı bulma işlemi
secili_satirlar = edited_df[edited_df["Seç"] == True]

if not secili_satirlar.empty:
    aktif_liman = secili_satirlar.iloc[0]["Liman"]
    st.caption(f"Aktif Kullanılan Yakıt Fiyatı: **{aktif_liman}** verileri baz alınacaktır.")
else:
    st.error("Lütfen tablonun ilk sütunundan yakıt alınacak en az bir limanı seçin!")
