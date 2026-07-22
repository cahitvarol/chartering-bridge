import streamlit as st
import pandas as pd
from datetime import datetime, date
from supabase import create_client, Client

# =====================================================================
# SUPABASE BAĞLANTI AYARLARI (Kendi bilgilerinizi buraya girin)
# =====================================================================
SUPABASE_URL = "https://hoygbxuspdtfdfpwkgod.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhveWdieHVzcGR0ZmRmcHdrZ29kIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM3NzQ4NjMsImV4cCI6MjA5OTM1MDg2M30.zkLZE6B9rFO-7bZZGBUOIwcyNtFI_xIeED2PPICrk4A"

@st.cache_resource
def init_connection():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return None

supabase = init_connection()

# =====================================================================
# SAYI FORMATLAMA FONKSİYONU (10.000,00 - Türkiye/Avrupa Formatı)
# =====================================================================
def format_tr(val, is_int=False):
    if pd.isna(val): return "0"
    if is_int:
        return "{:,.0f}".format(val).replace(",", ".")
    else:
        return "{:,.2f}".format(val).replace(",", "X").replace(".", ",").replace("X", ".")

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
# IMO OTOMATİK DOLDURMA FONKSİYONU VE STATE AYARLARI
# =====================================================================
vessel_keys = {
    "v_imo": "", "v_name": "", "v_type": "", "v_flag": "", "v_class": "", "v_built": "",
    "v_dwt": 0.0, "v_dwcc": 0.0, "v_grain": 0.0, "v_bale": 0.0,
    "v_gt": 0.0, "v_nt": 0.0, "v_loa": 0.0, "v_beam": 0.0
}
for k, v in vessel_keys.items():
    if k not in st.session_state:
        st.session_state[k] = v

def reset_vessel_data():
    for key in vessel_keys.keys():
        if key != "v_imo":
            st.session_state[key] = vessel_keys[key]

def fetch_vessel_data():
    imo_val = str(st.session_state.v_imo).strip()
    
    if not imo_val:
        reset_vessel_data()
        return
        
    if supabase is None:
        st.error("Supabase bağlantısı kurulamadı. Lütfen URL ve KEY bilgilerinizi kontrol edin.")
        return

    try:
        response = supabase.table("vesseldatabase").select("*").ilike("IMO Number", f"%{imo_val}%").execute()
        data = response.data
        
        if data and len(data) > 0:
            v = data[0]
            
            st.session_state.v_name = str(v.get("Name of Ship", ""))
            st.session_state.v_type = str(v.get("Type of Ship", ""))
            st.session_state.v_flag = str(v.get("Flag", ""))
            st.session_state.v_class = str(v.get("Class", ""))
            st.session_state.v_built = str(v.get("Year of Build", ""))
            
            st.session_state.v_dwt = float(v.get("DWT", 0.0) or 0.0)
            st.session_state.v_dwcc = float(v.get("DWCC", 0.0) or 0.0)
            st.session_state.v_grain = float(v.get("Grain Cap (cuft)", 0.0) or 0.0)
            st.session_state.v_bale = float(v.get("Bale Cap (cuft)", 0.0) or 0.0)
            st.session_state.v_gt = float(v.get("Gross Tonnage", 0.0) or 0.0)
            st.session_state.v_nt = float(v.get("Net Tonnage", 0.0) or 0.0)
            st.session_state.v_loa = float(v.get("LOA", 0.0) or 0.0)
            st.session_state.v_beam = float(v.get("Beam", 0.0) or 0.0)
            
            st.toast(f"Gemi veritabanından çekildi: {st.session_state.v_name}", icon="✅")
        else:
            reset_vessel_data()
            st.toast("Veritabanında bu IMO numarasına ait gemi bulunamadı.", icon="⚠️")
            
    except Exception as e:
        reset_vessel_data()
        st.error(f"Sorgu hatası: {e}")


