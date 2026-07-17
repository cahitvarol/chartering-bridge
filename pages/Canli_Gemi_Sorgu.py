import streamlit as st
import asyncio
import websockets
import json
import time

st.set_page_config(page_title="Canlı Bölge Takibi", page_icon="📡", layout="wide")
st.title("📡 Ege, Marmara ve Karadeniz Canlı Gemi Radarı")

api_key = st.text_input("AISStream API Anahtarınız:", type="password")

# Haritadaki geniş alanı kapsayan koordinat kutusu
# [Lat_Alt, Lon_Sol], [Lat_Ust, Lon_Sag]
# Ege, Marmara ve Karadeniz batısını kapsar
bbox = [[[35.0, 25.0], [45.0, 30.0]]]

if st.button("Bölgeyi 5 Dakika İzle 🔍"):
    if not api_key:
        st.error("Lütfen API anahtarını girin.")
    else:
        st.info("İzleme başladı, veriler akıyor...")
        placeholder = st.empty()
        
        # 5 dakikalık (300 saniye) döngü
        end_time = time.time() + 300
        
        async def run_stream():
            async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
                subscribe_message = {
                    "APIKey": api_key,
                    "BoundingBoxes": bbox,
                    "FilterMessageTypes": ["PositionReport"]
                }
                # Bağlantı sonrası 3 saniye içinde abonelik mesajı gönderilmeli
                await websocket.send(json.dumps(subscribe_message))
                
                while time.time() < end_time:
                    try:
                        # Akıştan veri oku
                        message_json = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        message = json.loads(message_json)
                        
                        if message["MessageType"] == "PositionReport":
                            msg = message['Message']['PositionReport']
                            meta = message['MetaData']
                            
                            # Ekrana anlık veri bas
                            with placeholder.container():
                                st.write(f"**Gemi:** {meta.get('ShipName', 'Bilinmiyor')}")
                                st.write(f"**Koordinat:** {msg['Latitude']}, {msg['Longitude']}")
                                st.write(f"**Hız:** {msg['Sog']} kn")
                                st.divider()
                    except asyncio.TimeoutError:
                        continue
        
        # asyncio döngüsünü başlat
        asyncio.run(run_stream())
        st.success("5 dakikalık izleme süresi doldu.")
