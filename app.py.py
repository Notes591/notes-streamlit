import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ====== الاتصال بجوجل شيت ======
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

# نجيب بيانات الجيسون من Secrets (مش ملف خارجي)
creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# افتح أول شيت متاح
sheets = client.openall()
if not sheets:
    st.error("❌ مفيش أي شيت متشارك مع الإيميل ده.")
    st.stop()
sheet = sheets[0].sheet1

st.title("📒 برنامج الملاحظات (نسخة ويب)")

# ========== التحديث التلقائي ==========
refresh_interval = 15  # بالثواني
st.caption(f"⏳ يتم التحديث التلقائي كل {refresh_interval} ثانية")
st_autorefresh = st.experimental_autorefresh(
    interval=refresh_interval * 1000, limit=None, key="refresh"
)

# تحميل الملاحظات
notes = sheet.get_all_records()

# اختيار ملاحظة
titles = [row.get("Title", "بدون عنوان") for row in notes]
selected = st.selectbox("اختر ملاحظة:", [""] + titles)

# عرض الملاحظة
title = st.text_input("العنوان", value=selected if selected else "")
content = st.text_area(
    "المحتوى",
    value=next((n["Content"] for n in notes if n["Title"] == selected), "")
)

col1, col2, col3 = st.columns(3)

# ====== إضافة ======
with col1:
    if st.button("➕ إضافة"):
        sheet.append_row([title or f"Note {len(notes)+1}", content])
        st.success("✅ تمت إضافة الملاحظة")
        st.rerun()

# ====== تعديل ======
with col2:
    if st.button("💾 تعديل") and selected:
        index = titles.index(selected) + 2  # الصف الفعلي (1 للهيدر)
        sheet.update_cell(index, 1, title)
        sheet.update_cell(index, 2, content)
        st.success("✅ تم تعديل الملاحظة")
        st.rerun()

# ====== حذف ======
with col3:
    if st.button("🗑 حذف") and selected:
        index = titles.index(selected) + 2
        sheet.delete_rows(index)
        st.success("🗑 تم حذف الملاحظة")
        st.rerun()
