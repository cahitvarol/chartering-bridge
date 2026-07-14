import streamlit as st
import pandas as pd
from datetime import datetime

# Sayfa Yapılandırması
st.set_page_config(page_title="Chartering Bridge", layout="wide")

# CSS ile Excel benzeri bir tablo görünümü sağlıyoruz
st.markdown("""
    <style>
    .stNumberInput label { font-size: 12px !important; color: #888 !important; }
    .stTextInput label { font-size: 12px !important; color: #888 !important; }
    .main-header { font-size: 24px; font-weight: bold; margin-bottom: 20px; border-bottom: 2px solid #f0f2f6; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">1 - General Information</p>', unsafe_allow_html=True)

# ----------------- ANA DÜZEN -----------------
# Ekranı iki ana sütuna bölüyoruz: Sol (Voyage Bilgileri), Sağ (Bunker Tablosu ve Buton)
col_left, col_right, col_button = st.columns([1.2, 3, 0.8])

with col_left:
    st.write("") # Boşluk
    # Voyage ID No
    v_id_col1, v_id_col2 = st.columns([1, 1.5])
    with v_id_col1: st.info("Voyage ID No")
    with v_id_col2: voyage_id = st.text_input("", value="2026-001", label_visibility="collapsed")
    
    # Date
    date_col1, date_col2 = st.columns([1, 1.5])
    with date_col1: st.info("Date")
    with date_col2: voyage_date = st.date_input("", value=datetime(2026, 7, 14), label_visibility="collapsed")
    
    # Currency Rate
    curr_col1, curr_col2 = st.columns([1, 1.5])
    with curr_col1: st.info("Currency Rate")
    with curr_col2: currency_rate = st.number_input("", value=1.050, format="%.3f", label_visibility="collapsed")

with col_right:
    # Bunker Tablosu Başlıkları
    h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns([0.4, 1.2, 1, 1, 1, 1])
    h_col2.markdown("**Bunker Prices**")
    h_col3.markdown("**MGO %0,10**")
    h_col4.markdown("**ULSFO %0,10**")
    h_col5.markdown("**VLSFO %0,50**")
    h_col6.markdown("**IFO 380 %3,50**")
    
    # Session State: Fiyatları hafızada tutmak için (Get Prices butonuna basınca değişecek)
    if 'bunker_data' not in st.session_state:
        st.session_state.bunker_data = {
            'Istanbul': [1050.0, 820.0, 640.0, 580.0],
            'Gibraltar': [1020.0, 790.0, 610.0, 550.0],
            '3rd Port': [0.0, 0.0, 0.0, 0.0],
            '4th Port': [0.0, 0.0, 0.0, 0.0]
        }

    # Liman Listesi
    ports = ["Istanbul", "Gibraltar", "3rd Port", "4th Port"]
    
    # Radyo Butonu (Hangi liman seçili?)
    # Streamlit'te radyo butonu dikey bir listedir. 
    # Tablonun soluna hizalamak için boşluklarla simüle ediyoruz.
    selected_port = st.radio("Seç", ports, label_visibility="collapsed")

    # Satırları oluşturma
    for port in ports:
        r_col1, r_col2, r_col3, r_col4, r_col5, r_col6 = st.columns([0.4, 1.2, 1, 1, 1, 1])
        
        # Seçili olan limanı görsel olarak belirtmek için arka planı farklı hissettirebiliriz
        is_selected = "✅" if selected_port == port else "⬜"
        r_col1.write(is_selected)
        
        r_col2.info(port)
        
        # Fiyat girişleri
        p1 = r_col3.number_input(f"MGO_{port}", value=st.session_state.bunker_data[port][0], label_visibility="collapsed")
        p2 = r_col4.number_input(f"ULSFO_{port}", value=st.session_state.bunker_data[port][1], label_visibility="collapsed")
        p3 = r_col5.number_input(f"VLSFO_{port}", value=st.session_state.bunker_data[port][2], label_visibility="collapsed")
        p4 = r_col6.number_input(f"IFO_{port}", value=st.session_state.bunker_data[port][3], label_visibility="collapsed")
        
        # Güncel değerleri kaydet
        st.session_state.bunker_data[port] = [p1, p2, p3, p4]

with col_button:
    st.write("") # Üstten hizalama için boşluk
    st.write("")
    if st.button("Get Bunker Prices", type="primary", use_container_width=True):
        # Bu kısım Step 2'de API'ye bağlanacak
        st.toast("Güncel fiyatlar çekiliyor...", icon="⛽")
        # Örnek güncelleme:
        st.session_state.bunker_data['Istanbul'] = [1090.0, 850.0, 680.0, 610.0]
        st.rerun()

# ----------------- ALT BİLGİ -----------------
st.divider()
st.caption(f"Aktif Kullanılan Yakıt Fiyatı: {selected_port} verileri baz alınacaktır.")

**Bu Adımda Ne Yaptık?**
1.  **Görsel Hizalama:** "Voyage ID No" gibi yazıları gri kutuların yanına getirdik.
2.  **Yakıt Matrisi:** Excel'deki gibi 4 liman ve 4 yakıt tipini içeren şık bir tablo kurduk.
3.  **Liman Seçimi:** Satırların solundaki "⬜/✅" işaretleri ve radyo butonu ile hangi liman fiyatının hesaplamaya gireceğini belirledik.
4.  **Hafıza Yönetimi:** `st.session_state` kullanarak fiyatların sayfa yenilendiğinde kaybolmamasını sağladık.

Uygulamanın görüntüsü istediğiniz gibiyse, Bölüm 2 için Excel görselini bekliyorum!
