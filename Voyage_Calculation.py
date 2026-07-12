import streamlit as st
import pandas as pd

# Sayfa ayarları
st.set_page_config(page_title="Chartering Bridge", layout="wide")

st.title("🚢 Chartering Bridge - Voyage Calculation")
st.markdown("Mavi hücreler (Girdiler) / Otomatik Hesaplanan Alanlar (Çıktılar)")
st.markdown("---")

# ================= 1. ÜST BÖLÜM (Genel Bilgiler) =================
top1, top2, top3, top4 = st.columns(4)
with top1:
    vessel_name = st.text_input("Vessel Name", "TBN")
    voyage_no = st.text_input("Voyage No", "")
with top2:
    date = st.date_input("Date")
    currency_rate = st.number_input("Currency Rate (1 EUR = X USD)", value=1.050, format="%.3f")
with top3:
    bunker_price = st.number_input("Bunker Price (USD)", value=750.0, step=10.0)
with top4:
    bunker_cons_sea = st.number_input("Bunker Cons. (Mts @ Sea)", value=6.0, step=0.5)
    bunker_cons_port = st.number_input("Bunker Cons. (Mts @ Port)", value=0.20, step=0.05)

st.markdown("---")

# ================= 2. ORTA BÖLÜM (Detaylar ve Rota) =================
col1, col2, col3, col4 = st.columns([1.2, 1.2, 1.5, 1])

with col1:
    st.markdown("### CHARTER PARTY DETAILS")
    account = st.text_input("Account", "TBN")
    cargo_item = st.text_input("Cargo Item", "Mineral")
    freight_type = st.selectbox("Freight Type", ["PMT", "LUMPSUM"])
    freight_rate = st.number_input("Freight Rate (USD)", value=50.0, step=1.0)
    loaded_qty = st.number_input("Loaded Quantity (Mts)", value=6500.0, step=500.0)
    terms = st.text_input("Load/Disch. Term", "FIOST")
    add_comm = st.number_input("Add Comm. (%)", value=0.0, step=0.5)
    broker_comm = st.number_input("Broker Comm. (%)", value=2.50, step=0.25)
    load_rate = st.number_input("Load Rate (days)", value=3.0, step=0.5)
    disch_rate = st.number_input("Disch.Rate (days)", value=3.0, step=0.5)

with col2:
    st.markdown("### PORT ROTATION & DA's")
    ballast_port = st.text_input("Ballast Port", "İskenderun")
    ballast_da = st.number_input("Ballast DA (USD)", value=0.0, step=1000.0)
    
    st.markdown("**Load Ports**")
    load_port = st.text_input("Load Port #1", "Alexandria")
    load_da = st.number_input("Load Port DA (USD)", value=14000.0, step=1000.0)
    
    st.markdown("**Discharge Ports**")
    disch_port = st.text_input("Disch. Port #1", "Kaliningrad")
    disch_da = st.number_input("Disch. Port DA (USD)", value=20000.0, step=1000.0)

with col3:
    st.markdown("### Distances & Speed")
    st.markdown(f"**1.** {ballast_port} ➔ {load_port}")
    dist1 = st.number_input("Distance 1 (miles)", value=465.0, step=10.0)
    speed1 = st.number_input("Speed 1 (knots)", value=11.0, step=0.5)
    
    st.markdown(f"**2.** {load_port} ➔ {disch_port}")
    dist2 = st.number_input("Distance 2 (miles)", value=4200.0, step=10.0)
    speed2 = st.number_input("Speed 2 (knots)", value=9.0, step=0.5)
    
    st.markdown("**Ekstra Bekleme/Seyir**")
    extra_days = st.number_input("Extra Days", value=6.0, step=0.5)
    turkish_straits = st.number_input("Turkish Straits (Boğaz Masrafı USD)", value=4000.0, step=500.0)

# ----------------- ARKA PLAN HESAPLAMALARI -----------------

