import streamlit as st
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Gemi Sorgula", page_icon="🚢")
st.title("🚢 Gemi Bilgi İstasyonu")
st.write("REST API altyapısı ile geminin bilinen son konumunu ve detaylarını anında getirin.")

# Operasyonel Not
st.info("💡 Operasyonel İpucu: Aqaba - Gemlik hattındaki silika kumu taşıması gibi kiralama operasyonlarınızda, geminin en güncel pozisyonunu anında buradan teyit edebilirsiniz.")

# Kullanıcı Girişleri
api_key = st.text_input("API Anahtarınız (Örn: Datalastic vb.):", type="password")
imo_input = st.text_input("Sorgulanacak Gemi IMO Numarası:", placeholder="Örn: 9468372")

if st.button("Gemiyi Sorgula 🔍", use_container_width=True):
    if not api_key or not imo_input:
        st.error("Lütfen API anahtarı ve IMO numarasını eksiksiz girin.")
    else:
        with st.spinner("Sunucuya bağlanılıyor ve veriler çekiliyor..."):
            try:
                # Örnek bir REST API uç noktası (Endpoint). 
                # Hangi API sağlayıcısını kullanırsan URL'yi ona göre güncellemelisin.
                api_url = f"https://api.datalastic.com/api/v0/vessel_info?api-key={api_key}&imo={imo_input}"
                
                # Soru sorulur ve cevap anında alınır (Request-Response)
                response = requests.get(api_url)
                
                # Gelen cevap başarılı mı kontrol edilir (HTTP 200 OK)
                if response.status_code == 200:
                    data = response.json()
                    
                    # API'nin yapısına göre gelen JSON verisini ayrıştırma
                    # (Bu kısım kullanılan API'nin dokümantasyonuna göre değişiklik gösterebilir)
                    if "data" in data and len(data["data"]) > 0:
                        vessel_data = data["data"][0]
                        
                        st.success("Veri başarıyla çekildi!")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Gemi Adı", vessel_data.get("name", "Bilinmiyor"))
                            st.metric("IMO No", vessel_data.get("imo", "Bilinmiyor"))
                            st.metric("DWT", vessel_data.get("dwt", "N/A"))
                        with col2:
                            st.metric("Enlem (Lat)", vessel_data.get("lat", "N/A"))
                            st.metric("Boylam (Lon)", vessel_data.get("lon", "N/A"))
                            st.metric("Son Güncelleme", vessel_data.get("last_position_epoch", "N/A"))
                    else:
                        st.warning("Girdiğiniz IMO numarasına ait kayıt bulunamadı.")
                else:
                    st.error(f"API Hatası: Sunucu {response.status_code} kodu ile yanıt verdi.")
                    
            except Exception as e:
                st.error(f"Bağlantı hatası oluştu: {str(e)}")
