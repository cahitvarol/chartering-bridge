import streamlit as st
import pandas as pd
from datetime import datetime, date

# Sayfa Yapılandırması
st.set_page_config(page_title="Chartering Bridge", layout="wide")

# CSS Ayarları
st.markdown("""
    <style>
    .stNumberInput label { font-size: 13px !important; color: black !important; font-weight: bold !important; }
    .stTextInput label { font-size: 13px !important; color: black !important; font-weight: bold !important; }
    .stSelectbox label { font-size: 13px !important; color: black !important; font-weight: bold !important; }
    .main-header { font-size: 22px; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #f0f2f6; padding-top: 20px;}
    .align-text { margin-top: 8px; font-weight: bold; font-size: 14px; color: black; }
    </style>
""", unsafe_allow_html=True)

# EN ÜST ANA BAŞLIK
st.markdown("<h1 style='text-align: center; font-weight: bold; font-size: 42px;'>VOYAGE CALCULATION</h1>", unsafe_allow_html=True)

# =====================================================================
# BÖLÜM 1: GENERAL INFORMATION
# =====================================================================
st.markdown('<p class="main-header">1 - General Information</p>', unsafe_allow_html=True)

col_left, col_right = st.columns([1.5, 3])

with col_left:
    st.write("") 
    
    v_id_col1, v_id_col2 = st.columns([1, 1.5])
    with v_id_col1: st.markdown("<div class='align-text'>Voyage ID No</div>", unsafe_allow_html=True)
    with v_id_col2: voyage_id = st.text_input("", value="2026-001", label_visibility="collapsed")
    
    date_col1, date_col2 = st.columns([1, 1.5])
    with date_col1: st.markdown("<div class='align-text'>Date</div>", unsafe_allow_html=True)
    with date_col2: voyage_date = st.date_input("", value=datetime(2026, 7, 14), format="DD.MM.YYYY", label_visibility="collapsed")
    
    curr_col1, curr_col2 = st.columns([1, 1.5])
    with curr_col1: st.markdown("<div class='align-text'>Currency Rate</div>", unsafe_allow_html=True)
    with curr_col2: currency_rate = st.number_input("", value=1.050, format="%.3f", label_visibility="collapsed")