# Süre Hesapları (Gün)
days_sea1 = (dist1 / (speed1 * 24)) if speed1 > 0 else 0
days_sea2 = (dist2 / (speed2 * 24)) if speed2 > 0 else 0
total_sea_days = days_sea1 + days_sea2
total_days = total_sea_days + load_rate + disch_rate + extra_days

# Yakıt Hesapları (Tonaj)
bunker_sea = total_sea_days * bunker_cons_sea
bunker_load = load_rate * bunker_cons_port
bunker_disch = disch_rate * bunker_cons_port
bunker_extra = extra_days * bunker_cons_port
total_bunker = bunker_sea + bunker_load + bunker_disch + bunker_extra

with col4:
    st.markdown("### Days & Bunker")
    
    # Sağ üstteki özet tabloyu oluşturuyoruz
    summary_data = {
        "Steaming Time": [f"{total_sea_days:.2f}", f"{bunker_sea:.2f}"],
        "@ Load Port": [f"{load_rate:.2f}", f"{bunker_load:.2f}"],
        "@ Disch.Port": [f"{disch_rate:.2f}", f"{bunker_disch:.2f}"],
        "Extra": [f"{extra_days:.2f}", f"{bunker_extra:.2f}"],
        "TOTAL": [f"{total_days:.2f}", f"{total_bunker:.2f}"]
    }
    df_summary = pd.DataFrame(summary_data, index=["Days", "Bunker (Mts)"]).T
    st.dataframe(df_summary, use_container_width=True)

st.markdown("---")

# ================= 3. ALT BÖLÜM (Finansal Sonuçlar) =================
st.markdown("## VOYAGE CALCULATION (RESULTS)")
bot1, bot2, bot3 = st.columns(3)

# Gelir - Gider Matematiği
if freight_type == "PMT":
    freight_revenue = freight_rate * loaded_qty
else:
    freight_revenue = freight_rate # Lumpsum ise direkt girilen rakamı alır

total_revenue = freight_revenue # İleride Demurrage eklenebilir
total_comm = total_revenue * ((add_comm + broker_comm) / 100)
port_charges = ballast_da + load_da + disch_da
bunker_expense = total_bunker * bunker_price
total_expenses = total_comm + port_charges + bunker_expense + turkish_straits

op_profit = total_revenue - total_expenses
daily_profit = (op_profit / total_days) if total_days > 0 else 0

with bot1:
    st.markdown("#### Revenue")
    df_rev = pd.DataFrame({
        "Item": ["Freight", "Demurrage", "TOTAL"],
        "Amount (USD)": [f"{freight_revenue:,.2f}", "0.00", f"{total_revenue:,.2f}"]
    })
    st.dataframe(df_rev, hide_index=True, use_container_width=True)

with bot2:
    st.markdown("#### Operational Expenses")
    df_exp = pd.DataFrame({
        "Item": ["Broker Comm.", "Port Charges", "Bunker Expense", "Turkish Straits", "TOTAL"],
        "Cost (USD)": [f"{total_comm:,.2f}", f"{port_charges:,.2f}", f"{bunker_expense:,.2f}", f"{turkish_straits:,.2f}", f"{total_expenses:,.2f}"]
    })
    st.dataframe(df_exp, hide_index=True, use_container_width=True)

with bot3:
    st.markdown("#### RESULT")
    df_res = pd.DataFrame({
        "Metric": ["Total Revenue", "Total Op. Expens.", "Operational Profit", "Net Daily Profit (TCE)"],
        "Value (USD)": [f"{total_revenue:,.2f}", f"{total_expenses:,.2f}", f"{op_profit:,.2f}", f"{daily_profit:,.2f}"]
    })
    st.dataframe(df_res, hide_index=True, use_container_width=True)
    
    if daily_profit > 0:
        st.success(f"💰 TCE: ${daily_profit:,.2f} / Gün")
    else:
        st.error(f"🚨 TCE: ${daily_profit:,.2f} / Gün (ZARAR)")
