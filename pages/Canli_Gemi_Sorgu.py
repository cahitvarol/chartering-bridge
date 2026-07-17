import streamlit as st
import requests
import pandas as pd

# Sayfa yapılandırması
st.set_page_config(page_title="Gemi ve Rota Takibi", page_icon="🚢", layout="wide")
st.title("🚢 RapidAPI - Global Vessels Takibi")

# Giriş formu
with st.form("rapid_api_form"):
    api_key = st.text_input("X-RapidAPI-Key:", type="password")
    mmsi = st.text_input("Sorgulanacak MMSI Numarası:")
    submit = st.form_submit_button("Bilgileri Getir 🔍")

if submit:
    if not api_key or not mmsi:
        st.warning("Lütfen API Key ve MMSI numaralarını girin.")
    else:
        # API Başlıkları (RapidAPI'nin istediği format)
        headers = {
            "x-rapidapi-key": api_key.strip(),
            "x-rapidapi-host": "global-vessels.p.rapidapi.com",
            "Content-Type": "application/json"
        }

        # URL yapısı (CURL komutundaki adresle birebir aynı)
        detay_url = f"https://global-vessels.p.rapidapi.com/trade-service/marketplace/v1/vessels/{mmsi}"
        
        try:
            # İstek gönderiliyor
            detay_res = requests.get(detay_url, headers=headers)
            
            # Sonuç değerlendirme
            if detay_res.status_code == 200:
                data = detay_res.json()
                st.success("Gemi detayları başarıyla alındı.")
                
                # Özet metrikler
                col1, col2 = st.columns(2)
                col1.metric("Gemi Adı", data.get("name", "Bilinmiyor"))
                col2.metric("DWT", str(data.get("deadweight", "Bilgi yok")))
                
                # Tüm teknik detaylar (Genişletilebilir)
                with st.expander("Tüm Teknik Bilgiler"):
                    st.json(data)
            
            elif detay_res.status_code == 404:
                st.error("Gemi bulunamadı (404). Lütfen MMSI numarasını kontrol edin.")
            elif detay_res.status_code == 403:
                st.error("Erişim reddedildi (403). Lütfen API planınıza abone olduğunuzdan emin olun.")
            else:
                st.error(f"API Hatası (Kod: {detay_res.status_code})")
                st.write("Sunucudan gelen mesaj:", detay_res.text)
                
        except Exception as e:
            st.error(f"Sistem veya bağlantı hatası oluştu: {e}")
