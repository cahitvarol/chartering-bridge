import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Gemi ve Rota Takibi", page_icon="🚢", layout="wide")
st.title("🚢 RapidAPI - Global Vessels Takibi")

# RapidAPI bilgilerini güvenli almak için form
with st.form("rapid_api_form"):
    api_key = st.text_input("X-RapidAPI-Key:", type="password")
    mmsi = st.text_input("Sorgulanacak MMSI Numarası:")
    submit = st.form_submit_button("Bilgileri ve Rotayı Getir 🔍")

if submit:
   headers = {
        "x-rapidapi-key": api_key.strip(), # Baştaki/sondaki boşlukları temizler
        "x-rapidapi-host": "global-vessels.p.rapidapi.com"
    }

    # 1. Gemi Detaylarını Çek
    detay_url = f"https://global-vessels.p.rapidapi.com/v1/vessels/{mmsi}"
    
    # 2. Rota Verisini Çek
    rota_url = f"https://global-vessels.p.rapidapi.com/v1/vessels/{mmsi}/route"
    
    try:
        detay_res = requests.get(detay_url, headers=headers)
        
        if detay_res.status_code == 200:
            data = detay_res.json()
            st.success("Gemi detayları alındı.")
            
            # Teknik verileri göster
            col1, col2 = st.columns(2)
            col1.metric("Gemi Adı", data.get("name"))
            col2.metric("DWT", data.get("deadweight"))
            
            with st.expander("Tüm Teknik Bilgiler"):
                st.json(data)
                
            # Rota Sorgusu
            rota_res = requests.get(rota_url, headers=headers)
            if rota_res.status_code == 200:
                st.subheader("🗺️ Rota Bilgisi")
                st.json(rota_res.json()) # Rotayı burada haritaya dönüştürebiliriz
        else:
            st.error(f"API Hatası (Kod: {detay_res.status_code})")
            st.write("Sunucudan gelen mesaj:", detay_res.text) # Hatanın gerçek sebebini buraya yazacak
            
    except Exception as e:
        st.error(f"Bağlantı hatası: {e}")
