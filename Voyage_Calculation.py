import streamlit as st
import pandas as pd
from datetime import datetime, date
from supabase import create_client, Client
import html 

# =====================================================================
# SUPABASE BAĞLANTI AYARLARI
# =====================================================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_connection():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return None

supabase = init_connection()

# =====================================================================
# SAYI FORMATLAMA FONKSİYONU 
# =====================================================================
def format_tr(val, is_int=False):
    if pd.isna(val): return "0"
    if is_int:
        return "{:,.0f}".format(val).replace(",", ".")
    else:
        return "{:,.2f}".format(val).replace(",", "X").replace(".", ",").replace("X", ".")

# Sayfa Yapılandırması
st.set_page_config(page_title="Chartering Bridge", layout="wide")

st.markdown("""
    <style>
    .stNumberInput label { font-size: 13px !important; color: black !important; font-weight: bold !important; }
    .stTextInput label { font-size: 13px !important; color: black !important; font-weight: bold !important; }
    .stSelectbox label { font-size: 13px !important; color: black !important; font-weight: bold !important; }
    .main-header { font-size: 22px; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #f0f2f6; padding-top: 20px;}
    .align-text { margin-top: 8px; font-weight: bold; font-size: 14px; color: black; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; font-weight: bold; font-size: 42px;'>VOYAGE CALCULATION</h1>", unsafe_allow_html=True)


# =====================================================================
# VESSEL DATA VE VOYAGE LOAD (GERİ ÇAĞIRMA) FONKSİYONLARI
# =====================================================================
vessel_keys = {
    "v_imo": "", "v_name": "", "v_type": "", "v_flag": "", "v_class": "", "v_built": "",
    "v_dwt": 0.0, "v_dwcc": 0.0, "v_grain": 0.0, "v_bale": 0.0,
    "v_gt": 0.0, "v_nt": 0.0, "v_loa": 0.0, "v_beam": 0.0
}
for k, v in vessel_keys.items():
    if k not in st.session_state:
        st.session_state[k] = v

def reset_vessel_data():
    for key in vessel_keys.keys():
        if key != "v_imo":
            st.session_state[key] = vessel_keys[key]

def fetch_vessel_data():
    imo_val = str(st.session_state.v_imo).strip()
    if not imo_val:
        reset_vessel_data()
        return
    if supabase is None:
        st.error("Supabase bağlantısı kurulamadı.")
        return
    try:
        if not imo_val.isdigit():
            reset_vessel_data()
            st.toast("IMO numarası sadece rakamlardan oluşmalıdır.", icon="⚠️")
            return
        imo_int = int(imo_val)
        response = supabase.table("vesseldatabase").select("*").eq("imo_number", imo_int).execute()
        data = response.data
        if data and len(data) > 0:
            v = data[0]
            st.session_state.v_name = str(v.get("name_of_ship", ""))
            st.session_state.v_type = str(v.get("type_of_ship", ""))
            st.session_state.v_flag = str(v.get("flag", ""))
            st.session_state.v_class = str(v.get("class", ""))
            st.session_state.v_built = str(v.get("year_of_build", ""))
            st.session_state.v_dwt = float(v.get("dwt", 0.0) or 0.0)
            st.session_state.v_dwcc = float(v.get("dwcc", 0.0) or 0.0)
            st.session_state.v_grain = float(v.get("grain_cap_-cuft-", 0.0) or 0.0)
            st.session_state.v_bale = float(v.get("bale_cap_-cuft-", 0.0) or 0.0)
            st.session_state.v_gt = float(v.get("gross_tonnage", 0.0) or 0.0)
            st.session_state.v_nt = float(v.get("net_tonnage", 0.0) or 0.0)
            st.session_state.v_loa = float(v.get("loa", 0.0) or 0.0)
            st.session_state.v_beam = float(v.get("beam", 0.0) or 0.0)
            st.toast(f"Gemi veritabanından çekildi: {st.session_state.v_name}", icon="✅")
        else:
            reset_vessel_data()
            st.toast("Veritabanında bu IMO numarasına ait gemi bulunamadı.", icon="⚠️")
    except Exception as e:
        reset_vessel_data()
        st.error(f"Sorgu hatası: {e}")

# Veritabanındaki eski seferleri getiren fonksiyon
def get_saved_voyages():
    if supabase:
        try:
            res = supabase.table("voyage_calculations").select("voyage_id").order("created_at", desc=True).execute()
            return [r["voyage_id"] for r in res.data]
        except:
            return []
    return []

# Seçilen seferi hafızaya yükleyen fonksiyon
def load_voyage_data(vid):
    if not supabase: return
    try:
        res = supabase.table("voyage_calculations").select("*").eq("voyage_id", vid).execute()
        if res.data and len(res.data) > 0:
            row = res.data[0]
            all_data = row.get("all_data", {})
            
            # Gemi Verilerini Yükle
            vessel_data = all_data.get("vessel", {})
            for k, v in vessel_data.items():
                st.session_state[k] = v
            
            # Form Inputlarını Yükle
            inputs = all_data.get("inputs", {})
            if "voyage_date" in inputs:
                try:
                    st.session_state["voyage_date_input"] = datetime.strptime(inputs["voyage_date"], "%Y-%m-%d").date()
                except: pass
            if "laycan_date" in inputs:
                try:
                    st.session_state["laycan_date_input"] = datetime.strptime(inputs["laycan_date"], "%Y-%m-%d").date()
                except: pass
                
            text_num_keys = ["currency_rate", "account", "cargo_item", "stowage_factor", "quantity", 
                             "freight_term", "terms", "gear", "freight", "demurrage", "despatch", 
                             "freight_tax", "extra_insurance", "cargo_survey", "strait_canal", 
                             "add_comm", "broker_comm", "other_exp"]
            for k in text_num_keys:
                if k in inputs:
                    st.session_state[f"{k}_input"] = inputs[k]
                    
            st.session_state["voyage_id_input"] = vid
            
            # Tablo (Dataframe) Verilerini Yükle
            dfs = all_data.get("dataframes", {})
            if "bunker_base" in dfs: st.session_state.bunker_base = pd.DataFrame(dfs["bunker_base"])
            if "sea_base" in dfs: st.session_state.sea_base = pd.DataFrame(dfs["sea_base"])
            if "port_base" in dfs: st.session_state.port_base = pd.DataFrame(dfs["port_base"])
            if "port_rotation_base" in dfs: st.session_state.port_rotation_base = pd.DataFrame(dfs["port_rotation_base"])
            if "port_charges_base" in dfs: st.session_state.port_charges_base = pd.DataFrame(dfs["port_charges_base"])
            if "ld_details_base" in dfs: st.session_state.ld_details_base = pd.DataFrame(dfs["ld_details_base"])
            
            # Editör widget hafızalarını temizleyip tabloların yenilenmesini sağla
            for key in ["bunker_editor_widget", "sea_editor_widget", "port_editor_widget", "rotation_editor_widget", "charges_editor_widget", "ld_editor_widget"]:
                if key in st.session_state:
                    del st.session_state[key]
                    
            st.session_state.calc_done = False
            st.toast("Geçmiş sefer başarıyla yüklendi!", icon="✅")
    except Exception as e:
        st.error(f"Yükleme hatası: {e}")


# =====================================================================
# BÖLÜM 1: GENERAL INFORMATION
# =====================================================================
st.markdown('<p class="main-header">1 - General Information</p>', unsafe_allow_html=True)

col_left, col_right = st.columns([1.5, 3])

with col_left:
    st.write("") 
    
    v_id_col1, v_id_col2 = st.columns([1, 1.5])
    with v_id_col1: st.markdown("<div class='align-text'>Voyage ID No</div>", unsafe_allow_html=True)
    with v_id_col2: voyage_id = st.text_input("", key="voyage_id_input", label_visibility="collapsed")
    
    date_col1, date_col2 = st.columns([1, 1.5])
    with date_col1: st.markdown("<div class='align-text'>Date</div>", unsafe_allow_html=True)
    with date_col2: voyage_date = st.date_input("", value=date.today(), key="voyage_date_input", format="DD.MM.YYYY", label_visibility="collapsed")
    
    curr_col1, curr_col2 = st.columns([1, 1.5])
    with curr_col1: st.markdown("<div class='align-text'>Currency Rate</div>", unsafe_allow_html=True)
    with curr_col2: currency_rate = st.number_input("", value=0.0, format="%.3f", key="currency_rate_input", label_visibility="collapsed")

    # LOAD VOYAGE ALANI
    st.write("---")
    st.markdown("<div class='align-text' style='margin-bottom: 5px;'>Geçmiş Seferleri Yükle</div>", unsafe_allow_html=True)
    saved_voyages = get_saved_voyages()
    selected_voy = st.selectbox("Load Voyage", [""] + saved_voyages, label_visibility="collapsed")
    if st.button("📂 Eski Seferi Getir", use_container_width=True):
        if selected_voy:
            load_voyage_data(selected_voy)
            st.rerun()
        else:
            st.warning("Lütfen listeden bir sefer seçin.")

with col_right:
    st.markdown("**Bunker Prices**")
    
    if 'bunker_base' not in st.session_state:
        st.session_state.bunker_base = pd.DataFrame({
            "Seç": [True, False, False, False],
            "Liman": ["Istanbul", "Gibraltar", "3rd Port", "4th Port"],
            "MGO %0,1": [1400.0, 1020.0, 0.0, 0.0],
            "ULSFO %0,1": [900.0, 790.0, 0.0, 0.0],
            "VLSFO %0,5": [897.0, 610.0, 0.0, 0.0],
            "IFO380 %3,5": [720.0, 550.0, 0.0, 0.0]
        })

    edited_df = st.data_editor(
        st.session_state.bunker_base,
        column_config={
            "Seç": st.column_config.CheckboxColumn("Seç", default=False, width="small"),
            "Liman": st.column_config.TextColumn("Liman", width="medium"),
            "MGO %0,1": st.column_config.NumberColumn("MGO %0,1", format="%.2f"),
            "ULSFO %0,1": st.column_config.NumberColumn("ULSFO %0,1", format="%.2f"),
            "VLSFO %0,5": st.column_config.NumberColumn("VLSFO %0,5", format="%.2f"),
            "IFO380 %3,5": st.column_config.NumberColumn("IFO380 %3,5", format="%.2f"),
        },
        hide_index=True,
        use_container_width=True,
        key="bunker_editor_widget"
    )
    
    prev_selections = st.session_state.bunker_base["Seç"].tolist()
    curr_selections = edited_df["Seç"].tolist()
    changed_to_true = [i for i, (p, c) in enumerate(zip(prev_selections, curr_selections)) if not p and c]
    
    if changed_to_true:
        edited_df["Seç"] = False
        edited_df.loc[changed_to_true[0], "Seç"] = True
        st.session_state.bunker_base = edited_df 
        st.rerun() 

    st.session_state.bunker_df = edited_df

secili_satirlar = st.session_state.bunker_df[st.session_state.bunker_df["Seç"] == True]
if not secili_satirlar.empty:
    aktif_liman = secili_satirlar.iloc[0]["Liman"]
    st.caption(f"Aktif Liman: **{aktif_liman}**")

# =====================================================================
# BÖLÜM 2: VESSEL DETAILS
# =====================================================================
st.markdown('<p class="main-header">2 - Vessel Details</p>', unsafe_allow_html=True)

v1, v2, v3, v4, v5, v6 = st.columns(6)
with v1:
    imo = st.text_input("IMO", key="v_imo", on_change=fetch_vessel_data)
    name = st.text_input("Name", key="v_name")
    v_type = st.text_input("Type", key="v_type")
with v2:
    flag = st.text_input("Flag", key="v_flag")
    v_class = st.text_input("Class", key="v_class")
    built = st.text_input("Built", key="v_built")
with v3:
    dwt = st.number_input("DWT", key="v_dwt", format="%.2f")
    dwcc = st.number_input("DWCC", key="v_dwcc", format="%.2f")
with v4:
    grain = st.number_input("Grain Cap (cuft)", key="v_grain", format="%.0f")
    bale = st.number_input("Bale Cap (cuft)", key="v_bale", format="%.0f")
with v5:
    gt = st.number_input("GT", key="v_gt", format="%.0f")
    nt = st.number_input("NT", key="v_nt", format="%.0f")
with v6:
    loa = st.number_input("LOA", key="v_loa", format="%.2f")
    beam = st.number_input("Beam", key="v_beam", format="%.2f")

st.write("") 
st.markdown("**Speed & Consumption**")
sc1, sc2 = st.columns([1.2, 1]) 

yakit_tipleri = ["MGO %0,1", "ULSFO %0,1", "VLSFO %0,5", "IFO380 %3,5"]

with sc1:
    if 'sea_base' not in st.session_state:
        st.session_state.sea_base = pd.DataFrame({
            "At Sea": ["Ballast", "Laden"],
            "Speed": [0.0, 0.0],
            "Cons": [0.0, 0.0],
            "Select": ["MGO %0,1", "MGO %0,1"]
        })
    current_sea = st.data_editor(
        st.session_state.sea_base, 
        column_config={
            "At Sea": st.column_config.TextColumn("At Sea"),
            "Speed": st.column_config.NumberColumn("Speed", format="%.2f knot"),
            "Cons": st.column_config.NumberColumn("Cons", format="%.2f mts"),
            "Select": st.column_config.SelectboxColumn("Select", options=yakit_tipleri)
        },
        hide_index=True, use_container_width=True, key="sea_editor_widget"
    )
    st.session_state.sea_df = current_sea

with sc2:
    if 'port_base' not in st.session_state:
        st.session_state.port_base = pd.DataFrame({
            "At Port": ["Idle", "Work"],
            "Cons": [0.0, 0.0],
            "Select": ["MGO %0,1", "MGO %0,1"]
        })
    current_port = st.data_editor(
        st.session_state.port_base, 
        column_config={
            "At Port": st.column_config.TextColumn("At Port"),
            "Cons": st.column_config.NumberColumn("Cons", format="%.2f mts"),
            "Select": st.column_config.SelectboxColumn("Select", options=yakit_tipleri)
        },
        hide_index=True, use_container_width=True, key="port_editor_widget"
    )
    st.session_state.port_df = current_port

# =====================================================================
# BÖLÜM 3: C/P DETAILS
# =====================================================================
st.markdown('<p class="main-header">3 - C/P Details</p>', unsafe_allow_html=True)

cp1, cp2, cp3, cp4, cp5 = st.columns(5)
with cp1:
    account = st.text_input("Account", key="account_input")
    cargo_item = st.text_input("Cargo Item", key="cargo_item_input")
    stowage_factor = st.number_input("Stowage Factor (cuft/ton)", value=0.0, format="%.2f", key="stowage_factor_input")
    quantity = st.number_input("Quantity", value=0.0, format="%.2f", key="quantity_input")
with cp2:
    freight_term = st.selectbox("Freight Term", ["pmt", "lumpsum"], key="freight_term_input")
    terms = st.selectbox("Terms", ["FIO", "FIOS", "FIOST", "LIFO", "FILO", "LILO"], index=2, key="terms_input")
    gear = st.selectbox("Gear", ["Gearless", "Geared"], key="gear_input")
    laycan_date = st.date_input("Laycan", value=date.today(), format="DD.MM.YYYY", key="laycan_date_input")
    st.markdown(f"<span style='color:#c5a059; font-size:14px; font-weight:bold;'>{laycan_date.strftime('%d %B %Y, %A')}</span>", unsafe_allow_html=True)
with cp3:
    freight = st.number_input("Freight", value=0.0, format="%.2f", key="freight_input")
    demurrage = st.number_input("Demurrage", value=0.0, format="%.2f", key="demurrage_input")
    despatch = st.number_input("Despatch", value=0.0, format="%.2f", key="despatch_input")
    freight_tax = st.number_input("Freight Tax", value=0.0, format="%.2f", key="freight_tax_input")
with cp4:
    extra_insurance = st.number_input("Extra Insurance", value=0.0, format="%.2f", key="extra_insurance_input")
    cargo_survey = st.number_input("Cargo Survey", value=0.0, format="%.2f", key="cargo_survey_input")
    strait_canal = st.number_input("Strait / Canal Passage Expenses", value=0.0, format="%.2f", key="strait_canal_input")
with cp5:
    add_comm = st.number_input("Address Commission (%)", value=0.0, step=0.25, format="%.2f", key="add_comm_input")
    broker_comm = st.number_input("Brokerage Commission (%)", value=0.0, step=0.25, format="%.2f", key="broker_comm_input")
    other_exp = st.number_input("Other", value=0.0, format="%.2f", key="other_exp_input")

st.write("")

# ----- TABLO 1: PORT ROTATION -----
st.markdown("**Port Rotation**")

if 'port_rotation_base' not in st.session_state:
    st.session_state.port_rotation_base = pd.DataFrame({
        "Port Type": ["Ballast Port"],
        "Port Name": [""],
        "Distance": [0.0],
        "Weather Margin (%)": [5]
    })

current_rotation = st.data_editor(
    st.session_state.port_rotation_base,
    key="rotation_editor_widget",
    column_config={
        "Port Type": st.column_config.SelectboxColumn("**Port Type**", options=["Ballast Port", "Load Port", "Discharge Port", "Bunker Port", "Return Ballast"], required=True),
        "Port Name": st.column_config.TextColumn("**Port Name**"),
        "Distance": st.column_config.NumberColumn("**Distance**", help="Geminin sefer başlangıç noktasında olduğunu belirtmek için ilk mesafeyi 0 bırakın. Bu bacak hesaplamada görünmeyecektir."), 
        "Weather Margin (%)": st.column_config.NumberColumn("**Weather Margin (%)**", format="%d %%", step=1)
    },
    hide_index=True, 
    num_rows="dynamic", 
    use_container_width=True
)

st.session_state.port_rotation_df = current_rotation

# ----- GET DISTANCE BUTONU VE VERİ AKTARIMI -----
_, btn_col = st.columns([5, 1])
with btn_col:
    if st.button("Get Distance", type="primary", use_container_width=True):
        st.toast("Mesafeler çekiliyor ve tablolar güncelleniyor...", icon="🔄")
        
        df = st.session_state.port_rotation_df 
        filtered_df = df[df["Port Type"].isin(["Load Port", "Discharge Port"])]
        
        if not filtered_df.empty:
            st.session_state.port_charges_base = pd.DataFrame({
                "Port Type": filtered_df["Port Type"].tolist(),
                "Port Name": filtered_df["Port Name"].tolist(),
                "PDA": [0.0] * len(filtered_df),
                "Liner Expenses": [0.0] * len(filtered_df)
            })
            st.session_state.ld_details_base = pd.DataFrame({
                "Port Type": filtered_df["Port Type"].tolist(),
                "Port Name": filtered_df["Port Name"].tolist(),
                "Rate": [0.0] * len(filtered_df),
                "Unit": ["mts/day"] * len(filtered_df),
                "L/D Terms": ["SSHEX"] * len(filtered_df),
                "Extra Days": [0.0] * len(filtered_df)
            })
        else:
            st.session_state.port_charges_base = pd.DataFrame({"Port Type": [""], "Port Name": [""], "PDA": [0.0], "Liner Expenses": [0.0]})
            st.session_state.ld_details_base = pd.DataFrame({"Port Type": [""], "Port Name": [""], "Rate": [0.0], "Unit": ["mts/day"], "L/D Terms": ["SSHEX"], "Extra Days": [0.0]})
        
        if "charges_editor_widget" in st.session_state:
            del st.session_state["charges_editor_widget"]
        if "ld_editor_widget" in st.session_state:
            del st.session_state["ld_editor_widget"]
            
        st.rerun()

st.write("")
col_t2, col_t3 = st.columns([1.2, 1.8]) 

# ----- TABLO 2: PORT CHARGES -----
with col_t2:
    st.markdown("**Port Charges**")
    if 'port_charges_base' not in st.session_state:
        st.session_state.port_charges_base = pd.DataFrame({"Port Type": [""], "Port Name": [""], "PDA": [0.0], "Liner Expenses": [0.0]})
    
    current_charges = st.data_editor(
        st.session_state.port_charges_base,
        key="charges_editor_widget",
        column_config={
            "Port Type": st.column_config.TextColumn("**Port Type**", disabled=True),
            "Port Name": st.column_config.TextColumn("**Port Name**"),
            "PDA": st.column_config.NumberColumn("**PDA**", format="%.2f"),
            "Liner Expenses": st.column_config.NumberColumn("**Liner Expenses**", format="%.2f")
        },
        hide_index=True, num_rows="dynamic", use_container_width=True
    )
    st.session_state.port_charges_df = current_charges

# ----- TABLO 3: L/D DETAILS -----
with col_t3:
    st.markdown("**L/D Details**")
    if 'ld_details_base' not in st.session_state:
        st.session_state.ld_details_base = pd.DataFrame({
            "Port Type": [""], "Port Name": [""], "Rate": [0.0], "Unit": ["mts/day"], "L/D Terms": ["SSHEX"], "Extra Days": [0.0]
        })
    
    current_ld = st.data_editor(
        st.session_state.ld_details_base,
        key="ld_editor_widget",
        column_config={
            "Port Type": st.column_config.TextColumn("**Port Type**", disabled=True),
            "Port Name": st.column_config.TextColumn("**Port Name**", disabled=True),
            "Rate": st.column_config.NumberColumn("**Rate**", format="%.2f"),
            "Unit": st.column_config.SelectboxColumn("**Unit**", options=["mts/day", "days", "ttl days"]),
            "L/D Terms": st.column_config.SelectboxColumn("**L/D Terms**", options=["SSHEX", "SSHINC", "SHEX", "SHINC", "FHEX", "FHINC"]),
            "Extra Days": st.column_config.NumberColumn("**Extra Days**", format="%.2f")
        },
        hide_index=True, num_rows="dynamic", use_container_width=True
    )
    st.session_state.ld_details_df = current_ld
    

# =====================================================================
# HESAPLAMA BUTONU VE MATEMATİKSEL İŞLEMLER
# =====================================================================
st.write("")
st.write("")
_, calc_btn_col, _ = st.columns([2, 2, 2])

with calc_btn_col:
    hesapla_basildi = st.button("🚀 CALCULATE VOYAGE", type="primary", use_container_width=True)

if "rc_input" not in st.session_state: st.session_state.rc_input = 0.0
if "fc_1" not in st.session_state: st.session_state.fc_1 = 0.5
if "tc_1" not in st.session_state: st.session_state.tc_1 = 100.0
if "fc_2" not in st.session_state: st.session_state.fc_2 = 0.5
if "dc_2" not in st.session_state: st.session_state.dc_2 = 1.0
if "calc_done" not in st.session_state: st.session_state.calc_done = False

if "res_summary" not in st.session_state:
    st.session_state.res_summary = {"total_days": 0.0, "sea_days": 0.0, "port_days": 0.0, "sea_cost": 0.0, "port_cost": 0.0}
    st.session_state.sea_legs_data = [] 
    st.session_state.port_ops_data = []
    st.session_state.res_revenue = 0.0
    st.session_state.res_opex = 0.0
    st.session_state.res_profit = 0.0
    st.session_state.res_tce = 0.0
    st.session_state.res_breakeven = 0.0
    st.session_state.res_bunker_cost = 0.0
    st.session_state.res_opex_details = []

if hesapla_basildi:
    q = quantity if quantity > 0 else 1.0 
    f_rate = freight
    
    spd_bal = float(st.session_state.sea_df.iloc[0]["Speed"]) 
    spd_ldn = float(st.session_state.sea_df.iloc[1]["Speed"]) 
    
    if spd_bal <= 0 or spd_ldn <= 0:
        st.error("Lütfen geminin Speed (Hız) değerlerini 0'dan büyük giriniz!")
    else:
        cons_bal = float(st.session_state.sea_df.iloc[0]["Cons"])
        cons_ldn = float(st.session_state.sea_df.iloc[1]["Cons"])
        cons_port_work = float(st.session_state.port_df.iloc[1]["Cons"])

        secili_satirlar = st.session_state.bunker_df[st.session_state.bunker_df["Seç"] == True]
        if secili_satirlar.empty:
            aktif_fiyatlar = st.session_state.bunker_df.iloc[0]
            st.warning("⚠️ Hiçbir yakıt limanı seçilmedi! Hesaplamada varsayılan olarak ilk liman fiyatları kullanılıyor.")
        else:
            aktif_fiyatlar = secili_satirlar.iloc[0]
            
        fuel_type_bal = str(st.session_state.sea_df.iloc[0]["Select"])
        fuel_type_ldn = str(st.session_state.sea_df.iloc[1]["Select"])
        fuel_type_port_work = str(st.session_state.port_df.iloc[1]["Select"])
        
        price_bal = float(aktif_fiyatlar.get(fuel_type_bal, 0.0))
        if fuel_type_bal not in aktif_fiyatlar.index:
            st.warning(f"'{fuel_type_bal}' fiyat listesinde bulunamadı, maliyet $0 olarak hesaplanıyor.")
            
        price_ldn = float(aktif_fiyatlar.get(fuel_type_ldn, 0.0))
        if fuel_type_ldn not in aktif_fiyatlar.index:
            st.warning(f"'{fuel_type_ldn}' fiyat listesinde bulunamadı, maliyet $0 olarak hesaplanıyor.")
            
        price_port_work = float(aktif_fiyatlar.get(fuel_type_port_work, 0.0))
        if fuel_type_port_work not in aktif_fiyatlar.index:
            st.warning(f"'{fuel_type_port_work}' fiyat listesinde bulunamadı, maliyet $0 olarak hesaplanıyor.")

        # --- 1. SEYİR (AT SEA) HESAPLAMALARI ---
        sea_legs = []
        total_sea_days = 0.0
        total_sea_cost = 0.0
        
        port_names = []
        for i, r in st.session_state.port_rotation_df.iterrows():
            name = str(r.get("Port Name", "")).strip()
            if not name: name = f"Port {i+1}"
            port_names.append(name)

        prev_port = "Origin"
        for idx, row in st.session_state.port_rotation_df.iterrows():
            port_name = port_names[idx]
            dist = float(row.get("Distance", 0.0))
            margin = float(row.get("Weather Margin (%)", 5.0)) / 100.0
            port_type = str(row.get("Port Type", ""))
            
            if port_type in ["Ballast Port", "Load Port", "Return Ballast"]:
                days = (dist / (spd_bal * 24)) * (1 + margin)
                fuel_mts = days * cons_bal
                cost = fuel_mts * price_bal
            else:
                days = (dist / (spd_ldn * 24)) * (1 + margin)
                fuel_mts = days * cons_ldn
                cost = fuel_mts * price_ldn
                
            if idx == 0 and dist == 0:
                prev_port = port_name
                continue
                
            total_sea_days += days
            total_sea_cost += cost
            
            leg_name = f"{prev_port} - {port_name}" if idx > 0 else f"Ballast -> {port_name}"
            sea_legs.append({"At Sea": leg_name, "Duration (days)": days, "Bunker Cons. (USD)": cost})
            prev_port = port_name

        # --- 2. LİMAN (AT PORT) HESAPLAMALARI ---
        port_ops = []
        total_port_days = 0.0
        total_port_cost = 0.0
        
        for idx, row in st.session_state.ld_details_df.iterrows():
            p_name = str(row.get("Port Name", "")).strip()
            if not p_name: p_name = f"Port {idx+1}"
            
            rate = float(row.get("Rate", 0.0))
            ex_days = float(row.get("Extra Days", 0.0))
            unit = str(row.get("Unit", ""))
            
            if unit == "mts/day" and rate > 0:
                p_days = (q / rate) + ex_days
            else:
                p_days = rate + ex_days
                
            fuel_mts = p_days * cons_port_work
            cost = fuel_mts * price_port_work 
            
            port_ops.append({"At Port": p_name, "Duration (days)": p_days, "Bunker Cons. (USD)": cost})
            total_port_days += p_days
            total_port_cost += cost

        total_days = total_sea_days + total_port_days
        total_bunker_cost = total_sea_cost + total_port_cost

        # --- 3. DİĞER HESAPLAMALAR ---
        gross_freight = f_rate * q if freight_term == "pmt" else f_rate
        total_revenue = gross_freight 

        commissions = gross_freight * ((add_comm + broker_comm) / 100.0)
        total_pda = st.session_state.port_charges_df["PDA"].sum()
        total_liner = st.session_state.port_charges_df["Liner Expenses"].sum()

        total_opex = (total_bunker_cost + total_pda + total_liner + 
                      despatch + strait_canal + extra_insurance + 
                      cargo_survey + other_exp + commissions + freight_tax)

        op_profit = total_revenue - total_opex
        tce = op_profit / total_days if total_days > 0 else 0.0

        st.session_state.base_f = f_rate
        st.session_state.base_q = q
        st.session_state.base_d = total_days
        comm_pct = (add_comm + broker_comm) / 100.0
        st.session_state.comm_multiplier = comm_pct
        st.session_state.base_fixed_opex = total_opex - commissions
        st.session_state.demurrage_val = 0.0 
        st.session_state.tce_val = tce
        st.session_state.calc_done = True

        st.session_state.sea_legs_data = sea_legs
        st.session_state.port_ops_data = port_ops
        st.session_state.res_summary = {
            "total_days": total_days, "sea_days": total_sea_days, "port_days": total_port_days,
            "sea_cost": total_sea_cost, "port_cost": total_port_cost
        }
        st.session_state.res_revenue = total_revenue
        st.session_state.res_opex = total_opex
        st.session_state.res_profit = op_profit
        st.session_state.res_tce = tce
        st.session_state.res_bunker_cost = total_bunker_cost
        st.session_state.res_opex_details = [
            total_bunker_cost, total_pda, freight_tax, total_liner, 0.0, 
            despatch, strait_canal, extra_insurance, cargo_survey, other_exp, 
            gross_freight * (add_comm/100), gross_freight * (broker_comm/100), total_opex
        ]
        
        # =====================================================================
        # SUPABASE UPSERT (KAYDETME) İŞLEMİ
        # =====================================================================
        # 1. Voyage ID Kontrolü ve Üretimi
        vid = st.session_state.get("voyage_id_input", "").strip()
        vname = st.session_state.get("v_name", "").strip()
        if not vname: vname = "UNNAMED_VESSEL"
        
        if not vid:
            # Eğer bu pencerede daha önce otomatik bir ID üretildiyse onu kullan (Mükerrer kaydı önler)
            if "auto_generated_vid" in st.session_state and st.session_state.auto_generated_vid:
                vid = st.session_state.auto_generated_vid
            else:
                # İlk kez hesaplanıyorsa yeni üret ve widget'a değil, arka plan hafızasına yaz
                vid = f"{vname.upper().replace(' ', '_')}-{datetime.now().strftime('%y%m%d-%H%M%S')}"
                st.session_state.auto_generated_vid = vid
            
        # 2. Port Rotation'dan Load ve Discharge limanlarını yakalama
        load_port_val = ""
        discharge_port_val = ""
        for _, r in st.session_state.port_rotation_df.iterrows():
            if r["Port Type"] == "Load Port" and not load_port_val:
                load_port_val = str(r["Port Name"])
            if r["Port Type"] == "Discharge Port" and not discharge_port_val:
                discharge_port_val = str(r["Port Name"])
                
        # 3. JSONB Paketini (all_data) Hazırlama
        all_data_payload = {
            "vessel": {k: st.session_state.get(k) for k in vessel_keys.keys()},
            "inputs": {
                "voyage_date": str(st.session_state.get("voyage_date_input", date.today())),
                "currency_rate": st.session_state.get("currency_rate_input", 0.0),
                "account": st.session_state.get("account_input", ""),
                "cargo_item": st.session_state.get("cargo_item_input", ""),
                "stowage_factor": st.session_state.get("stowage_factor_input", 0.0),
                "quantity": st.session_state.get("quantity_input", 0.0),
                "freight_term": st.session_state.get("freight_term_input", "pmt"),
                "terms": st.session_state.get("terms_input", "FIOST"),
                "gear": st.session_state.get("gear_input", "Gearless"),
                "laycan_date": str(st.session_state.get("laycan_date_input", date.today())),
                "freight": st.session_state.get("freight_input", 0.0),
                "demurrage": st.session_state.get("demurrage_input", 0.0),
                "despatch": st.session_state.get("despatch_input", 0.0),
                "freight_tax": st.session_state.get("freight_tax_input", 0.0),
                "extra_insurance": st.session_state.get("extra_insurance_input", 0.0),
                "cargo_survey": st.session_state.get("cargo_survey_input", 0.0),
                "strait_canal": st.session_state.get("strait_canal_input", 0.0),
                "add_comm": st.session_state.get("add_comm_input", 0.0),
                "broker_comm": st.session_state.get("broker_comm_input", 0.0),
                "other_exp": st.session_state.get("other_exp_input", 0.0)
            },
            "dataframes": {
                "bunker_base": st.session_state.bunker_df.to_dict('records') if 'bunker_df' in st.session_state else [],
                "sea_base": st.session_state.sea_df.to_dict('records') if 'sea_df' in st.session_state else [],
                "port_base": st.session_state.port_df.to_dict('records') if 'port_df' in st.session_state else [],
                "port_rotation_base": st.session_state.port_rotation_df.to_dict('records') if 'port_rotation_df' in st.session_state else [],
                "port_charges_base": st.session_state.port_charges_df.to_dict('records') if 'port_charges_df' in st.session_state else [],
                "ld_details_base": st.session_state.ld_details_df.to_dict('records') if 'ld_details_df' in st.session_state else []
            }
        }
        
        # 4. Veritabanına Gönderilecek Tablo Satırı
        db_payload = {
            "voyage_id": vid,
            "vessel_name": vname,
            "load_port": load_port_val,
            "discharge_port": discharge_port_val,
            "cargo_item": st.session_state.get("cargo_item_input", ""),
            "account": st.session_state.get("account_input", ""),
            "date": str(st.session_state.get("voyage_date_input", date.today())),
            "quantity": st.session_state.get("quantity_input", 0.0),
            "all_data": all_data_payload
        }
        
        # 5. Kaydet (Upsert)
        if supabase:
            try:
                supabase.table("voyage_calculations").upsert(db_payload).execute()
                st.toast(f"Sefer veritabanına kaydedildi: {vid}", icon="💾")
            except Exception as e:
                st.error(f"Veritabanı kayıt hatası: {e}")
                
        st.toast("Sefer hesaplaması başarıyla tamamlandı!", icon="📈")


# =====================================================================
# BÖLÜM 4: CALCULATION & STRATEGY (SONUÇ EKRANI)
# =====================================================================
st.markdown('<p class="main-header">4 - Calculation & Strategy</p>', unsafe_allow_html=True)

def render_html_table(df, right_cols):
    html_out = '<table style="width:100%; border-collapse: collapse; font-size: 14px; margin-bottom: 20px; color: black;">'
    html_out += '<thead><tr style="background-color: #f0f2f6; border-bottom: 2px solid #ddd;">'
    for col in df.columns:
        align = 'right' if col in right_cols else 'left'
        html_out += f'<th style="text-align: {align}; padding: 8px;">{html.escape(str(col))}</th>'
    html_out += '</tr></thead><tbody>'
    
    for i, row in df.iterrows():
        first_col_val = str(row[df.columns[0]]).strip().upper()
        is_total = first_col_val in ["TOTAL", "GRAND TOTAL"]
        fw = "bold" if is_total else "normal"
        bg = "#f9f9f9" if is_total else "transparent"
        
        html_out += f'<tr style="border-bottom: 1px solid #eee; background-color: {bg}; font-weight: {fw};">'
        for col in df.columns:
            align = 'right' if col in right_cols else 'left'
            cell_val = html.escape(str(row[col]))
            html_out += f'<td style="text-align: {align}; padding: 8px;">{cell_val}</td>'
        html_out += '</tr>'
    html_out += '</tbody></table>'
    return html_out

calc_col1, calc_col2, calc_col3 = st.columns([2.5, 1.2, 1.2])

with calc_col1:
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px; margin-bottom: 5px;'>Voyage Summary</div>", unsafe_allow_html=True)
    
    sea_list = []
    if "sea_legs_data" in st.session_state and st.session_state.sea_legs_data:
        for leg in st.session_state.sea_legs_data:
            sea_list.append([leg["At Sea"], format_tr(leg["Duration (days)"]), format_tr(leg["Bunker Cons. (USD)"])])
        sea_list.append(["TOTAL", format_tr(st.session_state.res_summary['sea_days']), format_tr(st.session_state.res_summary['sea_cost'])])
    else:
        sea_list = [["TOTAL", "0,00", "0,00"]]

    sea_df = pd.DataFrame(sea_list, columns=["At Sea", "Duration (days)", "Bunker Cons. (USD)"])
    st.markdown(render_html_table(sea_df, ["Duration (days)", "Bunker Cons. (USD)"]), unsafe_allow_html=True)

    port_list = []
    if "port_ops_data" in st.session_state and st.session_state.port_ops_data:
        for pop in st.session_state.port_ops_data:
            port_list.append([pop["At Port"], format_tr(pop["Duration (days)"]), format_tr(pop["Bunker Cons. (USD)"])])
        port_list.append(["TOTAL", format_tr(st.session_state.res_summary['port_days']), format_tr(st.session_state.res_summary['port_cost'])])
    else:
        port_list = [["TOTAL", "0,00", "0,00"]]

    port_df = pd.DataFrame(port_list, columns=["At Port", "Duration (days)", "Bunker Cons. (USD)"])
    st.markdown(render_html_table(port_df, ["Duration (days)", "Bunker Cons. (USD)"]), unsafe_allow_html=True)

    vtot_list = [
        ["At Sea", format_tr(st.session_state.res_summary['sea_days']), format_tr(st.session_state.res_summary['sea_cost'])],
        ["At Port", format_tr(st.session_state.res_summary['port_days']), format_tr(st.session_state.res_summary['port_cost'])],
        ["Grand Total", format_tr(st.session_state.res_summary['total_days']), format_tr(st.session_state.res_summary['sea_cost'] + st.session_state.res_summary['port_cost'])]
    ]
    vtot_df = pd.DataFrame(vtot_list, columns=["Voyage Total", "Duration (days)", "Bunker Cons. (USD)"])
    st.markdown(render_html_table(vtot_df, ["Duration (days)", "Bunker Cons. (USD)"]), unsafe_allow_html=True)


with calc_col2:
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px; margin-bottom: 5px;'>Operational Expenses</div>", unsafe_allow_html=True)
    
    opex_vals = st.session_state.res_opex_details if st.session_state.res_opex_details else [0.0] * 13
    formatted_opex = [f"$ {format_tr(v)}" for v in opex_vals]
    
    op_exp_df = pd.DataFrame({
        "Item": ["Bunker Expense", "Port Charges", "Freight Tax", "Liner IN", "Liner OUT", "Despatch", "Strait / Canal Exp.", "Extra Insurance", "Cargo Survey", "Other", "Add Comm.", "Brkg Comm.", "TOTAL"],
        "Cost": formatted_opex
    })
    st.markdown(render_html_table(op_exp_df, ["Cost"]), unsafe_allow_html=True)

with calc_col3:
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px; margin-bottom: 5px;'>Revenue</div>", unsafe_allow_html=True)
    
    rev = st.session_state.res_revenue
    dem = 0.0 
    
    rev_df = pd.DataFrame({
        "Item": ["Freight", "Demurrage", "TOTAL"],
        "Amount": [f"$ {format_tr(rev)}", f"$ {format_tr(dem)}", f"$ {format_tr(rev)}"] 
    })
    st.markdown(render_html_table(rev_df, ["Amount"]), unsafe_allow_html=True)
    
    st.markdown("<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; color: black; padding: 5px; margin-bottom: 5px;'>RESULT</div>", unsafe_allow_html=True)
    
    res_df = pd.DataFrame({
        "Metric": ["Total Revenue", "Total Op. Expens.", "Operational Profit", "Duration", "Daily Profit (TCE)"],
        "Value": [
            f"$ {format_tr(st.session_state.res_revenue)}", 
            f"$ {format_tr(st.session_state.res_opex)}", 
            f"$ {format_tr(st.session_state.res_profit)}", 
            f"{format_tr(st.session_state.res_summary['total_days'])} days",
            f"$ {format_tr(st.session_state.res_tce)}"
        ]
    })
    st.markdown(render_html_table(res_df, ["Value"]), unsafe_allow_html=True)


# =====================================================================
# BÖLÜM 5: ANALYSIS & STRATEGY
# =====================================================================
if st.session_state.get("calc_done", False):
    st.markdown('<p class="main-header">5 - Analysis & Strategy</p>', unsafe_allow_html=True)

    def get_matrix_ndp(f, q, d, rc):
        gross_freight = f * q 
        comm = gross_freight * st.session_state.comm_multiplier
        opex = st.session_state.base_fixed_opex + comm
        revenue = gross_freight + st.session_state.demurrage_val 
        profit = revenue - opex
        tce = profit / d if d > 0 else 0
        return tce - rc

    def generate_matrix_html(matrix_type, f_base, var_base, d_base, f_step, var_step, rc):
        f_vals = [f_base + (i - 5) * f_step for i in range(11)]
        v_vals = [var_base + (i - 4) * var_step for i in range(9)]
        
        html_out = '<table style="width:100%; border-collapse: collapse; font-size: 13px; text-align: center; border: 1px solid #ccc; background-color: white; color: black;">'
        html_out += '<tr><th style="border: 1px solid #ccc; background-color: #f0f2f6; padding: 4px;"></th>'
        for v in v_vals:
            html_out += f'<th style="border: 1px solid #ccc; background-color: #f0f2f6; padding: 4px;">{format_tr(v, is_int=(matrix_type=="tonnage"))}</th>'
        html_out += '</tr>'
        
        for r_idx, f in enumerate(f_vals):
            row_bg = "#d9e1f2" if r_idx == 5 else "transparent"
            html_out += f'<tr><td style="border: 1px solid #ccc; background-color: #f0f2f6; font-weight: bold; padding: 4px;">{format_tr(f)}</td>'
            for c_idx, v in enumerate(v_vals):
                cell_bg = row_bg
                if c_idx == 4:
                    cell_bg = "#ffe699" if r_idx == 5 else "#d9e1f2"
                    
                if matrix_type == 'tonnage':
                    val = get_matrix_ndp(f, v, d_base, rc)
                else:
                    val = get_matrix_ndp(f, st.session_state.base_q, v, rc)
                
                fw_cell = "bold" if (r_idx == 5 or c_idx == 4) else "normal"    
                html_out += f'<td style="border: 1px solid #ccc; background-color: {cell_bg}; font-weight: {fw_cell}; padding: 4px;">{format_tr(val)}</td>'
            html_out += '</tr>'
        html_out += '</table>'
        return html_out

    daily_profit = st.session_state.tce_val
    rc = st.session_state.rc_input
    net_daily_profit = daily_profit - rc
    
    divisor = st.session_state.base_q * (1.0 - st.session_state.comm_multiplier)
    if divisor > 0:
        be_point = ((rc * st.session_state.base_d) + st.session_state.base_fixed_opex - st.session_state.demurrage_val) / divisor 
    else:
        be_point = 0.0

    st.write("")
    
    top1, top2, top3, top4 = st.columns([1.2, 1.2, 0.5, 4])
    with top1:
        st.markdown("<div style='line-height:2.6;'><b>Daily Profit (TCE)</b></div>", unsafe_allow_html=True)
        st.markdown("<div style='line-height:2.6;'><b>R/C</b></div>", unsafe_allow_html=True)
        st.markdown("<div style='line-height:2.6;'><b>Net Daily Profit</b></div>", unsafe_allow_html=True)
        st.markdown("<div style='line-height:2.6;'><b>Break-Even Point</b></div>", unsafe_allow_html=True)
    with top2:
        st.markdown(f"<div style='line-height:2.6; text-align:right;'>{format_tr(daily_profit)}</div>", unsafe_allow_html=True)
        new_rc = st.number_input("RC", value=st.session_state.rc_input, step=500.0, label_visibility="collapsed")
        st.markdown(f"<div style='line-height:2.6; text-align:right;'>{format_tr(net_daily_profit)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='line-height:2.6; text-align:right;'>{format_tr(be_point)}</div>", unsafe_allow_html=True)
    with top3:
        st.markdown("<div style='line-height:2.6;'>usd</div>", unsafe_allow_html=True)
        st.markdown("<div style='line-height:2.6;'>usd</div>", unsafe_allow_html=True)
        st.markdown("<div style='line-height:2.6;'>usd</div>", unsafe_allow_html=True)
        st.markdown("<div style='line-height:2.6;'>usd</div>", unsafe_allow_html=True)
    with top4:
        st.write("")
        update_btn = st.button("🔄 Update Analysis", type="secondary")
        
    if update_btn:
        st.session_state.rc_input = new_rc
        st.rerun()

    st.write("---")

    mat_col1, mat_col2 = st.columns(2)
    
    with mat_col1:
        c1, c2 = st.columns(2)
        with c1:
            fc1 = st.number_input("Freight Change (usd)", value=st.session_state.fc_1, step=0.1, key="f_ch1")
        with c2:
            tc1 = st.number_input("Tonnage Change (mts)", value=st.session_state.tc_1, step=100.0, key="t_ch1")
            
        st.markdown("<div style='text-align: center; font-weight: bold; margin-bottom: 5px;'>Freight (usd) / Tonnage (mts) Matris</div>", unsafe_allow_html=True)
        html_tonnage = generate_matrix_html('tonnage', st.session_state.base_f, st.session_state.base_q, st.session_state.base_d, fc1, tc1, new_rc)
        st.markdown(html_tonnage, unsafe_allow_html=True)
        
    with mat_col2:
        c3, c4 = st.columns(2)
        with c3:
            fc2 = st.number_input("Freight Change (usd)", value=st.session_state.fc_2, step=0.1, key="f_ch2")
        with c4:
            dc2 = st.number_input("Duration Change (days)", value=st.session_state.dc_2, step=1.0, key="d_ch2")
            
        st.markdown("<div style='text-align: center; font-weight: bold; margin-bottom: 5px;'>Freight (usd) / Duration (days) Matris</div>", unsafe_allow_html=True)
        html_duration = generate_matrix_html('duration', st.session_state.base_f, st.session_state.base_d, st.session_state.base_d, fc2, dc2, new_rc)
        st.markdown(html_duration, unsafe_allow_html=True)
        
    st.session_state.fc_1 = fc1
    st.session_state.tc_1 = tc1
    st.session_state.fc_2 = fc2
    st.session_state.dc_2 = dc2
