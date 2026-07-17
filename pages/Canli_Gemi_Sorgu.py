import streamlit as st
import asyncio
import websockets
import json
import time

st.set_page_config(page_title="Canlı Gemi Sorgula", page_icon="🚢")
st.title("🚢 Canlı Gemi Bilgi İstasyonu")
st.write("Aisstream.io altyapısı ile geminin anlık konumunu yakalayın.")

api_key = st.text_input("Aisstream.io API Anahtarınız:", type="password")
imo_input = st.text_input("Sorgulanacak Gemi IMO Numarası:", placeholder="Örn: 9468372")
timeout_sure = st.slider("Dinleme Süresi (Saniye): Limandaki gemiler için süreyi uzun tutun.", min_value=15, max_value=300, value=60)

async def fetch_vessel_by_imo(api_token, target_imo, timeout_limit):
    uri = "wss://stream.aisstream.io/v0/stream"
    async with websockets.connect(uri) as websocket:
        subscribe_message = {
            "APIKey": api_token,
            "BoundingBoxes": [[[-90, -180], [90, 180]]] 
        }
        await websocket.send(json.dumps(subscribe_message))
        
        status_text = st.empty()
        status_text.info("Canlı yayın tüneli açıldı... Küresel veri akışından geminiz aranıyor (Maks. 15 saniye)...")
        
        start_time = time.time()
        timeout = timeout_limit
        result = loop.run_until_complete(fetch_vessel_by_imo(api_key, imo_input, timeout_sure))
        
        async for message_json in websocket:
            if time.time() - start_time > timeout:
                status_text.warning("Zaman aşımı! Gemi şu an sinyal göndermiyor olabilir.")
                return None
                
            message = json.loads(message_json)
            msg_imo = message.get("MetaData", {}).get("IMO")
            
            if msg_imo and str(msg_imo) == str(target_imo):
                status_text.success("Sinyal yakalandı!")
                return message
        return None

if st.button("Gemiyi Sorgula 🔍", use_container_width=True):
    if not api_key or not imo_input:
        st.error("Lütfen API anahtarı ve IMO numarasını eksiksiz girin.")
    else:
        with st.spinner("Aisstream tüneli dinleniyor..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(fetch_vessel_by_imo(api_key, imo_input))
                loop.close()
                
                if result:
                    metadata = result.get("MetaData", {})
                    pos_report = result.get("Message", {}).get("PositionReport", {})
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Gemi Adı", metadata.get("ShipName", "Bilinmiyor"))
                        st.metric("IMO No", metadata.get("IMO", "Bilinmiyor"))
                    with col2:
                        st.metric("Enlem (Lat)", pos_report.get("Latitude", "N/A"))
                        st.metric("Boylam (Lon)", pos_report.get("Longitude", "N/A"))
            except Exception as e:
                st.error(f"Hata: {str(e)}")
