import streamlit as st

# Sayfanın daha geniş ve ferah görünmesi için yapılandırma
st.set_page_config(page_title="Chartering Bridge", layout="wide")

st.title("🚢 Chartering Bridge")
st.subheader("Basit Sefer Hesaplama (Voyage Calculation)")
st.markdown("---") # Araya ince bir çizgi çeker

# Ekranı Sol (Girdiler) ve Sağ (Çıktılar) olarak iki kolona bölüyoruz
col1, col2 = st.columns(2)

with col1:
    st.write("### 📥 Sefer Girdileri")
    
    # Yük ve Gelir Bilgileri
    cargo_qty = st.number_input("Yük Miktarı (Ton)", min_value=0.0, value=10000.0, step=500.0)
    freight_rate = st.number_input("Navlun (Ton Başına $)", min_value=0.0, value=25.0, step=1.0)
    
    # Masraf Bilgileri
    port_costs = st.number_input("Toplam Liman Masrafları (Yükleme + Tahliye $)", min_value=0.0, value=30000.0, step=1000.0)
    bunker_price = st.number_input("Yakıt Birim Fiyatı ($/Ton)", min_value=0.0, value=600.0, step=10.0)
    
    # Seyir Bilgileri
    distance = st.number_input("Toplam Mesafe (Deniz Mili - NM)", min_value=0.0, value=2000.0, step=100.0)
    speed = st.number_input("Gemi Hızı (Knot)", min_value=0.0, value=12.0, step=0.5)
    port_days = st.number_input("Limanda Geçecek Toplam Süre (Gün)", min_value=0.0, value=4.0, step=0.5)
    bunker_cons = st.number_input("Günlük Yakıt Tüketimi (Ton)", min_value=0.0, value=20.0, step=1.0)

with col2:
    st.write("### 📊 Hesaplama Sonuçları")
    
    # ARKA PLANDAKİ MATEMATİKSEL HESAPLAMALAR
    # 1. Süre Hesapları
    if speed > 0:
        sea_days = distance / (speed * 24) # Mesafe / (Hız * 24 Saat)
    else:
        sea_days = 0
        
    total_days = sea_days + port_days
    
    # 2. Gelir ve Gider Hesapları
    revenue = cargo_qty * freight_rate
    bunker_cost = total_days * bunker_cons * bunker_price # Basit yakıt hesabı
    total_cost = port_costs + bunker_cost
    
    # 3. Kâr Hesapları
    net_profit = revenue - total_cost
    
    if total_days > 0:
        tce = net_profit / total_days # Time Charter Equivalent
    else:
        tce = 0
        
    # SONUÇLARI EKRANA ŞIK KUTULAR (METRIC) HALİNDE BASTIRMA
    st.metric(label="Toplam Gelir (Brüt)", value=f"${revenue:,.2f}")
    st.metric(label="Toplam Gider (Yakıt + Liman)", value=f"${total_cost:,.2f}")
    
    st.markdown("---")
    
    st.metric(label="Toplam Sefer Süresi", value=f"{total_days:,.1f} Gün")
    
    # Kâr durumuna göre renk değiştiren gösterim
    if net_profit > 0:
        st.success(f"💰 NET KÂR: ${net_profit:,.2f}")
    else:
        st.error(f"🚨 ZARAR: ${net_profit:,.2f}")
        
    st.info(f"📈 Günlük Kazanç (TCE): ${tce:,.2f} / Gün")