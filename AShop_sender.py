__version__ = "1.3.4"

######################################

import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
                             QFileDialog, QCheckBox, QHBoxLayout, QColorDialog, QTabWidget, QFormLayout, QTextEdit,
                             QGridLayout, QDialog, QScrollArea, QMessageBox)
from PyQt5.QtGui import QPixmap, QColor, QIcon
from PyQt5.QtCore import Qt, QSize
from PIL import Image
from functools import partial
import qrcode
import svgwrite


class QRCodeApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Advanced QR Code Generator")
        self.setGeometry(100, 100, 800, 600)

        # تعيين أيقونة البرنامج
        self.setWindowIcon(QIcon("E:/PYTHON CODES/QrCode/LOGO/LOGO/LOGO_png.png"))  # تأكد من وضع المسار الصحيح للأيقونة

        # تعيين لون افتراضي للـ QR Code
        self.qr_color = QColor("black")

        main_layout = QVBoxLayout()

        # QR Code Display at the top center
        self.qr_label = QLabel(alignment=Qt.AlignCenter)
        main_layout.addWidget(self.qr_label, alignment=Qt.AlignCenter)

        # Tab widget for QR code types
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_url_tab(), "URL")
        self.tab_widget.addTab(self.create_text_tab(), "Text")
        self.tab_widget.addTab(self.create_vcard_tab(), "vCard")
        self.tab_widget.addTab(self.create_wifi_tab(), "WiFi")
        self.tab_widget.addTab(self.create_email_tab(), "E-mail")
        self.tab_widget.addTab(self.create_sms_tab(), "SMS")

        main_layout.addWidget(self.tab_widget)

        # Right-side options for color and logo
        self.right_options = self.create_right_options()
        main_layout.addLayout(self.right_options)

        # Save buttons
        download_layout = QHBoxLayout()
        self.export_png_button = QPushButton("Export as PNG")
        self.export_png_button.clicked.connect(self.export_as_png)
        self.export_svg_button = QPushButton("Export as SVG")
        self.export_svg_button.clicked.connect(self.export_as_svg)
        download_layout.addWidget(self.export_png_button)
        download_layout.addWidget(self.export_svg_button)
        main_layout.addLayout(download_layout)

        self.setLayout(main_layout)

        # Apply the custom CSS style to buttons and tabs
        self.apply_custom_styles()

    def apply_custom_styles(self):
        # CSS style for buttons with different blue gradients
        export_png_style = """
            QPushButton {
                font-family: inherit;
                font-weight: 500;
                font-size: 18px;
                letter-spacing: 0.05em;
                border-radius: 5px;
                color: ghostwhite;
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #3b8dff, stop:1 #0057e7);
                padding: 5px 12px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #2b6ad9, stop:1 #004bb5);
            }
            QPushButton:pressed {
                transform: scale(0.95);
            }
        """

        export_svg_style = """
            QPushButton {
                font-family: inherit;
                font-weight: 500;
                font-size: 18px;
                letter-spacing: 0.05em;
                border-radius: 5px;
                color: ghostwhite;
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #2a82db, stop:1 #003a99);
                padding: 5px 12px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1e60b2, stop:1 #002d73);
            }
            QPushButton:pressed {
                transform: scale(0.95);
            }
        """

        color_button_style = """
            QPushButton {
                font-family: inherit;
                font-weight: 500;
                font-size: 18px;
                letter-spacing: 0.05em;
                border-radius: 5px;
                color: ghostwhite;
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1f6db8, stop:1 #003380);
                padding: 5px 12px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #144d85, stop:1 #002456);
            }
            QPushButton:pressed {
                transform: scale(0.95);
            }
        """

        browse_button_style = """
            QPushButton {
                font-family: inherit;
                font-weight: 500;
                font-size: 18px;
                letter-spacing: 0.05em;
                border-radius: 5px;
                color: ghostwhite;
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #165893, stop:1 #002456);
                padding: 5px 12px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #0e3e6b, stop:1 #001832);
            }
            QPushButton:pressed {
                transform: scale(0.95);
            }
        """

        # ستايل الزر الخاص باختيار الأيقونة
        icon_button_style = """
            QPushButton {
                font-family: inherit;
                font-weight: 500;
                font-size: 18px;
                letter-spacing: 0.05em;
                border-radius: 5px;
                color: ghostwhite;
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1f6db8, stop:1 #003380);
                padding: 5px 12px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #144d85, stop:1 #002456);
            }
            QPushButton:pressed {
                transform: scale(0.95);
            }
        """

        # Tab style with a general blue gradient
        tab_style = """
            QTabBar::tab {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #3b8dff, stop:1 #0057e7);
                color: ghostwhite;
                padding: 5px 30px;
                margin: 1px;
                border-radius: 5px;
                font-size: 10px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #2b6ad9, stop:1 #004bb5);
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #2b6ad9, stop:1 #004bb5);
            }
        """

        # Apply styles to buttons and tabs
        self.tab_widget.setStyleSheet(tab_style)

        # Apply individual button styles
        self.export_png_button.setStyleSheet(export_png_style)
        self.export_svg_button.setStyleSheet(export_svg_style)
        self.color_button.setStyleSheet(color_button_style)
        self.icon_button.setStyleSheet(icon_button_style)  # تعيين ستايل الزر الخاص بالأيقونة
        self.browse_button.setStyleSheet(browse_button_style)

    def create_right_options(self):
        layout = QVBoxLayout()

        # Color Picker
        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self.choose_color)
        layout.addWidget(QLabel("QR Code Color:"))
        layout.addWidget(self.color_button)

        # Logo Option
        self.add_logo = QCheckBox("Add Logo")
        self.add_logo.setChecked(True)  # تعيين الخيار كمعلم بشكل افتراضي
        self.add_logo.stateChanged.connect(self.toggle_logo)
        layout.addWidget(self.add_logo)

        # Logo Path
        self.logo_path = QLineEdit()
        self.logo_path.setDisabled(False)  # اجعلها قابلة للاستخدام
        layout.addWidget(QLabel("Logo Path:"))
        layout.addWidget(self.logo_path)

        # Upload Logo Button
        self.browse_button = QPushButton("Upload Logo")
        self.browse_button.setDisabled(False)  # اجعلها قابلة للاستخدام
        self.browse_button.clicked.connect(self.select_logo)
        layout.addWidget(self.browse_button)

        # Button to open icon selection window
        self.icon_button = QPushButton("Choose Icon from Folder")
        self.icon_button.setDisabled(False)  # اجعلها قابلة للاستخدام
        self.icon_button.clicked.connect(self.show_icon_selection_window)
        layout.addWidget(self.icon_button)

        return layout

    def toggle_logo(self):
        if self.add_logo.isChecked():
            self.logo_path.setDisabled(False)  # تفعيل حقل إدخال الشعار
            self.browse_button.setDisabled(False)  # تفعيل زر تحميل الشعار
            self.icon_button.setDisabled(False)  # تفعيل زر اختيار الأيقونة
        else:
            self.logo_path.setDisabled(True)  # تعطيل حقل إدخال الشعار
            self.browse_button.setDisabled(True)  # تعطيل زر تحميل الشعار
            self.icon_button.setDisabled(True)  # تعطيل زر اختيار الأيقونة

        self.generate_qr()

    def show_icon_selection_window(self):
        icon_selection_dialog = IconSelectionDialog(self)
        icon_selection_dialog.exec_()

    def select_logo(self):
        logo, _ = QFileDialog.getOpenFileName(self, "Select Logo Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if logo:
            self.logo_path.setText(logo)
        self.generate_qr()

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.qr_color = color
            self.color_button.setStyleSheet(f"background-color: {color.name()};")
            self.generate_qr()

    def create_url_tab(self):
        url_widget = QWidget()
        layout = QFormLayout()
        self.url_input = QLineEdit()
        layout.addRow("URL:", self.url_input)
        url_widget.setLayout(layout)

        # Connect to live preview
        self.url_input.textChanged.connect(self.generate_qr)

        return url_widget

    def create_text_tab(self):
        text_widget = QWidget()
        layout = QFormLayout()
        self.text_input = QTextEdit()
        layout.addRow("Text:", self.text_input)
        text_widget.setLayout(layout)

        # Connect to live preview
        self.text_input.textChanged.connect(self.generate_qr)

        return text_widget

    def create_vcard_tab(self):
        vcard_widget = QWidget()
        layout = QGridLayout()

        # Fields for vCard
        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.mobile = QLineEdit()
        self.phone = QLineEdit()
        self.fax = QLineEdit()
        self.email = QLineEdit()
        self.company = QLineEdit()
        self.job = QLineEdit()
        self.street = QLineEdit()
        self.city = QLineEdit()
        self.zip_code = QLineEdit()
        self.state = QLineEdit()
        self.country = QLineEdit()
        self.website = QLineEdit()

        # Adding fields to layout
        layout.addWidget(QLabel("First Name:"), 0, 0)
        layout.addWidget(self.first_name, 0, 1)
        layout.addWidget(QLabel("Last Name:"), 0, 2)
        layout.addWidget(self.last_name, 0, 3)
        layout.addWidget(QLabel("Mobile:"), 1, 0)
        layout.addWidget(self.mobile, 1, 1)
        layout.addWidget(QLabel("Phone:"), 1, 2)
        layout.addWidget(self.phone, 1, 3)
        layout.addWidget(QLabel("Fax:"), 2, 0)
        layout.addWidget(self.fax, 2, 1)
        layout.addWidget(QLabel("Email:"), 2, 2)
        layout.addWidget(self.email, 2, 3)
        layout.addWidget(QLabel("Company:"), 3, 0)
        layout.addWidget(self.company, 3, 1)
        layout.addWidget(QLabel("Job:"), 3, 2)
        layout.addWidget(self.job, 3, 3)
        layout.addWidget(QLabel("Street:"), 4, 0)
        layout.addWidget(self.street, 4, 1)
        layout.addWidget(QLabel("City:"), 4, 2)
        layout.addWidget(self.city, 4, 3)
        layout.addWidget(QLabel("ZIP:"), 5, 0)
        layout.addWidget(self.zip_code, 5, 1)
        layout.addWidget(QLabel("State:"), 5, 2)
        layout.addWidget(self.state, 5, 3)
        layout.addWidget(QLabel("Country:"), 6, 0)
        layout.addWidget(self.country, 6, 1)
        layout.addWidget(QLabel("Website:"), 6, 2)
        layout.addWidget(self.website, 6, 3)

        # Connect to live preview
        fields = [self.first_name, self.last_name, self.mobile, self.phone, self.fax,
                  self.email, self.company, self.job, self.street, self.city, self.zip_code,
                  self.state, self.country, self.website]
        for field in fields:
            field.textChanged.connect(self.generate_qr)

        vcard_widget.setLayout(layout)
        return vcard_widget

    def create_wifi_tab(self):
        wifi_widget = QWidget()
        layout = QFormLayout()
        self.ssid_input = QLineEdit()
        self.password_input = QLineEdit()
        layout.addRow("SSID:", self.ssid_input)
        layout.addRow("Password:", self.password_input)
        wifi_widget.setLayout(layout)

        # Connect to live preview
        self.ssid_input.textChanged.connect(self.generate_qr)
        self.password_input.textChanged.connect(self.generate_qr)

        return wifi_widget

    def create_email_tab(self):
        email_widget = QWidget()
        layout = QFormLayout()
        self.email_input = QLineEdit()
        self.subject_input = QLineEdit()
        self.message_input = QTextEdit()
        layout.addRow("Email:", self.email_input)
        layout.addRow("Subject:", self.subject_input)
        layout.addRow("Message:", self.message_input)
        email_widget.setLayout(layout)

        # Connect to live preview
        self.email_input.textChanged.connect(self.generate_qr)
        self.subject_input.textChanged.connect(self.generate_qr)
        self.message_input.textChanged.connect(self.generate_qr)

        return email_widget

    def create_sms_tab(self):
        sms_widget = QWidget()
        layout = QFormLayout()
        self.phone_number_input = QLineEdit()
        self.sms_message_input = QTextEdit()
        layout.addRow("Phone Number:", self.phone_number_input)
        layout.addRow("Message:", self.sms_message_input)
        sms_widget.setLayout(layout)

        # Connect to live preview
        self.phone_number_input.textChanged.connect(self.generate_qr)
        self.sms_message_input.textChanged.connect(self.generate_qr)

        return sms_widget

    def generate_qr(self):
        qr_type = self.tab_widget.tabText(self.tab_widget.currentIndex())
        content = ""

        if qr_type == "URL":
            content = self.url_input.text()
        elif qr_type == "Text":
            content = self.text_input.toPlainText()
        elif qr_type == "WiFi":
            ssid = self.ssid_input.text()
            password = self.password_input.text()
            content = f"WIFI:S:{ssid};T:WPA;P:{password};;"
        elif qr_type == "E-mail":
            email = self.email_input.text()
            subject = self.subject_input.text()
            message = self.message_input.toPlainText()
            content = f"mailto:{email}?subject={subject}&body={message}"
        elif qr_type == "SMS":
            phone_number = self.phone_number_input.text()
            message = self.sms_message_input.toPlainText()
            content = f"SMSTO:{phone_number}:{message}"
        elif qr_type == "vCard":
            first_name = self.first_name.text()
            last_name = self.last_name.text()
            mobile = self.mobile.text()
            phone = self.phone.text()
            fax = self.fax.text()
            email = self.email.text()
            company = self.company.text()
            job = self.job.text()
            street = self.street.text()
            city = self.city.text()
            zip_code = self.zip_code.text()
            state = self.state.text()
            country = self.country.text()
            website = self.website.text()

            content = (
                f"BEGIN:VCARD\n"
                f"VERSION:3.0\n"
                f"N:{last_name};{first_name}\n"
                f"FN:{first_name} {last_name}\n"
                f"ORG:{company}\n"
                f"TITLE:{job}\n"
                f"TEL;TYPE=cell:{mobile}\n"
                f"TEL;TYPE=work:{phone}\n"
                f"TEL;TYPE=fax:{fax}\n"
                f"EMAIL:{email}\n"
                f"ADR;TYPE=work:;;{street};{city};{state};{zip_code};{country}\n"
                f"URL:{website}\n"
                f"END:VCARD"
            )

        # إعداد QR Code بأبعاد كبيرة لتقليل البيكسلة
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,  # حجم لكل مربع
            border=4  # الحد الخارجي
        )
        qr.add_data(content)
        qr.make(fit=True)

        img = qr.make_image(fill_color=self.qr_color.name(), back_color="white").convert("RGB")

        if self.add_logo.isChecked() and self.logo_path.text():
            try:
                logo = Image.open(self.logo_path.text())
                qr_width, qr_height = img.size

                # تحديد حجم الشعار كنسبة من حجم QR Code
                logo_size = qr_width // 4  # يمكن تعديل هذه النسبة حسب الحاجة
                logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

                # تحديد موقع الشعار في منتصف QR Code
                logo_position = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)

                # إنشاء مساحة بيضاء للشعار
                white_space_size = logo_size + 20  # إضافة هامش حول الشعار
                white_space_position = ((qr_width - white_space_size) // 2, (qr_height - white_space_size) // 2)

                # رسم مستطيل أبيض
                from PIL import ImageDraw
                draw = ImageDraw.Draw(img)
                draw.rectangle([white_space_position,
                                (white_space_position[0] + white_space_size, white_space_position[1] + white_space_size)],
                               fill="white")

                # لصق الشعار في المساحة البيضاء
                img.paste(logo, logo_position, logo.convert("RGBA"))
            except Exception as e:
                self.show_error_message(f"Error adding logo: {e}")

        img.save("temp_qr.png")
        self.qr_label.setPixmap(QPixmap("temp_qr.png").scaled(200, 200))

    def export_as_png(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save as PNG", "", "PNG Files (*.png)")
            if file_path:
                # حفظ الصورة بأبعاد كبيرة وجودة عالية مباشرةً
                img = Image.open("temp_qr.png")
                img.save(file_path, format="PNG", dpi=(300, 300))
        except Exception as e:
            self.show_error_message(str(e))

    def export_as_svg(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save as SVG", "", "SVG Files (*.svg)")
            if file_path:
                qr_type = self.tab_widget.tabText(self.tab_widget.currentIndex())
                content = ""

                if qr_type == "URL":
                    content = self.url_input.text()
                elif qr_type == "Text":
                    content = self.text_input.toPlainText()
                elif qr_type == "WiFi":
                    ssid = self.ssid_input.text()
                    password = self.password_input.text()
                    content = f"WIFI:S:{ssid};T:WPA;P:{password};;"
                elif qr_type == "E-mail":
                    email = self.email_input.text()
                    subject = self.subject_input.text()
                    message = self.message_input.toPlainText()
                    content = f"mailto:{email}?subject={subject}&body={message}"
                elif qr_type == "SMS":
                    phone_number = self.phone_number_input.text()
                    message = self.sms_message_input.toPlainText()
                    content = f"SMSTO:{phone_number}:{message}"
                elif qr_type == "vCard":
                    first_name = self.first_name.text()
                    last_name = self.last_name.text()
                    mobile = self.mobile.text()
                    phone = self.phone.text()
                    fax = self.fax.text()
                    email = self.email.text()
                    company = self.company.text()
                    job = self.job.text()
                    street = self.street.text()
                    city = self.city.text()
                    zip_code = self.zip_code.text()
                    state = self.state.text()
                    country = self.country.text()
                    website = self.website.text()

                    content = (
                        f"BEGIN:VCARD\n"
                        f"VERSION:3.0\n"
                        f"N:{last_name};{first_name}\n"
                        f"FN:{first_name} {last_name}\n"
                        f"ORG:{company}\n"
                        f"TITLE:{job}\n"
                        f"TEL;TYPE=cell:{mobile}\n"
                        f"TEL;TYPE=work:{phone}\n"
                        f"TEL;TYPE=fax:{fax}\n"
                        f"EMAIL:{email}\n"
                        f"ADR;TYPE=work:;;{street};{city};{state};{zip_code};{country}\n"
                        f"URL:{website}\n"
                        f"END:VCARD"
                    )

                qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
                qr.add_data(content)
                qr.make(fit=True)

                img_size = 300
                dwg = svgwrite.Drawing(file_path, profile='tiny', size=(img_size, img_size))

                # رسم الـ QR Code كنقاط
                for row, qr_row in enumerate(qr.get_matrix()):
                    for col, val in enumerate(qr_row):
                        if val:
                            dwg.add(dwg.rect(insert=(col * (img_size // len(qr_row)), row * (img_size // len(qr_row))),
                                             size=((img_size // len(qr_row)), (img_size // len(qr_row))),
                                             fill=self.qr_color.name()))

                # إدراج الشعار إذا كان موجوداً
                if self.add_logo.isChecked() and self.logo_path.text():
                    try:
                        logo = Image.open(self.logo_path.text())
                        logo_size = img_size // 4
                        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

                        # إنشاء مساحة بيضاء في SVG
                        white_space_size = logo_size + 20
                        white_space_position = ((img_size - white_space_size) // 2, (img_size - white_space_size) // 2)
                        dwg.add(dwg.rect(insert=white_space_position,
                                         size=(white_space_size, white_space_size),
                                         fill="white"))

                        # حفظ الشعار المؤقت
                        logo_with_border_path = "temp_logo_with_border.png"
                        logo_with_border = Image.new("RGBA", (logo_size, logo_size), "white")
                        logo_with_border.paste(logo, (0, 0), logo.convert("RGBA"))
                        logo_with_border.save(logo_with_border_path)

                        # إضافة الشعار إلى SVG في المركز
                        dwg.add(dwg.image(href=logo_with_border_path,
                                          insert=((img_size - logo_size) // 2, (img_size - logo_size) // 2),
                                          size=(logo_size, logo_size)))
                    except Exception as e:
                        self.show_error_message(f"Error adding logo to SVG: {e}")

                dwg.save()
        except Exception as e:
            self.show_error_message(str(e))

    def show_error_message(self, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText("An error occurred")
        error_dialog.setInformativeText(message)
        error_dialog.exec_()


class IconSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Icon")
        self.setFixedSize(400, 300)  # تحديد حجم ثابت للنافذة

        # Scrollable area for icons
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # تفعيل شريط التمرير العمودي دائمًا
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # تعطيل شريط التمرير الأفقي

        # Container widget for the grid layout
        container_widget = QWidget()
        layout = QGridLayout(container_widget)

        # مسار المجلد الذي يحتوي على الأيقونات
        icon_folder_path = "E:/PYTHON CODES/QrCode/LOGO/iconspng"

        # إعداد المتغيرات للتحكم في العرض وعدد الأيقونات في كل صف
        num_columns = 5  # عدد الأيقونات في كل صف
        row = 0
        col = 0

        try:
            for icon_file in os.listdir(icon_folder_path):
                if icon_file.endswith((".png", ".jpg", ".jpeg", ".bmp")):
                    icon_path = os.path.join(icon_folder_path, icon_file)
                    icon_button = QPushButton()
                    icon_button.setIcon(QIcon(icon_path))
                    icon_button.setIconSize(QSize(40, 40))  # حجم الأيقونة داخل الزر
                    icon_button.clicked.connect(partial(self.select_icon, icon_path))
                    layout.addWidget(icon_button, row, col)

                    col += 1
                    if col >= num_columns:  # الانتقال إلى الصف التالي بعد عدد الأيقونات المحدد
                        col = 0
                        row += 1
        except Exception as e:
            print("Error loading icons:", e)

        scroll_area.setWidget(container_widget)

        # إعداد التخطيط العام وإضافة منطقة التمرير
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)

    def select_icon(self, icon_path):
        # تعيين الأيقونة المحددة كالشعار الرئيسي
        self.parent().logo_path.setText(icon_path)
        self.parent().generate_qr()
        self.accept()  # إغلاق النافذة بعد اختيار الأيقونة


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QRCodeApp()
    window.show()
    sys.exit(app.exec_())
