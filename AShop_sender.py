__version__ = "1.0.0"

######################################
import os
import sys
import json
import time
import urllib.parse
import atexit
import signal
import copy
import shutil

from googleapiclient.discovery import build

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QAbstractItemView, QLabel, QDialog, QDialogButtonBox, QTextEdit,
    QLineEdit, QFileDialog, QMenu, QMessageBox, QScrollArea, QFrame, QInputDialog,
    QPlainTextEdit, QRadioButton, QCheckBox, QTabWidget, QComboBox
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

############################################################################
# 1) تحميل/حفظ إعدادات الإدارة (multiple workers)
############################################################################

def load_admin_settings():
    filename = "admin_settings.json"
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"workers": []}
    return {"workers": []}

def save_admin_settings(settings):
    filename = "admin_settings.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

############################################################################
# 2) تحميل/حفظ إعدادات Google Sheets (محفوظة في sheet_settings.json)
############################################################################

def load_sheet_settings():
    settings_file = "sheet_settings.json"
    if os.path.exists(settings_file):
        with open(settings_file, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {"SPREADSHEET_ID": "", "RANGE_NAME": "", "API_KEY": ""}

def save_sheet_settings(settings):
    settings_file = "sheet_settings.json"
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

sheet_settings = load_sheet_settings()
SPREADSHEET_ID = sheet_settings.get("SPREADSHEET_ID", "")
RANGE_NAME = sheet_settings.get("RANGE_NAME", "")
API_KEY = sheet_settings.get("API_KEY", "")

############################################################################
# 3) تنظيف جلسة المتصفح عند انتهاء البرنامج
############################################################################

def cleanup_driver():
    global driver
    if driver is not None:
        try:
            driver.quit()
            print("تم إنهاء جلسة المتصفح بنجاح.")
        except Exception as e:
            print("خطأ أثناء إنهاء المتصفح:", e)

atexit.register(cleanup_driver)

def signal_handler(sig, frame):
    cleanup_driver()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

############################################################################
# 4) Google Sheets APIs
############################################################################

def fetch_sheet_data_public():
    if not API_KEY or not SPREADSHEET_ID or not RANGE_NAME:
        return []
    service = build('sheets', 'v4', developerKey=API_KEY)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    return values

############################################################################
# 5) دوال مساعدة
############################################################################

def convert_phone(phone):
    phone = phone.strip()
    if phone.startswith("0"):
        return "212" + phone[1:]
    elif phone.startswith("212"):
        return phone
    else:
        return phone

settings_data = {
    "sleep_config": {
        "sleep_open_chat": 8.0,
        "sleep_send_text_wait": 1.0,
        "sleep_after_send": 1.0,
        "sleep_clear_box": 0.5,
        "sleep_scroll_wait": 0.5,
        "sleep_attach_click_retry": 1.0,
        "sleep_file_attach_wait": 2.0
    }
}

def get_sleep_time(key):
    return settings_data.get("sleep_config", {}).get(key, 2.0)

def filter_non_bmp(text):
    return ''.join(c for c in text if ord(c) <= 0xFFFF)

############################################################################
# 6) تحميل وحفظ القوالب (مع خاصية enabled)
############################################################################

def load_templates():
    templates_file = "templates.json"
    if not os.path.exists(templates_file):
        return []
    else:
        with open(templates_file, "r", encoding="utf-8") as f:
            templates = json.load(f)
        for t in templates:
            if "enabled" not in t:
                t["enabled"] = True
        return templates

def save_templates(templates):
    for t in templates:
        if "enabled" not in t:
            t["enabled"] = True
    with open("templates.json", "w", encoding="utf-8") as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)

############################################################################
# 7) إنشاء جلسة المتصفح
############################################################################

def create_driver(visible=True):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    user_data_dir = os.path.join(base_dir, "whatsapp_profile")
    options = Options()
    if visible:
        options.add_argument("--start-maximized")
    else:
        options.add_argument("--headless")
        options.add_argument("--window-size=1400,900")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver_ = webdriver.Chrome(service=service, options=options)
    driver_.get("https://web.whatsapp.com")
    return driver_

############################################################################
# 8) المتغيرات العالمية
############################################################################

driver = None
ui_instance = None
processed_orders = set()

############################################################################
# 9) دوال إرسال الرسائل دون خيط منفصل
############################################################################

def clear_message_box():
    try:
        msg_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "footer div[role='textbox'][contenteditable='true']"))
        )
        msg_box.click()
        ActionChains(driver).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(Keys.DELETE).perform()
        time.sleep(get_sleep_time("sleep_clear_box"))
    except:
        pass

def send_text_in_one_message(text):
    text = filter_non_bmp(text.strip())
    if not text:
        return
    try:
        clear_message_box()
        msg_box = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "footer div[role='textbox'][contenteditable='true']"))
        )
        lines = text.split("\n")
        for i, line in enumerate(lines):
            line = filter_non_bmp(line)
            if line:
                msg_box.send_keys(line)
            if i < len(lines) - 1:
                ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
        time.sleep(get_sleep_time("sleep_send_text_wait"))
        msg_box.send_keys(Keys.ENTER)
        time.sleep(get_sleep_time("sleep_send_text_wait"))
    except Exception as e:
        ui_instance.log(f"[⚠️] خطأ في إرسال الرسالة النصية: {e}")

def click_main_send_button():
    for _ in range(3):
        try:
            send_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Send' and @role='button']"))
            )
            driver.execute_script("arguments[0].scrollIntoViewIfNeeded();", send_btn)
            time.sleep(get_sleep_time("sleep_scroll_wait"))
            send_btn.click()
            time.sleep(get_sleep_time("sleep_after_send"))
            return
        except:
            ui_instance.log("[⚠️] لم نتمكن من النقر على زر الإرسال، إعادة المحاولة...")
            time.sleep(get_sleep_time("sleep_attach_click_retry"))

