import streamlit as st
import pandas as pd

# =====================================================================
# SAYFA VE YARDIMCI FONKSİYON AYARLARI
# =====================================================================
st.set_page_config(layout="wide", page_title="Chartering Bridge")

# Sayıları Türkiye/Avrupa formatına (10.000,00) çeviren fonksiyon
def format_tr(val, is_int=False):
    if pd.isna(val): return "0"
    if is_int:
        return "{:,.0f}".format(val).replace(",", ".")
    else:
        return "{:,.2f}".format(val).replace(",", "X").replace(".", ",").replace("X", ".")

# Uygulama CSS Ayarları (Opsiyonel görsel iyileştirmeler için)
st.markdown("""
    <style>
    .main-header { font-size: 24px; font-weight: bold; color: #2C3E50; margin-top: 20px; border-bottom: 2px solid #3498DB; padding-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# BÖLÜM 1: CARGO & FREIGHT DETAILS (Varsayılan Değişkenler)
# =====================================================================
st.markdown('<p class="main-header">1 - Cargo & Freight Details</p>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)

with c1:
    quantity = st.number_input("Cargo Quantity (mts)", value=10000.0, step=500.0)
    freight = st.number_input("Freight Rate ($)", value=25.0, step=1.0)
    freight_term = st.selectbox("Freight Term", ["pmt", "lumpsum"])

with c2:
    demurrage = st.number_input("Demurrage ($/day)", value=5000.0, step=500.0)
    despatch = st.number_input("Despatch ($)", value=0.0)
    freight_tax = st.number_input("Freight Tax ($)", value=0.0)

with c3:
    add_comm = st.number_input("Address Comm. (%)", value=2.5, step=1.25)
    broker_comm = st.number_input("Broker Comm. (%)", value=1.25, step=1.25)

with c4:
    strait_canal = st.number_input("Strait / Canal Exp. ($)", value=0.0)
    extra_insurance = st.number_input("Extra Insurance ($)", value=0.0)
    cargo_survey = st.number_input("Cargo Survey ($)", value=0.0)
    other_exp = st.number_input("Other Expenses ($)", value=0.0)


# =====================================================================
# BÖLÜM 2: VESSEL DETAILS
# =====================================================================
st.markdown('<p class="main-header">2 - Vessel Details</p>', unsafe_allow_html=True)

# Not: Gemi adının veritabanından çekildiği "Name of Ship" (küçük o ile) düzeltmesi burada varsayılmıştır.
v1, v2, v3, v4, v5 = st.columns(5)
with v1:
    vessel_name = st.text_input("Vessel Name", key="v_name")
with v2:
    dwt = st.number_input("DWT", key="v_dwt", format="%.0f")
with v3:
    draft = st.number_input("Draft", key="v_draft", format="%.2f")
with v4:
    grain = st.number_input("Grain Cap (cuft)", key="v_grain", format="%.0f") # Ondalık kaldırıldı
    bale = st.number_input("Bale Cap (cuft)", key="v_bale", format="%.0f")   # Ondalık kaldırıldı
with v5:
    gt = st.number_input("GT", key="v_gt", format="%.0f") # Ondalık kaldırıldı
    nt = st.number_input("NT", key="v_nt", format="%.0f") # Ondalık kaldırıldı


# =====================================================================
# BÖLÜM 3: PORT ROTATION & OPERATIONS
# =====================================================================
st.markdown('<p class="main-header">3 - Port Rotation & Operations</p>', unsafe_allow_html=True)

# --- 1. PORT ROTATION TABLOSU (Sıfırlanma Sorunu Çözüldü) ---
st.write("**Port Rotation (Distances)**")
if "port_rotation_df" not in st.session_state:
    st.session_state.port_rotation_df = pd.DataFrame({
        "Port Name": ["", ""],
        "Port Type": ["Load Port", "Discharge Port"],
        "Distance": [0.0, 0.0],
        "Weather Margin (%)": [5, 5]
    })

st.session_state.port_rotation_df = st.data_editor(
    st.session_state.port_rotation_df,
    key="port_rot_editor",
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "Distance": st.column_config.NumberColumn("Distance (NM)", format="%,.2f"),
        "Weather Margin (%)": st.column_config.NumberColumn("Weather Margin", format="%d %%", step=1)
    }
)

col_op1, col_op2 = st.columns(2)

# --- 2. SPEED & CONSUMPTION (SEA) ---
with col_op1:
    st.write("**Speed & Consumption (At Sea)**")
    if "sea_df" not in st.session_state:
        st.session_state.sea_df = pd.DataFrame({
            "Condition": ["Ballast", "Laden"],
            "Speed": [12.0, 11.5],
            "Cons": [20.0, 22.0],
            "Select": ["VLSFO", "VLSFO"]
        })
    st.session_state.sea_df = st.data_editor(st.session_state.sea_df, key="sea_editor", use_container_width=True)

# --- 3. PORT CONSUMPTION (IDLE/WORK) ---
with col_op2:
    st.write("**Port Consumption (Mts/Day)**")
    if "port_df" not in st.session_state:
        st.session_state.port_df = pd.DataFrame({
            "Condition": ["Idle", "Working"],
            "Cons": [1.5, 2.5],
            "Select": ["MGO", "MGO"]
        })
    st.session_state.port_df = st.data_editor(st.session_state.port_df, key="port_editor", use_container_width=True)

col_op3, col_op4 = st.columns(2)

# --- 4. LOAD / DISCHARGE DETAILS ---
with col_op3:
    st.write("**L/D Details**")
    if "ld_details_df" not in st.session_state:
        st.session_state.ld_details_df = pd.DataFrame({
            "Operation": ["Loading", "Discharging"],
            "Rate": [5000.0, 3500.0],
            "Unit": ["mts/day", "mts/day"],
            "Extra Days": [0.0, 0.0]
        })
    st.session_state.ld_details_df = st.data_editor(st.session_state.ld_details_df, key="ld_editor", use_container_width=True)

# --- 5. PORT CHARGES & PDA ---
with col_op4:
    st.write("**Port Charges & Liner Expenses**")
    if "port_charges_df" not in st.session_state:
        st.session_state.port_charges_df = pd.DataFrame({
            "Port": ["Load Port", "Discharge Port"],
            "PDA": [15000.0, 18000.0],
            "Liner Expenses": [0.0, 0.0]
        })
    st.session_state.port_charges_df = st.data_editor(st.session_state.port_charges_df, key="pda_editor", use_container_width=True, num_rows="dynamic")

# --- 6. BUNKER PRICES ---
st.write("**Bunker Prices ($/mt)**")
if "bunker_df" not in st.session_state:
    st.session_state.bunker_df = pd.DataFrame({
        "Port": ["Load Port", "Discharge Port", "Bunkering Port"],
        "MGO": [850.0, 870.0, 800.0],
        "ULSFO": [650.0, 660.0, 620.0],
        "VLSFO": [600.0, 610.0, 580.0],
        "IFO380": [450.0, 460.0, 440.0],
        "Seç": [True, False, False] # Hangi limanın fiyatı kullanılacak
    })
st.session_state.bunker_df = st.data_editor(st.session_state.bunker_df, key="bunker_editor", use_container_width=True)


# =====================================================================
# HESAPLAMA BUTONU VE BÖLÜNME (LEG) MANTIĞI
# =====================================================================
st.write("")
st.write("")
_, calc_btn_col, _ = st.columns([2, 2, 2])

with calc_btn_col:
    hesapla_basildi = st.button("🚀 CALCULATE VOYAGE", type="primary", use_container_width=True)

# State Başlangıç Değerleri
if "res_summary" not in st.session_state:
    st.session_state.res_summary = {"total_days": 0.0, "sea_days": 0.0, "port_days": 0.0}
    st.session_state.voyage_legs_data = [] 
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

    # Seçili yakıt fiyatlarını al
    secili_satir = st.session_state.bunker_df[st.session_state.bunker_df["Seç"] == True]
    aktif_fiyatlar = secili_satir.iloc[0] if not secili_satir.empty else st.session_state.bunker_df.iloc[0]

    # --- BACAK (LEG) BAZLI SÜRE VE MESAFE HESABI ---
    voyage_legs = []
    total_sea_days = 0.0
    
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
        
        if port_type in ["Ballast Port", "Load Port"]:
            days = (dist / (spd_bal * 24)) * (1 + margin)
        else:
            days = (dist / (spd_ldn * 24)) * (1 + margin)
            
        total_sea_days += days
        leg_name = f"{prev_port} - {port_name}" if idx > 0 else f"Ballast -> {port_name}"
        
        voyage_legs.append({
            "Leg": leg_name,
            "Sea Days": days,
            "Port Days": 0.0 
        })
        prev_port = port_name

    # L/D Details tablosundan liman sürelerini ilgili bacaklara dağıt
    total_port_days = 0.0
    for idx, row in st.session_state.ld_details_df.iterrows():
        rate = float(row.get("Rate", 0.0))
        ex_days = float(row.get("Extra Days", 0.0))
        unit = str(row.get("Unit", ""))
        
        if unit == "mts/day" and rate > 0:
            p_days = (q / rate) + ex_days
        else:
            p_days = rate + ex_days
            
        total_port_days += p_days
        
        if idx < len(voyage_legs):
            voyage_legs[idx]["Port Days"] = p_days

    total_days = total_sea_days + total_port_days

    # --- DİĞER HESAPLAMALAR ---
    sea_fuel_type_ldn = str(st.session_state.sea_df.iloc[1]["Select"])
    total_sea_fuel_mts = ((total_sea_days / 2) * cons_bal) + ((total_sea_days / 2) * cons_ldn)
    total_port_fuel_mts = total_port_days * cons_port_work
    total_fuel_mts = total_sea_fuel_mts + total_port_fuel_mts
    
    fuel_price = float(aktif_fiyatlar.get(sea_fuel_type_ldn, 0.0))
    total_bunker_cost = total_fuel_mts * fuel_price

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

    st.session_state.voyage_legs_data = voyage_legs
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
# BÖLÜM 4: CALCULATION & STRATEGY (SONUÇ EKRANI)
# =====================================================================
st.markdown('<p class="main-header">4 - Calculation & Strategy</p>', unsafe_allow_html=True)

calc_col1, calc_col2, calc_col3 = st.columns([2.5, 1.2, 1.2])

with calc_col1:
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px;'>Voyage Summary</div>", unsafe_allow_html=True)
    
    summary_list = []
    if "voyage_legs_data" in st.session_state and st.session_state.voyage_legs_data:
        for leg in st.session_state.voyage_legs_data:
            leg_total = leg["Sea Days"] + leg["Port Days"]
            summary_list.append([
                leg["Leg"], 
                format_tr(leg_total), 
                format_tr(leg["Sea Days"]), 
                format_tr(leg["Port Days"])
            ])
        
        # En Alta Toplam Satırını Ekle
        summary_list.append([
            "TOTAL VOYAGE", 
            format_tr(st.session_state.res_summary['total_days']), 
            format_tr(st.session_state.res_summary['sea_days']), 
            format_tr(st.session_state.res_summary['port_days'])
        ])
    else:
        summary_list = [["TOTAL VOYAGE", "0,00", "0,00", "0,00"]]

    bunker_calc_df = pd.DataFrame(
        summary_list, 
        columns=["Voyage Legs", "Total Duration", "Sea Days", "Port Days"]
    )
    st.dataframe(bunker_calc_df, hide_index=True, use_container_width=True)
    
    st.info(f"💡 **Bunker Cost (Total):** $ {format_tr(st.session_state.get('res_bunker_cost', 0.0))}")

with calc_col2:
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px;'>Operational Expenses</div>", unsafe_allow_html=True)
    
    opex_vals = st.session_state.res_opex_details if st.session_state.res_opex_details else [0.0] * 13
    formatted_opex = [f"$ {format_tr(v)}" for v in opex_vals]
    
    op_exp_df = pd.DataFrame({
        "Item": ["Bunker Expense", "Port Charges", "Freight Tax", "Liner IN", "Liner OUT", "Despatch", "Strait / Canal Exp.", "Extra Insurance", "Cargo Survey", "Other", "Add Comm.", "Brkg Comm.", "TOTAL"],
        "Cost": formatted_opex
    })
    st.dataframe(op_exp_df, hide_index=True, use_container_width=True, height=520)

with calc_col3:
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px;'>Revenue</div>", unsafe_allow_html=True)
    
    rev = st.session_state.res_revenue
    dem = demurrage if "demurrage" in locals() else 0.0
    
    rev_df = pd.DataFrame({
        "Item": ["Freight", "Demurrage", "TOTAL"],
        "Amount": [f"$ {format_tr(rev - dem)}", f"$ {format_tr(dem)}", f"$ {format_tr(rev)}"]
    })
    st.dataframe(rev_df, hide_index=True, use_container_width=True)
    
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px;'>RESULT</div>", unsafe_allow_html=True)
    res_df = pd.DataFrame({
        "Metric": ["Total Revenue", "Total Op. Expens.", "Operational Profit", "Daily Profit (TCE)"],
        "Value": [
            f"$ {format_tr(st.session_state.res_revenue)}", 
            f"$ {format_tr(st.session_state.res_opex)}", 
            f"$ {format_tr(st.session_state.res_profit)}", 
            f"$ {format_tr(st.session_state.res_tce)}"
        ]
    })
    st.dataframe(res_df, hide_index=True, use_container_width=True)
    
    st.write("")
    st.metric(label="🎯 Break-even Freight", value=f"$ {format_tr(st.session_state.res_breakeven)} / mt", delta="- Zarar Sınırı", delta_color="inverse")
