import streamlit as st
import asyncio
import websockets
import json
import time

st.set_page_config(page_title="MMSI Canlı Takip", page_icon="🚢", layout="wide")
st.title("🚢 MMSI ile Canlı Gemi Takip Radarı")

api_key = st.text_input("AISStream API Anahtarınız:", type="password")
mmsi_input = st.text_input("Takip Edilecek Gemi MMSI Numarası:")

# Marmara, Karadeniz, Ege ve Sicilya doğusunu kapsayan geniş alan
bbox = [[[33.0, 15.0], [46.0, 42.0]]]

if st.button("MMSI ile 5 Dakika İzle 🔍"):
    if not api_key or not mmsi_input:
        st.error("Lütfen API anahtarını ve MMSI numarasını girin.")
    else:
        st.info(f"{mmsi_input} MMSI numaralı gemi aranıyor...")
        placeholder = st.empty()
        end_time = time.time() + 300
        
        async def run_stream():
            async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
                # Sunucu seviyesinde MMSI filtrelemesi (daha performanslı)
                subscribe_message = {
                    "APIKey": api_key,
                    "BoundingBoxes": bbox,
                    "FiltersShipMMSI": [mmsi_input],  # API'nin doğrudan filtreleme özelliği
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
                            
                            with placeholder.container():
                                st.write(f"### 📍 Gemi Takip Ediliyor: {meta.get('ShipName', 'Bilinmiyor')}")
                                st.write(f"**Koordinat:** {msg['Latitude']}, {msg['Longitude']}")
                                st.write(f"**Hız:** {msg['Sog']} kn")
                                st.write(f"**MMSI:** {meta.get('MMSI')}")
                                st.divider()
                    except asyncio.TimeoutError:
                        continue
        
        asyncio.run(run_stream())
        st.success("5 dakikalık izleme süresi doldu.")