# =====================================================================
# BÖLÜM 1: GENERAL INFORMATION
# =====================================================================
st.markdown('<p class="main-header">1 - General Information</p>', unsafe_allow_html=True)

col_left, col_right = st.columns([1.5, 3])

with col_left:
    st.write("") 
    
    v_id_col1, v_id_col2 = st.columns([1, 1.5])
    with v_id_col1: st.markdown("<div class='align-text'>Voyage ID No</div>", unsafe_allow_html=True)
    with v_id_col2: voyage_id = st.text_input("", value="", label_visibility="collapsed")
    
    date_col1, date_col2 = st.columns([1, 1.5])
    with date_col1: st.markdown("<div class='align-text'>Date</div>", unsafe_allow_html=True)
    with date_col2: voyage_date = st.date_input("", value=datetime(2026, 7, 14), format="DD.MM.YYYY", label_visibility="collapsed")
    
    curr_col1, curr_col2 = st.columns([1, 1.5])
    with curr_col1: st.markdown("<div class='align-text'>Currency Rate</div>", unsafe_allow_html=True)
    with curr_col2: currency_rate = st.number_input("", value=0.0, format="%.3f", label_visibility="collapsed")

with col_right:
    st.markdown("**Bunker Prices**")
    
    # 1. Base (İskelet) oluştur
    if 'bunker_base' not in st.session_state:
        st.session_state.bunker_base = pd.DataFrame({
            "Seç": [True, False, False, False],
            "Liman": ["Istanbul", "Gibraltar", "3rd Port", "4th Port"],
            "MGO %0,1": [1050.0, 1020.0, 0.0, 0.0],
            "ULSFO %0,1": [820.0, 790.0, 0.0, 0.0],
            "VLSFO %0,5": [640.0, 610.0, 0.0, 0.0],
            "IFO380 %3,5": [580.0, 550.0, 0.0, 0.0]
        })

    # 2. Data Editor'u Base üzerinden çağır
    edited_df = st.data_editor(
        st.session_state.bunker_base,
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
        key="bunker_editor_widget"
    )
    
    # Checkbox Seçim Mantığı
    prev_selections = st.session_state.bunker_base["Seç"].tolist()
    curr_selections = edited_df["Seç"].tolist()
    changed_to_true = [i for i, (p, c) in enumerate(zip(prev_selections, curr_selections)) if not p and c]
    
    if changed_to_true:
        edited_df["Seç"] = False
        edited_df.loc[changed_to_true[0], "Seç"] = True
        st.session_state.bunker_base = edited_df # Rerun için iskeleti güncelliyoruz
        st.rerun() 

    # 3. Hesaplamalar için çıktıyı eski df ismine aktar
    st.session_state.bunker_df = edited_df

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
    imo = st.text_input("IMO", key="v_imo", on_change=fetch_vessel_data)
    name = st.text_input("Name", key="v_name")
    v_type = st.text_input("Type", key="v_type")
with v2:
    flag = st.text_input("Flag", key="v_flag")
    v_class = st.text_input("Class", key="v_class")
    built = st.text_input("Built", key="v_built")
with v3:
    dwt = st.number_input("DWT", key="v_dwt", format="%.2f")
    dwcc = st.number_input("DWCC", key="v_dwcc", format="%.2f")
with v4:
    grain = st.number_input("Grain Cap (cuft)", key="v_grain", format="%.0f")
    bale = st.number_input("Bale Cap (cuft)", key="v_bale", format="%.0f")
with v5:
    gt = st.number_input("GT", key="v_gt", format="%.0f")
    nt = st.number_input("NT", key="v_nt", format="%.0f")
with v6:
    loa = st.number_input("LOA", key="v_loa", format="%.2f")
    beam = st.number_input("Beam", key="v_beam", format="%.2f")

st.write("") 
st.markdown("**Speed & Consumption**")
sc1, sc2 = st.columns([1.2, 1]) 

