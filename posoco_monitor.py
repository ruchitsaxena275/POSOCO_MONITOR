import time
import streamlit as st
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

# ==============================
# TWILIO CONFIG
# ==============================
account_sid = "YOUR_TWILIO_SID"
auth_token = "YOUR_TWILIO_AUTH"
whatsapp_from = "whatsapp:+14155238886"   # Twilio Sandbox number
whatsapp_to = "whatsapp:+918005737127"   # Your WhatsApp number
client = Client(account_sid, auth_token)

# ==============================
# POSOCO CONFIG
# ==============================
URL = "https://oms.nrldc.in/posoco/shutdown?action=otherlist&list=true"

# Optional: If POSOCO requires login, paste cookies here (from browser DevTools)
COOKIES = {
    # "sessionid": "xxxx",
    # "csrftoken": "xxxx"
}

# ==============================
# STREAMLIT UI
# ==============================
st.set_page_config(page_title="POSOCO Monitor", layout="wide")
st.title("🔍 POSOCO Portal Monitor")

placeholder = st.empty()
status_box = st.empty()

if "last_seen" not in st.session_state:
    st.session_state.last_seen = None

def send_whatsapp(msg):
    message = client.messages.create(
        from_=whatsapp_from,
        body=msg,
        to=whatsapp_to
    )
    return message.sid

def fetch_table():
    resp = requests.get(URL, cookies=COOKIES, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Grab the table body (adjust selector as per page structure)
    table = soup.select_one("table.dataTable tbody")
    if table:
        return table.get_text(strip=True)
    return None

# ==============================
# MONITOR LOOP (polling refresh every 60s)
# ==============================
while True:
    try:
        current_text = fetch_table()
        if current_text:
            if st.session_state.last_seen != current_text:
                status_box.success("⚡ Change detected in POSOCO table!")
                send_whatsapp("🚨 POSOCO Outage Table Updated:\n\n" + current_text[:1500])
                st.session_state.last_seen = current_text
            else:
                status_box.info("✅ No change detected yet...")
        else:
            status_box.warning("⚠️ Table not found, check selector or login.")

    except Exception as e:
        status_box.error(f"Error: {e}")

    time.sleep(60)  # refresh every 60 sec