def send_attachment_with_caption(filepath, caption):
    try:
        cap = filter_non_bmp(caption.strip())
        clear_message_box()
        if cap:
            msg_box = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "footer div[role='textbox'][contenteditable='true']"))
            )
            lines = cap.split("\n")
            for i, line in enumerate(lines):
                line = filter_non_bmp(line)
                if line:
                    msg_box.send_keys(line)
                if i < len(lines) - 1:
                    ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
        time.sleep(get_sleep_time("sleep_clear_box"))

        attach_btn = None
        for _ in range(3):
            try:
                attach_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@title='Attach']"))
                )
                driver.execute_script("arguments[0].scrollIntoViewIfNeeded();", attach_btn)
                time.sleep(get_sleep_time("sleep_scroll_wait"))
                attach_btn.click()
                time.sleep(get_sleep_time("sleep_attach_click_retry"))
                break
            except:
                ui_instance.log("[⚠️] لم نتمكن من النقر على زر الإرفاق، إعادة المحاولة...")
                time.sleep(get_sleep_time("sleep_attach_click_retry"))
        if not attach_btn:
            ui_instance.log("[⚠️] فشل العثور على زر الإرفاق.")
            return

        file_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file' and contains(@accept, 'image')]"))
        )
        driver.execute_script("arguments[0].style.display = 'block';", file_input)
        time.sleep(get_sleep_time("sleep_scroll_wait"))
        file_input.send_keys(filepath)
        time.sleep(get_sleep_time("sleep_file_attach_wait"))
        click_main_send_button()
        clear_message_box()
    except Exception as e:
        ui_instance.log(f"[⚠️] خطأ في إرسال المرفق: {e}")

def process_message_template(template_content, row_dict):
    msg = template_content
    for key, value in row_dict.items():
        if key.lower().strip() == "statu":
            continue
        placeholder = "{" + key + "}"
        msg = msg.replace(placeholder, value)
    return msg


class LoadingDialog(QDialog):
    def __init__(self, message="جاري الإرسال، يرجى الانتظار..."):
        super().__init__()
        self.setWindowTitle("يرجى الانتظار")
        self.setModal(True)
        self.setFixedSize(300, 100)
        layout = QVBoxLayout(self)
        self.label = QLabel(message)
        layout.addWidget(self.label)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # وضع الانتظار "غير محدد"
        layout.addWidget(self.progress)
        self.setLayout(layout)


def send_message_to_new_number(phone_number, template_content, attachments=None, row_dict=None):
    try:
        # إنشاء نافذة التحميل
        loading = LoadingDialog("جاري إرسال الرسالة، يرجى الانتظار...")
        loading.show()
        QApplication.processEvents()  # تحديث الواجهة

        if attachments is None:
            attachments = []

        final_message = template_content
        if row_dict:
            final_message = process_message_template(template_content, row_dict)

        ph = convert_phone(phone_number)
        encoded_message = urllib.parse.quote(final_message, safe='')
        chat_url = f"https://web.whatsapp.com/send?phone={ph}&text={encoded_message}"
        driver.get(chat_url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "footer div[role='textbox'][contenteditable='true']"))
            )
        except:
            ui_instance.log(f"🔴 الرقم {ph} غير متاح على واتساب. تم التجاوز.")
            loading.close()
            return

        time.sleep(get_sleep_time("sleep_open_chat"))
        if final_message.strip():
            send_text_in_one_message(final_message)

        for att in attachments:
            send_attachment_with_caption(att['filepath'], att.get('caption', ''))
            time.sleep(get_sleep_time("sleep_after_send"))

        ui_instance.log(f"✅ تم إرسال الرسالة بنجاح إلى {phone_number}.")
        loading.close()
    except Exception as e:
        ui_instance.log(f"خطأ في إرسال الرسالة للرقم {phone_number}: {e}")
        loading.close()

############################################################################
# 10) قاعدة بيانات محلية لحفظ حالات الطلب ومعالجة الطلبات
############################################################################

