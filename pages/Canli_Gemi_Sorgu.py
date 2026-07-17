import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Gemi Sefer Ekranı", page_icon="🚢", layout="wide")
st.title("🚢 Operasyonel Gemi Bilgi Ekranı")

api_key = st.text_input("VesselAPI Anahtarınız:", type="password")
imo_input = st.text_input("Sorgulanacak Gemi IMO Numarası:", placeholder="Örn: 9704609")

if st.button("Seferi Analiz Et 🔍", use_container_width=True):
    if not api_key or not imo_input:
        st.error("Lütfen bilgileri girin.")
    else:
        headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
        params = {"filter.idType": "imo"}
        
        with st.spinner("Tüm gemi verileri çekiliyor..."):
            try:
                # 1. Statik Verileri Çek
                s_res = requests.get(f"https://api.vesselapi.com/v1/vessel/{imo_input}", headers=headers, params=params)
                # 2. Konum Verisini Çek
                p_res = requests.get(f"https://api.vesselapi.com/v1/vessel/{imo_input}/position", headers=headers, params=params)
                
                if s_res.status_code == 200:
                    static_data = s_res.json().get("vessel", {})
                    
                    # --- Gemi Özelliklerini Listele ---
                    st.subheader("📋 Gemi Teknik Özellikleri")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Gemi Adı", static_data.get("name"))
                    col2.metric("DWT", f"{static_data.get('deadweight_tonnage')} ton")
                    col3.metric("Yapım Yılı", static_data.get("year_built"))
                    
                    with st.expander("Tüm Teknik Detayları Gör"):
                        st.json(static_data)
                
                if p_res.status_code == 200:
                    pos_data = p_res.json()
                    lat = pos_data.get("latitude")
                    lon = pos_data.get("longitude")
                    
                    # --- Konum Bilgisi ve Hata Yönetimi ---
                    st.subheader("📍 Konum Bilgisi")
                    if lat and lon:
                        col1, col2 = st.columns(2)
                        col1.metric("Enlem", lat)
                        col2.metric("Boylam", lon)
                        df = pd.DataFrame({'lat': [float(lat)], 'lon': [float(lon)]})
                        st.map(df, zoom=6)
                    else:
                        st.warning("Bu gemi şu an karasal sinyal vermiyor (Uydu verisi gerebilir).")
                else:
                    st.error("Konum bilgisi şu an alınamıyor.")
                    
            except Exception as e:
                st.error(f"Sistem Hatası: {e}")
