import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from twilio.rest import Client

# ==============================
# TWILIO CONFIG
# ==============================
account_sid = "YOUR_TWILIO_SID"
auth_token = "YOUR_TWILIO_AUTH"
whatsapp_from = "whatsapp:+14155238886"   # Twilio Sandbox number
whatsapp_to = "whatsapp:+91XXXXXXXXXX"   # Your number (must join sandbox first)
client = Client(account_sid, auth_token)

# ==============================
# SELENIUM CONFIG
# ==============================
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

# ATTACH to an already logged-in Chrome session (so you don’t need to login again)
options.debugger_address = "127.0.0.1:9222"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# POSOCO page (you must already be logged in on that Chrome session)
url = "YOUR_POSOCO_PORTAL_URL"
driver.get(url)

print("Monitoring POSOCO page...")

last_seen = None

while True:
    try:
        # Example: fetch the first row of Code Issue column
        element = driver.find_element(By.CSS_SELECTOR, "table.dataTable tbody tr td:nth-child(4)")
        current_text = element.text.strip()

        if last_seen != current_text:
            print(f"[UPDATE] New entry found: {current_text}")
            last_seen = current_text

            # Send WhatsApp alert
            msg = client.messages.create(
                from_=whatsapp_from,
                to=whatsapp_to,
                body=f"🚨 POSOCO Update Detected:\n{current_text}"
            )
            print(f"WhatsApp sent (SID: {msg.sid})")

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(30)  # check every 30 sec
