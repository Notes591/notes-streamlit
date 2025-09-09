import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ====== الاتصال بجوجل شيت ======
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# أوراق جوجل شيت
SHEET_NAME = "Complaints"
complaints_sheet = client.open(SHEET_NAME).worksheet("Complaints")
archive_sheet = client.open(SHEET_NAME).worksheet("Archive")
types_sheet = client.open(SHEET_NAME).worksheet("Types")

# ====== واجهة التطبيق ======
st.set_page_config(page_title="📢 نظام الشكاوى", page_icon="⚠️")
st.title("⚠️ نظام إدارة الشكاوى")

# تحميل الأنواع من Google Sheet
types_list = [row[0] for row in types_sheet.get_all_values()[1:]]

# ====== 1. البحث ======
st.header("🔍 البحث عن شكوى")
search_id = st.text_input("🆔 اكتب رقم الشكوى")

if st.button("🔍 بحث"):
    if search_id.strip():
        complaints = complaints_sheet.get_all_values()
        archive = archive_sheet.get_all_values()
        found = False

        # بحث في الشكاوى النشطة
        for i, row in enumerate(complaints[1:], start=2):
            if row[0] == search_id:
                found = True
                with st.expander(f"🆔 شكوى رقم {row[0]}"):
                    st.write(f"📌 النوع: {row[1]}")
                    st.write(f"✅ الإجراء: {row[2]}")
                    st.caption(f"📅 تاريخ التسجيل: {row[3]}")

                    new_action = st.text_area("✏️ عدل الإجراء", value=row[2], key=f"search_act_{i}")
                    col1, col2, col3 = st.columns(3)

                    if col1.button("💾 حفظ", key=f"search_save_{i}"):
                        complaints_sheet.update(f"C{i}", [[new_action]])
                        st.success("✅ تم تعديل الشكوى")
                        st.rerun()

                    if col2.button("🗑️ حذف", key=f"search_del_{i}"):
                        complaints_sheet.delete_rows(i)
                        st.warning("🗑️ تم حذف الشكوى")
                        st.rerun()

                    if col3.button("📦 أرشفة", key=f"search_arc_{i}"):
                        archive_sheet.append_row([row[0], row[1], new_action, row[3]])
                        complaints_sheet.delete_rows(i)
                        st.success("♻️ الشكوى اتنقلت للأرشيف")
                        st.rerun()

        # بحث في الأرشيف
        for i, row in enumerate(archive[1:], start=2):
            if row[0] == search_id:
                found = True
                with st.expander(f"📦 شكوى رقم {row[0]} (في الأرشيف)"):
                    st.write(f"📌 النوع: {row[1]}")
                    st.write(f"✅ الإجراء: {row[2]}")
                    st.caption(f"📅 تاريخ التسجيل: {row[3]}")

                    if st.button("♻️ استرجاع", key=f"search_restore_{i}"):
                        complaints_sheet.append_row([row[0], row[1], row[2], row[3], "🔄 مسترجعة"])
                        archive_sheet.delete_rows(i)
                        st.success("✅ تم استرجاع الشكوى")
                        st.rerun()

        if not found:
            st.error("❌ لم يتم العثور على الشكوى")

# ====== 2. تسجيل شكوى جديدة ======
st.header("➕ تسجيل شكوى جديدة")

with st.form("add_complaint", clear_on_submit=True):  # 🟢 clear_on_submit يفضي الحقول بعد الإضافة
    comp_id = st.text_input("🆔 رقم الشكوى")
    comp_type = st.selectbox("📌 نوع الشكوى", ["اختر نوع الشكوى..."] + types_list, index=0)
    action = st.text_area("✅ الإجراء المتخذ")

    submitted = st.form_submit_button("➕ إضافة شكوى")
    if submitted:
        if comp_id.strip() and comp_type != "اختر نوع الشكوى...":
            complaints = complaints_sheet.get_all_records()
            archive = archive_sheet.get_all_records()
            all_ids = [str(c["ID"]) for c in complaints] + [str(a["ID"]) for a in archive]

            if comp_id in all_ids:
                st.error("⚠️ رقم الشكوى موجود بالفعل (في النشطة أو الأرشيف)")
            else:
                date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                complaints_sheet.append_row([comp_id, comp_type, action, date_now, ""])
                st.success("✅ تم تسجيل الشكوى")
                st.rerun()
        else:
            st.error("⚠️ لازم تدخل رقم شكوى وتختار نوع")

# ====== 3. عرض الشكاوى النشطة ======
st.header("📋 الشكاوى النشطة:")

notes = complaints_sheet.get_all_values()
if len(notes) > 1:
    for i, row in enumerate(notes[1:], start=2):
        comp_id = row[0]
        comp_type = row[1]
        action = row[2]
        date_added = row[3]
        restored = row[4] if len(row) > 4 else ""

        with st.expander(f"🆔 شكوى رقم {comp_id} {restored}"):
            st.write(f"📌 النوع: {comp_type}")
            st.write(f"✅ الإجراء: {action}")
            st.caption(f"📅 تاريخ التسجيل: {date_added}")

            new_action = st.text_area("✏️ عدل الإجراء", value=action, key=f"act_{i}")
            col1, col2, col3 = st.columns(3)

            if col1.button("💾 حفظ", key=f"save_{i}"):
                complaints_sheet.update(f"C{i}", [[new_action]])
                st.success("✅ تم تعديل الشكوى")
                st.rerun()

            if col2.button("🗑️ حذف", key=f"delete_{i}"):
                complaints_sheet.delete_rows(i)
                st.warning("🗑️ تم حذف الشكوى")
                st.rerun()

            if col3.button("📦 أرشفة", key=f"archive_{i}"):
                archive_sheet.append_row([comp_id, comp_type, new_action, date_added])
                complaints_sheet.delete_rows(i)
                st.success("♻️ الشكوى انتقلت للأرشيف")
                st.rerun()
else:
    st.info("لا توجد شكاوى حالياً.")

# ====== 4. عرض الأرشيف ======
st.header("📦 الأرشيف (الشكاوى المحلولة):")

archived = archive_sheet.get_all_values()
if len(archived) > 1:
    for row in archived[1:]:
        comp_id, comp_type, action, date_added = row
        with st.expander(f"📦 شكوى رقم {comp_id}"):
            st.write(f"📌 النوع: {comp_type}")
            st.write(f"✅ الإجراء: {action}")
            st.caption(f"📅 تاريخ التسجيل: {date_added}")
else:
    st.info("لا يوجد شكاوى في الأرشيف.")
