import streamlit as st
import asyncio
import websockets
import json
import time

st.set_page_config(page_title="Canlı Gemi Takibi", page_icon="🚢", layout="wide")
st.title("🚢 Belirli Gemi Canlı Takip Radarı")

api_key = st.text_input("AISStream API Anahtarınız:", type="password")
imo_input = st.text_input("Takip Edilecek Gemi IMO Numarası:")

# Marmara, Karadeniz, Ege ve Sicilya doğusunu kapsayan geniş alan
# [Lat_Alt, Lon_Sol], [Lat_Ust, Lon_Sag]
bbox = [[[33.0, 15.0], [46.0, 42.0]]]

if st.button("Gemiyi 5 Dakika İzle 🔍"):
    if not api_key or not imo_input:
        st.error("Lütfen API anahtarını ve IMO numarasını girin.")
    else:
        st.info(f"{imo_input} IMO numaralı gemi aranıyor...")
        placeholder = st.empty()
        end_time = time.time() + 300
        
        async def run_stream():
            async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
                # Gemi özelinde filtreleme (MMSI üzerinden çalışır, IMO doğrudan desteklenmiyorsa genel filtreleme yapılır)
                subscribe_message = {
                    "APIKey": api_key,
                    "BoundingBoxes": bbox,
                    "FilterMessageTypes": ["PositionReport"]
                }
                await websocket.send(json.dumps(subscribe_message))
                
                while time.time() < end_time:
                    try:
                        message_json = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        message = json.loads(message_json)
                        
                        if message["MessageType"] == "PositionReport":
                            msg = message['Message']['PositionReport']
                            meta = message['MetaData']
                            
                            # IMO ile eşleşmeyi kontrol et
                            if str(meta.get('ImoNumber', '')) == str(imo_input):
                                with placeholder.container():
                                    st.write(f"### 📍 Gemi Takip Ediliyor: {meta.get('ShipName', 'Bilinmiyor')}")
                                    st.write(f"**Koordinat:** {msg['Latitude']}, {msg['Longitude']}")
                                    st.write(f"**Hız:** {msg['Sog']} kn")
                                    st.divider()
                    except asyncio.TimeoutError:
                        continue
        
        asyncio.run(run_stream())
        st.success("5 dakikalık izleme süresi doldu.")
