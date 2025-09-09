import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# ====== الاتصال بجوجل شيت ======
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

# تحميل بيانات الاعتماد من Secrets
creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# افتح الشيت
SHEET_NAME = "Notes"
sheet = client.open(SHEET_NAME).sheet1

st.set_page_config(page_title="برنامج الملاحظات (نسخة ويب)", page_icon="📝", layout="centered")

st.title("🟨 برنامج الملاحظات (نسخة ويب)")

# ====== التحديث التلقائي ======
refresh_interval = 15  # بالثواني
st.caption(f"⏳ يتم التحديث التلقائي كل {refresh_interval} ثانية")

st_autorefresh = st.autorefresh(
    interval=refresh_interval * 1000,  # بالمللي ثانية
    key="datarefresh"
)

# ====== إدخال ملاحظة جديدة ======
with st.form("note_form"):
    note_text = st.text_area("✍️ اكتب ملاحظة جديدة:")
    submitted = st.form_submit_button("➕ إضافة الملاحظة")

    if submitted and note_text.strip():
        sheet.append_row([note_text])
        st.success("✅ تم إضافة الملاحظة!")

# ====== عرض كل الملاحظات ======
st.subheader("📋 قائمة الملاحظات")
notes = sheet.get_all_records()

if notes:
    df = pd.DataFrame(notes)
    st.table(df)
else:
    st.info("لا توجد ملاحظات بعد. أضف واحدة من فوق ⬆️")
