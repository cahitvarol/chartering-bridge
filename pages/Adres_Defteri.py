import streamlit as st
import pandas as pd

st.title("📖 Adres Defteri")
st.write("Burası bizim ikinci uygulamamız! İleride Supabase'e bağlandığında broker ve müşteri iletişim bilgileri burada yer alacak.")

# Basit ve sahte bir tablo oluşturuyoruz
sahte_veri = {
    "Firma / Kişi": ["Oceangoing Shipping", "Ahmet Kaptan", "Global Chartering Ltd."],
    "Rol": ["Armatör", "Liman Kaptanı", "Broker"],
    "Telefon": ["+44 20 1234", "+90 532 123", "+49 40 9876"],
    "E-Posta": ["ops@oceangoing.com", "ahmet@port.com", "chartering@global.com"]
}

# Veriyi tablo (dataframe) formatına çevirip ekrana basıyoruz
df = pd.DataFrame(sahte_veri)
st.dataframe(df, use_container_width=True)