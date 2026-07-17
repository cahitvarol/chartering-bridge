import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Gemi ve Rota Takibi", page_icon="🚢", layout="wide")
st.title("🚢 RapidAPI - Global Vessels Takibi")

with st.form("rapid_api_form"):
    api_key = st.text_input("X-RapidAPI-Key:", type="password")
    mmsi = st.text_input("Sorgulanacak MMSI Numarası:")
    submit = st.form_submit_button("Bilgileri ve Rotayı Getir 🔍")

if submit:
    if not api_key or not mmsi:
        st.warning("Lütfen API Key ve MMSI numaralarını girin.")
    else:
        headers = {
            "x-rapidapi-key": api_key.strip(),
            "x-rapidapi-host": "global-vessels.p.rapidapi.com"
        }

        detay_url = f"https://global-vessels.p.rapidapi.com/v1/vessels/{mmsi}"
        
        try:
            detay_res = requests.get(detay_url, headers=headers)
            
            if detay_res.status_code == 200:
                data = detay_res.json()
                st.success("Gemi detayları başarıyla alındı.")
                
                col1, col2 = st.columns(2)
                col1.metric("Gemi Adı", data.get("name", "Bilinmiyor"))
                col2.metric("DWT", str(data.get("deadweight", "Bilgi yok")))
                
                with st.expander("Tüm Teknik Bilgiler"):
                    st.json(data)
            else:
                st.error(f"API Hatası (Kod: {detay_res.status_code})")
                st.write("Sunucudan gelen mesaj:", detay_res.text)
                
        except Exception as e:
            st.error(f"Bağlantı hatası: {e}")
