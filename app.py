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

# ====== إضافة ملاحظة ======
with st.form("add_note_form"):
    title = st.text_input("العنوان")
    content = st.text_area("المحتوى")
    submitted = st.form_submit_button("➕ إضافة")
    if submitted and (title.strip() or content.strip()):
        sheet.append_row([title, content])
        st.success("✅ تمت الإضافة")
        st.rerun()

# ====== عرض وتعديل/حذف الملاحظات ======
st.subheader("📋 كل الملاحظات:")

notes = sheet.get_all_values()

if len(notes) > 1:  # فيه بيانات
    for i, row in enumerate(notes[1:], start=2):  # نتجاهل الهيدر
        title = row[0] if len(row) > 0 else ""
        content = row[1] if len(row) > 1 else ""

        with st.expander(f"📌 {i-1}. {title}"):
            st.write(content)

            # خانات التعديل
            new_title = st.text_input("✏️ العنوان", value=title, key=f"title_{i}")
            new_content = st.text_area("📝 المحتوى", value=content, key=f"content_{i}")

            col1, col2 = st.columns(2)

            if col1.button("💾 حفظ التعديلات", key=f"save_{i}"):
                sheet.update(f"A{i}:B{i}", [[new_title, new_content]])
                st.success("✅ تم الحفظ")
                st.rerun()

            if col2.button("🗑️ حذف", key=f"delete_{i}"):
                sheet.delete_rows(i)
                st.warning("🗑️ تم الحذف")
                st.rerun()
else:
    st.info("لا توجد ملاحظات حتى الآن.")
