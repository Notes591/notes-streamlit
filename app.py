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

# افتح أول شيت متاح
sheets = client.openall()
if not sheets:
    st.error("❌ مفيش أي Google Sheet متشارك مع الحساب ده.")
    st.stop()

sheet = sheets[0].sheet1
st.caption(f"✅ متصل بالشيت: {sheets[0].title}")

# ====== إعداد واجهة Streamlit ======
st.set_page_config(page_title="برنامج الملاحظات (نسخة ويب)", page_icon="📝", layout="centered")

st.title("🟨 برنامج الملاحظات (نسخة ويب)")

# ====== التحديث التلقائي ======
refresh_interval = 15  # بالثواني
st.caption(f"⏳ يتم التحديث التلقائي كل {refresh_interval} ثانية")

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > refresh_interval:
    st.session_state.last_refresh = time.time()
    st.experimental_rerun()

# ====== تحميل الملاحظات ======
notes = sheet.get_all_records()
titles = [row.get("Title", f"Note {i+1}") for i, row in enumerate(notes)]

# ====== اختيار ملاحظة ======
selected = st.selectbox("📋 اختر ملاحظة للتعديل أو الحذف:", [""] + titles)

# ====== عرض/إضافة ملاحظة ======
title = st.text_input("العنوان", value=selected if selected else "")
content = st.text_area(
    "المحتوى",
    value=next((n["Content"] for n in notes if n.get("Title") == selected), "")
)

col1, col2, col3 = st.columns(3)

# ➕ إضافة
with col1:
    if st.button("➕ إضافة"):
        sheet.append_row([title or f"Note {len(notes)+1}", content])
        st.success("✅ تمت إضافة الملاحظة")
        st.experimental_rerun()

# 💾 تعديل
with col2:
    if st.button("💾 تعديل") and selected:
        index = titles.index(selected) + 2  # +2 لأن أول صف header
        sheet.update_cell(index, 1, title)
        sheet.update_cell(index, 2, content)
        st.success("✅ تم تعديل الملاحظة")
        st.experimental_rerun()

# 🗑 حذف
with col3:
    if st.button("🗑 حذف") and selected:
        index = titles.index(selected) + 2
        sheet.delete_rows(index)
        st.success("🗑 تم حذف الملاحظة")
        st.experimental_rerun()