def load_local_status():
    fn = "local_statu.json"
    if os.path.exists(fn):
        with open(fn, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_local_status(status_dict):
    fn = "local_statu.json"
    with open(fn, "w", encoding="utf-8") as f:
        json.dump(status_dict, f, ensure_ascii=False, indent=2)

def check_new_orders(ui_instance):
    """
    فحص Google Sheets وإرسال الرسائل عند الطلبات الجديدة
    أو تغير حالتها (statu)، مع إشعار العمال (admin_settings) إذا لزم.
    """
    try:
        data = fetch_sheet_data_public()
        if not data or len(data) < 2:
            ui_instance.log("الشيت لا يحتوي على بيانات كافية.")
            return
        headers = data[0]
        rows = data[1:]
        phone_index = None
        statu_index = None
        admin_settings = load_admin_settings()
        workers = admin_settings.get("workers", [])

        # إيجاد phone_index و statu_index
        for i, h in enumerate(headers):
            hh = h.lower().strip()
            if hh == "phone":
                phone_index = i
            if hh == "statu":
                statu_index = i

        if phone_index is None:
            ui_instance.log(f"لم يتم العثور على عمود 'Phone'. الأعمدة المتوفرة: {headers}")
            return

        local_statu_db = load_local_status()
        templates = ui_instance.templates

        # تحضير القالب الافتراضي (للطلبات الجديدة)
        default_template = ui_instance.get_default_template_data()
        if default_template.get("statu") == "__DEFAULT__":
            found_index = None
            for idx, t in enumerate(templates):
                if t["statu"] == "__DEFAULT__":
                    found_index = idx
                    break
            if found_index is not None:
                templates[found_index] = default_template
            else:
                templates.append(default_template)

        # المرور على كل صف (طلب)
        for row in rows:
            if not row or len(row) < 1:
                continue
            order_id = row[0].strip()
            if not order_id:
                continue

            row_dict = {}
            for i, val in enumerate(row):
                if i < len(headers):
                    row_dict[headers[i]] = val

            if len(row) <= phone_index:
                continue
            phone_number = row[phone_index].strip()
            if not phone_number:
                continue

            # إرسال القالب الافتراضي إذا كان طلب جديد
            if order_id not in processed_orders:
                dtempl = None
                for t in templates:
                    if t["statu"] == "__DEFAULT__" and t.get("enabled", True):
                        dtempl = t
                        break
                if dtempl:
                    # تحقق مما إذا كان تشيك بوكس الإرسال التلقائي مفعل
                    if ui_instance.default_msg_widget.auto_send_checkbox.isChecked():
                        ui_instance.log(f"طلب جديد {order_id}: إرسال الرسالة الافتراضية للرقم {phone_number}")
                        attachments = dtempl.get("attachments", [])
                        send_message_to_new_number(
                            phone_number,
                            dtempl["content"],
                            attachments,
                            row_dict
                        )
                    else:
                        ui_instance.log(f"طلب جديد {order_id}: تم استقبال الطلب لكن الإرسال الافتراضي غير مفعل.")

                # إشعار العمال (إذا كانت الخاصية __DEFAULT__ مفعلة)
                    for w in workers:
                        wphone = w.get("phone", "").strip()
                        wname = w.get("name", "غير معروف")
                        wnotif = w.get("notifications", {})
                        wmsgs = w.get("message_templates", {})
                        if wphone and wnotif.get("__DEFAULT__", False):
                            msg_for_admin = wmsgs.get("__DEFAULT__", "")
                            if msg_for_admin.strip():
                                msg_for_admin = process_message_template(msg_for_admin, row_dict)
                            else:
                                msg_for_admin = f"طلب جديد {order_id} من العميل {phone_number}."
                            send_message_to_new_number(wphone, msg_for_admin)
                            ui_instance.log(
                                f"تم إرسال الرسالة إلى عضو الإدارة: {wname} | رقم الطلب: {order_id} | الحالة: __DEFAULT__ | للعميل: {phone_number}")

                processed_orders.add(order_id)

            # التحقق من تغيّر الحقل statu
            new_statu = ""
            if statu_index is not None and len(row) > statu_index:
                new_statu = row[statu_index].strip()
            old_statu = local_statu_db.get(order_id, "").strip()

            if new_statu and new_statu != old_statu:
                matched_template = None
                for t in templates:
                    if t.get("enabled", True) and t["statu"] == new_statu and new_statu != "__DEFAULT__":
                        matched_template = t
                        break
                if matched_template:
                    ui_instance.log(f"تغيّر حالة الطلب {order_id}: {old_statu} => {new_statu}.")
                    attachments = matched_template.get("attachments", [])
                    send_message_to_new_number(phone_number, matched_template["content"], attachments, row_dict)

                # إشعار العمال (إذا كانت الحالة مفعلة لديهم)
                for w in workers:
                    wphone = w.get("phone", "").strip()
                    wname = w.get("name", "غير معروف")
                    wnotif = w.get("notifications", {})
                    wmsgs = w.get("message_templates", {})
                    if wphone and wnotif.get(new_statu, False):
                        msg_for_admin = wmsgs.get(new_statu, "")
                        if msg_for_admin.strip():
                            msg_for_admin = process_message_template(msg_for_admin, row_dict)
                        else:
                            msg_for_admin = f"تحديث طلب {order_id}: الحالة تغيرت إلى {new_statu}."
                        send_message_to_new_number(wphone, msg_for_admin)
                        ui_instance.log(
                            f"تم إرسال الرسالة إلى عضو الإدارة: {wname} | رقم الطلب: {order_id} | الحالة: {new_statu} | للعميل: {phone_number}")

                local_statu_db[order_id] = new_statu

        save_local_status(local_statu_db)
        save_templates(templates)

    except Exception as e:
        ui_instance.log(f"خطأ أثناء فحص الشيت: {e}")

############################################################################
# 11) أصناف المرفقات + واجهة التحرير (رسالة افتراضية)
############################################################################

class Attachment:
    def __init__(self, filepath="", caption=""):
        self.filepath = filepath
        self.caption = caption

class DefaultMessageWidget(QWidget):
    def __init__(self, parent_ui, columns):
        super().__init__()
        self.parent_ui = parent_ui
        self.columns = columns
        self.attachments = []

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        lbl_title = QLabel("الرسالة الافتراضية (للطلبات الجديدة)")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(lbl_title)

        # أضف تشيك بوكس لتفعيل الإرسال التلقائي للرسالة الافتراضية
        self.auto_send_checkbox = QCheckBox("تفعيل الإرسال التلقائي للرسالة الافتراضية")
        self.auto_send_checkbox.setChecked(True)  # تُفعّل افتراضيًا
        layout.addWidget(self.auto_send_checkbox)

        txt_layout = QHBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("اكتب نص الرسالة الافتراضية هنا...")
        txt_layout.addWidget(self.text_edit, 3)

        var_frame = QFrame()
        var_layout = QVBoxLayout()
        var_layout.addWidget(QLabel("المتغيرات:"))
        for var in self.columns:
            btn = QPushButton(var)
            btn.clicked.connect(lambda _, v=var: self.insert_variable(v))
            var_layout.addWidget(btn)
        var_frame.setLayout(var_layout)

        scroll = QScrollArea()
        scroll.setWidget(var_frame)
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(150)
        txt_layout.addWidget(scroll, 1)
        layout.addLayout(txt_layout)

        attach_label = QLabel("المرفقات الافتراضية:")
        attach_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(attach_label)

        self.attach_table = QTableWidget()
        self.attach_table.setColumnCount(2)
        self.attach_table.setHorizontalHeaderLabels(["المسار", "التعليق"])
        self.attach_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.attach_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.attach_table.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.attach_table)

        btn_layout = QHBoxLayout()
        self.btn_add_file = QPushButton("إضافة مرفق")
        self.btn_add_file.clicked.connect(self.add_file)
        self.btn_remove_file = QPushButton("حذف المرفق")
        self.btn_remove_file.clicked.connect(self.remove_file)
        self.btn_set_caption = QPushButton("تعديل التعليق")
        self.btn_set_caption.clicked.connect(self.set_caption)
        btn_layout.addWidget(self.btn_add_file)
        btn_layout.addWidget(self.btn_remove_file)
        btn_layout.addWidget(self.btn_set_caption)
        layout.addLayout(btn_layout)

        btn_save = QPushButton("حفظ الرسالة الافتراضية")
        btn_save.clicked.connect(self.save_default_message)
        layout.addWidget(btn_save)

        self.load_default_template()

    def insert_variable(self, var):
        cursor = self.text_edit.textCursor()
        cursor.insertText(f"{{{var}}}")

    def add_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "اختر مرفق")
        if file_path:
            self.attachments.append(Attachment(file_path, ""))
            self.refresh_attach_table()

    def remove_file(self):
        row = self.attach_table.currentRow()
        if 0 <= row < len(self.attachments):
            self.attachments.pop(row)
            self.refresh_attach_table()

    def set_caption(self):
        row = self.attach_table.currentRow()
        if 0 <= row < len(self.attachments):
            att = self.attachments[row]
            cap, ok = QInputDialog.getMultiLineText(self, "تعديل التعليق", "التعليق:", att.caption)
            if ok:
                att.caption = cap
                self.refresh_attach_table()

    def refresh_attach_table(self):
        self.attach_table.setRowCount(len(self.attachments))
        for i, att in enumerate(self.attachments):
            self.attach_table.setItem(i, 0, QTableWidgetItem(att.filepath))
            self.attach_table.setItem(i, 1, QTableWidgetItem(att.caption))
        self.attach_table.resizeColumnsToContents()

    def load_default_template(self):
        default_tpl = None
        for t in self.parent_ui.templates:
            if t.get("statu") == "__DEFAULT__":
                default_tpl = t
                break
        if default_tpl:
            self.text_edit.setPlainText(default_tpl["content"])
            self.attachments = [Attachment(a["filepath"], a["caption"]) for a in default_tpl.get("attachments", [])]
            self.refresh_attach_table()
        else:
            self.text_edit.clear()
            self.attachments = []
            self.refresh_attach_table()

    def get_default_template_data(self):
        return {
            "statu": "__DEFAULT__",
            "content": self.text_edit.toPlainText(),
            "attachments": [{"filepath": a.filepath, "caption": a.caption} for a in self.attachments],
            "enabled": True
        }

    def save_default_message(self):
        default_data = self.get_default_template_data()
        found_index = None
        for i, t in enumerate(self.parent_ui.templates):
            if t["statu"] == "__DEFAULT__":
                found_index = i
                break
        if found_index is not None:
            self.parent_ui.templates[found_index] = default_data
        else:
            self.parent_ui.templates.append(default_data)
        save_templates(self.parent_ui.templates)
        QMessageBox.information(self, "نجاح", "تم حفظ الرسالة الافتراضية بنجاح.")

