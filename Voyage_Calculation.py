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
# Gemi kutuları için hafıza (Session State) tanımlaması
vessel_keys = {
    "v_imo": "", "v_name": "", "v_type": "", "v_flag": "", "v_class": "", "v_built": "",
    "v_dwt": 0.0, "v_dwcc": 0.0, "v_grain": 0.0, "v_bale": 0.0,
    "v_gt": 0.0, "v_nt": 0.0, "v_loa": 0.0, "v_beam": 0.0
}
for k, v in vessel_keys.items():
    if k not in st.session_state:
        st.session_state[k] = v

def reset_vessel_data():
    """Gemi bulunamazsa kutuları temizler"""
    for key in vessel_keys.keys():
        if key != "v_imo":
            st.session_state[key] = vessel_keys[key]

def fetch_vessel_data():
    """Supabase'den IMO numarasına göre gemiyi çeker"""
    imo_val = str(st.session_state.v_imo).strip()
    
    if not imo_val:
        reset_vessel_data()
        return
        
    if supabase is None:
        st.error("Supabase bağlantısı kurulamadı. Lütfen URL ve KEY bilgilerinizi kontrol edin.")
        return

    try:
        # Supabase Sorgusu (IMO Number kolonunda arama yapar)
        response = supabase.table("vesseldatabase").select("*").ilike("IMO Number", f"%{imo_val}%").execute()
        data = response.data
        
        if data and len(data) > 0:
            v = data[0] # Gelen ilk satırı alıyoruz
            
            # Excel'deki kolon isimleriyle eşleşecek şekilde verileri atıyoruz
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

secili_satirlar = st.session_state.bunker_df[st.session_state.bunker_df["Seç"] == True]
if not secili_satirlar.empty:
    aktif_liman = secili_satirlar.iloc[0]["Liman"]
    st.caption(f"Aktif Liman: **{aktif_liman}**")


# =====================================================================
# BÖLÜM 2: VESSEL DETAILS (Dinamik Veritabanı Kutuları)
# =====================================================================
st.markdown('<p class="main-header">2 - Vessel Details</p>', unsafe_allow_html=True)

v1, v2, v3, v4, v5, v6 = st.columns(6)
with v1:
    # IMO girişi on_change (değişim olduğunda) fetch_vessel_data fonksiyonunu tetikler
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
    if 'sea_df' not in st.session_state:
        st.session_state.sea_df = pd.DataFrame({
            "At Sea": ["Ballast", "Laden"],
            "Speed": [0.0, 0.0],
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
            "Cons": [0.0, 0.0],
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
    account = st.text_input("Account", "")
    cargo_item = st.text_input("Cargo Item", "")
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
        "Distance": [0.0],
        "Weather Margin (%)": [5.0]
    })