yakit_tipleri = ["MGO %0,1", "ULSFO %0,1", "VLSFO %0,5", "IFO380 %3,5"]

with sc1:
    if 'sea_base' not in st.session_state:
        st.session_state.sea_base = pd.DataFrame({
            "At Sea": ["Ballast", "Laden"],
            "Speed": [0.0, 0.0],
            "Cons": [0.0, 0.0],
            "Select": ["MGO %0,1", "MGO %0,1"]
        })
    current_sea = st.data_editor(
        st.session_state.sea_base, 
        column_config={
            "At Sea": st.column_config.TextColumn("At Sea"),
            "Speed": st.column_config.NumberColumn("Speed", format="%.2f knot"),
            "Cons": st.column_config.NumberColumn("Cons", format="%.2f mts"),
            "Select": st.column_config.SelectboxColumn("Select", options=yakit_tipleri)
        },
        hide_index=True, use_container_width=True, key="sea_editor_widget"
    )
    st.session_state.sea_df = current_sea

with sc2:
    if 'port_base' not in st.session_state:
        st.session_state.port_base = pd.DataFrame({
            "At Port": ["Idle", "Work"],
            "Cons": [0.0, 0.0],
            "Select": ["MGO %0,1", "MGO %0,1"]
        })
    current_port = st.data_editor(
        st.session_state.port_base, 
        column_config={
            "At Port": st.column_config.TextColumn("At Port"),
            "Cons": st.column_config.NumberColumn("Cons", format="%.2f mts"),
            "Select": st.column_config.SelectboxColumn("Select", options=yakit_tipleri)
        },
        hide_index=True, use_container_width=True, key="port_editor_widget"
    )
    st.session_state.port_df = current_port

# =====================================================================
# BÖLÜM 3: C/P DETAILS
# =====================================================================
st.markdown('<p class="main-header">3 - C/P Details</p>', unsafe_allow_html=True)

cp1, cp2, cp3, cp4, cp5 = st.columns(5)
with cp1:
    account = st.text_input("Account", "")
    cargo_item = st.text_input("Cargo Item", "")
    stowage_factor = st.number_input("Stowage Factor (cuft/ton)", value=0.0, format="%.2f")
    quantity = st.number_input("Quantity", value=0.0, format="%.2f")
with cp2:
    freight_term = st.selectbox("Freight Term", ["pmt", "lumpsum"])
    terms = st.selectbox("Terms", ["FIO", "FIOS", "FIOST", "LIFO", "FILO", "LILO"], index=2)
    gear = st.selectbox("Gear", ["Gearless", "Geared"])
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

# ----- TABLO 1: PORT ROTATION (Kesin Çözüm) -----
st.markdown("**Port Rotation**")

# 1. AŞAMA: Tablonun iskeletini (base) BİR KERE oluşturuyoruz ve bir daha kodla ASLA değiştirmiyoruz.
if 'port_rotation_base' not in st.session_state:
    st.session_state.port_rotation_base = pd.DataFrame({
        "Port Type": ["Ballast Port"],
        "Port Name": [""],
        "Distance": [0.0],
        "Weather Margin (%)": [5]
    })

# 2. AŞAMA: Data Editor sadece sabit 'base' veriyi okur. Siz satır ekledikçe bunu 'key' hafızasında tutar.
current_rotation = st.data_editor(
    st.session_state.port_rotation_base,
    key="rotation_editor_widget",
    column_config={
        "Port Type": st.column_config.SelectboxColumn("**Port Type**", options=["Ballast Port", "Load Port", "Discharge Port", "Bunker Port", "Return Ballast"], required=True),
        "Port Name": st.column_config.TextColumn("**Port Name**"),
        "Distance": st.column_config.NumberColumn("**Distance**"), 
        "Weather Margin (%)": st.column_config.NumberColumn("**Weather Margin (%)**", format="%d %%", step=1)
    },
    hide_index=True, 
    num_rows="dynamic", 
    use_container_width=True
)

