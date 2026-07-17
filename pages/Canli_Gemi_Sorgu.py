import streamlit as st
import requests

st.set_page_config(page_title="Gemi Sorgula", page_icon="🚢")
st.title("🚢 Gemi Bilgi İstasyonu (RapidAPI)")
st.write("RapidAPI altyapısı ile gemi bilgilerini anında sorgulayın.")

# Kullanıcı Girişleri
col1, col2 = st.columns(2)
with col1:
    rapid_key = st.text_input("X-RapidAPI-Key:", type="password", help="RapidAPI üzerinden aldığınız şifre")
with col2:
    rapid_host = st.text_input("X-RapidAPI-Host:", placeholder="Örn: ship-data.p.rapidapi.com")

imo_input = st.text_input("Sorgulanacak Gemi IMO Numarası:", placeholder="Örn: 9468372")

if st.button("Gemiyi Sorgula 🔍", use_container_width=True):
    if not rapid_key or not rapid_host or not imo_input:
        st.error("Lütfen API Key, Host ve IMO numarası alanlarını eksiksiz doldurun.")
    else:
        with st.spinner("RapidAPI sunucusuna bağlanılıyor..."):
            try:
                # DİKKAT: Aşağıdaki URL, seçtiğin API'ye göre değişiklik gösterecektir.
                # Seçtiğin servisin Endpoint URL'sini buraya yapıştırmalısın.
                api_url = "https://" + rapid_host + "/vessel"
                
                querystring = {"imo": imo_input}
                
                # RapidAPI güvenlik başlıkları
                headers = {
                    "X-RapidAPI-Key": rapid_key,
                    "X-RapidAPI-Host": rapid_host
                }
                
                response = requests.get(api_url, headers=headers, params=querystring)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Veri başarıyla çekildi!")
                    
                    # Not: Gelen verinin yapısı (JSON etiketleri) API'den API'ye değişir.
                    # Seçtiğin servise göre aşağıdaki 'name', 'dwt' gibi kelimeleri güncellemen gerekebilir.
                    with st.expander("Gelen Ham Veriyi İncele (JSON Etiketleri İçin)", expanded=True):
                        st.json(data)
                        
                else:
                    st.error(f"API Hatası: Sunucu {response.status_code} kodu ile yanıt verdi. Limitlerinizi veya API anahtarınızı kontrol edin.")
                    
            except Exception as e:
                st.error(f"Bağlantı hatası oluştu: {str(e)}")