st.session_state.port_rotation_df = st.data_editor(
    st.session_state.port_rotation_df,
    column_config={
        "Port Type": st.column_config.SelectboxColumn("**Port Type**", options=["Ballast Port", "Load Port", "Discharge Port", "Bunker Port", "Return Ballast"], required=True),
        "Port Name": st.column_config.TextColumn("**Port Name**"),
        "Distance": st.column_config.NumberColumn("**Distance**", format="%.2f"),
        "Weather Margin (%)": st.column_config.NumberColumn("**Weather Margin (%)**", format="%.1f", default=5.0)
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
# =====================================================================
# HESAPLAMA BUTONU VE MATEMATİKSEL İŞLEMLER
# =====================================================================
st.write("")
_, calc_btn_col, _ = st.columns([2, 2, 2])

with calc_btn_col:
    hesapla_basildi = st.button("🚀 CALCULATE VOYAGE", type="primary", use_container_width=True)

# Hesaplama sonuçlarını tutacağımız varsayılan değişkenler (Butona basılmadan önce 0 görünmesi için)
if "res_summary" not in st.session_state:
    st.session_state.res_summary = {"total_days": 0.0, "sea_days": 0.0, "port_days": 0.0}
    st.session_state.res_fuel_mts = {"MGO": 0.0, "ULSFO": 0.0, "VLSFO": 0.0, "IFO380": 0.0}
    st.session_state.res_fuel_cost = {"MGO": 0.0, "ULSFO": 0.0, "VLSFO": 0.0, "IFO380": 0.0}
    st.session_state.res_opex = 0.0
    st.session_state.res_revenue = 0.0
    st.session_state.res_profit = 0.0
    st.session_state.res_tce = 0.0
    st.session_state.res_breakeven = 0.0
    st.session_state.res_opex_details = []

if hesapla_basildi:
    # 1. TEMEL VERİLERİ ÇEKME
    # Yük miktarı ve Navlun
    q = quantity if quantity > 0 else 1.0 # Sıfıra bölme hatasını önlemek için
    f_rate = freight
    
    # Hız ve Tüketim (Sea) - Index 0: Ballast, Index 1: Laden
    spd_bal = float(st.session_state.sea_df.iloc[0]["Speed"]) if float(st.session_state.sea_df.iloc[0]["Speed"]) > 0 else 1.0
    spd_ldn = float(st.session_state.sea_df.iloc[1]["Speed"]) if float(st.session_state.sea_df.iloc[1]["Speed"]) > 0 else 1.0
    cons_bal = float(st.session_state.sea_df.iloc[0]["Cons"])
    cons_ldn = float(st.session_state.sea_df.iloc[1]["Cons"])
    
    # Hız ve Tüketim (Port) - Index 0: Idle, Index 1: Work
    cons_port_idle = float(st.session_state.port_df.iloc[0]["Cons"])
    cons_port_work = float(st.session_state.port_df.iloc[1]["Cons"])

    # Aktif Liman Yakıt Fiyatları
    aktif_fiyatlar = st.session_state.bunker_df[st.session_state.bunker_df["Seç"] == True].iloc[0]

    # 2. SÜRE VE MESAFE HESAPLAMALARI
    total_sea_days = 0.0
    for idx, row in st.session_state.port_rotation_df.iterrows():
        dist = float(row["Distance"])
        margin = float(row["Weather Margin (%)"]) / 100.0
        
        # Basit mantık: Yükleme limanına gidiş Ballast, Tahliye limanına gidiş Laden
        if str(row["Port Type"]) in ["Ballast Port", "Load Port"]:
            days = (dist / (spd_bal * 24)) * (1 + margin)
        else:
            days = (dist / (spd_ldn * 24)) * (1 + margin)
        total_sea_days += days

    total_port_days = 0.0
    for idx, row in st.session_state.ld_details_df.iterrows():
        rate = float(row["Rate"])
        ex_days = float(row["Extra Days"])
        unit = str(row["Unit"])
        
        if unit == "mts/day" and rate > 0:
            p_days = (q / rate) + ex_days
        elif unit == "days":
            p_days = rate + ex_days
        else:
            p_days = rate + ex_days
        total_port_days += p_days

    total_days = total_sea_days + total_port_days

    # 3. YAKIT (BUNKER) HESAPLAMASI
    # Basitleştirilmiş Yakıt Seçimi: Şimdilik ana tüketimi temsil eden yakıt türüne göre hesaplanır
    # Proje geliştikçe her bacak için ayrı yakıt tipi formüle edilebilir.
    sea_fuel_type_bal = str(st.session_state.sea_df.iloc[0]["Select"])
    sea_fuel_type_ldn = str(st.session_state.sea_df.iloc[1]["Select"])
    port_fuel_type = str(st.session_state.port_df.iloc[1]["Select"])

    total_sea_fuel_mts = ((total_sea_days / 2) * cons_bal) + ((total_sea_days / 2) * cons_ldn)
    total_port_fuel_mts = total_port_days * cons_port_work
    
    total_fuel_mts = total_sea_fuel_mts + total_port_fuel_mts
    
    # Tüketilen yakıtın fiyat karşılığı (Şimdilik tek yakıt tipi üzerinden maliyetlendirme)
    fuel_price = float(aktif_fiyatlar.get(sea_fuel_type_ldn, 0.0))
    total_bunker_cost = total_fuel_mts * fuel_price

    # 4. GELİR VE GİDER (OPEX) HESAPLAMALARI
    gross_freight = f_rate * q if freight_term == "pmt" else f_rate
    total_revenue = gross_freight + demurrage

    commissions = gross_freight * ((add_comm + broker_comm) / 100.0)
    total_pda = st.session_state.port_charges_df["PDA"].sum()
    total_liner = st.session_state.port_charges_df["Liner Expenses"].sum()

    total_opex = (total_bunker_cost + total_pda + total_liner + 
                  despatch + strait_canal + extra_insurance + 
                  cargo_survey + other_exp + commissions + freight_tax)

    # 5. KARLILIK SONUÇLARI
    op_profit = total_revenue - total_opex
    tce = op_profit / total_days if total_days > 0 else 0.0
    breakeven = total_opex / q if q > 0 else 0.0

    # Sonuçları State'e kaydet
    st.session_state.res_summary = {"total_days": total_days, "sea_days": total_sea_days, "port_days": total_port_days}
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
# BÖLÜM 4: CALCULATION & STRATEGY (GÜNCELLENMİŞ GÖRSEL)
# =====================================================================
st.markdown('<p class="main-header">4 - Calculation & Strategy</p>', unsafe_allow_html=True)

calc_col1, calc_col2, calc_col3 = st.columns([2.5, 1.2, 1.2])

with calc_col1:
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px;'>Voyage Summary</div>", unsafe_allow_html=True)
    header_tuples = [
        (" ", "Metrics"), (" ", "Duration (Days)"),
        ("Sea", "Days"), ("Port", "Days")
    ]
    calc_multi_columns = pd.MultiIndex.from_tuples(header_tuples)
    
    summary_data = [
        ["Total Voyage", f"{st.session_state.res_summary['total_days']:.2f}", 
         f"{st.session_state.res_summary['sea_days']:.2f}", 
         f"{st.session_state.res_summary['port_days']:.2f}"]
    ]
    
    bunker_calc_df = pd.DataFrame(summary_data, columns=calc_multi_columns)
    st.dataframe(bunker_calc_df, hide_index=True, use_container_width=True)
    
    st.info(f"💡 **Bunker Cost (Total):** $ {st.session_state.get('res_bunker_cost', 0.0):,.2f}")

with calc_col2:
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px;'>Operational Expenses</div>", unsafe_allow_html=True)
    
    opex_vals = st.session_state.res_opex_details if st.session_state.res_opex_details else [0.0] * 13
    
    op_exp_df = pd.DataFrame({
        "Item": ["Bunker Expense", "Port Charges", "Freight Tax", "Liner IN", "Liner OUT", "Despatch", "Strait / Canal Exp.", "Extra Insurance", "Cargo Survey", "Other", "Add Comm.", "Brkg Comm.", "TOTAL"],
        "Cost": opex_vals
    })
    st.dataframe(op_exp_df, hide_index=True, use_container_width=True, height=520, column_config={"Cost": st.column_config.NumberColumn(format="$ %.2f")})

with calc_col3:
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px;'>Revenue</div>", unsafe_allow_html=True)
    rev_df = pd.DataFrame({
        "Item": ["Freight", "Demurrage", "TOTAL"],
        "Amount": [st.session_state.res_revenue - demurrage, demurrage, st.session_state.res_revenue]
    })
    st.dataframe(rev_df, hide_index=True, use_container_width=True, column_config={"Amount": st.column_config.NumberColumn(format="$ %.2f")})
    
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px;'>RESULT</div>", unsafe_allow_html=True)
    res_df = pd.DataFrame({
        "Metric": ["Total Revenue", "Total Op. Expens.", "Operational Profit", "Daily Profit (TCE)"],
        "Value": [
            st.session_state.res_revenue, 
            st.session_state.res_opex, 
            st.session_state.res_profit, 
            st.session_state.res_tce
        ]
    })
    st.dataframe(res_df, hide_index=True, use_container_width=True, column_config={"Value": st.column_config.NumberColumn(format="$ %.2f")})
    
    st.write("")
    st.metric(label="🎯 Break-even Freight", value=f"$ {st.session_state.res_breakeven:,.2f} / mt", delta="- Zarar Sınırı", delta_color="inverse")
