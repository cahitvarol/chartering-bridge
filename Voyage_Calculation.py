import streamlit as st
import pandas as pd
from datetime import datetime, date

# Sayfa Yapılandırması
st.set_page_config(page_title="Chartering Bridge", layout="wide")

st.markdown("""
    <style>
    .stNumberInput label { font-size: 12px !important; color: #888 !important; }
    .stTextInput label { font-size: 12px !important; color: #888 !important; }
    .stSelectbox label { font-size: 12px !important; color: #888 !important; }
    .main-header { font-size: 22px; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #f0f2f6; padding-top: 20px;}
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# BÖLÜM 1: GENERAL INFORMATION
# =====================================================================
st.markdown('<p class="main-header">1 - General Information</p>', unsafe_allow_html=True)

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
    st.markdown("**Bunker Prices**")
    if 'bunker_df' not in st.session_state:
        st.session_state.bunker_df = pd.DataFrame({
            "Seç": [True, False, False, False],
            "Liman": ["Istanbul", "Gibraltar", "3rd Port", "4th Port"],
            "MGO %0,10": [1050.0, 1020.0, 0.0, 0.0],
            "ULSFO %0,10": [820.0, 790.0, 0.0, 0.0],
            "VLSFO %0,50": [640.0, 610.0, 0.0, 0.0],
            "IFO 380 %3,50": [580.0, 550.0, 0.0, 0.0]
        })

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
        use_container_width=True,
        key="bunker_editor"
    )
    
    prev_selections = st.session_state.bunker_df["Seç"].tolist()
    curr_selections = edited_df["Seç"].tolist()
    changed_to_true = [i for i, (p, c) in enumerate(zip(prev_selections, curr_selections)) if not p and c]
    
    if changed_to_true:
        edited_df["Seç"] = False
        edited_df.loc[changed_to_true[0], "Seç"] = True
        st.session_state.bunker_df = edited_df
        st.rerun() 
    else:
        st.session_state.bunker_df = edited_df

with col_button:
    st.write("") 
    st.write("")
    if st.button("Get Bunker Prices", type="primary", use_container_width=True):
        st.toast("Güncel fiyatlar çekiliyor...", icon="⛽")
        st.session_state.bunker_df.loc[st.session_state.bunker_df["Liman"] == "Istanbul", ["MGO %0,10", "ULSFO %0,10", "VLSFO %0,50", "IFO 380 %3,50"]] = [1090.0, 850.0, 680.0, 610.0]
        st.rerun()

secili_satirlar = st.session_state.bunker_df[st.session_state.bunker_df["Seç"] == True]
if not secili_satirlar.empty:
    aktif_liman = secili_satirlar.iloc[0]["Liman"]
    st.caption(f"Aktif Liman: **{aktif_liman}**")
else:
    st.warning("Lütfen yakıt alınacak en az bir limanı seçin!")


# =====================================================================
# BÖLÜM 2: VESSEL DETAILS
# =====================================================================
st.markdown('<p class="main-header">2 - Vessel Details</p>', unsafe_allow_html=True)

v1, v2, v3, v4, v5, v6 = st.columns(6)
with v1:
    imo = st.text_input("IMO", "")
    name = st.text_input("Name", "")
    v_type = st.text_input("Type", "")
with v2:
    flag = st.text_input("Flag", "")
    v_class = st.text_input("Class", "")
    built = st.text_input("Built", "")
with v3:
    dwt = st.number_input("DWT", value=0)
    dwcc = st.number_input("DWCC", value=0)
with v4:
    grain = st.number_input("Grain Cap", value=0)
    bale = st.number_input("Bale Cap", value=0)
with v5:
    gt = st.number_input("GT", value=0)
    nt = st.number_input("NT", value=0)
with v6:
    loa = st.number_input("LOA", value=0.0, format="%.2f")
    beam = st.number_input("Beam", value=0.0, format="%.2f")

st.write("") 
st.markdown("**Speed & Consumption**")
sc1, sc2 = st.columns([1.3, 1]) 

with sc1:
    if 'sea_df' not in st.session_state:
        st.session_state.sea_df = pd.DataFrame({
            "At Sea": ["Ballast", "Laden"],
            "Speed": [12.0, 11.5],
            "MGO %0,10": [0.0, 0.0],
            "ULSFO %0,10": [0.0, 0.0],
            "VLSFO %0,50": [22.0, 24.0],
            "IFO 380 %3,50": [0.0, 0.0]
        })
    edited_sea = st.data_editor(st.session_state.sea_df, hide_index=True, use_container_width=True, key="sea_editor")

with sc2:
    if 'port_df' not in st.session_state:
        st.session_state.port_df = pd.DataFrame({
            "At Port": ["Idle", "Work"],
            "MGO %0,10": [0.2, 0.2],
            "ULSFO %0,10": [0.0, 0.0],
            "VLSFO %0,50": [2.0, 4.5],
            "IFO 380 %3,50": [0.0, 0.0]
        })
    edited_port = st.data_editor(st.session_state.port_df, hide_index=True, use_container_width=True, key="port_editor")


# =====================================================================
# BÖLÜM 3: C/P DETAILS
# =====================================================================
st.markdown('<p class="main-header">3 - C/P Details</p>', unsafe_allow_html=True)

cp1, cp2, cp3, cp4, cp5 = st.columns(5)

with cp1:
    account = st.text_input("Account", "TBN")
    cargo_item = st.text_input("Cargo Item", "Mineral")
    quantity = st.number_input("Quantity", value=0.0)

with cp2:
    freight_term = st.selectbox("Freight Term", ["pmt", "lumpsum"])
    # Terimler güncellendi ve varsayılan değer 2. indeks olan FIOST yapıldı (0'dan başlar: 0,1,2)
    terms = st.selectbox("Terms", ["FIO", "FIOS", "FIOST", "LIFO", "FILO", "LILO"], index=2)
    
    # Laycan takvimi eklendi
    laycan_date = st.date_input("Laycan", value=date.today())
    # Seçilen tarih İngilizce gün ismiyle gösteriliyor (Örn: 14 July 2026, Tuesday)
    st.markdown(f"<span style='color:#c5a059; font-size:14px; font-weight:bold;'>{laycan_date.strftime('%d %B %Y, %A')}</span>", unsafe_allow_html=True)

with cp3:
    freight = st.number_input("Freight", value=0.0)
    demurrage = st.number_input("Demurrage", value=0.0)
    despatch = st.number_input("Despatch", value=0.0)

with cp4:
    extra_insurance = st.number_input("Extra Insurance", value=0.0)
    cargo_survey = st.number_input("Cargo Survey", value=0.0)
    strait_canal = st.number_input("Strait / Canal Passage Expenses", value=0.0)

with cp5:
    add_comm = st.number_input("Address Commission (%)", value=0.0, step=0.25)
    broker_comm = st.number_input("Brokerage Commission (%)", value=0.0, step=0.25)
    other_exp = st.number_input("Other", value=0.0)

st.write("")
st.markdown("**Port Rotation**")

if 'rotation_df' not in st.session_state:
    st.session_state.rotation_df = pd.DataFrame({
        "Port Rotation": ["Ballast Port", "Load Port", "Discharge Port"],
        "Port Name": ["", "", ""],
        "Rate": [0.0, 0.0, 0.0],
        "Unit": ["mts/day", "mts/day", "mts/day"],            # Başlık güncellendi
        "L/D Terms": ["SSHEX", "SSHEX", "SSHEX"],             # Yeni sütun eklendi
        "Extra Days": [0.0, 0.0, 0.0],                        # Yeni sütun eklendi
        "Distance": [0.0, 0.0, 0.0],
        "PDA": [0.0, 0.0, 0.0]                                # Yeni sütun eklendi
    })

# Sütun ayarları
edited_rotation = st.data_editor(
    st.session_state.rotation_df,
    column_config={
        "Port Rotation": st.column_config.SelectboxColumn(
            "Port Rotation",
            options=["Ballast Port", "Load Port", "Discharge Port"],
            required=True
        ),
        "Port Name": st.column_config.TextColumn("Port Name"),
        "Rate": st.column_config.NumberColumn("Rate", format="%.2f"),
        "Unit": st.column_config.SelectboxColumn(
            "Unit",
            options=["mts/day", "days", "ttl days"],
            required=True
        ),
        "L/D Terms": st.column_config.SelectboxColumn(
            "L/D Terms",
            options=["SSHEX", "SSHINC", "SHEX", "SHINC", "FHEX", "FHINC"],
            required=True
        ),
        "Extra Days": st.column_config.NumberColumn("Extra Days", format="%.2f"),
        "Distance": st.column_config.NumberColumn("Distance", format="%.2f"),
        "PDA": st.column_config.NumberColumn("PDA", format="$ %.2f")
    },
    hide_index=True,
    num_rows="dynamic",
    use_container_width=True,
    key="rotation_editor"
)