# 3. AŞAMA: Hesaplama butonunun (aşağıdaki kodların) görebilmesi için GÜNCEL halini eski isme eşitliyoruz.
st.session_state.port_rotation_df = current_rotation

# ----- GET DISTANCE BUTONU VE VERİ AKTARIMI -----
_, btn_col = st.columns([5, 1])
with btn_col:
    if st.button("Get Distance", type="primary", use_container_width=True):
        st.toast("Mesafeler çekiliyor ve tablolar güncelleniyor...", icon="🔄")
        
        df = st.session_state.port_rotation_df 
        filtered_df = df[df["Port Type"].isin(["Load Port", "Discharge Port"])]
        
        if not filtered_df.empty:
            # DİKKAT: Artık df'leri değil, base'leri değiştiriyoruz
            st.session_state.port_charges_base = pd.DataFrame({
                "Port Type": filtered_df["Port Type"].tolist(),
                "Port Name": filtered_df["Port Name"].tolist(),
                "PDA": [0.0] * len(filtered_df),
                "Liner Expenses": [0.0] * len(filtered_df)
            })
            st.session_state.ld_details_base = pd.DataFrame({
                "Port Type": filtered_df["Port Type"].tolist(),
                "Port Name": filtered_df["Port Name"].tolist(),
                "Rate": [0.0] * len(filtered_df),
                "Unit": ["mts/day"] * len(filtered_df),
                "L/D Terms": ["SSHEX"] * len(filtered_df),
                "Extra Days": [0.0] * len(filtered_df)
            })
        else:
            st.session_state.port_charges_base = pd.DataFrame({"Port Type": [""], "Port Name": [""], "PDA": [0.0], "Liner Expenses": [0.0]})
            st.session_state.ld_details_base = pd.DataFrame({"Port Type": [""], "Port Name": [""], "Rate": [0.0], "Unit": ["mts/day"], "L/D Terms": ["SSHEX"], "Extra Days": [0.0]})
        
        if "charges_editor_widget" in st.session_state:
            del st.session_state["charges_editor_widget"]
        if "ld_editor_widget" in st.session_state:
            del st.session_state["ld_editor_widget"]
            
        st.rerun()

st.write("")
col_t2, col_t3 = st.columns([1.2, 1.8]) 

# ----- TABLO 2: PORT CHARGES -----
with col_t2:
    st.markdown("**Port Charges**")
    if 'port_charges_base' not in st.session_state:
        st.session_state.port_charges_base = pd.DataFrame({"Port Type": [""], "Port Name": [""], "PDA": [0.0], "Liner Expenses": [0.0]})
    
    current_charges = st.data_editor(
        st.session_state.port_charges_base,
        key="charges_editor_widget",
        column_config={
            "Port Type": st.column_config.TextColumn("**Port Type**", disabled=True),
            "Port Name": st.column_config.TextColumn("**Port Name**"),
            "PDA": st.column_config.NumberColumn("**PDA**", format="%.2f"),
            "Liner Expenses": st.column_config.NumberColumn("**Liner Expenses**", format="%.2f")
        },
        hide_index=True, num_rows="dynamic", use_container_width=True
    )
    st.session_state.port_charges_df = current_charges

# ----- TABLO 3: L/D DETAILS -----
with col_t3:
    st.markdown("**L/D Details**")
    if 'ld_details_base' not in st.session_state:
        st.session_state.ld_details_base = pd.DataFrame({
            "Port Type": [""], "Port Name": [""], "Rate": [0.0], "Unit": ["mts/day"], "L/D Terms": ["SSHEX"], "Extra Days": [0.0]
        })
    
    current_ld = st.data_editor(
        st.session_state.ld_details_base,
        key="ld_editor_widget",
        column_config={
            "Port Type": st.column_config.TextColumn("**Port Type**", disabled=True),
            "Port Name": st.column_config.TextColumn("**Port Name**", disabled=True),
            "Rate": st.column_config.NumberColumn("**Rate**", format="%.2f"),
            "Unit": st.column_config.SelectboxColumn("**Unit**", options=["mts/day", "days", "ttl days"]),
            "L/D Terms": st.column_config.SelectboxColumn("**L/D Terms**", options=["SSHEX", "SSHINC", "SHEX", "SHINC", "FHEX", "FHINC"]),
            "Extra Days": st.column_config.NumberColumn("**Extra Days**", format="%.2f")
        },
        hide_index=True, num_rows="dynamic", use_container_width=True
    )
    st.session_state.ld_details_df = current_ld
    