############################################################################
# 12) الجدول TemplatesTable
############################################################################

class TemplatesTable(QTableWidget):
    def __init__(self, parent_ui):
        super().__init__()
        self.parent_ui = parent_ui
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["تفعيل", "Statu", "نص الرسالة (جزء)", "مرفقات"])
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.cellChanged.connect(self.onCellChanged)

    def update_table(self):
        normal_templates = [t for t in self.parent_ui.templates if t["statu"] != "__DEFAULT__"]
        self.setRowCount(len(normal_templates))
        for i, t in enumerate(normal_templates):
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            state = Qt.Checked if t.get("enabled", True) else Qt.Unchecked
            check_item.setCheckState(state)
            self.setItem(i, 0, check_item)

            statu_item = QTableWidgetItem(t["statu"])
            preview = t["content"][:50] + "..." if len(t["content"]) > 50 else t["content"]
            content_item = QTableWidgetItem(preview)
            attach_count = len(t.get("attachments", []))
            attach_item = QTableWidgetItem(str(attach_count))

            self.setItem(i, 1, statu_item)
            self.setItem(i, 2, content_item)
            self.setItem(i, 3, attach_item)

        self.resizeColumnsToContents()

    def onCellChanged(self, row, column):
        if column == 0:
            normal_templates = [t for t in self.parent_ui.templates if t["statu"] != "__DEFAULT__"]
            if row < 0 or row >= len(normal_templates):
                return
            item = self.item(row, column)
            if item is not None:
                new_state = item.checkState()
                old_data = normal_templates[row]
                real_index = self.parent_ui.templates.index(old_data)
                self.parent_ui.templates[real_index]["enabled"] = (new_state == Qt.Checked)
                save_templates(self.parent_ui.templates)

    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return
        menu = QMenu(self)
        edit_action = menu.addAction("تعديل القالب")
        duplicate_action = menu.addAction("نسخ القالب")
        delete_action = menu.addAction("حذف القالب")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        row = index.row()
        if action == edit_action:
            self.parent_ui.edit_template(row)
        elif action == duplicate_action:
            self.parent_ui.duplicate_template(row)
        elif action == delete_action:
            self.parent_ui.delete_template(row)

############################################################################
# 13) حوار تحرير التعليق للمرفقات
############################################################################

class CaptionEditorDialog(QDialog):
    def __init__(self, parent=None, initial_caption="", variables=None):
        super().__init__(parent)
        self.setWindowTitle("تحرير تعليق المرفق")
        self.result_caption = initial_caption
        self.variables = variables if variables is not None else []

        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(initial_caption)
        layout.addWidget(self.text_edit)

        var_layout = QHBoxLayout()
        var_label = QLabel("المتغيرات:")
        var_layout.addWidget(var_label)
        for var in self.variables:
            btn = QPushButton(var)
            btn.clicked.connect(lambda checked, v=var: self.insert_variable(v))
            var_layout.addWidget(btn)
        layout.addLayout(var_layout)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        self.setLayout(layout)

    def insert_variable(self, var):
        cursor = self.text_edit.textCursor()
        cursor.insertText(f"{{{var}}}")

    def get_caption(self):
        return self.text_edit.toPlainText()

    def accept(self):
        self.result_caption = self.text_edit.toPlainText()
        super().accept()

############################################################################
# 14) حوار إعدادات Google Sheets
############################################################################

class SheetSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إعدادات Google Sheets")
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("معرف الشيت:"))
        self.id_edit = QLineEdit()
        layout.addWidget(self.id_edit)

        layout.addWidget(QLabel("نطاق الشيت:"))
        self.range_edit = QLineEdit()
        layout.addWidget(self.range_edit)

        layout.addWidget(QLabel("مفتاح API:"))
        self.api_edit = QLineEdit()
        layout.addWidget(self.api_edit)

        self.test_btn = QPushButton("اختبار الاتصال")
        self.test_btn.clicked.connect(self.test_connection)
        layout.addWidget(self.test_btn)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        s = load_sheet_settings()
        self.id_edit.setText(s.get("SPREADSHEET_ID", ""))
        self.range_edit.setText(s.get("RANGE_NAME", ""))
        self.api_edit.setText(s.get("API_KEY", ""))

        self.setLayout(layout)
        self.resize(400, 300)

    def test_connection(self):
        test_id = self.id_edit.text().strip()
        test_range = self.range_edit.text().strip()
        test_api = self.api_edit.text().strip()
        if not (test_id and test_range and test_api):
            QMessageBox.warning(self, "تنبيه", "يرجى تعبئة جميع الحقول قبل الاختبار.")
            return
        try:
            service = build('sheets', 'v4', developerKey=test_api)
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=test_id, range=test_range).execute()
            values = result.get('values', [])
            if values:
                QMessageBox.information(self, "نجاح", "تم الاتصال وجلب البيانات بنجاح.")
            else:
                QMessageBox.warning(self, "تنبيه", "اتصال ناجح لكن لا توجد بيانات.")
        except Exception as e:
            QMessageBox.critical(self, "فشل الاتصال", str(e))

    def get_settings(self):
        return {
            "SPREADSHEET_ID": self.id_edit.text().strip(),
            "RANGE_NAME": self.range_edit.text().strip(),
            "API_KEY": self.api_edit.text().strip()
        }