with col_right:
    st.markdown("**Bunker Prices**")
    if 'bunker_df' not in st.session_state:
        st.session_state.bunker_df = pd.DataFrame({
            "Seç": [True, False, False, False],
            "Liman": ["Istanbul", "Gibraltar", "3rd Port", "4th Port"],
            "MGO %0,1": [1050.0, 1020.0, 0.0, 0.0],
            "ULSFO %0,1": [820.0, 790.0, 0.0, 0.0],
            "VLSFO %0,5": [640.0, 610.0, 0.0, 0.0],
            "IFO380 %3,5": [580.0, 550.0, 0.0, 0.0]
        })

    edited_df = st.data_editor(
        st.session_state.bunker_df,
        column_config={
            "Seç": st.column_config.CheckboxColumn("Seç", default=False, width="small"),
            "Liman": st.column_config.TextColumn("Liman", width="medium"),
            "MGO %0,1": st.column_config.NumberColumn("MGO %0,1", format="%.2f"),
            "ULSFO %0,1": st.column_config.NumberColumn("ULSFO %0,1", format="%.2f"),
            "VLSFO %0,5": st.column_config.NumberColumn("VLSFO %0,5", format="%.2f"),
            "IFO380 %3,5": st.column_config.NumberColumn("IFO380 %3,5", format="%.2f"),
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

    btn_col_empty, btn_col_actual = st.columns([1, 1])
    with btn_col_actual:
        if st.button("Update Bunker Prices", type="primary", use_container_width=True):
            st.toast("Güncel fiyatlar çekiliyor...", icon="⛽")
            st.session_state.bunker_df.loc[st.session_state.bunker_df["Liman"] == "Istanbul", ["MGO %0,1", "ULSFO %0,1", "VLSFO %0,5", "IFO380 %3,5"]] = [1090.0, 850.0, 680.0, 610.0]
            st.rerun()

secili_satirlar = st.session_state.bunker_df[st.session_state.bunker_df["Seç"] == True]
if not secili_satirlar.empty:
    aktif_liman = secili_satirlar.iloc[0]["Liman"]
    st.caption(f"Aktif Liman: **{aktif_liman}**")


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
    dwt = st.number_input("DWT", value=0.0, format="%.2f")
    dwcc = st.number_input("DWCC", value=0.0, format="%.2f")
with v4:
    grain = st.number_input("Grain Cap (cuft)", value=0.0, format="%.2f")
    bale = st.number_input("Bale Cap (cuft)", value=0.0, format="%.2f")
with v5:
    gt = st.number_input("GT", value=0.0, format="%.2f")
    nt = st.number_input("NT", value=0.0, format="%.2f")
with v6:
    loa = st.number_input("LOA", value=0.0, format="%.2f")
    beam = st.number_input("Beam", value=0.0, format="%.2f")

st.write("") 
st.markdown("**Speed & Consumption**")
sc1, sc2 = st.columns([1.2, 1]) 

yakit_tipleri = ["MGO %0,1", "ULSFO %0,1", "VLSFO %0,5", "IFO380 %3,5"]

with sc1:
    if 'sea_df' not in st.session_state:
        st.session_state.sea_df = pd.DataFrame({
            "At Sea": ["Ballast", "Laden"],
            "Speed": [12.0, 11.5],
            "Cons": [0.0, 0.0],
            "Select": ["MGO %0,1", "MGO %0,1"]
        })
    st.session_state.sea_df = st.data_editor(
        st.session_state.sea_df, 
        column_config={
            "At Sea": st.column_config.TextColumn("At Sea"),
            "Speed": st.column_config.NumberColumn("Speed", format="%.2f knot"),
            "Cons": st.column_config.NumberColumn("Cons", format="%.2f mts"),
            "Select": st.column_config.SelectboxColumn("Select", options=yakit_tipleri)
        },
        hide_index=True, use_container_width=True, key="sea_editor_main"
    )

with sc2:
    if 'port_df' not in st.session_state:
        st.session_state.port_df = pd.DataFrame({
            "At Port": ["Idle", "Work"],
            "Cons": [0.2, 0.2],
            "Select": ["MGO %0,1", "MGO %0,1"]
        })
    st.session_state.port_df = st.data_editor(
        st.session_state.port_df, 
        column_config={
            "At Port": st.column_config.TextColumn("At Port"),
            "Cons": st.column_config.NumberColumn("Cons", format="%.2f mts"),
            "Select": st.column_config.SelectboxColumn("Select", options=yakit_tipleri)
        },
        hide_index=True, use_container_width=True, key="port_editor_main"
    )


# =====================================================================
# BÖLÜM 3: C/P DETAILS
# =====================================================================
st.markdown('<p class="main-header">3 - C/P Details</p>', unsafe_allow_html=True)

cp1, cp2, cp3, cp4, cp5 = st.columns(5)
with cp1:
    account = st.text_input("Account", "TBN")
    cargo_item = st.text_input("Cargo Item", "Mineral")
    stowage_factor = st.number_input("Stowage Factor (cuft/ton)", value=0.0, format="%.2f")
    quantity = st.number_input("Quantity", value=0.0, format="%.2f")
with cp2:
    freight_term = st.selectbox("Freight Term", ["pmt", "lumpsum"])
    terms = st.selectbox("Terms", ["FIO", "FIOS", "FIOST", "LIFO", "FILO", "LILO"], index=2)
    gear = st.selectbox("Gear", ["Geared", "Gearless"])
    laycan_date = st.date_input("Laycan", value=date.today(), format="DD.MM.YYYY")
    st.markdown(f"<span style='color:#c5a059; font-size:14px; font-weight:bold;'>{laycan_date.strftime('%d %B %Y, %A')}</span>", unsafe_allow_html=True)
with cp3:
    freight = st.number_input("Freight", value=0.0, format="%.2f")
    demurrage = st.number_input("Demurrage", value=0.0, format="%.2f")
    despatch = st.number_input("Despatch", value=0.0, format="%.2f")
    freight_tax = st.number_input("Freight Tax", value=0.0, format="%.2f")
with cp4:
    extra_insurance = st.number_input("Extra Insurance", value=0.0, format="%.2f")
    cargo_survey = st.number_input("Cargo Survey", value=0.0, format="%.2f")
    strait_canal = st.number_input("Strait / Canal Passage Expenses", value=0.0, format="%.2f")
with cp5:
    add_comm = st.number_input("Address Commission (%)", value=0.0, step=0.25, format="%.2f")
    broker_comm = st.number_input("Brokerage Commission (%)", value=0.0, step=0.25, format="%.2f")
    other_exp = st.number_input("Other", value=0.0, format="%.2f")

st.write("")

# ----- TABLO 1: PORT ROTATION -----
st.markdown("**Port Rotation**")
if 'port_rotation_df' not in st.session_state:
    st.session_state.port_rotation_df = pd.DataFrame({
        "Port Type": ["Ballast Port"],
        "Port Name": [""],
        "Distance": [0.0]
    })

st.session_state.port_rotation_df = st.data_editor(
    st.session_state.port_rotation_df,
    column_config={
        "Port Type": st.column_config.SelectboxColumn("**Port Type**", options=["Ballast Port", "Load Port", "Discharge Port", "Bunker Port", "Return Ballast"], required=True),
        "Port Name": st.column_config.TextColumn("**Port Name**"),
        "Distance": st.column_config.NumberColumn("**Distance**", format="%.2f")
    },
    hide_index=True, num_rows="dynamic", use_container_width=True, key="rotation_editor_main"
)

# ----- GET DISTANCE BUTONU VE VERİ AKTARIMI -----
_, btn_col = st.columns([5, 1])
with btn_col:
    if st.button("Get Distance", type="primary", use_container_width=True):
        st.toast("Mesafeler çekiliyor ve tablolar güncelleniyor...", icon="🔄")
        
        df = st.session_state.port_rotation_df 
        filtered_df = df[df["Port Type"].isin(["Load Port", "Discharge Port"])]
        
        if not filtered_df.empty:
            st.session_state.port_charges_df = pd.DataFrame({
                "Port Type": filtered_df["Port Type"].tolist(),
                "Port Name": filtered_df["Port Name"].tolist(),
                "PDA": [0.0] * len(filtered_df),
                "Liner Expenses": [0.0] * len(filtered_df)
            })
            st.session_state.ld_details_df = pd.DataFrame({
                "Port Type": filtered_df["Port Type"].tolist(),
                "Port Name": filtered_df["Port Name"].tolist(),
                "Rate": [0.0] * len(filtered_df),
                "Unit": ["mts/day"] * len(filtered_df),
                "L/D Terms": ["SSHEX"] * len(filtered_df),
                "Extra Days": [0.0] * len(filtered_df)
            })
        else:
            st.session_state.port_charges_df = pd.DataFrame({"Port Type": [""], "Port Name": [""], "PDA": [0.0], "Liner Expenses": [0.0]})
            st.session_state.ld_details_df = pd.DataFrame({"Port Type": [""], "Port Name": [""], "Rate": [0.0], "Unit": ["mts/day"], "L/D Terms": ["SSHEX"], "Extra Days": [0.0]})
        
        if "charges_editor_main" in st.session_state:
            del st.session_state["charges_editor_main"]
        if "ld_editor_main" in st.session_state:
            del st.session_state["ld_editor_main"]
            
        st.rerun()

st.write("")
col_t2, col_t3 = st.columns([1.2, 1.8]) 

# ----- TABLO 2: PORT CHARGES -----
with col_t2:
    st.markdown("**Port Charges**")
    if 'port_charges_df' not in st.session_state:
        st.session_state.port_charges_df = pd.DataFrame({"Port Type": [""], "Port Name": [""], "PDA": [0.0], "Liner Expenses": [0.0]})
    
    st.session_state.port_charges_df = st.data_editor(
        st.session_state.port_charges_df,
        column_config={
            "Port Type": st.column_config.TextColumn("**Port Type**", disabled=True),
            "Port Name": st.column_config.TextColumn("**Port Name**"),
            "PDA": st.column_config.NumberColumn("**PDA**", format="%.2f"),
            "Liner Expenses": st.column_config.NumberColumn("**Liner Expenses**", format="%.2f")
        },
        hide_index=True, num_rows="dynamic", use_container_width=True, key="charges_editor_main"
    )

# ----- TABLO 3: L/D DETAILS -----
with col_t3:
    st.markdown("**L/D Details**")
    if 'ld_details_df' not in st.session_state:
        st.session_state.ld_details_df = pd.DataFrame({
            "Port Type": [""], "Port Name": [""], "Rate": [0.0], "Unit": ["mts/day"], "L/D Terms": ["SSHEX"], "Extra Days": [0.0]
        })
    
    st.session_state.ld_details_df = st.data_editor(
        st.session_state.ld_details_df,
        column_config={
            "Port Type": st.column_config.TextColumn("**Port Type**", disabled=True),
            "Port Name": st.column_config.TextColumn("**Port Name**", disabled=True),
            "Rate": st.column_config.NumberColumn("**Rate**", format="%.2f"),
            "Unit": st.column_config.SelectboxColumn("**Unit**", options=["mts/day", "days", "ttl days"]),
            "L/D Terms": st.column_config.SelectboxColumn("**L/D Terms**", options=["SSHEX", "SSHINC", "SHEX", "SHINC", "FHEX", "FHINC"]),
            "Extra Days": st.column_config.NumberColumn("**Extra Days**", format="%.2f")
        },
        hide_index=True, num_rows="dynamic", use_container_width=True, key="ld_editor_main"
    )


# =====================================================================
# BÖLÜM 4: CALCULATION & STRATEGY (GÖRSEL ŞABLON)
# =====================================================================
st.markdown('<p class="main-header">4 - Calculation & Strategy</p>', unsafe_allow_html=True)

calc_col1, calc_col2, calc_col3 = st.columns([2.5, 1.2, 1.2])

with calc_col1:
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px;'>Voyage Summary</div>", unsafe_allow_html=True)
    header_tuples = [
        (" ", "Port Rotation"), (" ", "Duration"),
        ("MGO", "mts"), ("MGO", "Cost"),
        ("ULSFO", "mts"), ("ULSFO", "Cost"),
        ("VLSFO", "mts"), ("VLSFO", "Cost"),
        ("IFO380", "mts"), ("IFO380", "Cost")
    ]
    calc_multi_columns = pd.MultiIndex.from_tuples(header_tuples)
    row_names = ["Ballast Port", "Steaming (Bal)", "Load Port", "Steaming (Ldn)", "Discharge Port", "Steaming (Return Ballast)", "Total"]
    bunker_calc_df = pd.DataFrame(0.0, index=range(len(row_names)), columns=calc_multi_columns)
    bunker_calc_df[(" ", "Port Rotation")] = row_names
    st.dataframe(bunker_calc_df, hide_index=True, use_container_width=True)

with calc_col2:
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px;'>Operational Expenses</div>", unsafe_allow_html=True)
    op_exp_df = pd.DataFrame({
        "Item": ["Bunker Expense", "Port Charges", "Freight Tax", "Liner IN", "Liner OUT", "Despatch", "Strait / Canal Exp.", "Extra Insurance", "Cargo Survey", "Other", "Add Comm.", "Brkg Comm.", "TOTAL"],
        "Cost": [0.0] * 13
    })
    # Tablonun yüksekliği scrollbar (kaydırma çubuğu) çıkmaması için 520 piksel olarak sabitlendi
    st.dataframe(op_exp_df, hide_index=True, use_container_width=True, height=520, column_config={"Cost": st.column_config.NumberColumn(format="%.2f")})

with calc_col3:
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px;'>Revenue</div>", unsafe_allow_html=True)
    rev_df = pd.DataFrame({
        "Item": ["Freight", "Demurrage", "TOTAL"],
        "Amount": [0.0, 0.0, 0.0]
    })
    st.dataframe(rev_df, hide_index=True, use_container_width=True, column_config={"Amount": st.column_config.NumberColumn(format="%.2f")})
    
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px;'>RESULT</div>", unsafe_allow_html=True)
    res_df = pd.DataFrame({
        "Metric": ["Total Revenue", "Total Op. Expens.", "Operational Profit", "Daily Profit", "R/C", "Net Daily Profit"],
        "Value": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    })
    st.dataframe(res_df, hide_index=True, use_container_width=True, column_config={"Value": st.column_config.NumberColumn(format="%.2f")})
    
    st.write("")
    st.metric(label="🎯 Break-even Freight", value="$ 26.50 / mt", delta="- Zarar Sınırı", delta_color="inverse")


# =====================================================================
# SENSITIVITY MATRIX (DUYARLILIK ANALİZİ)
# =====================================================================
st.divider()
st.markdown("<h4 style='color: #c5a059; text-align: center;'>Strategic Sensitivity Analysis (Daily Profit)</h4>", unsafe_allow_html=True)

# Örnek senaryo değerleri: Tam ortadaki Daily Profit $10,000 olacak şekilde hesaplama
base_f = freight if freight > 0 else 30.0 
base_q = quantity if quantity > 0 else 10000.0
dummy_days = 20.0 
target_daily_profit = 10000.0

# Formül: Ortadaki kesişim değerinin her zaman hedef günlük kara (Örn: 10.000$) eşit olması için gereken gizli "Toplam Maliyet" (Cost)
base_revenue = base_f * base_q
dummy_cost = base_revenue - (target_daily_profit * dummy_days)

f_vals = [base_f + i for i in range(-4, 5)] # Navlun (Düşey: 9 satır, 1 usd artış/azalış)
q_vals = [base_q + (i * 100) for i in range(-4, 5)] # Yük (Yatay: 9 sütun, 100 mt artış/azalış)

mat_data = []
for f in f_vals:
    row = []
    for q in q_vals:
        prof = ((f * q) - dummy_cost) / dummy_days
        row.append(prof)
    mat_data.append(row)
    
df_mat = pd.DataFrame(mat_data, index=[f"$ {x:.2f}" for x in f_vals], columns=[f"{x:,.0f} mt" for x in q_vals])

# Strateji tablosunun ortasındaki hedef satır ve sütunu (crosshair) renklendirme
def style_matrix(df):
    style_df = pd.DataFrame('', index=df.index, columns=df.columns)
    
    # 9x9 matriste tam orta indeks (4. indeks)
    mid_row = df.index[4]
    mid_col = df.columns[4]
    
    for r in df.index:
        for c in df.columns:
            val = df.loc[r, c]
            text_color = '#ff4b4b' if val < 0 else '#00cc96' # Eksi kırmızı, Artı yeşil
            
            bg_color = ''
            if r == mid_row or c == mid_col:
                bg_color = 'background-color: rgba(59, 130, 246, 0.2); ' # Hedef hattı için hafif şeffaf mavi
            
            style_df.loc[r, c] = f'color: {text_color}; font-weight: bold; {bg_color}'
            
    return style_df

# Tabloya formatlama ve stili uygulama
styled_mat = df_mat.style.apply(style_matrix, axis=None).format("$ {:,.0f}")

st.dataframe(styled_mat, use_container_width=True)
