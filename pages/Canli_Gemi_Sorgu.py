import streamlit as st
import requests
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Gemi Detay Sorgulama", page_icon="🚢")
st.title("🚢 Gemi Bilgi İstasyonu (VesselAPI)")
st.write("VesselAPI altyapısı ile gemiye ait boyut, tip ve (eğer destekleniyorsa) konum verilerini çekin.")

# Kullanıcı Girişleri
api_key = st.text_input("VesselAPI Anahtarınız (Bearer Token):", type="password")
imo_input = st.text_input("Sorgulanacak Gemi IMO Numarası:", placeholder="Örn: 9468372")

if st.button("Verileri Çek 🔍", use_container_width=True):
    if not api_key or not imo_input:
        st.error("Lütfen API Key ve IMO numarası alanlarını eksiksiz doldurun.")
    else:
        with st.spinner("VesselAPI sunucusuna bağlanılıyor..."):
            try:
                # Bulduğun yeni uç nokta (Endpoint) yapısı
                api_url = f"https://api.vesselapi.com/v1/vessel/{imo_input}" 
                
                # Dokümantasyondaki 'filter.idType' parametresi
                querystring = {"filter.idType": "imo"}
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Accept": "application/json"
                }
                
                response = requests.get(api_url, headers=headers, params=querystring)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Veri başarıyla çekildi!")
                    
                    # Gelen tüm veriyi ekrana basıyoruz ki içinde neler olduğunu görelim
                    st.subheader("📦 Sunucudan Gelen JSON Paketi")
                    st.json(data)
                        
                else:
                    st.error(f"API Hatası: {response.status_code}.")
                    with st.expander("Hata Detayı"):
                        st.json(response.json())
                        
            except Exception as e:
                st.error(f"Sistem Hatası: {str(e)}")