############################################################################
# 15) إعدادات إشعارات الإدارة (متعددة العمال)
############################################################################

class SingleWorkerStatusWidget(QWidget):
    """
    عنصر واجهة لكل حالة (statu) كي يحدد العامل تفعيلها والرسالة الخاصة بها.
    """
    def __init__(self, status_name, enabled, message_text, columns):
        super().__init__()
        self.status_name = status_name
        self.columns = columns

        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)

        self.cb_enable = QCheckBox(f"تفعيل للحالة: {status_name}")
        self.cb_enable.setChecked(enabled)
        self.layout.addWidget(self.cb_enable)

        self.btn_edit_message = QPushButton("تعديل الرسالة")
        self.btn_edit_message.clicked.connect(self.edit_message)
        self.layout.addWidget(self.btn_edit_message)

        self.message_text = message_text

    def edit_message(self):
        dlg = MessageForStatusEditorDialog(None, self.message_text, self.columns, self.status_name)
        if dlg.exec_() == QDialog.Accepted:
            self.message_text = dlg.get_message()

    def get_data(self):
        return {
            "status": self.status_name,
            "enabled": self.cb_enable.isChecked(),
            "message": self.message_text
        }

class MessageForStatusEditorDialog(QDialog):
    """
    نافذة لتحرير الرسالة الخاصة بحالة معيّنة (statu).
    """
    def __init__(self, parent, initial_msg, columns, status_name):
        super().__init__(parent)
        self.setWindowTitle(f"تحرير الرسالة - {status_name}")
        self.result_msg = initial_msg
        self.columns = columns

        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(initial_msg)
        layout.addWidget(self.text_edit)

        var_layout = QHBoxLayout()
        var_label = QLabel("المتغيرات:")
        var_layout.addWidget(var_label)
        for var in self.columns:
            btn = QPushButton(var)
            btn.clicked.connect(lambda _, v=var: self.insert_variable(v))
            var_layout.addWidget(btn)
        layout.addLayout(var_layout)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        self.setLayout(layout)
        self.resize(500, 400)

    def insert_variable(self, var):
        cursor = self.text_edit.textCursor()
        cursor.insertText(f"{{{var}}}")

    def get_message(self):
        return self.text_edit.toPlainText()

    def accept(self):
        self.result_msg = self.text_edit.toPlainText()
        super().accept()

class WorkerTab(QWidget):
    """
    تبويب خاص بكل عامل، حيث يمكنه إدخال اسمه ورقمه وتفعيل/تعطيل حالات
    (statu) مع الرسائل الخاصة بها.
    """
    def __init__(self, worker_data=None, all_statuses=None, columns=None, parent=None):
        super().__init__(parent)
        self.worker_data = worker_data or {
            "name": "عامل جديد",
            "phone": "",
            "notifications": {},
            "message_templates": {}
        }
        self.all_statuses = all_statuses if all_statuses else ["__DEFAULT__"]
        self.columns = columns if columns else []

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        lbl_name = QLabel("اسم العامل:")
        self.main_layout.addWidget(lbl_name)
        self.name_edit = QLineEdit(self.worker_data.get("name", ""))
        self.main_layout.addWidget(self.name_edit)

        lbl_phone = QLabel("رقم الهاتف:")
        self.main_layout.addWidget(lbl_phone)
        self.phone_edit = QLineEdit(self.worker_data.get("phone", ""))
        self.main_layout.addWidget(self.phone_edit)

        self.status_widgets = {}
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        container = QWidget()
        self.status_layout = QVBoxLayout(container)

        for st in self.all_statuses:
            enabled = self.worker_data.get("notifications", {}).get(st, False)
            msg_text = self.worker_data.get("message_templates", {}).get(st, "")
            w = SingleWorkerStatusWidget(st, enabled, msg_text, self.columns)
            self.status_layout.addWidget(w)
            self.status_widgets[st] = w

        container.setLayout(self.status_layout)
        scroll_area.setWidget(container)
        self.main_layout.addWidget(scroll_area)
        self.main_layout.addStretch()

    def get_data(self):
        wdata = {
            "name": self.name_edit.text().strip(),
            "phone": self.phone_edit.text().strip(),
            "notifications": {},
            "message_templates": {}
        }
        for st, widget in self.status_widgets.items():
            d = widget.get_data()
            wdata["notifications"][st] = d["enabled"]
            wdata["message_templates"][st] = d["message"]
        return wdata

class AdminTabsDialog(QDialog):
    """
    نافذة لإدارة أكثر من عامل (tabs لكل عامل).
    """
    def __init__(self, parent=None, all_statuses=None, columns=None):
        super().__init__(parent)
        self.setWindowTitle("إعدادات إشعارات الإدارة (متعددة العمال)")
        self.all_statuses = all_statuses if all_statuses else ["__DEFAULT__"]
        self.columns = columns if columns else []

        layout = QVBoxLayout(self)

        btn_layout = QHBoxLayout()
        self.btn_add_worker = QPushButton("إضافة عامل جديد")
        self.btn_add_worker.clicked.connect(self.add_worker_tab)
        btn_layout.addWidget(self.btn_add_worker)

        self.btn_delete_worker = QPushButton("حذف العامل الحالي")
        self.btn_delete_worker.clicked.connect(self.delete_current_worker_tab)
        btn_layout.addWidget(self.btn_delete_worker)

        layout.addLayout(btn_layout)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        self.setLayout(layout)
        self.resize(600, 500)

        self.admin_settings = load_admin_settings()
        workers = self.admin_settings.get("workers", [])
        for w in workers:
            self.add_worker_tab(w)

    def add_worker_tab(self, worker_data=None):
        if not worker_data:
            worker_data = {
                "name": "عامل جديد",
                "phone": "",
                "notifications": {},
                "message_templates": {}
            }
        wtab = WorkerTab(worker_data, all_statuses=self.all_statuses, columns=self.columns, parent=self.tab_widget)
        idx = self.tab_widget.addTab(wtab, worker_data.get("name", "عامل"))
        self.tab_widget.setCurrentIndex(idx)

    def delete_current_worker_tab(self):
        idx = self.tab_widget.currentIndex()
        if idx >= 0:
            self.tab_widget.removeTab(idx)

    def get_admin_settings(self):
        new_workers = []
        for i in range(self.tab_widget.count()):
            page = self.tab_widget.widget(i)
            wdata = page.get_data()
            self.tab_widget.setTabText(i, wdata["name"])
            new_workers.append(wdata)
        return {"workers": new_workers}