# =====================================================================
# HESAPLAMA BUTONU VE MATEMATİKSEL İŞLEMLER
# =====================================================================
st.write("")
st.write("")
_, calc_btn_col, _ = st.columns([2, 2, 2])

with calc_btn_col:
    hesapla_basildi = st.button("🚀 CALCULATE VOYAGE", type="primary", use_container_width=True)

if "res_summary" not in st.session_state:
    st.session_state.res_summary = {"total_days": 0.0, "sea_days": 0.0, "port_days": 0.0, "sea_cost": 0.0, "port_cost": 0.0}
    st.session_state.sea_legs_data = [] 
    st.session_state.port_ops_data = []
    st.session_state.res_revenue = 0.0
    st.session_state.res_opex = 0.0
    st.session_state.res_profit = 0.0
    st.session_state.res_tce = 0.0
    st.session_state.res_breakeven = 0.0
    st.session_state.res_bunker_cost = 0.0
    st.session_state.res_opex_details = []

if hesapla_basildi:
    q = quantity if quantity > 0 else 1.0 
    f_rate = freight
    
    spd_bal = float(st.session_state.sea_df.iloc[0]["Speed"]) if float(st.session_state.sea_df.iloc[0]["Speed"]) > 0 else 1.0
    spd_ldn = float(st.session_state.sea_df.iloc[1]["Speed"]) if float(st.session_state.sea_df.iloc[1]["Speed"]) > 0 else 1.0
    cons_bal = float(st.session_state.sea_df.iloc[0]["Cons"])
    cons_ldn = float(st.session_state.sea_df.iloc[1]["Cons"])
    cons_port_work = float(st.session_state.port_df.iloc[1]["Cons"])

    aktif_fiyatlar = st.session_state.bunker_df[st.session_state.bunker_df["Seç"] == True].iloc[0]
    sea_fuel_type_ldn = str(st.session_state.sea_df.iloc[1]["Select"])
    fuel_price = float(aktif_fiyatlar.get(sea_fuel_type_ldn, 0.0))

    # --- 1. SEYİR (AT SEA) HESAPLAMALARI ---
    sea_legs = []
    total_sea_days = 0.0
    total_sea_cost = 0.0
    
    port_names = []
    for i, r in st.session_state.port_rotation_df.iterrows():
        name = str(r.get("Port Name", "")).strip()
        if not name: name = f"Port {i+1}"
        port_names.append(name)

    prev_port = "Origin"
    for idx, row in st.session_state.port_rotation_df.iterrows():
        port_name = port_names[idx]
        dist = float(row.get("Distance", 0.0))
        margin = float(row.get("Weather Margin (%)", 5.0)) / 100.0
        port_type = str(row.get("Port Type", ""))
        
        if port_type in ["Ballast Port", "Load Port", "Return Ballast"]:
            days = (dist / (spd_bal * 24)) * (1 + margin)
            fuel_mts = days * cons_bal
        else:
            days = (dist / (spd_ldn * 24)) * (1 + margin)
            fuel_mts = days * cons_ldn
            
        cost = fuel_mts * fuel_price
        total_sea_days += days
        total_sea_cost += cost
        
        leg_name = f"{prev_port} - {port_name}" if idx > 0 else f"Ballast -> {port_name}"
        sea_legs.append({"At Sea": leg_name, "Duration (days)": days, "Bunker Cons. (USD)": cost})
        prev_port = port_name

    # --- 2. LİMAN (AT PORT) HESAPLAMALARI ---
    port_ops = []
    total_port_days = 0.0
    total_port_cost = 0.0
    
    for idx, row in st.session_state.ld_details_df.iterrows():
        p_name = str(row.get("Port Name", "")).strip()
        if not p_name: p_name = f"Port {idx+1}"
        
        rate = float(row.get("Rate", 0.0))
        ex_days = float(row.get("Extra Days", 0.0))
        unit = str(row.get("Unit", ""))
        
        if unit == "mts/day" and rate > 0:
            p_days = (q / rate) + ex_days
        else:
            p_days = rate + ex_days
            
        fuel_mts = p_days * cons_port_work
        cost = fuel_mts * fuel_price
        
        port_ops.append({"At Port": p_name, "Duration (days)": p_days, "Bunker Cons. (USD)": cost})
        total_port_days += p_days
        total_port_cost += cost

    total_days = total_sea_days + total_port_days
    total_bunker_cost = total_sea_cost + total_port_cost

    # --- 3. DİĞER HESAPLAMALAR ---
    gross_freight = f_rate * q if freight_term == "pmt" else f_rate
    total_revenue = gross_freight + demurrage

    commissions = gross_freight * ((add_comm + broker_comm) / 100.0)
    total_pda = st.session_state.port_charges_df["PDA"].sum()
    total_liner = st.session_state.port_charges_df["Liner Expenses"].sum()

    total_opex = (total_bunker_cost + total_pda + total_liner + 
                  despatch + strait_canal + extra_insurance + 
                  cargo_survey + other_exp + commissions + freight_tax)

    op_profit = total_revenue - total_opex
    tce = op_profit / total_days if total_days > 0 else 0.0
    breakeven = total_opex / q if q > 0 else 0.0

    st.session_state.sea_legs_data = sea_legs
    st.session_state.port_ops_data = port_ops
    st.session_state.res_summary = {
        "total_days": total_days, "sea_days": total_sea_days, "port_days": total_port_days,
        "sea_cost": total_sea_cost, "port_cost": total_port_cost
    }
    st.session_state.res_revenue = total_revenue
    st.session_state.res_opex = total_opex
    st.session_state.res_profit = op_profit
    st.session_state.res_tce = tce
    st.session_state.res_breakeven = breakeven
    st.session_state.res_bunker_cost = total_bunker_cost
    st.session_state.res_opex_details = [
        total_bunker_cost, total_pda, freight_tax, total_liner, 0.0, 
        despatch, strait_canal, extra_insurance, cargo_survey, other_exp, 
        gross_freight * (add_comm/100), gross_freight * (broker_comm/100), total_opex
    ]
    st.toast("Sefer hesaplaması başarıyla tamamlandı!", icon="📈")
    

