import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# ====== الاتصال بجوجل شيت ======
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# اسم الشيت
SHEET_NAME = "Shared Notes"
sheet = client.open(SHEET_NAME).sheet1

# ====== واجهة التطبيق ======
st.set_page_config(page_title="برنامج الملاحظات (نسخة ويب)", page_icon="📝")

st.title("🟨 برنامج الملاحظات (نسخة ويب)")

# Checkbox للتأكد من الاتصال
st.checkbox("متصل بالجداول ✅", value=True)

# ====== التحديث التلقائي ======
refresh_interval = 15  # بالثواني
st.caption(f"⏳ يتم التحديث التلقائي كل {refresh_interval} ثانية")

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > refresh_interval:
    st.session_state.last_refresh = time.time()
    st.experimental_rerun()

# ====== إضافة ملاحظة ======
with st.form("add_note_form"):
    note = st.text_area("✍️ اكتب ملاحظة جديدة")
    submitted = st.form_submit_button("➕ إضافة")
    if submitted and note.strip():
        sheet.append_row([note])
        st.success("✅ تم إضافة الملاحظة!")

# ====== عرض الملاحظات ======
st.subheader("📋 كل الملاحظات:")

notes = sheet.get_all_values()
if notes:
    for i, row in enumerate(notes, start=1):
        st.write(f"{i}- {row[0]}")
else:
    st.info("لا توجد ملاحظات حتى الآن.")