############################################################################
# 16) فتح المتصفح في خيط منفصل (دون خيط للرسائل)
############################################################################

class BrowserOpenerWorker(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    log_signal = pyqtSignal(str)

    def run(self):
        """
        المحاولة الأولى: خلفية (دون واجهة) باستخدام الجلسة
        إذا لم يظهر pane-side نفتح واجهة مرئية لمسح QR.
        """
        # خلفية
        try:
            self.log_signal.emit("تسجيل الدخول إلى واتساب في الخلفية...")
            dr = create_driver(visible=False)
            WebDriverWait(dr, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            try:
                WebDriverWait(dr, 15).until(EC.presence_of_element_located((By.ID, "pane-side")))
                self.finished.emit(dr)
                return
            except:
                self.log_signal.emit("لم يتم العثور على pane-side في الخلفية. نغلقه ونفتح واجهة مرئية لمسح QR.")
                dr.quit()
        except Exception as e:
            self.error.emit(f"فشل فتح المتصفح في الخلفية: {e}")

        # واجهة مرئية
        self.log_signal.emit("فتح المتصفح بشكل مرئي لإتاحة مسح QR ...")
        try:
            dr_vis = create_driver(visible=True)
            WebDriverWait(dr_vis, 60).until(EC.presence_of_element_located((By.ID, "pane-side")))
            self.log_signal.emit("✅ تم تسجيل الدخول بنجاح (مرئي).")
            dr_vis.quit()

            dr_bg = create_driver(visible=False)
            try:
                WebDriverWait(dr_bg, 10).until(EC.presence_of_element_located((By.ID, "pane-side")))
            except:
                pass
            self.finished.emit(dr_bg)
        except Exception as e:
            self.error.emit(f"⚠️ لم يتم تسجيل الدخول في الوقت المحدد في الوضع المرئي. يرجى إعادة المحاولة.\n{e}")
            self.finished.emit(None)

class BrowserOpenerThread(QThread):
    driver_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.worker = BrowserOpenerWorker()
        self.worker.moveToThread(self)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.error_occurred)
        self.worker.log_signal.connect(self.log_signal)

    def run(self):
        self.worker.run()

    def on_finished(self, driver_obj):
        self.driver_ready.emit(driver_obj)

############################################################################
# 17) واجهة التطبيق الرئيسية
############################################################################

class WhatsAppSenderUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("لوحة تحكم إرسال رسائل واتساب")
        self.driver = None
        self.monitor_timer = None
        self.monitoring = False
        self.driver_visible = False

        # صندوق الإشعارات
        self.notification_box = QPlainTextEdit()
        self.notification_box.setReadOnly(True)

        # تحميل القوالب
        self.templates = load_templates()
        # أعمدة جوجل شيت (بدون statu)
        self.columns = self.fetch_columns_excluding_statu()

        main_layout = QHBoxLayout(self)

        # ===== الجانب الأيسر =====
        left_layout = QVBoxLayout()

        # جدول القوالب
        self.templates_table = TemplatesTable(self)
        left_layout.addWidget(self.templates_table)

        # أزرار التحكم
        btn_templates_layout = QHBoxLayout()
        self.btn_add_template = QPushButton("إضافة قالب")
        self.btn_add_template.clicked.connect(self.add_template)
        btn_templates_layout.addWidget(self.btn_add_template)

        self.btn_send_manual = QPushButton("إرسال يدوي")
        self.btn_send_manual.clicked.connect(self.send_manual)
        btn_templates_layout.addWidget(self.btn_send_manual)

        self.monitor_radio = QRadioButton("تفعيل المراقبة")
        self.monitor_radio.toggled.connect(self.toggle_monitoring)
        btn_templates_layout.addWidget(self.monitor_radio)

        left_layout.addLayout(btn_templates_layout)

        # زر فتح المتصفح
        self.open_browser_btn = QPushButton("فتح المتصفح (غير متصل)")
        self.open_browser_btn.setStyleSheet("background-color: red;")
        self.open_browser_btn.clicked.connect(self.open_browser)
        left_layout.addWidget(self.open_browser_btn)

        # حقل الإشعارات
        notif_label = QLabel("إشعارات النظام:")
        left_layout.addWidget(notif_label)
        left_layout.addWidget(self.notification_box)

        # زر إعدادات Google Sheets
        self.sheet_settings_btn = QPushButton("إعدادات Google Sheets")
        self.sheet_settings_btn.clicked.connect(self.open_sheet_settings)
        left_layout.addWidget(self.sheet_settings_btn)

        # زر إعدادات الإدارة
        self.admin_settings_btn = QPushButton("إعدادات إشعارات الإدارة")
        self.admin_settings_btn.clicked.connect(self.open_admin_settings)
        left_layout.addWidget(self.admin_settings_btn)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget, 2)

        # ===== الجانب الأيمن: واجهة الرسالة الافتراضية =====
        self.default_msg_widget = DefaultMessageWidget(self, self.columns)
        main_layout.addWidget(self.default_msg_widget, 3)

        self.setLayout(main_layout)
        self.resize(1200, 600)

        # تحديث الجدول
        self.refresh_templates_table()

    def fetch_columns_excluding_statu(self):
        data = fetch_sheet_data_public()
        if data and len(data) > 0:
            cols = data[0]
            return [c for c in cols if c.lower().strip() != "statu"]
        return []

    def open_sheet_settings(self):
        dlg = SheetSettingsDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            new_settings = dlg.get_settings()
            save_sheet_settings(new_settings)
            global SPREADSHEET_ID, RANGE_NAME, API_KEY
            SPREADSHEET_ID = new_settings.get("SPREADSHEET_ID", "")
            RANGE_NAME = new_settings.get("RANGE_NAME", "")
            API_KEY = new_settings.get("API_KEY", "")
            self.log("تم تحديث إعدادات Google Sheets.")

    def open_admin_settings(self):
        # جميع الحالات (statu) الموجودة في القوالب
        statuses = set()
        for t in self.templates:
            s = t.get("statu", "").strip()
            if s:
                statuses.add(s)
        if "__DEFAULT__" not in statuses:
            statuses.add("__DEFAULT__")
        statuses = list(statuses)

        dlg = AdminTabsDialog(self, all_statuses=statuses, columns=self.columns)
        if dlg.exec_() == QDialog.Accepted:
            new_data = dlg.get_admin_settings()
            save_admin_settings(new_data)
            self.log("تم تحديث إعدادات إشعارات الإدارة (متعددة العمال).")

    def open_browser(self):
        """
        فتح المتصفح في خيط منفصل؛ إذا نجح، driver يصبح جاهزاً.
        """
        global driver
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

        self.log("جاري التحضير...")
        self.browser_thread = BrowserOpenerThread()
        self.browser_thread.log_signal.connect(self.log)
        self.browser_thread.driver_ready.connect(self.on_browser_ready)
        self.browser_thread.error_occurred.connect(self.on_browser_error)
        self.browser_thread.start()

    def on_browser_ready(self, drv):
        global driver
        if drv is not None:
            self.driver = drv
            driver = self.driver
            self.driver_visible = False
            self.open_browser_btn.setText("واتساب متصل (خلفية)")
            self.open_browser_btn.setStyleSheet("background-color: green;")
            self.log("✅ تم تسجيل الدخول بنجاح (خلفية).")
        else:
            self.log("⚠️ فشل فتح المتصفح بشكل صحيح.")
            self.open_browser_btn.setText("فتح المتصفح (غير متصل)")
            self.open_browser_btn.setStyleSheet("background-color: red;")

    def on_browser_error(self, error_msg):
        self.log(error_msg)
        self.open_browser_btn.setText("فتح المتصفح (غير متصل)")
        self.open_browser_btn.setStyleSheet("background-color: red;")
        self.driver = None

    def refresh_templates_table(self):
        self.templates_table.update_table()

    def add_template(self):
        dlg = TemplateEditorDialog(self, self.columns, None)
        if dlg.exec_() == QDialog.Accepted:
            tdata = dlg.get_template_data()
            if not tdata["statu"]:
                QMessageBox.warning(self, "تنبيه", "يجب تحديد حقل Statu لهذا القالب.")
                return
            if "enabled" not in tdata:
                tdata["enabled"] = True
            self.templates.append(tdata)
            save_templates(self.templates)
            self.refresh_templates_table()

    def edit_template(self, row):
        normal_templates = [t for t in self.templates if t["statu"] != "__DEFAULT__"]
        if row < 0 or row >= len(normal_templates):
            return
        old_data = normal_templates[row]
        real_index = self.templates.index(old_data)
        dlg = TemplateEditorDialog(self, self.columns, old_data)
        if dlg.exec_() == QDialog.Accepted:
            new_data = dlg.get_template_data()
            new_data["enabled"] = old_data.get("enabled", True)
            self.templates[real_index] = new_data
            save_templates(self.templates)
            self.refresh_templates_table()

    def duplicate_template(self, row):
        normal_templates = [t for t in self.templates if t["statu"] != "__DEFAULT__"]
        if row < 0 or row >= len(normal_templates):
            return
        old_data = normal_templates[row]
        new_data = copy.deepcopy(old_data)
        new_data["statu"] = new_data["statu"] + "_نسخة"
        self.templates.append(new_data)
        save_templates(self.templates)
        self.refresh_templates_table()

    def delete_template(self, row):
        normal_templates = [t for t in self.templates if t["statu"] != "__DEFAULT__"]
        if row < 0 or row >= len(normal_templates):
            return
        old_data = normal_templates[row]
        res = QMessageBox.question(self, "حذف قالب", "هل أنت متأكد من حذف هذا القالب؟",
                                   QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            self.templates.remove(old_data)
            save_templates(self.templates)
            self.refresh_templates_table()

    def send_manual(self):
        """
        إرسال يدوي دون خيط مستقل.
        """
        if not self.driver:
            QMessageBox.warning(self, "تنبيه", "يرجى فتح المتصفح أولاً (التسجيل).")
            return
        dlg = ManualSendDialog(self, self.columns)
        dlg.exec_()

    def toggle_monitoring(self, checked):
        if not self.driver and checked:
            self.log("يرجى فتح المتصفح قبل البدء بالمراقبة.")
            self.monitor_radio.setChecked(False)
            return
        if not (SPREADSHEET_ID and RANGE_NAME and API_KEY) and checked:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال إعدادات Google Sheets قبل بدء المراقبة.")
            self.monitor_radio.setChecked(False)
            return
        if checked:
            self.monitor_timer = QTimer()
            self.monitor_timer.timeout.connect(lambda: check_new_orders(self))
            self.monitor_timer.start(5000)
            self.monitoring = True
            self.log("تم بدء المراقبة على الشيت.")
        else:
            if self.monitor_timer is not None:
                self.monitor_timer.stop()
            self.monitoring = False
            self.log("تم إيقاف المراقبة.")

    def get_default_template_data(self):
        return self.default_msg_widget.get_default_template_data()

    def log(self, text):
        print(text)
        self.notification_box.appendPlainText(text)

############################################################################
# 18) حوار تحرير القوالب + حوار الإرسال اليدوي
############################################################################

class TemplateEditorDialog(QDialog):
    def __init__(self, parent, columns, template_data=None):
        super().__init__(parent)
        self.parent_ui = parent
        self.columns = columns
        self.attachments = []
        self.setWindowTitle("إنشاء/تعديل القالب")
        self.template_data = template_data or {"statu": "", "content": "", "attachments": [], "enabled": True}

        self.main_layout = QVBoxLayout(self)

        self.main_layout.addWidget(QLabel("قيمة Statu لهذا القالب:"))
        self.statu_line = QLineEdit()
        self.statu_line.setPlaceholderText("مثال: شحن ، دفع ، ... إلخ")
        self.statu_line.setText(self.template_data.get("statu", ""))
        self.main_layout.addWidget(self.statu_line)

        txt_layout = QHBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("أدخل نص الرسالة هنا...")
        self.text_edit.setPlainText(self.template_data.get("content", ""))
        txt_layout.addWidget(self.text_edit, 3)

        var_frame = QFrame()
        var_layout = QVBoxLayout()
        var_layout.addWidget(QLabel("المتغيرات:"))
        for var in self.columns:
            btn = QPushButton(var)
            btn.clicked.connect(lambda _, v=var: self.insert_variable(v))
            var_layout.addWidget(btn)
        var_frame.setLayout(var_layout)

        scroll = QScrollArea()
        scroll.setWidget(var_frame)
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(150)
        txt_layout.addWidget(scroll, 1)

        self.main_layout.addLayout(txt_layout)

        self.attach_table = QTableWidget()
        self.attach_table.setColumnCount(2)
        self.attach_table.setHorizontalHeaderLabels(["المسار", "التعليق"])
        self.attach_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.attach_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.attach_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.main_layout.addWidget(self.attach_table)

        # تحميل المرفقات إن وجدت
        if "attachments" in self.template_data:
            self.attachments = [Attachment(a["filepath"], a["caption"]) for a in self.template_data["attachments"]]

        btn_layout = QHBoxLayout()
        self.btn_add_att = QPushButton("إضافة مرفق")
        self.btn_add_att.clicked.connect(self.add_file)
        self.btn_del_att = QPushButton("حذف المرفق")
        self.btn_del_att.clicked.connect(self.remove_file)
        self.btn_edit_cap = QPushButton("تعديل التعليق")
        self.btn_edit_cap.clicked.connect(self.set_caption)
        btn_layout.addWidget(self.btn_add_att)
        btn_layout.addWidget(self.btn_del_att)
        btn_layout.addWidget(self.btn_edit_cap)
        self.main_layout.addLayout(btn_layout)

        self.refresh_attach_table()

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        self.main_layout.addWidget(btn_box)

        self.setLayout(self.main_layout)
        self.resize(700, 500)

    def insert_variable(self, var):
        cursor = self.text_edit.textCursor()
        cursor.insertText(f"{{{var}}}")

    def add_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "اختر مرفق")
        if file_path:
            self.attachments.append(Attachment(file_path, ""))
            self.refresh_attach_table()

    def remove_file(self):
        row = self.attach_table.currentRow()
        if 0 <= row < len(self.attachments):
            self.attachments.pop(row)
            self.refresh_attach_table()

    def set_caption(self):
        row = self.attach_table.currentRow()
        if 0 <= row < len(self.attachments):
            att = self.attachments[row]
            cap, ok = QInputDialog.getMultiLineText(self, "تعديل التعليق", "التعليق:", att.caption)
            if ok:
                att.caption = cap
                self.refresh_attach_table()

    def refresh_attach_table(self):
        self.attach_table.setRowCount(len(self.attachments))
        for i, att in enumerate(self.attachments):
            self.attach_table.setItem(i, 0, QTableWidgetItem(att.filepath))
            self.attach_table.setItem(i, 1, QTableWidgetItem(att.caption))
        self.attach_table.resizeColumnsToContents()

    def get_template_data(self):
        return {
            "statu": self.statu_line.text().strip(),
            "content": self.text_edit.toPlainText(),
            "attachments": [{"filepath": a.filepath, "caption": a.caption} for a in self.attachments],
            "enabled": self.template_data.get("enabled", True)
        }

