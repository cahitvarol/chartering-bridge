import streamlit as st
import pandas as pd

st.set_page_config(page_title="Chartering Bridge - Voyage Calc", layout="wide")

st.title("🚢 Voyage Calculation (Adım 1: Görsel Tasarım)")
st.markdown("---")

# Yan yana etiket ve kutucuk oluşturmak için pratik bir yardımcı fonksiyon
def satir_olustur(etiket, varsayilan_deger, tip="metin", adim=1.0):
    col1, col2 = st.columns([1, 1.5]) # Etiket ve kutu genişlik oranı
    with col1:
        st.write(f"**{etiket}**")
    with col2:
        if tip == "metin":
            return st.text_input(etiket, value=varsayilan_deger, label_visibility="collapsed")
        elif tip == "sayi":
            return st.number_input(etiket, value=varsayilan_deger, step=adim, format="%.2f", label_visibility="collapsed")

# ================= 1. ÜST BÖLÜM (Genel Bilgiler) =================
top1, top2, top3, top4 = st.columns(4)
with top1:
    vessel_name = satir_olustur("Vessel Name :", "TBN", "metin")
    voyage_no = satir_olustur("Voyage No :", "", "metin")
with top2:
    date = satir_olustur("Date :", "14.07.2026", "metin")
    currency = satir_olustur("Currency Rate :", 1.050, "sayi", 0.01)
with top3:
    bunker_price = satir_olustur("Bunker Price :", 750.0, "sayi", 10.0)
with top4:
    bunker_sea = satir_olustur("Bunker Cons (Sea):", 6.0, "sayi", 0.5)
    bunker_port = satir_olustur("Bunker Cons (Port):", 0.20, "sayi", 0.05)

st.markdown("---")

# ================= FORM BAŞLANGICI =================
# Tüm girdileri bir form içine alıyoruz ki sayfa sürekli yenilenip çökmesin
with st.form("voyage_form"):
    
    # ================= 2. ORTA BÖLÜM =================
    col1, col2, col3 = st.columns([1, 1, 1.5])
    
    with col1:
        st.markdown("### 📋 CHARTER PARTY DETAILS")
        account = satir_olustur("Account", "TBN", "metin")
        cargo = satir_olustur("Cargo Item", "Mineral", "metin")
        freight_type = st.selectbox("Freight Type", ["PMT", "LUMPSUM"])
        freight_rate = satir_olustur("Freight Rate ($)", 50.0, "sayi")
        qty = satir_olustur("Loaded Qty (Mts)", 6500.0, "sayi", 500.0)
        terms = satir_olustur("Load/Disch Term", "FIOST", "metin")
        broker_comm = satir_olustur("Broker Comm (%)", 2.50, "sayi", 0.25)
        load_rate = satir_olustur("Load Rate (Days)", 3.0, "sayi", 0.5)
        disch_rate = satir_olustur("Disch Rate (Days)", 3.0, "sayi", 0.5)

    with col2:
        st.markdown("### ⚓ PORT ROTATION & DA's")
        st.markdown("**Ballast**")
        ballast_port = satir_olustur("Ballast Port", "İskenderun", "metin")
        ballast_da = satir_olustur("Ballast DA ($)", 0.0, "sayi", 1000.0)
        
        st.markdown("**Load Ports**")
        load_port = satir_olustur("Load Port #1", "Alexandria", "metin")
        load_da = satir_olustur("Load DA ($)", 14000.0, "sayi", 1000.0)
        
        st.markdown("**Discharge Ports**")
        disch_port = satir_olustur("Disch Port #1", "Kaliningrad", "metin")
        disch_da = satir_olustur("Disch DA ($)", 20000.0, "sayi", 1000.0)

    with col3:
        st.markdown("### 🗺️ DISTANCES & SPEED")
        st.markdown("**(1) Ballast ➔ Load**")
        dist1 = satir_olustur("Distance 1 (NM)", 465.0, "sayi", 10.0)
        speed1 = satir_olustur("Speed 1 (Knots)", 11.0, "sayi", 0.5)
        
        st.markdown("**(2) Load ➔ Discharge**")
        dist2 = satir_olustur("Distance 2 (NM)", 4200.0, "sayi", 10.0)
        speed2 = satir_olustur("Speed 2 (Knots)", 9.0, "sayi", 0.5)
        
        st.markdown("**Diğer**")
        extra_days = satir_olustur("Extra Days", 6.0, "sayi", 0.5)
        strait_cost = satir_olustur("Turkish Straits ($)", 4000.0, "sayi", 500.0)
        
    st.markdown("---")
    
    # Butonları Formun Altına Koyuyoruz (Şimdilik aksiyonları yok, Adım 2'de eklenecek)
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        submit_btn = st.form_submit_button("🧮 HESAPLA (Adım 3'te çalışacak)", use_container_width=True)
    with col_btn2:
        st.info("Bunker fiyatlarını çekme butonu Adım 2'de buraya gelecek.")