# =====================================================================
# BÖLÜM 4: CALCULATION & STRATEGY (SONUÇ EKRANI)
# =====================================================================
st.markdown('<p class="main-header">4 - Calculation & Strategy</p>', unsafe_allow_html=True)

calc_col1, calc_col2, calc_col3 = st.columns([2.5, 1.2, 1.2])

with calc_col1:
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px; margin-bottom: 5px;'>Voyage Summary</div>", unsafe_allow_html=True)
    
    # --- TABLO 1: AT SEA (SEYİR) ---
    sea_list = []
    if "sea_legs_data" in st.session_state and st.session_state.sea_legs_data:
        for leg in st.session_state.sea_legs_data:
            sea_list.append([leg["At Sea"], format_tr(leg["Duration (days)"]), format_tr(leg["Bunker Cons. (USD)"])])
        sea_list.append(["TOTAL", format_tr(st.session_state.res_summary['sea_days']), format_tr(st.session_state.res_summary['sea_cost'])])
    else:
        sea_list = [["TOTAL", "0,00", "0,00"]]

    sea_df = pd.DataFrame(sea_list, columns=["At Sea", "Duration (days)", "Bunker Cons. (USD)"])
    # Sayıları Sağa Dayama İşlemi
    styled_sea = sea_df.style.set_properties(**{'text-align': 'right'}, subset=["Duration (days)", "Bunker Cons. (USD)"])
    st.dataframe(styled_sea, hide_index=True, use_container_width=True)

    st.write("") # İki tablo arasına boşluk

    # --- TABLO 2: AT PORT (LİMAN) ---
    port_list = []
    if "port_ops_data" in st.session_state and st.session_state.port_ops_data:
        for pop in st.session_state.port_ops_data:
            port_list.append([pop["At Port"], format_tr(pop["Duration (days)"]), format_tr(pop["Bunker Cons. (USD)"])])
        port_list.append(["TOTAL", format_tr(st.session_state.res_summary['port_days']), format_tr(st.session_state.res_summary['port_cost'])])
    else:
        port_list = [["TOTAL", "0,00", "0,00"]]

    port_df = pd.DataFrame(port_list, columns=["At Port", "Duration (days)", "Bunker Cons. (USD)"])
    # Sayıları Sağa Dayama İşlemi
    styled_port = port_df.style.set_properties(**{'text-align': 'right'}, subset=["Duration (days)", "Bunker Cons. (USD)"])
    st.dataframe(styled_port, hide_index=True, use_container_width=True)

