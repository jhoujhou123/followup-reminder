import os
import json
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

def send_email(to_email, subject, body):
    sender_email = os.environ["EMAIL_USER"]
    sender_password = os.environ["EMAIL_PASS"] # ⚠️ 不是登入密碼

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {to_email}")

    except Exception as e:
        print("Email error:", e)





# =========================
# 1️⃣ Google Sheet 連線
# =========================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


SERVICE_ACCOUNT_FILE = (
    r"C:\Users\Jinzer\Desktop\python\問卷收集\dogwood-cinema-494201-u6-248629932a97.json"
)

if os.path.exists(SERVICE_ACCOUNT_FILE):
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=scope
    )
else:
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )



client = gspread.authorize(creds)

sheet = client.open_by_key(
    "1Afrj6EkBm1qe0y6RMNjd7wQgAQtTaM1dCO7l_bG1yKQ"
).sheet1




data = sheet.get_all_records()
df = pd.DataFrame(data)

# =========================
# 2️⃣ 日期處理
# =========================
today = datetime.now().date()

df["follow_up_6m"] = pd.to_datetime(df["follow_up_6m"], errors="coerce").dt.date
due = df[df["follow_up_6m"] == today]



# =========================
# 3️⃣ 發送通知
# =========================
for _, row in due.iterrows():
    msg = f"""
⚠️ 追蹤提醒

ID: {row['subject_id']}
6個月追蹤到期
日期: {row['follow_up_6m']}
"""
    if "email" in row and pd.notna(row["email"]):
        send_email(row["email"], "追蹤提醒", msg)

print(f"done: {len(due)}")