class ManualSendDialog(QDialog):
    """
    حوار بسيط لإرسال رسالة يدوية لرقم معين مع مرفقات بشكل مباشر.
    """
    def __init__(self, parent, columns):
        super().__init__(parent)
        self.parent_ui = parent
        self.columns = columns
        self.attachments = []

        self.setWindowTitle("إرسال رسالة يدوية")
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("رقم الهاتف:"))
        self.phone_line = QLineEdit()
        layout.addWidget(self.phone_line)

        txt_layout = QHBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("أدخل نص الرسالة هنا...")
        txt_layout.addWidget(self.text_edit, 3)

        var_frame = QFrame()
        var_layout = QVBoxLayout()
        var_layout.addWidget(QLabel("المتغيرات:"))
        for var in self.columns:
            btn = QPushButton(var)
            btn.clicked.connect(lambda _, v=var: self.insert_variable(v))
            var_layout.addWidget(btn)
        var_frame.setLayout(var_layout)
        scroll = QScrollArea()
        scroll.setWidget(var_frame)
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(150)
        txt_layout.addWidget(scroll, 1)

        layout.addLayout(txt_layout)

        self.attach_table = QTableWidget()
        self.attach_table.setColumnCount(2)
        self.attach_table.setHorizontalHeaderLabels(["المسار", "التعليق"])
        self.attach_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.attach_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.attach_table.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.attach_table)

        btn_layout = QHBoxLayout()
        self.btn_add_att = QPushButton("إضافة مرفق")
        self.btn_add_att.clicked.connect(self.add_file)
        self.btn_del_att = QPushButton("حذف المرفق")
        self.btn_del_att.clicked.connect(self.remove_file)
        self.btn_edit_cap = QPushButton("تعديل التعليق")
        self.btn_edit_cap.clicked.connect(self.set_caption)
        btn_layout.addWidget(self.btn_add_att)
        btn_layout.addWidget(self.btn_del_att)
        btn_layout.addWidget(self.btn_edit_cap)
        layout.addLayout(btn_layout)

        self.refresh_attach_table()

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.send_message)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        self.setLayout(layout)
        self.resize(700, 500)

    def insert_variable(self, var):
        cursor = self.text_edit.textCursor()
        cursor.insertText(f"{{{var}}}")

    def add_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "اختر مرفق")
        if file_path:
            self.attachments.append(Attachment(file_path, ""))
            self.refresh_attach_table()

    def remove_file(self):
        row = self.attach_table.currentRow()
        if 0 <= row < len(self.attachments):
            self.attachments.pop(row)
            self.refresh_attach_table()

    def set_caption(self):
        row = self.attach_table.currentRow()
        if 0 <= row < len(self.attachments):
            att = self.attachments[row]
            cap, ok = QInputDialog.getMultiLineText(self, "تعديل التعليق", "التعليق:", att.caption)
            if ok:
                att.caption = cap
                self.refresh_attach_table()

    def refresh_attach_table(self):
        self.attach_table.setRowCount(len(self.attachments))
        for i, att in enumerate(self.attachments):
            self.attach_table.setItem(i, 0, QTableWidgetItem(att.filepath))
            self.attach_table.setItem(i, 1, QTableWidgetItem(att.caption))
        self.attach_table.resizeColumnsToContents()

    def send_message(self):
        phone_number = self.phone_line.text().strip()
        if not phone_number:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال رقم الهاتف.")
            return
        message_text = self.text_edit.toPlainText().strip()
        attachments = [{"filepath": a.filepath, "caption": a.caption} for a in self.attachments]

        send_message_to_new_number(phone_number, message_text, attachments)
        QMessageBox.information(self, "نجاح", "تم إرسال الرسالة اليدوية.")
        self.accept()

############################################################################
# 19) الدالة الرئيسية
############################################################################

def main():
    app = QApplication(sys.argv)
    qss_file = os.path.join(os.path.dirname(__file__), "style_sheet.qss")
    if os.path.exists(qss_file):
        with open(qss_file, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    window = WhatsAppSenderUI()
    global ui_instance
    ui_instance = window
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