with calc_col2:
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px; margin-bottom: 5px;'>Operational Expenses</div>", unsafe_allow_html=True)
    
    opex_vals = st.session_state.res_opex_details if st.session_state.res_opex_details else [0.0] * 13
    formatted_opex = [f"$ {format_tr(v)}" for v in opex_vals]
    
    op_exp_df = pd.DataFrame({
        "Item": ["Bunker Expense", "Port Charges", "Freight Tax", "Liner IN", "Liner OUT", "Despatch", "Strait / Canal Exp.", "Extra Insurance", "Cargo Survey", "Other", "Add Comm.", "Brkg Comm.", "TOTAL"],
        "Cost": formatted_opex
    })
    styled_opex = op_exp_df.style.set_properties(**{'text-align': 'right'}, subset=["Cost"])
    st.dataframe(styled_opex, hide_index=True, use_container_width=True, height=520)

with calc_col3:
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px; margin-bottom: 5px;'>Revenue</div>", unsafe_allow_html=True)
    
    rev = st.session_state.res_revenue
    dem = demurrage if "demurrage" in locals() else 0.0
    
    rev_df = pd.DataFrame({
        "Item": ["Freight", "Demurrage", "TOTAL"],
        "Amount": [f"$ {format_tr(rev - dem)}", f"$ {format_tr(dem)}", f"$ {format_tr(rev)}"]
    })
    styled_rev = rev_df.style.set_properties(**{'text-align': 'right'}, subset=["Amount"])
    st.dataframe(styled_rev, hide_index=True, use_container_width=True)
    
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px; margin-bottom: 5px;'>RESULT</div>", unsafe_allow_html=True)
    res_df = pd.DataFrame({
        "Metric": ["Total Revenue", "Total Op. Expens.", "Operational Profit", "Daily Profit (TCE)"],
        "Value": [
            f"$ {format_tr(st.session_state.res_revenue)}", 
            f"$ {format_tr(st.session_state.res_opex)}", 
            f"$ {format_tr(st.session_state.res_profit)}", 
            f"$ {format_tr(st.session_state.res_tce)}"
        ]
    })
    styled_res = res_df.style.set_properties(**{'text-align': 'right'}, subset=["Value"])
    st.dataframe(styled_res, hide_index=True, use_container_width=True)
    
    st.write("")
    st.metric(label="🎯 Break-even Freight", value=f"$ {format_tr(st.session_state.res_breakeven)} / mt", delta="- Zarar Sınırı", delta_color="inverse")
