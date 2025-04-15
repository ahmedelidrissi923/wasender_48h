__version__ ="1.3.1"#line:1
import os #line:5
import sys #line:6
import json #line:7
import time #line:8
import urllib .parse #line:9
import atexit #line:10
import signal #line:11
import copy #line:12
import shutil #line:13
from googleapiclient .discovery import build #line:15
from PyQt5 .QtWidgets import (QApplication ,QWidget ,QVBoxLayout ,QHBoxLayout ,QPushButton ,QTableWidget ,QTableWidgetItem ,QAbstractItemView ,QLabel ,QDialog ,QDialogButtonBox ,QTextEdit ,QLineEdit ,QFileDialog ,QMenu ,QMessageBox ,QScrollArea ,QFrame ,QInputDialog ,QPlainTextEdit ,QRadioButton ,QCheckBox ,QTabWidget ,QComboBox )#line:22
from PyQt5 .QtCore import Qt ,QTimer ,QThread ,pyqtSignal ,QObject #line:23
from PyQt5 .QtGui import QContextMenuEvent #line:24
from PyQt5 .QtWidgets import QDialog ,QVBoxLayout ,QProgressBar ,QLabel #line:25
from selenium import webdriver #line:27
from selenium .webdriver .chrome .options import Options #line:28
from selenium .webdriver .chrome .service import Service #line:29
from selenium .webdriver .common .by import By #line:30
from selenium .webdriver .common .keys import Keys #line:31
from selenium .webdriver .support .ui import WebDriverWait #line:32
from selenium .webdriver .support import expected_conditions as EC #line:33
from selenium .webdriver .common .action_chains import ActionChains #line:34
from webdriver_manager .chrome import ChromeDriverManager #line:35
def load_admin_settings ():#line:41
    OO00OO00O000OO000 ="admin_settings.json"#line:42
    if os .path .exists (OO00OO00O000OO000 ):#line:43
        try :#line:44
            with open (OO00OO00O000OO000 ,"r",encoding ="utf-8")as O0O000OOO0O0O0000 :#line:45
                return json .load (O0O000OOO0O0O0000 )#line:46
        except :#line:47
            return {"workers":[]}#line:48
    return {"workers":[]}#line:49
def save_admin_settings (O0O0O0000OOOO0OO0 ):#line:51
    O00OOOOOOO0000000 ="admin_settings.json"#line:52
    with open (O00OOOOOOO0000000 ,"w",encoding ="utf-8")as O00OOOO00OO0OOOOO :#line:53
        json .dump (O0O0O0000OOOO0OO0 ,O00OOOO00OO0OOOOO ,ensure_ascii =False ,indent =2 )#line:54
def load_sheet_settings ():#line:60
    O0OO00O00O0O0OO0O ="sheet_settings.json"#line:61
    if os .path .exists (O0OO00O00O0O0OO0O ):#line:62
        with open (O0OO00O00O0O0OO0O ,"r",encoding ="utf-8")as O0O0OOO00OOOOOO0O :#line:63
            return json .load (O0O0OOO00OOOOOO0O )#line:64
    else :#line:65
        return {"SPREADSHEET_ID":"","RANGE_NAME":"","API_KEY":""}#line:66
def save_sheet_settings (OO0OOOOOOOO00000O ):#line:68
    O00O000O00O0O0O0O ="sheet_settings.json"#line:69
    with open (O00O000O00O0O0O0O ,"w",encoding ="utf-8")as O000OO00O000O00O0 :#line:70
        json .dump (OO0OOOOOOOO00000O ,O000OO00O000O00O0 ,ensure_ascii =False ,indent =2 )#line:71
sheet_settings =load_sheet_settings ()#line:73
SPREADSHEET_ID =sheet_settings .get ("SPREADSHEET_ID","")#line:74
RANGE_NAME =sheet_settings .get ("RANGE_NAME","")#line:75
API_KEY =sheet_settings .get ("API_KEY","")#line:76
def cleanup_driver ():#line:82
    global driver #line:83
    if driver is not None :#line:84
        try :#line:85
            driver .quit ()#line:86
            print ("تم إنهاء جلسة المتصفح بنجاح.")#line:87
        except Exception as O00OO00O00O00O000 :#line:88
            print ("خطأ أثناء إنهاء المتصفح:",O00OO00O00O00O000 )#line:89
atexit .register (cleanup_driver )#line:91
def signal_handler (O0O0000OO000OO00O ,O00O000OOO000OO00 ):#line:93
    cleanup_driver ()#line:94
    sys .exit (0 )#line:95
signal .signal (signal .SIGINT ,signal_handler )#line:97
signal .signal (signal .SIGTERM ,signal_handler )#line:98
def fetch_sheet_data_public ():#line:104
    if not API_KEY or not SPREADSHEET_ID or not RANGE_NAME :#line:105
        return []#line:106
    OO0O0OO0OOOOOO0OO =build ('sheets','v4',developerKey =API_KEY )#line:107
    OOO0O0OOO000O000O =OO0O0OO0OOOOOO0OO .spreadsheets ()#line:108
    OOOOOOOOO0OOO0OOO =OOO0O0OOO000O000O .values ().get (spreadsheetId =SPREADSHEET_ID ,range =RANGE_NAME ).execute ()#line:109
    OOOOO000O0O0O0OOO =OOOOOOOOO0OOO0OOO .get ('values',[])#line:110
    return OOOOO000O0O0O0OOO #line:111
def convert_phone (O00000O0O000OOOOO ):#line:117
    O00000O0O000OOOOO =O00000O0O000OOOOO .strip ()#line:118
    if O00000O0O000OOOOO .startswith ("0"):#line:119
        return "212"+O00000O0O000OOOOO [1 :]#line:120
    elif O00000O0O000OOOOO .startswith ("212"):#line:121
        return O00000O0O000OOOOO #line:122
    else :#line:123
        return O00000O0O000OOOOO #line:124
settings_data ={"sleep_config":{"sleep_open_chat":8.0 ,"sleep_send_text_wait":1.0 ,"sleep_after_send":1.0 ,"sleep_clear_box":0.5 ,"sleep_scroll_wait":0.5 ,"sleep_attach_click_retry":1.0 ,"sleep_file_attach_wait":2.0 }}#line:136
def get_sleep_time (O00O00O00OO0000O0 ):#line:138
    return settings_data .get ("sleep_config",{}).get (O00O00O00OO0000O0 ,2.0 )#line:139
def filter_non_bmp (O0OOOO0O0OOOOO000 ):#line:141
    return ''.join (O0OOOO0O00000OO0O for O0OOOO0O00000OO0O in O0OOOO0O0OOOOO000 if ord (O0OOOO0O00000OO0O )<=0xFFFF )#line:142
def load_templates ():#line:148
    O00OO000000O00000 ="templates.json"#line:149
    if not os .path .exists (O00OO000000O00000 ):#line:150
        return []#line:151
    else :#line:152
        with open (O00OO000000O00000 ,"r",encoding ="utf-8")as O0OO0O00O00O00O00 :#line:153
            O0OO00O0OO0O0O000 =json .load (O0OO0O00O00O00O00 )#line:154
        for O00O0O00000OOOO0O in O0OO00O0OO0O0O000 :#line:155
            if "enabled"not in O00O0O00000OOOO0O :#line:156
                O00O0O00000OOOO0O ["enabled"]=True #line:157
        return O0OO00O0OO0O0O000 #line:158
def save_templates (OOO000OOO0O0OO00O ):#line:160
    for O0000OO0OOO00OO0O in OOO000OOO0O0OO00O :#line:161
        if "enabled"not in O0000OO0OOO00OO0O :#line:162
            O0000OO0OOO00OO0O ["enabled"]=True #line:163
    with open ("templates.json","w",encoding ="utf-8")as O000OO0O0OO00OOOO :#line:164
        json .dump (OOO000OOO0O0OO00O ,O000OO0O0OO00OOOO ,ensure_ascii =False ,indent =2 )#line:165
def create_driver (visible =True ):#line:171
    O0OO0OO0OO0OOO0OO =os .path .dirname (os .path .abspath (__file__ ))#line:172
    O0OOO000000OO0000 =os .path .join (O0OO0OO0OO0OOO0OO ,"whatsapp_profile")#line:173
    OO00O000000OO00OO =Options ()#line:174
    if visible :#line:175
        OO00O000000OO00OO .add_argument ("--start-maximized")#line:176
    else :#line:177
        OO00O000000OO00OO .add_argument ("--headless")#line:178
        OO00O000000OO00OO .add_argument ("--window-size=1400,900")#line:179
    OO00O000000OO00OO .add_argument (f"--user-data-dir={O0OOO000000OO0000}")#line:180
    OO00O000000OO00OO .add_argument ("--disable-extensions")#line:181
    OO00O000000OO00OO .add_argument ("--no-sandbox")#line:182
    OO00O000000OO00OO .add_argument ("--disable-dev-shm-usage")#line:183
    OOO0OO000O0000OOO =Service (ChromeDriverManager ().install ())#line:184
    O0OOOO000OO0O00OO =webdriver .Chrome (service =OOO0OO000O0000OOO ,options =OO00O000000OO00OO )#line:185
    O0OOOO000OO0O00OO .get ("https://web.whatsapp.com")#line:186
    return O0OOOO000OO0O00OO #line:187
driver =None #line:193
ui_instance =None #line:194
processed_orders =set ()#line:195
def clear_message_box ():#line:201
    try :#line:202
        O00O0OO0OOO00OOO0 =WebDriverWait (driver ,10 ).until (EC .element_to_be_clickable ((By .CSS_SELECTOR ,"footer div[role='textbox'][contenteditable='true']")))#line:205
        O00O0OO0OOO00OOO0 .click ()#line:206
        ActionChains (driver ).key_down (Keys .CONTROL ).send_keys ("a").key_up (Keys .CONTROL ).send_keys (Keys .DELETE ).perform ()#line:207
        time .sleep (get_sleep_time ("sleep_clear_box"))#line:208
    except :#line:209
        pass #line:210
def send_text_in_one_message (OO0OOOO0OO000O0O0 ):#line:212
    OO0OOOO0OO000O0O0 =filter_non_bmp (OO0OOOO0OO000O0O0 .strip ())#line:213
    if not OO0OOOO0OO000O0O0 :#line:214
        return #line:215
    try :#line:216
        clear_message_box ()#line:217
        OOOOOOOOOO0O00OO0 =WebDriverWait (driver ,15 ).until (EC .element_to_be_clickable ((By .CSS_SELECTOR ,"footer div[role='textbox'][contenteditable='true']")))#line:220
        OO00OO0000OO0OO00 =OO0OOOO0OO000O0O0 .split ("\n")#line:221
        for O0OOO00O0O000O00O ,O000OO0OOOO000000 in enumerate (OO00OO0000OO0OO00 ):#line:222
            O000OO0OOOO000000 =filter_non_bmp (O000OO0OOOO000000 )#line:223
            if O000OO0OOOO000000 :#line:224
                OOOOOOOOOO0O00OO0 .send_keys (O000OO0OOOO000000 )#line:225
            if O0OOO00O0O000O00O <len (OO00OO0000OO0OO00 )-1 :#line:226
                ActionChains (driver ).key_down (Keys .SHIFT ).send_keys (Keys .ENTER ).key_up (Keys .SHIFT ).perform ()#line:227
        time .sleep (get_sleep_time ("sleep_send_text_wait"))#line:228
        OOOOOOOOOO0O00OO0 .send_keys (Keys .ENTER )#line:229
        time .sleep (get_sleep_time ("sleep_send_text_wait"))#line:230
    except Exception as O00OO000OOOO0O0O0 :#line:231
        ui_instance .log (f"[⚠️] خطأ في إرسال الرسالة النصية: {O00OO000OOOO0O0O0}")#line:232
def click_main_send_button ():#line:234
    for _OO0OO0OO0OOO00000 in range (3 ):#line:235
        try :#line:236
            O0OOO00OO000000OO =WebDriverWait (driver ,5 ).until (EC .element_to_be_clickable ((By .XPATH ,"//div[@aria-label='Send' and @role='button']")))#line:239
            driver .execute_script ("arguments[0].scrollIntoViewIfNeeded();",O0OOO00OO000000OO )#line:240
            time .sleep (get_sleep_time ("sleep_scroll_wait"))#line:241
            O0OOO00OO000000OO .click ()#line:242
            time .sleep (get_sleep_time ("sleep_after_send"))#line:243
            return #line:244
        except :#line:245
            ui_instance .log ("[⚠️] لم نتمكن من النقر على زر الإرسال، إعادة المحاولة...")#line:246
            time .sleep (get_sleep_time ("sleep_attach_click_retry"))#line:247
def send_attachment_with_caption (OO0O0O0OOOO0O00OO ,OO00O000OOOO0O0O0 ):#line:249
    try :#line:250
        OO00000O0O00O0OO0 =filter_non_bmp (OO00O000OOOO0O0O0 .strip ())#line:251
        clear_message_box ()#line:252
        if OO00000O0O00O0OO0 :#line:253
            O0O000O00OOOO0O0O =WebDriverWait (driver ,15 ).until (EC .element_to_be_clickable ((By .CSS_SELECTOR ,"footer div[role='textbox'][contenteditable='true']")))#line:256
            O0000000OO0OO0OOO =OO00000O0O00O0OO0 .split ("\n")#line:257
            for O0O000OO000OO0O00 ,OOO00O0O00OOO0000 in enumerate (O0000000OO0OO0OOO ):#line:258
                OOO00O0O00OOO0000 =filter_non_bmp (OOO00O0O00OOO0000 )#line:259
                if OOO00O0O00OOO0000 :#line:260
                    O0O000O00OOOO0O0O .send_keys (OOO00O0O00OOO0000 )#line:261
                if O0O000OO000OO0O00 <len (O0000000OO0OO0OOO )-1 :#line:262
                    ActionChains (driver ).key_down (Keys .SHIFT ).send_keys (Keys .ENTER ).key_up (Keys .SHIFT ).perform ()#line:263
        time .sleep (get_sleep_time ("sleep_clear_box"))#line:264
        O0OOO0O0OOO0000O0 =None #line:266
        for _O00OO0O0O0OOOO0O0 in range (3 ):#line:267
            try :#line:268
                O0OOO0O0OOO0000O0 =WebDriverWait (driver ,10 ).until (EC .element_to_be_clickable ((By .XPATH ,"//button[@title='Attach']")))#line:271
                driver .execute_script ("arguments[0].scrollIntoViewIfNeeded();",O0OOO0O0OOO0000O0 )#line:272
                time .sleep (get_sleep_time ("sleep_scroll_wait"))#line:273
                O0OOO0O0OOO0000O0 .click ()#line:274
                time .sleep (get_sleep_time ("sleep_attach_click_retry"))#line:275
                break #line:276
            except :#line:277
                ui_instance .log ("[⚠️] لم نتمكن من النقر على زر الإرفاق، إعادة المحاولة...")#line:278
                time .sleep (get_sleep_time ("sleep_attach_click_retry"))#line:279
        if not O0OOO0O0OOO0000O0 :#line:280
            ui_instance .log ("[⚠️] فشل العثور على زر الإرفاق.")#line:281
            return #line:282
        OO0OO0O00O0OOOO0O =WebDriverWait (driver ,15 ).until (EC .presence_of_element_located ((By .XPATH ,"//input[@type='file' and contains(@accept, 'image')]")))#line:286
        driver .execute_script ("arguments[0].style.display = 'block';",OO0OO0O00O0OOOO0O )#line:287
        time .sleep (get_sleep_time ("sleep_scroll_wait"))#line:288
        OO0OO0O00O0OOOO0O .send_keys (OO0O0O0OOOO0O00OO )#line:289
        time .sleep (get_sleep_time ("sleep_file_attach_wait"))#line:290
        click_main_send_button ()#line:291
        clear_message_box ()#line:292
    except Exception as O0000OOO0O0O00OOO :#line:293
        ui_instance .log (f"[⚠️] خطأ في إرسال المرفق: {O0000OOO0O0O00OOO}")#line:294
def process_message_template (OOOO0000OOO00O000 ,OO0OO000O0O000OOO ):#line:296
    O00OO00OO0OOO000O =OOOO0000OOO00O000 #line:297
    for OOO00O000O0000000 ,OO0OO0OO00OO000OO in OO0OO000O0O000OOO .items ():#line:298
        if OOO00O000O0000000 .lower ().strip ()=="statu":#line:299
            continue #line:300
        O0OOO00OO00OOO00O ="{"+OOO00O000O0000000 +"}"#line:301
        O00OO00OO0OOO000O =O00OO00OO0OOO000O .replace (O0OOO00OO00OOO00O ,OO0OO0OO00OO000OO )#line:302
    return O00OO00OO0OOO000O #line:303
class LoadingDialog (QDialog ):#line:306
    def __init__ (O0O0OOOOO00OOO0O0 ,message ="جاري الإرسال، يرجى الانتظار..."):#line:307
        super ().__init__ ()#line:308
        O0O0OOOOO00OOO0O0 .setWindowTitle ("يرجى الانتظار")#line:309
        O0O0OOOOO00OOO0O0 .setModal (True )#line:310
        O0O0OOOOO00OOO0O0 .setFixedSize (300 ,100 )#line:311
        O000O00OOOO000000 =QVBoxLayout (O0O0OOOOO00OOO0O0 )#line:312
        O0O0OOOOO00OOO0O0 .label =QLabel (message )#line:313
        O000O00OOOO000000 .addWidget (O0O0OOOOO00OOO0O0 .label )#line:314
        O0O0OOOOO00OOO0O0 .progress =QProgressBar ()#line:315
        O0O0OOOOO00OOO0O0 .progress .setRange (0 ,0 )#line:316
        O000O00OOOO000000 .addWidget (O0O0OOOOO00OOO0O0 .progress )#line:317
        O0O0OOOOO00OOO0O0 .setLayout (O000O00OOOO000000 )#line:318
def send_message_to_new_number (O00O00O0O0O00O00O ,O0000O0OO0O0O0OO0 ,attachments =None ,row_dict =None ):#line:321
    try :#line:322
        OO0O0O00O0O0OO000 =LoadingDialog ("جاري إرسال الرسالة، يرجى الانتظار...")#line:324
        OO0O0O00O0O0OO000 .show ()#line:325
        QApplication .processEvents ()#line:326
        if attachments is None :#line:328
            attachments =[]#line:329
        OOO00OO0OOOOOO00O =O0000O0OO0O0O0OO0 #line:331
        if row_dict :#line:332
            OOO00OO0OOOOOO00O =process_message_template (O0000O0OO0O0O0OO0 ,row_dict )#line:333
        OO000O0OOO0O00OO0 =convert_phone (O00O00O0O0O00O00O )#line:335
        O00O00O0OOOOO0000 =urllib .parse .quote (OOO00OO0OOOOOO00O ,safe ='')#line:336
        O0OO0000OOOO0O0OO =f"https://web.whatsapp.com/send?phone={OO000O0OOO0O00OO0}&text={O00O00O0OOOOO0000}"#line:337
        driver .get (O0OO0000OOOO0O0OO )#line:338
        try :#line:340
            WebDriverWait (driver ,10 ).until (EC .presence_of_element_located ((By .CSS_SELECTOR ,"footer div[role='textbox'][contenteditable='true']")))#line:343
        except :#line:344
            ui_instance .log (f"🔴 الرقم {OO000O0OOO0O00OO0} غير متاح على واتساب. تم التجاوز.")#line:345
            OO0O0O00O0O0OO000 .close ()#line:346
            return #line:347
        time .sleep (get_sleep_time ("sleep_open_chat"))#line:349
        if OOO00OO0OOOOOO00O .strip ():#line:350
            send_text_in_one_message (OOO00OO0OOOOOO00O )#line:351
        for OO00O000O0000OOO0 in attachments :#line:353
            send_attachment_with_caption (OO00O000O0000OOO0 ['filepath'],OO00O000O0000OOO0 .get ('caption',''))#line:354
            time .sleep (get_sleep_time ("sleep_after_send"))#line:355
        ui_instance .log (f"✅ تم إرسال الرسالة بنجاح إلى {O00O00O0O0O00O00O}.")#line:357
        OO0O0O00O0O0OO000 .close ()#line:358
    except Exception as O00O000O0OOO0O00O :#line:359
        ui_instance .log (f"خطأ في إرسال الرسالة للرقم {O00O00O0O0O00O00O}: {O00O000O0OOO0O00O}")#line:360
        OO0O0O00O0O0OO000 .close ()#line:361
def load_local_status ():#line:367
    OOO0OOO00000OO000 ="local_statu.json"#line:368
    if os .path .exists (OOO0OOO00000OO000 ):#line:369
        with open (OOO0OOO00000OO000 ,"r",encoding ="utf-8")as O0OO00OO0O00OO0OO :#line:370
            return json .load (O0OO00OO0O00OO0OO )#line:371
    return {}#line:372
def save_local_status (O0000OOOO00O0O00O ):#line:374
    O00O0O000OO0O00OO ="local_statu.json"#line:375
    with open (O00O0O000OO0O00OO ,"w",encoding ="utf-8")as O00000O00O0OOOOO0 :#line:376
        json .dump (O0000OOOO00O0O00O ,O00000O00O0OOOOO0 ,ensure_ascii =False ,indent =2 )#line:377
def check_new_orders (O0OO00O0O00O000OO ):#line:379
    ""#line:383
    try :#line:384
        OOOO0000O00O0000O =fetch_sheet_data_public ()#line:385
        if not OOOO0000O00O0000O or len (OOOO0000O00O0000O )<2 :#line:386
            O0OO00O0O00O000OO .log ("الشيت لا يحتوي على بيانات كافية.")#line:387
            return #line:388
        OO0OO00O00OOO0O0O =OOOO0000O00O0000O [0 ]#line:389
        O00000OO0OO0O00O0 =OOOO0000O00O0000O [1 :]#line:390
        O00OO0000O0O0O0OO =None #line:391
        OO000OOOO00O0000O =None #line:392
        O00OOOO0OOO0OOO00 =load_admin_settings ()#line:393
        OOO0O0O00OOO0O00O =O00OOOO0OOO0OOO00 .get ("workers",[])#line:394
        for OO0O00O0O0OO0OO00 ,O00O00O00OO0OOOO0 in enumerate (OO0OO00O00OOO0O0O ):#line:397
            OOO0O00OOOOOO00O0 =O00O00O00OO0OOOO0 .lower ().strip ()#line:398
            if OOO0O00OOOOOO00O0 =="phone":#line:399
                O00OO0000O0O0O0OO =OO0O00O0O0OO0OO00 #line:400
            if OOO0O00OOOOOO00O0 =="statu":#line:401
                OO000OOOO00O0000O =OO0O00O0O0OO0OO00 #line:402
        if O00OO0000O0O0O0OO is None :#line:404
            O0OO00O0O00O000OO .log (f"لم يتم العثور على عمود 'Phone'. الأعمدة المتوفرة: {OO0OO00O00OOO0O0O}")#line:405
            return #line:406
        OO0OO0OOO0OOO00OO =load_local_status ()#line:408
        O000OO00OOOOO0O0O =O0OO00O0O00O000OO .templates #line:409
        OO000O000OOOOOO0O =O0OO00O0O00O000OO .get_default_template_data ()#line:412
        if OO000O000OOOOOO0O .get ("statu")=="__DEFAULT__":#line:413
            OOO00O00O0OO00O0O =None #line:414
            for OO00O00O000O000OO ,OOOO000O0O000O0O0 in enumerate (O000OO00OOOOO0O0O ):#line:415
                if OOOO000O0O000O0O0 ["statu"]=="__DEFAULT__":#line:416
                    OOO00O00O0OO00O0O =OO00O00O000O000OO #line:417
                    break #line:418
            if OOO00O00O0OO00O0O is not None :#line:419
                O000OO00OOOOO0O0O [OOO00O00O0OO00O0O ]=OO000O000OOOOOO0O #line:420
            else :#line:421
                O000OO00OOOOO0O0O .append (OO000O000OOOOOO0O )#line:422
        for OO00O0O0O0OOOOOOO in O00000OO0OO0O00O0 :#line:425
            if not OO00O0O0O0OOOOOOO or len (OO00O0O0O0OOOOOOO )<1 :#line:426
                continue #line:427
            O0OO00O0OO00OOOOO =OO00O0O0O0OOOOOOO [0 ].strip ()#line:428
            if not O0OO00O0OO00OOOOO :#line:429
                continue #line:430
            OO00OO000OO00000O ={}#line:432
            for OO0O00O0O0OO0OO00 ,O00OO0000O0O000O0 in enumerate (OO00O0O0O0OOOOOOO ):#line:433
                if OO0O00O0O0OO0OO00 <len (OO0OO00O00OOO0O0O ):#line:434
                    OO00OO000OO00000O [OO0OO00O00OOO0O0O [OO0O00O0O0OO0OO00 ]]=O00OO0000O0O000O0 #line:435
            if len (OO00O0O0O0OOOOOOO )<=O00OO0000O0O0O0OO :#line:437
                continue #line:438
            OO00OO0O000O000O0 =OO00O0O0O0OOOOOOO [O00OO0000O0O0O0OO ].strip ()#line:439
            if not OO00OO0O000O000O0 :#line:440
                continue #line:441
            if O0OO00O0OO00OOOOO not in processed_orders :#line:444
                O0O0O00OOOOOO0OO0 =None #line:445
                for OOOO000O0O000O0O0 in O000OO00OOOOO0O0O :#line:446
                    if OOOO000O0O000O0O0 ["statu"]=="__DEFAULT__"and OOOO000O0O000O0O0 .get ("enabled",True ):#line:447
                        O0O0O00OOOOOO0OO0 =OOOO000O0O000O0O0 #line:448
                        break #line:449
                if O0O0O00OOOOOO0OO0 :#line:450
                    if O0OO00O0O00O000OO .default_msg_widget .auto_send_checkbox .isChecked ():#line:452
                        O0OO00O0O00O000OO .log (f"طلب جديد {O0OO00O0OO00OOOOO}: إرسال الرسالة الافتراضية للرقم {OO00OO0O000O000O0}")#line:453
                        OO0O0O0OOOOO000OO =O0O0O00OOOOOO0OO0 .get ("attachments",[])#line:454
                        send_message_to_new_number (OO00OO0O000O000O0 ,O0O0O00OOOOOO0OO0 ["content"],OO0O0O0OOOOO000OO ,OO00OO000OO00000O )#line:460
                    else :#line:461
                        O0OO00O0O00O000OO .log (f"طلب جديد {O0OO00O0OO00OOOOO}: تم استقبال الطلب لكن الإرسال الافتراضي غير مفعل.")#line:462
                    for O0OOOO00000O0OO0O in OOO0O0O00OOO0O00O :#line:465
                        O00OOOOO00000O0OO =O0OOOO00000O0OO0O .get ("phone","").strip ()#line:466
                        OO0O00O000OOOO0OO =O0OOOO00000O0OO0O .get ("name","غير معروف")#line:467
                        OOOOO0O00OO0O0OO0 =O0OOOO00000O0OO0O .get ("notifications",{})#line:468
                        OOO0O00O00OOO0OOO =O0OOOO00000O0OO0O .get ("message_templates",{})#line:469
                        if O00OOOOO00000O0OO and OOOOO0O00OO0O0OO0 .get ("__DEFAULT__",False ):#line:470
                            O0OO0O00O0O0O00OO =OOO0O00O00OOO0OOO .get ("__DEFAULT__","")#line:471
                            if O0OO0O00O0O0O00OO .strip ():#line:472
                                O0OO0O00O0O0O00OO =process_message_template (O0OO0O00O0O0O00OO ,OO00OO000OO00000O )#line:473
                            else :#line:474
                                O0OO0O00O0O0O00OO =f"طلب جديد {O0OO00O0OO00OOOOO} من العميل {OO00OO0O000O000O0}."#line:475
                            send_message_to_new_number (O00OOOOO00000O0OO ,O0OO0O00O0O0O00OO )#line:476
                            O0OO00O0O00O000OO .log (f"تم إرسال الرسالة إلى عضو الإدارة: {OO0O00O000OOOO0OO} | رقم الطلب: {O0OO00O0OO00OOOOO} | الحالة: __DEFAULT__ | للعميل: {OO00OO0O000O000O0}")#line:478
                processed_orders .add (O0OO00O0OO00OOOOO )#line:480
            OOOOO0OOOO0O00000 =""#line:483
            if OO000OOOO00O0000O is not None and len (OO00O0O0O0OOOOOOO )>OO000OOOO00O0000O :#line:484
                OOOOO0OOOO0O00000 =OO00O0O0O0OOOOOOO [OO000OOOO00O0000O ].strip ()#line:485
            O0OOOO0OOOOOO00OO =OO0OO0OOO0OOO00OO .get (O0OO00O0OO00OOOOO ,"").strip ()#line:486
            if OOOOO0OOOO0O00000 and OOOOO0OOOO0O00000 !=O0OOOO0OOOOOO00OO :#line:488
                OO0OOOOOOOOOO0O00 =None #line:489
                for OOOO000O0O000O0O0 in O000OO00OOOOO0O0O :#line:490
                    if OOOO000O0O000O0O0 .get ("enabled",True )and OOOO000O0O000O0O0 ["statu"]==OOOOO0OOOO0O00000 and OOOOO0OOOO0O00000 !="__DEFAULT__":#line:491
                        OO0OOOOOOOOOO0O00 =OOOO000O0O000O0O0 #line:492
                        break #line:493
                if OO0OOOOOOOOOO0O00 :#line:494
                    O0OO00O0O00O000OO .log (f"تغيّر حالة الطلب {O0OO00O0OO00OOOOO}: {O0OOOO0OOOOOO00OO} => {OOOOO0OOOO0O00000}.")#line:495
                    OO0O0O0OOOOO000OO =OO0OOOOOOOOOO0O00 .get ("attachments",[])#line:496
                    send_message_to_new_number (OO00OO0O000O000O0 ,OO0OOOOOOOOOO0O00 ["content"],OO0O0O0OOOOO000OO ,OO00OO000OO00000O )#line:497
                for O0OOOO00000O0OO0O in OOO0O0O00OOO0O00O :#line:500
                    O00OOOOO00000O0OO =O0OOOO00000O0OO0O .get ("phone","").strip ()#line:501
                    OO0O00O000OOOO0OO =O0OOOO00000O0OO0O .get ("name","غير معروف")#line:502
                    OOOOO0O00OO0O0OO0 =O0OOOO00000O0OO0O .get ("notifications",{})#line:503
                    OOO0O00O00OOO0OOO =O0OOOO00000O0OO0O .get ("message_templates",{})#line:504
                    if O00OOOOO00000O0OO and OOOOO0O00OO0O0OO0 .get (OOOOO0OOOO0O00000 ,False ):#line:505
                        O0OO0O00O0O0O00OO =OOO0O00O00OOO0OOO .get (OOOOO0OOOO0O00000 ,"")#line:506
                        if O0OO0O00O0O0O00OO .strip ():#line:507
                            O0OO0O00O0O0O00OO =process_message_template (O0OO0O00O0O0O00OO ,OO00OO000OO00000O )#line:508
                        else :#line:509
                            O0OO0O00O0O0O00OO =f"تحديث طلب {O0OO00O0OO00OOOOO}: الحالة تغيرت إلى {OOOOO0OOOO0O00000}."#line:510
                        send_message_to_new_number (O00OOOOO00000O0OO ,O0OO0O00O0O0O00OO )#line:511
                        O0OO00O0O00O000OO .log (f"تم إرسال الرسالة إلى عضو الإدارة: {OO0O00O000OOOO0OO} | رقم الطلب: {O0OO00O0OO00OOOOO} | الحالة: {OOOOO0OOOO0O00000} | للعميل: {OO00OO0O000O000O0}")#line:513
                OO0OO0OOO0OOO00OO [O0OO00O0OO00OOOOO ]=OOOOO0OOOO0O00000 #line:515
        save_local_status (OO0OO0OOO0OOO00OO )#line:517
        save_templates (O000OO00OOOOO0O0O )#line:518
    except Exception as OOO0000OOOO000OO0 :#line:520
        O0OO00O0O00O000OO .log (f"خطأ أثناء فحص الشيت: {OOO0000OOOO000OO0}")#line:521
class Attachment :#line:527
    def __init__ (O0OO0OO0OO00O00OO ,filepath ="",caption =""):#line:528
        O0OO0OO0OO00O00OO .filepath =filepath #line:529
        O0OO0OO0OO00O00OO .caption =caption #line:530
class DefaultMessageWidget (QWidget ):#line:532
    def __init__ (O00O0O0OO00O00O0O ,OO00OOO0OO00OO0OO ,O0000OOOOOO0O000O ):#line:533
        super ().__init__ ()#line:534
        O00O0O0OO00O00O0O .parent_ui =OO00OOO0OO00OO0OO #line:535
        O00O0O0OO00O00O0O .columns =O0000OOOOOO0O000O #line:536
        O00O0O0OO00O00O0O .attachments =[]#line:537
        OO0OO000O0O0OO0OO =QVBoxLayout (O00O0O0OO00O00O0O )#line:539
        O00O0O0OO00O00O0O .setLayout (OO0OO000O0O0OO0OO )#line:540
        OOOOOO0OOO0OOO000 =QLabel ("الرسالة الافتراضية (للطلبات الجديدة)")#line:542
        OOOOOO0OOO0OOO000 .setStyleSheet ("font-weight: bold; font-size: 14px;")#line:543
        OO0OO000O0O0OO0OO .addWidget (OOOOOO0OOO0OOO000 )#line:544
        O00O0O0OO00O00O0O .auto_send_checkbox =QCheckBox ("تفعيل الإرسال التلقائي للرسالة الافتراضية")#line:547
        O00O0O0OO00O00O0O .auto_send_checkbox .setChecked (True )#line:548
        OO0OO000O0O0OO0OO .addWidget (O00O0O0OO00O00O0O .auto_send_checkbox )#line:549
        O00OO00OOO0O000OO =QHBoxLayout ()#line:551
        O00O0O0OO00O00O0O .text_edit =QTextEdit ()#line:552
        O00O0O0OO00O00O0O .text_edit .setPlaceholderText ("اكتب نص الرسالة الافتراضية هنا...")#line:553
        O00OO00OOO0O000OO .addWidget (O00O0O0OO00O00O0O .text_edit ,3 )#line:554
        O00OO0O0O00000OO0 =QFrame ()#line:556
        O0OO0OOO00O000OO0 =QVBoxLayout ()#line:557
        O0OO0OOO00O000OO0 .addWidget (QLabel ("المتغيرات:"))#line:558
        for O00O0OOOO0O000000 in O00O0O0OO00O00O0O .columns :#line:559
            O0O0O0O00O0O000O0 =QPushButton (O00O0OOOO0O000000 )#line:560
            O0O0O0O00O0O000O0 .clicked .connect (lambda _O0OO00OO000O0OO00 ,v =O00O0OOOO0O000000 :O00O0O0OO00O00O0O .insert_variable (v ))#line:561
            O0OO0OOO00O000OO0 .addWidget (O0O0O0O00O0O000O0 )#line:562
        O00OO0O0O00000OO0 .setLayout (O0OO0OOO00O000OO0 )#line:563
        OOO0OO0O0OOO0OO0O =QScrollArea ()#line:565
        OOO0OO0O0OOO0OO0O .setWidget (O00OO0O0O00000OO0 )#line:566
        OOO0OO0O0OOO0OO0O .setWidgetResizable (True )#line:567
        OOO0OO0O0OOO0OO0O .setFixedWidth (150 )#line:568
        O00OO00OOO0O000OO .addWidget (OOO0OO0O0OOO0OO0O ,1 )#line:569
        OO0OO000O0O0OO0OO .addLayout (O00OO00OOO0O000OO )#line:570
        OO0O0O0O0O00000O0 =QLabel ("المرفقات الافتراضية:")#line:572
        OO0O0O0O0O00000O0 .setStyleSheet ("font-weight: bold;")#line:573
        OO0OO000O0O0OO0OO .addWidget (OO0O0O0O0O00000O0 )#line:574
        O00O0O0OO00O00O0O .attach_table =QTableWidget ()#line:576
        O00O0O0OO00O00O0O .attach_table .setColumnCount (2 )#line:577
        O00O0O0OO00O00O0O .attach_table .setHorizontalHeaderLabels (["المسار","التعليق"])#line:578
        O00O0O0OO00O00O0O .attach_table .setEditTriggers (QAbstractItemView .NoEditTriggers )#line:579
        O00O0O0OO00O00O0O .attach_table .setSelectionBehavior (QAbstractItemView .SelectRows )#line:580
        O00O0O0OO00O00O0O .attach_table .setSelectionMode (QAbstractItemView .SingleSelection )#line:581
        OO0OO000O0O0OO0OO .addWidget (O00O0O0OO00O00O0O .attach_table )#line:582
        O0OOOOO0O00OOOOO0 =QHBoxLayout ()#line:584
        O00O0O0OO00O00O0O .btn_add_file =QPushButton ("إضافة مرفق")#line:585
        O00O0O0OO00O00O0O .btn_add_file .clicked .connect (O00O0O0OO00O00O0O .add_file )#line:586
        O00O0O0OO00O00O0O .btn_remove_file =QPushButton ("حذف المرفق")#line:587
        O00O0O0OO00O00O0O .btn_remove_file .clicked .connect (O00O0O0OO00O00O0O .remove_file )#line:588
        O00O0O0OO00O00O0O .btn_set_caption =QPushButton ("تعديل التعليق")#line:589
        O00O0O0OO00O00O0O .btn_set_caption .clicked .connect (O00O0O0OO00O00O0O .set_caption )#line:590
        O0OOOOO0O00OOOOO0 .addWidget (O00O0O0OO00O00O0O .btn_add_file )#line:591
        O0OOOOO0O00OOOOO0 .addWidget (O00O0O0OO00O00O0O .btn_remove_file )#line:592
        O0OOOOO0O00OOOOO0 .addWidget (O00O0O0OO00O00O0O .btn_set_caption )#line:593
        OO0OO000O0O0OO0OO .addLayout (O0OOOOO0O00OOOOO0 )#line:594
        OO0OOOOOO00OO0OO0 =QPushButton ("حفظ الرسالة الافتراضية")#line:596
        OO0OOOOOO00OO0OO0 .clicked .connect (O00O0O0OO00O00O0O .save_default_message )#line:597
        OO0OO000O0O0OO0OO .addWidget (OO0OOOOOO00OO0OO0 )#line:598
        O00O0O0OO00O00O0O .load_default_template ()#line:600
    def insert_variable (O0000OOO0O00O000O ,OOO0O0OO000000OOO ):#line:602
        OOOOOO0000O0OO00O =O0000OOO0O00O000O .text_edit .textCursor ()#line:603
        OOOOOO0000O0OO00O .insertText (f"{{{OOO0O0OO000000OOO}}}")#line:604
    def add_file (OOOO00OOO000O0O0O ):#line:606
        OO0O00O00O000O0O0 ,_OOOO0000OOO00OO0O =QFileDialog .getOpenFileName (OOOO00OOO000O0O0O ,"اختر مرفق")#line:607
        if OO0O00O00O000O0O0 :#line:608
            OOOO00OOO000O0O0O .attachments .append (Attachment (OO0O00O00O000O0O0 ,""))#line:609
            OOOO00OOO000O0O0O .refresh_attach_table ()#line:610
    def remove_file (O000OO0O0000O0000 ):#line:612
        OO0000000O0OOO00O =O000OO0O0000O0000 .attach_table .currentRow ()#line:613
        if 0 <=OO0000000O0OOO00O <len (O000OO0O0000O0000 .attachments ):#line:614
            O000OO0O0000O0000 .attachments .pop (OO0000000O0OOO00O )#line:615
            O000OO0O0000O0000 .refresh_attach_table ()#line:616
    def set_caption (O0O00OOOO0OOO0O00 ):#line:618
        OOOO0000O0OO0O00O =O0O00OOOO0OOO0O00 .attach_table .currentRow ()#line:619
        if 0 <=OOOO0000O0OO0O00O <len (O0O00OOOO0OOO0O00 .attachments ):#line:620
            O0OO00OO00O0OO0O0 =O0O00OOOO0OOO0O00 .attachments [OOOO0000O0OO0O00O ]#line:621
            OO0O00O0O00OO0O0O ,OOO0O00OOOO00O0OO =QInputDialog .getMultiLineText (O0O00OOOO0OOO0O00 ,"تعديل التعليق","التعليق:",O0OO00OO00O0OO0O0 .caption )#line:622
            if OOO0O00OOOO00O0OO :#line:623
                O0OO00OO00O0OO0O0 .caption =OO0O00O0O00OO0O0O #line:624
                O0O00OOOO0OOO0O00 .refresh_attach_table ()#line:625
    def refresh_attach_table (OOOO00O0O00OOOOO0 ):#line:627
        OOOO00O0O00OOOOO0 .attach_table .setRowCount (len (OOOO00O0O00OOOOO0 .attachments ))#line:628
        for OOO00000000000OOO ,O000OO0O0OOO0OOO0 in enumerate (OOOO00O0O00OOOOO0 .attachments ):#line:629
            OOOO00O0O00OOOOO0 .attach_table .setItem (OOO00000000000OOO ,0 ,QTableWidgetItem (O000OO0O0OOO0OOO0 .filepath ))#line:630
            OOOO00O0O00OOOOO0 .attach_table .setItem (OOO00000000000OOO ,1 ,QTableWidgetItem (O000OO0O0OOO0OOO0 .caption ))#line:631
        OOOO00O0O00OOOOO0 .attach_table .resizeColumnsToContents ()#line:632
    def load_default_template (OOO000O0000O0O0OO ):#line:634
        OOOO000OOO0OOOOOO =None #line:635
        for OOOO00O0000O0OOO0 in OOO000O0000O0O0OO .parent_ui .templates :#line:636
            if OOOO00O0000O0OOO0 .get ("statu")=="__DEFAULT__":#line:637
                OOOO000OOO0OOOOOO =OOOO00O0000O0OOO0 #line:638
                break #line:639
        if OOOO000OOO0OOOOOO :#line:640
            OOO000O0000O0O0OO .text_edit .setPlainText (OOOO000OOO0OOOOOO ["content"])#line:641
            OOO000O0000O0O0OO .attachments =[Attachment (O0O00O000O0OO00O0 ["filepath"],O0O00O000O0OO00O0 ["caption"])for O0O00O000O0OO00O0 in OOOO000OOO0OOOOOO .get ("attachments",[])]#line:642
            OOO000O0000O0O0OO .refresh_attach_table ()#line:643
        else :#line:644
            OOO000O0000O0O0OO .text_edit .clear ()#line:645
            OOO000O0000O0O0OO .attachments =[]#line:646
            OOO000O0000O0O0OO .refresh_attach_table ()#line:647
    def get_default_template_data (O000OO0O0O0O0O0OO ):#line:649
        return {"statu":"__DEFAULT__","content":O000OO0O0O0O0O0OO .text_edit .toPlainText (),"attachments":[{"filepath":OOO00OO00O00000OO .filepath ,"caption":OOO00OO00O00000OO .caption }for OOO00OO00O00000OO in O000OO0O0O0O0O0OO .attachments ],"enabled":True }#line:655
    def save_default_message (OO00O00O0OOOOO000 ):#line:657
        OOOOO000OO0O00OO0 =OO00O00O0OOOOO000 .get_default_template_data ()#line:658
        O000O0O00OOO00OO0 =None #line:659
        for OO0O000OO00O0O00O ,OOO00O0O0O000OO00 in enumerate (OO00O00O0OOOOO000 .parent_ui .templates ):#line:660
            if OOO00O0O0O000OO00 ["statu"]=="__DEFAULT__":#line:661
                O000O0O00OOO00OO0 =OO0O000OO00O0O00O #line:662
                break #line:663
        if O000O0O00OOO00OO0 is not None :#line:664
            OO00O00O0OOOOO000 .parent_ui .templates [O000O0O00OOO00OO0 ]=OOOOO000OO0O00OO0 #line:665
        else :#line:666
            OO00O00O0OOOOO000 .parent_ui .templates .append (OOOOO000OO0O00OO0 )#line:667
        save_templates (OO00O00O0OOOOO000 .parent_ui .templates )#line:668
        QMessageBox .information (OO00O00O0OOOOO000 ,"نجاح","تم حفظ الرسالة الافتراضية بنجاح.")#line:669
class TemplatesTable (QTableWidget ):#line:675
    def __init__ (OOO00O0OOOOO00000 ,OO0O0OO0OO0000O00 ):#line:676
        super ().__init__ ()#line:677
        OOO00O0OOOOO00000 .parent_ui =OO0O0OO0OO0000O00 #line:678
        OOO00O0OOOOO00000 .setColumnCount (4 )#line:679
        OOO00O0OOOOO00000 .setHorizontalHeaderLabels (["تفعيل","Statu","نص الرسالة (جزء)","مرفقات"])#line:680
        OOO00O0OOOOO00000 .setEditTriggers (QAbstractItemView .NoEditTriggers )#line:681
        OOO00O0OOOOO00000 .setSelectionBehavior (QAbstractItemView .SelectRows )#line:682
        OOO00O0OOOOO00000 .setSelectionMode (QAbstractItemView .SingleSelection )#line:683
        OOO00O0OOOOO00000 .cellChanged .connect (OOO00O0OOOOO00000 .onCellChanged )#line:684
    def update_table (OOOO000000O0OOO00 ):#line:686
        O0O000OO00O00OO00 =[OO00OO0O0000O0000 for OO00OO0O0000O0000 in OOOO000000O0OOO00 .parent_ui .templates if OO00OO0O0000O0000 ["statu"]!="__DEFAULT__"]#line:687
        OOOO000000O0OOO00 .setRowCount (len (O0O000OO00O00OO00 ))#line:688
        for O0O00O0O00000O0O0 ,O0O0O00O00OOOOO00 in enumerate (O0O000OO00O00OO00 ):#line:689
            O00OOO00OO000O00O =QTableWidgetItem ()#line:690
            O00OOO00OO000O00O .setFlags (Qt .ItemIsUserCheckable |Qt .ItemIsEnabled )#line:691
            OOO000O00O0O00000 =Qt .Checked if O0O0O00O00OOOOO00 .get ("enabled",True )else Qt .Unchecked #line:692
            O00OOO00OO000O00O .setCheckState (OOO000O00O0O00000 )#line:693
            OOOO000000O0OOO00 .setItem (O0O00O0O00000O0O0 ,0 ,O00OOO00OO000O00O )#line:694
            OOO00O0OO0000O0O0 =QTableWidgetItem (O0O0O00O00OOOOO00 ["statu"])#line:696
            OO0O0OO000OO00000 =O0O0O00O00OOOOO00 ["content"][:50 ]+"..."if len (O0O0O00O00OOOOO00 ["content"])>50 else O0O0O00O00OOOOO00 ["content"]#line:697
            O00OO0OO0OO00O00O =QTableWidgetItem (OO0O0OO000OO00000 )#line:698
            OO0OOO00O0O00O0O0 =len (O0O0O00O00OOOOO00 .get ("attachments",[]))#line:699
            O0OO0O0O0OO0O0O00 =QTableWidgetItem (str (OO0OOO00O0O00O0O0 ))#line:700
            OOOO000000O0OOO00 .setItem (O0O00O0O00000O0O0 ,1 ,OOO00O0OO0000O0O0 )#line:702
            OOOO000000O0OOO00 .setItem (O0O00O0O00000O0O0 ,2 ,O00OO0OO0OO00O00O )#line:703
            OOOO000000O0OOO00 .setItem (O0O00O0O00000O0O0 ,3 ,O0OO0O0O0OO0O0O00 )#line:704
        OOOO000000O0OOO00 .resizeColumnsToContents ()#line:706
    def onCellChanged (OO0O0O00O0000OOO0 ,O0OO00OOOO0OOO0OO ,O0O000OOOO0O0O000 ):#line:708
        if O0O000OOOO0O0O000 ==0 :#line:709
            OOO0OOO0OO00OO0O0 =[O00OOOO00O0OO0OO0 for O00OOOO00O0OO0OO0 in OO0O0O00O0000OOO0 .parent_ui .templates if O00OOOO00O0OO0OO0 ["statu"]!="__DEFAULT__"]#line:710
            if O0OO00OOOO0OOO0OO <0 or O0OO00OOOO0OOO0OO >=len (OOO0OOO0OO00OO0O0 ):#line:711
                return #line:712
            O0O0OOOOOO00OO00O =OO0O0O00O0000OOO0 .item (O0OO00OOOO0OOO0OO ,O0O000OOOO0O0O000 )#line:713
            if O0O0OOOOOO00OO00O is not None :#line:714
                O00O000O000OOOOO0 =O0O0OOOOOO00OO00O .checkState ()#line:715
                OOO0OOO00OO00O0O0 =OOO0OOO0OO00OO0O0 [O0OO00OOOO0OOO0OO ]#line:716
                OO00O0O00O00000OO =OO0O0O00O0000OOO0 .parent_ui .templates .index (OOO0OOO00OO00O0O0 )#line:717
                OO0O0O00O0000OOO0 .parent_ui .templates [OO00O0O00O00000OO ]["enabled"]=(O00O000O000OOOOO0 ==Qt .Checked )#line:718
                save_templates (OO0O0O00O0000OOO0 .parent_ui .templates )#line:719
    def contextMenuEvent (OO00OOO00OO00O00O ,OOOOO00O000O0O000 ):#line:721
        O00O00O0O00000000 =OO00OOO00OO00O00O .indexAt (OOOOO00O000O0O000 .pos ())#line:722
        if not O00O00O0O00000000 .isValid ():#line:723
            return #line:724
        O0OO00O00OO0O0000 =QMenu (OO00OOO00OO00O00O )#line:725
        OO0O000OOO0000000 =O0OO00O00OO0O0000 .addAction ("تعديل القالب")#line:726
        OOOOO0O0000OOO00O =O0OO00O00OO0O0000 .addAction ("نسخ القالب")#line:727
        O0OOO0OO0O000000O =O0OO00O00OO0O0000 .addAction ("حذف القالب")#line:728
        OOO0O000O0O0O0000 =O0OO00O00OO0O0000 .exec_ (OO00OOO00OO00O00O .mapToGlobal (OOOOO00O000O0O000 .pos ()))#line:729
        O0O0000OOO0O000OO =O00O00O0O00000000 .row ()#line:730
        if OOO0O000O0O0O0000 ==OO0O000OOO0000000 :#line:731
            OO00OOO00OO00O00O .parent_ui .edit_template (O0O0000OOO0O000OO )#line:732
        elif OOO0O000O0O0O0000 ==OOOOO0O0000OOO00O :#line:733
            OO00OOO00OO00O00O .parent_ui .duplicate_template (O0O0000OOO0O000OO )#line:734
        elif OOO0O000O0O0O0000 ==O0OOO0OO0O000000O :#line:735
            OO00OOO00OO00O00O .parent_ui .delete_template (O0O0000OOO0O000OO )#line:736
class CaptionEditorDialog (QDialog ):#line:742
    def __init__ (OO0OO0OO0O00OOOO0 ,parent =None ,initial_caption ="",variables =None ):#line:743
        super ().__init__ (parent )#line:744
        OO0OO0OO0O00OOOO0 .setWindowTitle ("تحرير تعليق المرفق")#line:745
        OO0OO0OO0O00OOOO0 .result_caption =initial_caption #line:746
        OO0OO0OO0O00OOOO0 .variables =variables if variables is not None else []#line:747
        O0O00OO00000OO0OO =QVBoxLayout (OO0OO0OO0O00OOOO0 )#line:749
        OO0OO0OO0O00OOOO0 .text_edit =QTextEdit ()#line:750
        OO0OO0OO0O00OOOO0 .text_edit .setPlainText (initial_caption )#line:751
        O0O00OO00000OO0OO .addWidget (OO0OO0OO0O00OOOO0 .text_edit )#line:752
        O0O0OOO00O00OO0OO =QHBoxLayout ()#line:754
        O0OOO00O000OO0O0O =QLabel ("المتغيرات:")#line:755
        O0O0OOO00O00OO0OO .addWidget (O0OOO00O000OO0O0O )#line:756
        for O00O0O00O00OO0000 in OO0OO0OO0O00OOOO0 .variables :#line:757
            O0OOOOO0OOOOOOOOO =QPushButton (O00O0O00O00OO0000 )#line:758
            O0OOOOO0OOOOOOOOO .clicked .connect (lambda OO00O00O0O000OOOO ,v =O00O0O00O00OO0000 :OO0OO0OO0O00OOOO0 .insert_variable (v ))#line:759
            O0O0OOO00O00OO0OO .addWidget (O0OOOOO0OOOOOOOOO )#line:760
        O0O00OO00000OO0OO .addLayout (O0O0OOO00O00OO0OO )#line:761
        O00O0000O0O00OOO0 =QDialogButtonBox (QDialogButtonBox .Ok |QDialogButtonBox .Cancel )#line:763
        O00O0000O0O00OOO0 .accepted .connect (OO0OO0OO0O00OOOO0 .accept )#line:764
        O00O0000O0O00OOO0 .rejected .connect (OO0OO0OO0O00OOOO0 .reject )#line:765
        O0O00OO00000OO0OO .addWidget (O00O0000O0O00OOO0 )#line:766
        OO0OO0OO0O00OOOO0 .setLayout (O0O00OO00000OO0OO )#line:767
    def insert_variable (OO0000O0O000OOOO0 ,OOOOOO0O0OO0OOO0O ):#line:769
        OOOO00OOO0O00OOOO =OO0000O0O000OOOO0 .text_edit .textCursor ()#line:770
        OOOO00OOO0O00OOOO .insertText (f"{{{OOOOOO0O0OO0OOO0O}}}")#line:771
    def get_caption (O00O0OO0000O0OO0O ):#line:773
        return O00O0OO0000O0OO0O .text_edit .toPlainText ()#line:774
    def accept (OO0O0OO000OOO0O0O ):#line:776
        OO0O0OO000OOO0O0O .result_caption =OO0O0OO000OOO0O0O .text_edit .toPlainText ()#line:777
        super ().accept ()#line:778
class SheetSettingsDialog (QDialog ):#line:784
    def __init__ (OOOOO0O0O00O00O00 ,parent =None ):#line:785
        super ().__init__ (parent )#line:786
        OOOOO0O0O00O00O00 .setWindowTitle ("إعدادات Google Sheets")#line:787
        OO00O000OOO0000O0 =QVBoxLayout (OOOOO0O0O00O00O00 )#line:788
        OO00O000OOO0000O0 .addWidget (QLabel ("معرف الشيت:"))#line:790
        OOOOO0O0O00O00O00 .id_edit =QLineEdit ()#line:791
        OO00O000OOO0000O0 .addWidget (OOOOO0O0O00O00O00 .id_edit )#line:792
        OO00O000OOO0000O0 .addWidget (QLabel ("نطاق الشيت:"))#line:794
        OOOOO0O0O00O00O00 .range_edit =QLineEdit ()#line:795
        OO00O000OOO0000O0 .addWidget (OOOOO0O0O00O00O00 .range_edit )#line:796
        OO00O000OOO0000O0 .addWidget (QLabel ("مفتاح API:"))#line:798
        OOOOO0O0O00O00O00 .api_edit =QLineEdit ()#line:799
        OO00O000OOO0000O0 .addWidget (OOOOO0O0O00O00O00 .api_edit )#line:800
        OOOOO0O0O00O00O00 .test_btn =QPushButton ("اختبار الاتصال")#line:802
        OOOOO0O0O00O00O00 .test_btn .clicked .connect (OOOOO0O0O00O00O00 .test_connection )#line:803
        OO00O000OOO0000O0 .addWidget (OOOOO0O0O00O00O00 .test_btn )#line:804
        O0OO0O0O0O0O00O0O =QDialogButtonBox (QDialogButtonBox .Ok |QDialogButtonBox .Cancel )#line:806
        O0OO0O0O0O0O00O0O .accepted .connect (OOOOO0O0O00O00O00 .accept )#line:807
        O0OO0O0O0O0O00O0O .rejected .connect (OOOOO0O0O00O00O00 .reject )#line:808
        OO00O000OOO0000O0 .addWidget (O0OO0O0O0O0O00O0O )#line:809
        O000O0OOOO000OO0O =load_sheet_settings ()#line:811
        OOOOO0O0O00O00O00 .id_edit .setText (O000O0OOOO000OO0O .get ("SPREADSHEET_ID",""))#line:812
        OOOOO0O0O00O00O00 .range_edit .setText (O000O0OOOO000OO0O .get ("RANGE_NAME",""))#line:813
        OOOOO0O0O00O00O00 .api_edit .setText (O000O0OOOO000OO0O .get ("API_KEY",""))#line:814
        OOOOO0O0O00O00O00 .setLayout (OO00O000OOO0000O0 )#line:816
        OOOOO0O0O00O00O00 .resize (400 ,300 )#line:817
    def test_connection (O0000OO0000OOO0O0 ):#line:819
        OO000O00OO0O000OO =O0000OO0000OOO0O0 .id_edit .text ().strip ()#line:820
        OOO000O0OOO0OOOO0 =O0000OO0000OOO0O0 .range_edit .text ().strip ()#line:821
        O0OOO0OO0OO0OOO00 =O0000OO0000OOO0O0 .api_edit .text ().strip ()#line:822
        if not (OO000O00OO0O000OO and OOO000O0OOO0OOOO0 and O0OOO0OO0OO0OOO00 ):#line:823
            QMessageBox .warning (O0000OO0000OOO0O0 ,"تنبيه","يرجى تعبئة جميع الحقول قبل الاختبار.")#line:824
            return #line:825
        try :#line:826
            O0OOOO0OOOO0OO0O0 =build ('sheets','v4',developerKey =O0OOO0OO0OO0OOO00 )#line:827
            OOOO00OO00OOOOO0O =O0OOOO0OOOO0OO0O0 .spreadsheets ()#line:828
            OO0O000000O00O0OO =OOOO00OO00OOOOO0O .values ().get (spreadsheetId =OO000O00OO0O000OO ,range =OOO000O0OOO0OOOO0 ).execute ()#line:829
            O0OOO0O00O0OO0OOO =OO0O000000O00O0OO .get ('values',[])#line:830
            if O0OOO0O00O0OO0OOO :#line:831
                QMessageBox .information (O0000OO0000OOO0O0 ,"نجاح","تم الاتصال وجلب البيانات بنجاح.")#line:832
            else :#line:833
                QMessageBox .warning (O0000OO0000OOO0O0 ,"تنبيه","اتصال ناجح لكن لا توجد بيانات.")#line:834
        except Exception as OO000O00OOO000OOO :#line:835
            QMessageBox .critical (O0000OO0000OOO0O0 ,"فشل الاتصال",str (OO000O00OOO000OOO ))#line:836
    def get_settings (OO00OOO00000O0O00 ):#line:838
        return {"SPREADSHEET_ID":OO00OOO00000O0O00 .id_edit .text ().strip (),"RANGE_NAME":OO00OOO00000O0O00 .range_edit .text ().strip (),"API_KEY":OO00OOO00000O0O00 .api_edit .text ().strip ()}#line:843
class SingleWorkerStatusWidget (QWidget ):#line:849
    ""#line:852
    def __init__ (O000O00O0000O00OO ,O000OO0OOO00O00OO ,OO00O00OOOOOO00O0 ,OOOOO00O0O000O0O0 ,OO000OO0OOOOO00O0 ):#line:853
        super ().__init__ ()#line:854
        O000O00O0000O00OO .status_name =O000OO0OOO00O00OO #line:855
        O000O00O0000O00OO .columns =OO000OO0OOOOO00O0 #line:856
        O000O00O0000O00OO .layout =QHBoxLayout (O000O00O0000O00OO )#line:858
        O000O00O0000O00OO .setLayout (O000O00O0000O00OO .layout )#line:859
        O000O00O0000O00OO .cb_enable =QCheckBox (f"تفعيل للحالة: {O000OO0OOO00O00OO}")#line:861
        O000O00O0000O00OO .cb_enable .setChecked (OO00O00OOOOOO00O0 )#line:862
        O000O00O0000O00OO .layout .addWidget (O000O00O0000O00OO .cb_enable )#line:863
        O000O00O0000O00OO .btn_edit_message =QPushButton ("تعديل الرسالة")#line:865
        O000O00O0000O00OO .btn_edit_message .clicked .connect (O000O00O0000O00OO .edit_message )#line:866
        O000O00O0000O00OO .layout .addWidget (O000O00O0000O00OO .btn_edit_message )#line:867
        O000O00O0000O00OO .message_text =OOOOO00O0O000O0O0 #line:869
    def edit_message (O000OOOOO00O00OO0 ):#line:871
        OO0OOO0O00OO0OO0O =MessageForStatusEditorDialog (None ,O000OOOOO00O00OO0 .message_text ,O000OOOOO00O00OO0 .columns ,O000OOOOO00O00OO0 .status_name )#line:872
        if OO0OOO0O00OO0OO0O .exec_ ()==QDialog .Accepted :#line:873
            O000OOOOO00O00OO0 .message_text =OO0OOO0O00OO0OO0O .get_message ()#line:874
    def get_data (OOOO00OO0OO0O0000 ):#line:876
        return {"status":OOOO00OO0OO0O0000 .status_name ,"enabled":OOOO00OO0OO0O0000 .cb_enable .isChecked (),"message":OOOO00OO0OO0O0000 .message_text }#line:881
class MessageForStatusEditorDialog (QDialog ):#line:883
    ""#line:886
    def __init__ (O0OO0OO0O000O0000 ,O0000O0O00OO00OO0 ,OOOOO0000O0O0OO00 ,OO0O0OO0000000OO0 ,OO000000OOO0000OO ):#line:887
        super ().__init__ (O0000O0O00OO00OO0 )#line:888
        O0OO0OO0O000O0000 .setWindowTitle (f"تحرير الرسالة - {OO000000OOO0000OO}")#line:889
        O0OO0OO0O000O0000 .result_msg =OOOOO0000O0O0OO00 #line:890
        O0OO0OO0O000O0000 .columns =OO0O0OO0000000OO0 #line:891
        OO0OO0OOOOO0OO000 =QVBoxLayout (O0OO0OO0O000O0000 )#line:893
        O0OO0OO0O000O0000 .text_edit =QTextEdit ()#line:894
        O0OO0OO0O000O0000 .text_edit .setPlainText (OOOOO0000O0O0OO00 )#line:895
        OO0OO0OOOOO0OO000 .addWidget (O0OO0OO0O000O0000 .text_edit )#line:896
        OO0OO0O00O000OO00 =QHBoxLayout ()#line:898
        O0O0OOO00O00000O0 =QLabel ("المتغيرات:")#line:899
        OO0OO0O00O000OO00 .addWidget (O0O0OOO00O00000O0 )#line:900
        for OO00OOO0OOO00OO0O in O0OO0OO0O000O0000 .columns :#line:901
            OO0OOO00OOO0O0OO0 =QPushButton (OO00OOO0OOO00OO0O )#line:902
            OO0OOO00OOO0O0OO0 .clicked .connect (lambda _O00O00O0OOOOOOO0O ,v =OO00OOO0OOO00OO0O :O0OO0OO0O000O0000 .insert_variable (v ))#line:903
            OO0OO0O00O000OO00 .addWidget (OO0OOO00OOO0O0OO0 )#line:904
        OO0OO0OOOOO0OO000 .addLayout (OO0OO0O00O000OO00 )#line:905
        O0O00O00OOOO0O00O =QDialogButtonBox (QDialogButtonBox .Ok |QDialogButtonBox .Cancel )#line:907
        O0O00O00OOOO0O00O .accepted .connect (O0OO0OO0O000O0000 .accept )#line:908
        O0O00O00OOOO0O00O .rejected .connect (O0OO0OO0O000O0000 .reject )#line:909
        OO0OO0OOOOO0OO000 .addWidget (O0O00O00OOOO0O00O )#line:910
        O0OO0OO0O000O0000 .setLayout (OO0OO0OOOOO0OO000 )#line:912
        O0OO0OO0O000O0000 .resize (500 ,400 )#line:913
    def insert_variable (OO00O00O0OOO00OO0 ,O00O0OO0O00OO0OOO ):#line:915
        O0OOO0000O0O0OOOO =OO00O00O0OOO00OO0 .text_edit .textCursor ()#line:916
        O0OOO0000O0O0OOOO .insertText (f"{{{O00O0OO0O00OO0OOO}}}")#line:917
    def get_message (O0O0000O00OOO0OO0 ):#line:919
        return O0O0000O00OOO0OO0 .text_edit .toPlainText ()#line:920
    def accept (O00O00O0O00O000OO ):#line:922
        O00O00O0O00O000OO .result_msg =O00O00O0O00O000OO .text_edit .toPlainText ()#line:923
        super ().accept ()#line:924
class WorkerTab (QWidget ):#line:926
    ""#line:930
    def __init__ (OOO0O00000O0OO0OO ,worker_data =None ,all_statuses =None ,columns =None ,parent =None ):#line:931
        super ().__init__ (parent )#line:932
        OOO0O00000O0OO0OO .worker_data =worker_data or {"name":"عامل جديد","phone":"","notifications":{},"message_templates":{}}#line:938
        OOO0O00000O0OO0OO .all_statuses =all_statuses if all_statuses else ["__DEFAULT__"]#line:939
        OOO0O00000O0OO0OO .columns =columns if columns else []#line:940
        OOO0O00000O0OO0OO .main_layout =QVBoxLayout (OOO0O00000O0OO0OO )#line:942
        OOO0O00000O0OO0OO .setLayout (OOO0O00000O0OO0OO .main_layout )#line:943
        O0O000O00OO000O0O =QLabel ("اسم العامل:")#line:945
        OOO0O00000O0OO0OO .main_layout .addWidget (O0O000O00OO000O0O )#line:946
        OOO0O00000O0OO0OO .name_edit =QLineEdit (OOO0O00000O0OO0OO .worker_data .get ("name",""))#line:947
        OOO0O00000O0OO0OO .main_layout .addWidget (OOO0O00000O0OO0OO .name_edit )#line:948
        O0O00O0OOOOOOOOO0 =QLabel ("رقم الهاتف:")#line:950
        OOO0O00000O0OO0OO .main_layout .addWidget (O0O00O0OOOOOOOOO0 )#line:951
        OOO0O00000O0OO0OO .phone_edit =QLineEdit (OOO0O00000O0OO0OO .worker_data .get ("phone",""))#line:952
        OOO0O00000O0OO0OO .main_layout .addWidget (OOO0O00000O0OO0OO .phone_edit )#line:953
        OOO0O00000O0OO0OO .status_widgets ={}#line:955
        OOOOO000OOO0OO000 =QScrollArea ()#line:956
        OOOOO000OOO0OO000 .setWidgetResizable (True )#line:957
        OOOO000O0O000O0OO =QWidget ()#line:958
        OOO0O00000O0OO0OO .status_layout =QVBoxLayout (OOOO000O0O000O0OO )#line:959
        for O0OO0O00O000O00O0 in OOO0O00000O0OO0OO .all_statuses :#line:961
            OO0O00O00O0OO00OO =OOO0O00000O0OO0OO .worker_data .get ("notifications",{}).get (O0OO0O00O000O00O0 ,False )#line:962
            O0OOO00OO0O00OO0O =OOO0O00000O0OO0OO .worker_data .get ("message_templates",{}).get (O0OO0O00O000O00O0 ,"")#line:963
            OOOO000OO0OO00OOO =SingleWorkerStatusWidget (O0OO0O00O000O00O0 ,OO0O00O00O0OO00OO ,O0OOO00OO0O00OO0O ,OOO0O00000O0OO0OO .columns )#line:964
            OOO0O00000O0OO0OO .status_layout .addWidget (OOOO000OO0OO00OOO )#line:965
            OOO0O00000O0OO0OO .status_widgets [O0OO0O00O000O00O0 ]=OOOO000OO0OO00OOO #line:966
        OOOO000O0O000O0OO .setLayout (OOO0O00000O0OO0OO .status_layout )#line:968
        OOOOO000OOO0OO000 .setWidget (OOOO000O0O000O0OO )#line:969
        OOO0O00000O0OO0OO .main_layout .addWidget (OOOOO000OOO0OO000 )#line:970
        OOO0O00000O0OO0OO .main_layout .addStretch ()#line:971
    def get_data (OOOOOO0OOO000O000 ):#line:973
        O0O00000OO0O00OOO ={"name":OOOOOO0OOO000O000 .name_edit .text ().strip (),"phone":OOOOOO0OOO000O000 .phone_edit .text ().strip (),"notifications":{},"message_templates":{}}#line:979
        for OOO0O000OO0OO0O0O ,OO00OO00OOO0O0OO0 in OOOOOO0OOO000O000 .status_widgets .items ():#line:980
            OO0O0OOO0OO0O0OO0 =OO00OO00OOO0O0OO0 .get_data ()#line:981
            O0O00000OO0O00OOO ["notifications"][OOO0O000OO0OO0O0O ]=OO0O0OOO0OO0O0OO0 ["enabled"]#line:982
            O0O00000OO0O00OOO ["message_templates"][OOO0O000OO0OO0O0O ]=OO0O0OOO0OO0O0OO0 ["message"]#line:983
        return O0O00000OO0O00OOO #line:984
class AdminTabsDialog (QDialog ):#line:986
    ""#line:989
    def __init__ (OOOOOO00O00O00O0O ,parent =None ,all_statuses =None ,columns =None ):#line:990
        super ().__init__ (parent )#line:991
        OOOOOO00O00O00O0O .setWindowTitle ("إعدادات إشعارات الإدارة (متعددة العمال)")#line:992
        OOOOOO00O00O00O0O .all_statuses =all_statuses if all_statuses else ["__DEFAULT__"]#line:993
        OOOOOO00O00O00O0O .columns =columns if columns else []#line:994
        OO0O0O0OO00O0O0OO =QVBoxLayout (OOOOOO00O00O00O0O )#line:996
        OO00OOO00O000000O =QHBoxLayout ()#line:998
        OOOOOO00O00O00O0O .btn_add_worker =QPushButton ("إضافة عامل جديد")#line:999
        OOOOOO00O00O00O0O .btn_add_worker .clicked .connect (OOOOOO00O00O00O0O .add_worker_tab )#line:1000
        OO00OOO00O000000O .addWidget (OOOOOO00O00O00O0O .btn_add_worker )#line:1001
        OOOOOO00O00O00O0O .btn_delete_worker =QPushButton ("حذف العامل الحالي")#line:1003
        OOOOOO00O00O00O0O .btn_delete_worker .clicked .connect (OOOOOO00O00O00O0O .delete_current_worker_tab )#line:1004
        OO00OOO00O000000O .addWidget (OOOOOO00O00O00O0O .btn_delete_worker )#line:1005
        OO0O0O0OO00O0O0OO .addLayout (OO00OOO00O000000O )#line:1007
        OOOOOO00O00O00O0O .tab_widget =QTabWidget ()#line:1009
        OO0O0O0OO00O0O0OO .addWidget (OOOOOO00O00O00O0O .tab_widget )#line:1010
        O0O00O0OOO0OO0O00 =QDialogButtonBox (QDialogButtonBox .Ok |QDialogButtonBox .Cancel )#line:1012
        O0O00O0OOO0OO0O00 .accepted .connect (OOOOOO00O00O00O0O .accept )#line:1013
        O0O00O0OOO0OO0O00 .rejected .connect (OOOOOO00O00O00O0O .reject )#line:1014
        OO0O0O0OO00O0O0OO .addWidget (O0O00O0OOO0OO0O00 )#line:1015
        OOOOOO00O00O00O0O .setLayout (OO0O0O0OO00O0O0OO )#line:1017
        OOOOOO00O00O00O0O .resize (600 ,500 )#line:1018
        OOOOOO00O00O00O0O .admin_settings =load_admin_settings ()#line:1020
        O00OO00O000O0OOOO =OOOOOO00O00O00O0O .admin_settings .get ("workers",[])#line:1021
        for O0OOO000OO00OOO00 in O00OO00O000O0OOOO :#line:1022
            OOOOOO00O00O00O0O .add_worker_tab (O0OOO000OO00OOO00 )#line:1023
    def add_worker_tab (OO0000OO00O00OOOO ,worker_data =None ):#line:1025
        if not worker_data :#line:1026
            worker_data ={"name":"عامل جديد","phone":"","notifications":{},"message_templates":{}}#line:1032
        OO0OOO0000O000O0O =WorkerTab (worker_data ,all_statuses =OO0000OO00O00OOOO .all_statuses ,columns =OO0000OO00O00OOOO .columns ,parent =OO0000OO00O00OOOO .tab_widget )#line:1033
        O0000OO00OO0OOOO0 =OO0000OO00O00OOOO .tab_widget .addTab (OO0OOO0000O000O0O ,worker_data .get ("name","عامل"))#line:1034
        OO0000OO00O00OOOO .tab_widget .setCurrentIndex (O0000OO00OO0OOOO0 )#line:1035
    def delete_current_worker_tab (OOOOO00O0O000O000 ):#line:1037
        O0O0OO0OOOOO0O0O0 =OOOOO00O0O000O000 .tab_widget .currentIndex ()#line:1038
        if O0O0OO0OOOOO0O0O0 >=0 :#line:1039
            OOOOO00O0O000O000 .tab_widget .removeTab (O0O0OO0OOOOO0O0O0 )#line:1040
    def get_admin_settings (O000O0000OO000OO0 ):#line:1042
        OO0O00OOO00O0000O =[]#line:1043
        for O0O00O0O0OO00OO0O in range (O000O0000OO000OO0 .tab_widget .count ()):#line:1044
            OOO0O00OO000OOOOO =O000O0000OO000OO0 .tab_widget .widget (O0O00O0O0OO00OO0O )#line:1045
            O00000O0O0O0000O0 =OOO0O00OO000OOOOO .get_data ()#line:1046
            O000O0000OO000OO0 .tab_widget .setTabText (O0O00O0O0OO00OO0O ,O00000O0O0O0000O0 ["name"])#line:1047
            OO0O00OOO00O0000O .append (O00000O0O0O0000O0 )#line:1048
        return {"workers":OO0O00OOO00O0000O }#line:1049
class BrowserOpenerWorker (QObject ):#line:1055
    finished =pyqtSignal (object )#line:1056
    error =pyqtSignal (str )#line:1057
    log_signal =pyqtSignal (str )#line:1058
    def run (O0OO00OOO00O0O00O ):#line:1060
        ""#line:1064
        try :#line:1066
            O0OO00OOO00O0O00O .log_signal .emit ("تسجيل الدخول إلى واتساب في الخلفية...")#line:1067
            O00O00O00O0OOOO00 =create_driver (visible =False )#line:1068
            WebDriverWait (O00O00O00O0OOOO00 ,15 ).until (EC .presence_of_element_located ((By .TAG_NAME ,"body")))#line:1069
            try :#line:1070
                WebDriverWait (O00O00O00O0OOOO00 ,15 ).until (EC .presence_of_element_located ((By .ID ,"pane-side")))#line:1071
                O0OO00OOO00O0O00O .finished .emit (O00O00O00O0OOOO00 )#line:1072
                return #line:1073
            except :#line:1074
                O0OO00OOO00O0O00O .log_signal .emit ("لم يتم العثور على pane-side في الخلفية. نغلقه ونفتح واجهة مرئية لمسح QR.")#line:1075
                O00O00O00O0OOOO00 .quit ()#line:1076
        except Exception as O00O0OOO0O00O0000 :#line:1077
            O0OO00OOO00O0O00O .error .emit (f"فشل فتح المتصفح في الخلفية: {O00O0OOO0O00O0000}")#line:1078
        O0OO00OOO00O0O00O .log_signal .emit ("فتح المتصفح بشكل مرئي لإتاحة مسح QR ...")#line:1081
        try :#line:1082
            OO0O000000OO0OO0O =create_driver (visible =True )#line:1083
            WebDriverWait (OO0O000000OO0OO0O ,60 ).until (EC .presence_of_element_located ((By .ID ,"pane-side")))#line:1084
            O0OO00OOO00O0O00O .log_signal .emit ("✅ تم تسجيل الدخول بنجاح (مرئي).")#line:1085
            OO0O000000OO0OO0O .quit ()#line:1086
            OO0OOO0O0O0OOO00O =create_driver (visible =False )#line:1088
            try :#line:1089
                WebDriverWait (OO0OOO0O0O0OOO00O ,10 ).until (EC .presence_of_element_located ((By .ID ,"pane-side")))#line:1090
            except :#line:1091
                pass #line:1092
            O0OO00OOO00O0O00O .finished .emit (OO0OOO0O0O0OOO00O )#line:1093
        except Exception as O00O0OOO0O00O0000 :#line:1094
            O0OO00OOO00O0O00O .error .emit (f"⚠️ لم يتم تسجيل الدخول في الوقت المحدد في الوضع المرئي. يرجى إعادة المحاولة.\n{O00O0OOO0O00O0000}")#line:1095
            O0OO00OOO00O0O00O .finished .emit (None )#line:1096
class BrowserOpenerThread (QThread ):#line:1098
    driver_ready =pyqtSignal (object )#line:1099
    error_occurred =pyqtSignal (str )#line:1100
    log_signal =pyqtSignal (str )#line:1101
    def __init__ (O00OO00O0OOO0OOO0 ):#line:1103
        super ().__init__ ()#line:1104
        O00OO00O0OOO0OOO0 .worker =BrowserOpenerWorker ()#line:1105
        O00OO00O0OOO0OOO0 .worker .moveToThread (O00OO00O0OOO0OOO0 )#line:1106
        O00OO00O0OOO0OOO0 .worker .finished .connect (O00OO00O0OOO0OOO0 .on_finished )#line:1107
        O00OO00O0OOO0OOO0 .worker .error .connect (O00OO00O0OOO0OOO0 .error_occurred )#line:1108
        O00OO00O0OOO0OOO0 .worker .log_signal .connect (O00OO00O0OOO0OOO0 .log_signal )#line:1109
    def run (O000O000O000O0O0O ):#line:1111
        O000O000O000O0O0O .worker .run ()#line:1112
    def on_finished (OO0O0000000O0OOO0 ,OOOO0OO0OOO0O0OOO ):#line:1114
        OO0O0000000O0OOO0 .driver_ready .emit (OOOO0OO0OOO0O0OOO )#line:1115
class WhatsAppSenderUI (QWidget ):#line:1121
    def __init__ (O00000OOO000OOOO0 ):#line:1122
        super ().__init__ ()#line:1123
        O00000OOO000OOOO0 .setWindowTitle ("لوحة تحكم إرسال رسائل واتساب")#line:1124
        O00000OOO000OOOO0 .driver =None #line:1125
        O00000OOO000OOOO0 .monitor_timer =None #line:1126
        O00000OOO000OOOO0 .monitoring =False #line:1127
        O00000OOO000OOOO0 .driver_visible =False #line:1128
        O00000OOO000OOOO0 .notification_box =QPlainTextEdit ()#line:1131
        O00000OOO000OOOO0 .notification_box .setReadOnly (True )#line:1132
        O00000OOO000OOOO0 .templates =load_templates ()#line:1135
        O00000OOO000OOOO0 .columns =O00000OOO000OOOO0 .fetch_columns_excluding_statu ()#line:1137
        O0OOOO00OO0OO0O00 =QHBoxLayout (O00000OOO000OOOO0 )#line:1139
        O0O00OO0O00000OO0 =QVBoxLayout ()#line:1142
        O00000OOO000OOOO0 .templates_table =TemplatesTable (O00000OOO000OOOO0 )#line:1145
        O0O00OO0O00000OO0 .addWidget (O00000OOO000OOOO0 .templates_table )#line:1146
        OO0O0OOO0OOOOOO00 =QHBoxLayout ()#line:1149
        O00000OOO000OOOO0 .btn_add_template =QPushButton ("إضافة قالب")#line:1150
        O00000OOO000OOOO0 .btn_add_template .clicked .connect (O00000OOO000OOOO0 .add_template )#line:1151
        OO0O0OOO0OOOOOO00 .addWidget (O00000OOO000OOOO0 .btn_add_template )#line:1152
        O00000OOO000OOOO0 .btn_send_manual =QPushButton ("إرسال يدوي")#line:1154
        O00000OOO000OOOO0 .btn_send_manual .clicked .connect (O00000OOO000OOOO0 .send_manual )#line:1155
        OO0O0OOO0OOOOOO00 .addWidget (O00000OOO000OOOO0 .btn_send_manual )#line:1156
        O00000OOO000OOOO0 .monitor_radio =QRadioButton ("تفعيل المراقبة")#line:1158
        O00000OOO000OOOO0 .monitor_radio .toggled .connect (O00000OOO000OOOO0 .toggle_monitoring )#line:1159
        OO0O0OOO0OOOOOO00 .addWidget (O00000OOO000OOOO0 .monitor_radio )#line:1160
        O0O00OO0O00000OO0 .addLayout (OO0O0OOO0OOOOOO00 )#line:1162
        O00000OOO000OOOO0 .open_browser_btn =QPushButton ("فتح المتصفح (غير متصل)")#line:1165
        O00000OOO000OOOO0 .open_browser_btn .setStyleSheet ("background-color: red;")#line:1166
        O00000OOO000OOOO0 .open_browser_btn .clicked .connect (O00000OOO000OOOO0 .open_browser )#line:1167
        O0O00OO0O00000OO0 .addWidget (O00000OOO000OOOO0 .open_browser_btn )#line:1168
        O00O00OOOO0OO0O0O =QLabel ("إشعارات النظام:")#line:1171
        O0O00OO0O00000OO0 .addWidget (O00O00OOOO0OO0O0O )#line:1172
        O0O00OO0O00000OO0 .addWidget (O00000OOO000OOOO0 .notification_box )#line:1173
        O00000OOO000OOOO0 .sheet_settings_btn =QPushButton ("إعدادات Google Sheets")#line:1176
        O00000OOO000OOOO0 .sheet_settings_btn .clicked .connect (O00000OOO000OOOO0 .open_sheet_settings )#line:1177
        O0O00OO0O00000OO0 .addWidget (O00000OOO000OOOO0 .sheet_settings_btn )#line:1178
        O00000OOO000OOOO0 .admin_settings_btn =QPushButton ("إعدادات إشعارات الإدارة")#line:1181
        O00000OOO000OOOO0 .admin_settings_btn .clicked .connect (O00000OOO000OOOO0 .open_admin_settings )#line:1182
        O0O00OO0O00000OO0 .addWidget (O00000OOO000OOOO0 .admin_settings_btn )#line:1183
        OOO0O0O0O00OO00OO =QWidget ()#line:1185
        OOO0O0O0O00OO00OO .setLayout (O0O00OO0O00000OO0 )#line:1186
        O0OOOO00OO0OO0O00 .addWidget (OOO0O0O0O00OO00OO ,2 )#line:1187
        O00000OOO000OOOO0 .default_msg_widget =DefaultMessageWidget (O00000OOO000OOOO0 ,O00000OOO000OOOO0 .columns )#line:1190
        O0OOOO00OO0OO0O00 .addWidget (O00000OOO000OOOO0 .default_msg_widget ,3 )#line:1191
        O00000OOO000OOOO0 .setLayout (O0OOOO00OO0OO0O00 )#line:1193
        O00000OOO000OOOO0 .resize (1200 ,600 )#line:1194
        O00000OOO000OOOO0 .refresh_templates_table ()#line:1197
    def fetch_columns_excluding_statu (OO0000O00O000O0OO ):#line:1199
        OO0O0OOOO00O0O00O =fetch_sheet_data_public ()#line:1200
        if OO0O0OOOO00O0O00O and len (OO0O0OOOO00O0O00O )>0 :#line:1201
            OO0O0O0OO00O00O00 =OO0O0OOOO00O0O00O [0 ]#line:1202
            return [O0OOOOO0OOO0OO00O for O0OOOOO0OOO0OO00O in OO0O0O0OO00O00O00 if O0OOOOO0OOO0OO00O .lower ().strip ()!="statu"]#line:1203
        return []#line:1204
    def open_sheet_settings (OO00OO0000000O000 ):#line:1206
        O0O00OO0O00O00O00 =SheetSettingsDialog (OO00OO0000000O000 )#line:1207
        if O0O00OO0O00O00O00 .exec_ ()==QDialog .Accepted :#line:1208
            O00O0000OO00O0OO0 =O0O00OO0O00O00O00 .get_settings ()#line:1209
            save_sheet_settings (O00O0000OO00O0OO0 )#line:1210
            global SPREADSHEET_ID ,RANGE_NAME ,API_KEY #line:1211
            SPREADSHEET_ID =O00O0000OO00O0OO0 .get ("SPREADSHEET_ID","")#line:1212
            RANGE_NAME =O00O0000OO00O0OO0 .get ("RANGE_NAME","")#line:1213
            API_KEY =O00O0000OO00O0OO0 .get ("API_KEY","")#line:1214
            OO00OO0000000O000 .log ("تم تحديث إعدادات Google Sheets.")#line:1215
    def open_admin_settings (O0O00O000OO000O00 ):#line:1217
        O0O0O0O000OOOOOOO =set ()#line:1219
        for OOOO00OOOO0OOO00O in O0O00O000OO000O00 .templates :#line:1220
            O0O000OO00O000OOO =OOOO00OOOO0OOO00O .get ("statu","").strip ()#line:1221
            if O0O000OO00O000OOO :#line:1222
                O0O0O0O000OOOOOOO .add (O0O000OO00O000OOO )#line:1223
        if "__DEFAULT__"not in O0O0O0O000OOOOOOO :#line:1224
            O0O0O0O000OOOOOOO .add ("__DEFAULT__")#line:1225
        O0O0O0O000OOOOOOO =list (O0O0O0O000OOOOOOO )#line:1226
        OOOOO000O0OOOO00O =AdminTabsDialog (O0O00O000OO000O00 ,all_statuses =O0O0O0O000OOOOOOO ,columns =O0O00O000OO000O00 .columns )#line:1228
        if OOOOO000O0OOOO00O .exec_ ()==QDialog .Accepted :#line:1229
            O00O00O00OOO0O0OO =OOOOO000O0OOOO00O .get_admin_settings ()#line:1230
            save_admin_settings (O00O00O00OOO0O0OO )#line:1231
            O0O00O000OO000O00 .log ("تم تحديث إعدادات إشعارات الإدارة (متعددة العمال).")#line:1232
    def open_browser (OOO0O0OO00O00OO0O ):#line:1234
        ""#line:1237
        global driver #line:1238
        if OOO0O0OO00O00OO0O .driver :#line:1239
            try :#line:1240
                OOO0O0OO00O00OO0O .driver .quit ()#line:1241
            except :#line:1242
                pass #line:1243
            OOO0O0OO00O00OO0O .driver =None #line:1244
        OOO0O0OO00O00OO0O .log ("جاري التحضير...")#line:1246
        OOO0O0OO00O00OO0O .browser_thread =BrowserOpenerThread ()#line:1247
        OOO0O0OO00O00OO0O .browser_thread .log_signal .connect (OOO0O0OO00O00OO0O .log )#line:1248
        OOO0O0OO00O00OO0O .browser_thread .driver_ready .connect (OOO0O0OO00O00OO0O .on_browser_ready )#line:1249
        OOO0O0OO00O00OO0O .browser_thread .error_occurred .connect (OOO0O0OO00O00OO0O .on_browser_error )#line:1250
        OOO0O0OO00O00OO0O .browser_thread .start ()#line:1251
    def on_browser_ready (O0000O0O00O000000 ,O000O0O0O00O000OO ):#line:1253
        global driver #line:1254
        if O000O0O0O00O000OO is not None :#line:1255
            O0000O0O00O000000 .driver =O000O0O0O00O000OO #line:1256
            driver =O0000O0O00O000000 .driver #line:1257
            O0000O0O00O000000 .driver_visible =False #line:1258
            O0000O0O00O000000 .open_browser_btn .setText ("واتساب متصل (خلفية)")#line:1259
            O0000O0O00O000000 .open_browser_btn .setStyleSheet ("background-color: green;")#line:1260
            O0000O0O00O000000 .log ("✅ تم تسجيل الدخول بنجاح (خلفية).")#line:1261
        else :#line:1262
            O0000O0O00O000000 .log ("⚠️ فشل فتح المتصفح بشكل صحيح.")#line:1263
            O0000O0O00O000000 .open_browser_btn .setText ("فتح المتصفح (غير متصل)")#line:1264
            O0000O0O00O000000 .open_browser_btn .setStyleSheet ("background-color: red;")#line:1265
    def on_browser_error (OO0O0O0OO0O0O00OO ,OOOO0000O000O0000 ):#line:1267
        OO0O0O0OO0O0O00OO .log (OOOO0000O000O0000 )#line:1268
        OO0O0O0OO0O0O00OO .open_browser_btn .setText ("فتح المتصفح (غير متصل)")#line:1269
        OO0O0O0OO0O0O00OO .open_browser_btn .setStyleSheet ("background-color: red;")#line:1270
        OO0O0O0OO0O0O00OO .driver =None #line:1271
    def refresh_templates_table (OOOO0O00OO0OO0000 ):#line:1273
        OOOO0O00OO0OO0000 .templates_table .update_table ()#line:1274
    def add_template (OOOO0O0O000O000OO ):#line:1276
        O0O0O0000OOOOO000 =TemplateEditorDialog (OOOO0O0O000O000OO ,OOOO0O0O000O000OO .columns ,None )#line:1277
        if O0O0O0000OOOOO000 .exec_ ()==QDialog .Accepted :#line:1278
            O0O0OOO0O00O0OOO0 =O0O0O0000OOOOO000 .get_template_data ()#line:1279
            if not O0O0OOO0O00O0OOO0 ["statu"]:#line:1280
                QMessageBox .warning (OOOO0O0O000O000OO ,"تنبيه","يجب تحديد حقل Statu لهذا القالب.")#line:1281
                return #line:1282
            if "enabled"not in O0O0OOO0O00O0OOO0 :#line:1283
                O0O0OOO0O00O0OOO0 ["enabled"]=True #line:1284
            OOOO0O0O000O000OO .templates .append (O0O0OOO0O00O0OOO0 )#line:1285
            save_templates (OOOO0O0O000O000OO .templates )#line:1286
            OOOO0O0O000O000OO .refresh_templates_table ()#line:1287
    def edit_template (OO00OO0OOO0O0OO0O ,O00O0O0000O0OOOO0 ):#line:1289
        OO00O0O0OO0O00O0O =[OO00O0OOOO0O00OOO for OO00O0OOOO0O00OOO in OO00OO0OOO0O0OO0O .templates if OO00O0OOOO0O00OOO ["statu"]!="__DEFAULT__"]#line:1290
        if O00O0O0000O0OOOO0 <0 or O00O0O0000O0OOOO0 >=len (OO00O0O0OO0O00O0O ):#line:1291
            return #line:1292
        O000OO00OOO0OO0OO =OO00O0O0OO0O00O0O [O00O0O0000O0OOOO0 ]#line:1293
        O0000OOO0O0OO00O0 =OO00OO0OOO0O0OO0O .templates .index (O000OO00OOO0OO0OO )#line:1294
        OOO0O0O000O00O00O =TemplateEditorDialog (OO00OO0OOO0O0OO0O ,OO00OO0OOO0O0OO0O .columns ,O000OO00OOO0OO0OO )#line:1295
        if OOO0O0O000O00O00O .exec_ ()==QDialog .Accepted :#line:1296
            O0O0000OO0O00OO00 =OOO0O0O000O00O00O .get_template_data ()#line:1297
            O0O0000OO0O00OO00 ["enabled"]=O000OO00OOO0OO0OO .get ("enabled",True )#line:1298
            OO00OO0OOO0O0OO0O .templates [O0000OOO0O0OO00O0 ]=O0O0000OO0O00OO00 #line:1299
            save_templates (OO00OO0OOO0O0OO0O .templates )#line:1300
            OO00OO0OOO0O0OO0O .refresh_templates_table ()#line:1301
    def duplicate_template (O0O0000OOOO0000OO ,OO0000OOOOO0O000O ):#line:1303
        OOO00O000OOOOOOOO =[O00OO00O0O0OO00O0 for O00OO00O0O0OO00O0 in O0O0000OOOO0000OO .templates if O00OO00O0O0OO00O0 ["statu"]!="__DEFAULT__"]#line:1304
        if OO0000OOOOO0O000O <0 or OO0000OOOOO0O000O >=len (OOO00O000OOOOOOOO ):#line:1305
            return #line:1306
        O000OOOOOOOO0OO0O =OOO00O000OOOOOOOO [OO0000OOOOO0O000O ]#line:1307
        O0O0000000O00O0OO =copy .deepcopy (O000OOOOOOOO0OO0O )#line:1308
        O0O0000000O00O0OO ["statu"]=O0O0000000O00O0OO ["statu"]+"_نسخة"#line:1309
        O0O0000OOOO0000OO .templates .append (O0O0000000O00O0OO )#line:1310
        save_templates (O0O0000OOOO0000OO .templates )#line:1311
        O0O0000OOOO0000OO .refresh_templates_table ()#line:1312
    def delete_template (OO000OO0OO00O0000 ,O000OO00O00O00OO0 ):#line:1314
        OOOO000000OOO000O =[O000OO0O0O0O0OO00 for O000OO0O0O0O0OO00 in OO000OO0OO00O0000 .templates if O000OO0O0O0O0OO00 ["statu"]!="__DEFAULT__"]#line:1315
        if O000OO00O00O00OO0 <0 or O000OO00O00O00OO0 >=len (OOOO000000OOO000O ):#line:1316
            return #line:1317
        O0O00O0O00O000000 =OOOO000000OOO000O [O000OO00O00O00OO0 ]#line:1318
        OO00OOO0O0O0O0OOO =QMessageBox .question (OO000OO0OO00O0000 ,"حذف قالب","هل أنت متأكد من حذف هذا القالب؟",QMessageBox .Yes |QMessageBox .No )#line:1320
        if OO00OOO0O0O0O0OOO ==QMessageBox .Yes :#line:1321
            OO000OO0OO00O0000 .templates .remove (O0O00O0O00O000000 )#line:1322
            save_templates (OO000OO0OO00O0000 .templates )#line:1323
            OO000OO0OO00O0000 .refresh_templates_table ()#line:1324
    def send_manual (O0O0O00OOOO00OOO0 ):#line:1326
        ""#line:1329
        if not O0O0O00OOOO00OOO0 .driver :#line:1330
            QMessageBox .warning (O0O0O00OOOO00OOO0 ,"تنبيه","يرجى فتح المتصفح أولاً (التسجيل).")#line:1331
            return #line:1332
        OO00O0OOO00OOOO00 =ManualSendDialog (O0O0O00OOOO00OOO0 ,O0O0O00OOOO00OOO0 .columns )#line:1333
        OO00O0OOO00OOOO00 .exec_ ()#line:1334
    def toggle_monitoring (O00O00OOOO0OO00OO ,OOOOO00000000OOO0 ):#line:1336
        if not O00O00OOOO0OO00OO .driver and OOOOO00000000OOO0 :#line:1337
            O00O00OOOO0OO00OO .log ("يرجى فتح المتصفح قبل البدء بالمراقبة.")#line:1338
            O00O00OOOO0OO00OO .monitor_radio .setChecked (False )#line:1339
            return #line:1340
        if not (SPREADSHEET_ID and RANGE_NAME and API_KEY )and OOOOO00000000OOO0 :#line:1341
            QMessageBox .warning (O00O00OOOO0OO00OO ,"تنبيه","يرجى إدخال إعدادات Google Sheets قبل بدء المراقبة.")#line:1342
            O00O00OOOO0OO00OO .monitor_radio .setChecked (False )#line:1343
            return #line:1344
        if OOOOO00000000OOO0 :#line:1345
            O00O00OOOO0OO00OO .monitor_timer =QTimer ()#line:1346
            O00O00OOOO0OO00OO .monitor_timer .timeout .connect (lambda :check_new_orders (O00O00OOOO0OO00OO ))#line:1347
            O00O00OOOO0OO00OO .monitor_timer .start (5000 )#line:1348
            O00O00OOOO0OO00OO .monitoring =True #line:1349
            O00O00OOOO0OO00OO .log ("تم بدء المراقبة على الشيت.")#line:1350
        else :#line:1351
            if O00O00OOOO0OO00OO .monitor_timer is not None :#line:1352
                O00O00OOOO0OO00OO .monitor_timer .stop ()#line:1353
            O00O00OOOO0OO00OO .monitoring =False #line:1354
            O00O00OOOO0OO00OO .log ("تم إيقاف المراقبة.")#line:1355
    def get_default_template_data (OOO0OOO00O0OOO000 ):#line:1357
        return OOO0OOO00O0OOO000 .default_msg_widget .get_default_template_data ()#line:1358
    def log (OO0O00OOOO00O0OO0 ,O00O0O0OO000OOOO0 ):#line:1360
        print (O00O0O0OO000OOOO0 )#line:1361
        OO0O00OOOO00O0OO0 .notification_box .appendPlainText (O00O0O0OO000OOOO0 )#line:1362
class TemplateEditorDialog (QDialog ):#line:1368
    def __init__ (OO00OO0O0O0OO0O0O ,OO0O0O00O0O0OO0OO ,O0OO0OOO00000OOOO ,template_data =None ):#line:1369
        super ().__init__ (OO0O0O00O0O0OO0OO )#line:1370
        OO00OO0O0O0OO0O0O .parent_ui =OO0O0O00O0O0OO0OO #line:1371
        OO00OO0O0O0OO0O0O .columns =O0OO0OOO00000OOOO #line:1372
        OO00OO0O0O0OO0O0O .attachments =[]#line:1373
        OO00OO0O0O0OO0O0O .setWindowTitle ("إنشاء/تعديل القالب")#line:1374
        OO00OO0O0O0OO0O0O .template_data =template_data or {"statu":"","content":"","attachments":[],"enabled":True }#line:1375
        OO00OO0O0O0OO0O0O .main_layout =QVBoxLayout (OO00OO0O0O0OO0O0O )#line:1377
        OO00OO0O0O0OO0O0O .main_layout .addWidget (QLabel ("قيمة Statu لهذا القالب:"))#line:1379
        OO00OO0O0O0OO0O0O .statu_line =QLineEdit ()#line:1380
        OO00OO0O0O0OO0O0O .statu_line .setPlaceholderText ("مثال: شحن ، دفع ، ... إلخ")#line:1381
        OO00OO0O0O0OO0O0O .statu_line .setText (OO00OO0O0O0OO0O0O .template_data .get ("statu",""))#line:1382
        OO00OO0O0O0OO0O0O .main_layout .addWidget (OO00OO0O0O0OO0O0O .statu_line )#line:1383
        O0O00O0O00OOOOOOO =QHBoxLayout ()#line:1385
        OO00OO0O0O0OO0O0O .text_edit =QTextEdit ()#line:1386
        OO00OO0O0O0OO0O0O .text_edit .setPlaceholderText ("أدخل نص الرسالة هنا...")#line:1387
        OO00OO0O0O0OO0O0O .text_edit .setPlainText (OO00OO0O0O0OO0O0O .template_data .get ("content",""))#line:1388
        O0O00O0O00OOOOOOO .addWidget (OO00OO0O0O0OO0O0O .text_edit ,3 )#line:1389
        OO00000OOOO0O000O =QFrame ()#line:1391
        O00000O00O0OO0000 =QVBoxLayout ()#line:1392
        O00000O00O0OO0000 .addWidget (QLabel ("المتغيرات:"))#line:1393
        for O000000O0O0OOO0O0 in OO00OO0O0O0OO0O0O .columns :#line:1394
            OOO0OO00OO00O0O0O =QPushButton (O000000O0O0OOO0O0 )#line:1395
            OOO0OO00OO00O0O0O .clicked .connect (lambda _O000OOO0OO00O00OO ,v =O000000O0O0OOO0O0 :OO00OO0O0O0OO0O0O .insert_variable (v ))#line:1396
            O00000O00O0OO0000 .addWidget (OOO0OO00OO00O0O0O )#line:1397
        OO00000OOOO0O000O .setLayout (O00000O00O0OO0000 )#line:1398
        O0O0O0O00O0O000OO =QScrollArea ()#line:1400
        O0O0O0O00O0O000OO .setWidget (OO00000OOOO0O000O )#line:1401
        O0O0O0O00O0O000OO .setWidgetResizable (True )#line:1402
        O0O0O0O00O0O000OO .setFixedWidth (150 )#line:1403
        O0O00O0O00OOOOOOO .addWidget (O0O0O0O00O0O000OO ,1 )#line:1404
        OO00OO0O0O0OO0O0O .main_layout .addLayout (O0O00O0O00OOOOOOO )#line:1406
        OO00OO0O0O0OO0O0O .attach_table =QTableWidget ()#line:1408
        OO00OO0O0O0OO0O0O .attach_table .setColumnCount (2 )#line:1409
        OO00OO0O0O0OO0O0O .attach_table .setHorizontalHeaderLabels (["المسار","التعليق"])#line:1410
        OO00OO0O0O0OO0O0O .attach_table .setEditTriggers (QAbstractItemView .NoEditTriggers )#line:1411
        OO00OO0O0O0OO0O0O .attach_table .setSelectionBehavior (QAbstractItemView .SelectRows )#line:1412
        OO00OO0O0O0OO0O0O .attach_table .setSelectionMode (QAbstractItemView .SingleSelection )#line:1413
        OO00OO0O0O0OO0O0O .main_layout .addWidget (OO00OO0O0O0OO0O0O .attach_table )#line:1414
        if "attachments"in OO00OO0O0O0OO0O0O .template_data :#line:1417
            OO00OO0O0O0OO0O0O .attachments =[Attachment (O000000000OOOOOOO ["filepath"],O000000000OOOOOOO ["caption"])for O000000000OOOOOOO in OO00OO0O0O0OO0O0O .template_data ["attachments"]]#line:1418
        O0OO0OOO0OOOO0OOO =QHBoxLayout ()#line:1420
        OO00OO0O0O0OO0O0O .btn_add_att =QPushButton ("إضافة مرفق")#line:1421
        OO00OO0O0O0OO0O0O .btn_add_att .clicked .connect (OO00OO0O0O0OO0O0O .add_file )#line:1422
        OO00OO0O0O0OO0O0O .btn_del_att =QPushButton ("حذف المرفق")#line:1423
        OO00OO0O0O0OO0O0O .btn_del_att .clicked .connect (OO00OO0O0O0OO0O0O .remove_file )#line:1424
        OO00OO0O0O0OO0O0O .btn_edit_cap =QPushButton ("تعديل التعليق")#line:1425
        OO00OO0O0O0OO0O0O .btn_edit_cap .clicked .connect (OO00OO0O0O0OO0O0O .set_caption )#line:1426
        O0OO0OOO0OOOO0OOO .addWidget (OO00OO0O0O0OO0O0O .btn_add_att )#line:1427
        O0OO0OOO0OOOO0OOO .addWidget (OO00OO0O0O0OO0O0O .btn_del_att )#line:1428
        O0OO0OOO0OOOO0OOO .addWidget (OO00OO0O0O0OO0O0O .btn_edit_cap )#line:1429
        OO00OO0O0O0OO0O0O .main_layout .addLayout (O0OO0OOO0OOOO0OOO )#line:1430
        OO00OO0O0O0OO0O0O .refresh_attach_table ()#line:1432
        OO0O00O0OO00OO00O =QDialogButtonBox (QDialogButtonBox .Ok |QDialogButtonBox .Cancel )#line:1434
        OO0O00O0OO00OO00O .accepted .connect (OO00OO0O0O0OO0O0O .accept )#line:1435
        OO0O00O0OO00OO00O .rejected .connect (OO00OO0O0O0OO0O0O .reject )#line:1436
        OO00OO0O0O0OO0O0O .main_layout .addWidget (OO0O00O0OO00OO00O )#line:1437
        OO00OO0O0O0OO0O0O .setLayout (OO00OO0O0O0OO0O0O .main_layout )#line:1439
        OO00OO0O0O0OO0O0O .resize (700 ,500 )#line:1440
    def insert_variable (OO0OO00OOO0OOO000 ,O0OO0OOO0OO0O0OOO ):#line:1442
        O0OOOOOOOO0OOO00O =OO0OO00OOO0OOO000 .text_edit .textCursor ()#line:1443
        O0OOOOOOOO0OOO00O .insertText (f"{{{O0OO0OOO0OO0O0OOO}}}")#line:1444
    def add_file (OO000O00OOO0OOOO0 ):#line:1446
        OO000O0OOO000OOOO ,_OOO00O000O0OO000O =QFileDialog .getOpenFileName (OO000O00OOO0OOOO0 ,"اختر مرفق")#line:1447
        if OO000O0OOO000OOOO :#line:1448
            OO000O00OOO0OOOO0 .attachments .append (Attachment (OO000O0OOO000OOOO ,""))#line:1449
            OO000O00OOO0OOOO0 .refresh_attach_table ()#line:1450
    def remove_file (O00O00O00O0OOOO0O ):#line:1452
        O0O00OO0O0O000OOO =O00O00O00O0OOOO0O .attach_table .currentRow ()#line:1453
        if 0 <=O0O00OO0O0O000OOO <len (O00O00O00O0OOOO0O .attachments ):#line:1454
            O00O00O00O0OOOO0O .attachments .pop (O0O00OO0O0O000OOO )#line:1455
            O00O00O00O0OOOO0O .refresh_attach_table ()#line:1456
    def set_caption (OOOO00OO00OO0O000 ):#line:1458
        O000O0O00OO00OO0O =OOOO00OO00OO0O000 .attach_table .currentRow ()#line:1459
        if 0 <=O000O0O00OO00OO0O <len (OOOO00OO00OO0O000 .attachments ):#line:1460
            OOOO0OO0OO00OO0OO =OOOO00OO00OO0O000 .attachments [O000O0O00OO00OO0O ]#line:1461
            OOO0OO00OOOO00000 ,O0O0O0O0O00OOOO00 =QInputDialog .getMultiLineText (OOOO00OO00OO0O000 ,"تعديل التعليق","التعليق:",OOOO0OO0OO00OO0OO .caption )#line:1462
            if O0O0O0O0O00OOOO00 :#line:1463
                OOOO0OO0OO00OO0OO .caption =OOO0OO00OOOO00000 #line:1464
                OOOO00OO00OO0O000 .refresh_attach_table ()#line:1465
    def refresh_attach_table (O0OOO0OO0OOO0000O ):#line:1467
        O0OOO0OO0OOO0000O .attach_table .setRowCount (len (O0OOO0OO0OOO0000O .attachments ))#line:1468
        for OOO0OOO00OO00OO00 ,O0OO0O00OOO0000OO in enumerate (O0OOO0OO0OOO0000O .attachments ):#line:1469
            O0OOO0OO0OOO0000O .attach_table .setItem (OOO0OOO00OO00OO00 ,0 ,QTableWidgetItem (O0OO0O00OOO0000OO .filepath ))#line:1470
            O0OOO0OO0OOO0000O .attach_table .setItem (OOO0OOO00OO00OO00 ,1 ,QTableWidgetItem (O0OO0O00OOO0000OO .caption ))#line:1471
        O0OOO0OO0OOO0000O .attach_table .resizeColumnsToContents ()#line:1472
    def get_template_data (O0O0OO0O00OO0OOOO ):#line:1474
        return {"statu":O0O0OO0O00OO0OOOO .statu_line .text ().strip (),"content":O0O0OO0O00OO0OOOO .text_edit .toPlainText (),"attachments":[{"filepath":O0O00O00O000OOO00 .filepath ,"caption":O0O00O00O000OOO00 .caption }for O0O00O00O000OOO00 in O0O0OO0O00OO0OOOO .attachments ],"enabled":O0O0OO0O00OO0OOOO .template_data .get ("enabled",True )}#line:1480
class ManualSendDialog (QDialog ):#line:1482
    ""#line:1485
    def __init__ (O0OOOOOO00O0OOO00 ,OO0OO0OO0O00O00OO ,O000000OOO00O0OO0 ):#line:1486
        super ().__init__ (OO0OO0OO0O00O00OO )#line:1487
        O0OOOOOO00O0OOO00 .parent_ui =OO0OO0OO0O00O00OO #line:1488
        O0OOOOOO00O0OOO00 .columns =O000000OOO00O0OO0 #line:1489
        O0OOOOOO00O0OOO00 .attachments =[]#line:1490
        O0OOOOOO00O0OOO00 .setWindowTitle ("إرسال رسالة يدوية")#line:1492
        O0O000OOOO00O0O00 =QVBoxLayout (O0OOOOOO00O0OOO00 )#line:1493
        O0O000OOOO00O0O00 .addWidget (QLabel ("رقم الهاتف:"))#line:1495
        O0OOOOOO00O0OOO00 .phone_line =QLineEdit ()#line:1496
        O0O000OOOO00O0O00 .addWidget (O0OOOOOO00O0OOO00 .phone_line )#line:1497
        O0OO000OO0O0O0OOO =QHBoxLayout ()#line:1499
        O0OOOOOO00O0OOO00 .text_edit =QTextEdit ()#line:1500
        O0OOOOOO00O0OOO00 .text_edit .setPlaceholderText ("أدخل نص الرسالة هنا...")#line:1501
        O0OO000OO0O0O0OOO .addWidget (O0OOOOOO00O0OOO00 .text_edit ,3 )#line:1502
        O00OOO000O000OOOO =QFrame ()#line:1504
        O000000OO0O00OO0O =QVBoxLayout ()#line:1505
        O000000OO0O00OO0O .addWidget (QLabel ("المتغيرات:"))#line:1506
        for O0OOOO0O0OO0O0OO0 in O0OOOOOO00O0OOO00 .columns :#line:1507
            OOO0O00O0OOOO0000 =QPushButton (O0OOOO0O0OO0O0OO0 )#line:1508
            OOO0O00O0OOOO0000 .clicked .connect (lambda _OOOOOO0OOO0O00OO0 ,v =O0OOOO0O0OO0O0OO0 :O0OOOOOO00O0OOO00 .insert_variable (v ))#line:1509
            O000000OO0O00OO0O .addWidget (OOO0O00O0OOOO0000 )#line:1510
        O00OOO000O000OOOO .setLayout (O000000OO0O00OO0O )#line:1511
        O00O0O0O0O000OO0O =QScrollArea ()#line:1512
        O00O0O0O0O000OO0O .setWidget (O00OOO000O000OOOO )#line:1513
        O00O0O0O0O000OO0O .setWidgetResizable (True )#line:1514
        O00O0O0O0O000OO0O .setFixedWidth (150 )#line:1515
        O0OO000OO0O0O0OOO .addWidget (O00O0O0O0O000OO0O ,1 )#line:1516
        O0O000OOOO00O0O00 .addLayout (O0OO000OO0O0O0OOO )#line:1518
        O0OOOOOO00O0OOO00 .attach_table =QTableWidget ()#line:1520
        O0OOOOOO00O0OOO00 .attach_table .setColumnCount (2 )#line:1521
        O0OOOOOO00O0OOO00 .attach_table .setHorizontalHeaderLabels (["المسار","التعليق"])#line:1522
        O0OOOOOO00O0OOO00 .attach_table .setEditTriggers (QAbstractItemView .NoEditTriggers )#line:1523
        O0OOOOOO00O0OOO00 .attach_table .setSelectionBehavior (QAbstractItemView .SelectRows )#line:1524
        O0OOOOOO00O0OOO00 .attach_table .setSelectionMode (QAbstractItemView .SingleSelection )#line:1525
        O0O000OOOO00O0O00 .addWidget (O0OOOOOO00O0OOO00 .attach_table )#line:1526
        OOO00O00OOO0O00O0 =QHBoxLayout ()#line:1528
        O0OOOOOO00O0OOO00 .btn_add_att =QPushButton ("إضافة مرفق")#line:1529
        O0OOOOOO00O0OOO00 .btn_add_att .clicked .connect (O0OOOOOO00O0OOO00 .add_file )#line:1530
        O0OOOOOO00O0OOO00 .btn_del_att =QPushButton ("حذف المرفق")#line:1531
        O0OOOOOO00O0OOO00 .btn_del_att .clicked .connect (O0OOOOOO00O0OOO00 .remove_file )#line:1532
        O0OOOOOO00O0OOO00 .btn_edit_cap =QPushButton ("تعديل التعليق")#line:1533
        O0OOOOOO00O0OOO00 .btn_edit_cap .clicked .connect (O0OOOOOO00O0OOO00 .set_caption )#line:1534
        OOO00O00OOO0O00O0 .addWidget (O0OOOOOO00O0OOO00 .btn_add_att )#line:1535
        OOO00O00OOO0O00O0 .addWidget (O0OOOOOO00O0OOO00 .btn_del_att )#line:1536
        OOO00O00OOO0O00O0 .addWidget (O0OOOOOO00O0OOO00 .btn_edit_cap )#line:1537
        O0O000OOOO00O0O00 .addLayout (OOO00O00OOO0O00O0 )#line:1538
        O0OOOOOO00O0OOO00 .refresh_attach_table ()#line:1540
        O00000OO00OO0O000 =QDialogButtonBox (QDialogButtonBox .Ok |QDialogButtonBox .Cancel )#line:1542
        O00000OO00OO0O000 .accepted .connect (O0OOOOOO00O0OOO00 .send_message )#line:1543
        O00000OO00OO0O000 .rejected .connect (O0OOOOOO00O0OOO00 .reject )#line:1544
        O0O000OOOO00O0O00 .addWidget (O00000OO00OO0O000 )#line:1545
        O0OOOOOO00O0OOO00 .setLayout (O0O000OOOO00O0O00 )#line:1547
        O0OOOOOO00O0OOO00 .resize (700 ,500 )#line:1548
    def insert_variable (O0OO00OOO00OOOOO0 ,OOO0O0OO000O00OOO ):#line:1550
        OO000OOO00O0O0O00 =O0OO00OOO00OOOOO0 .text_edit .textCursor ()#line:1551
        OO000OOO00O0O0O00 .insertText (f"{{{OOO0O0OO000O00OOO}}}")#line:1552
    def add_file (O000000O0O0OO0O00 ):#line:1554
        OOO0000O00OO0O0O0 ,_OOO00O0O0OOOO00OO =QFileDialog .getOpenFileName (O000000O0O0OO0O00 ,"اختر مرفق")#line:1555
        if OOO0000O00OO0O0O0 :#line:1556
            O000000O0O0OO0O00 .attachments .append (Attachment (OOO0000O00OO0O0O0 ,""))#line:1557
            O000000O0O0OO0O00 .refresh_attach_table ()#line:1558
    def remove_file (O0OOOO0000000O000 ):#line:1560
        OO0OOOO0O0O000000 =O0OOOO0000000O000 .attach_table .currentRow ()#line:1561
        if 0 <=OO0OOOO0O0O000000 <len (O0OOOO0000000O000 .attachments ):#line:1562
            O0OOOO0000000O000 .attachments .pop (OO0OOOO0O0O000000 )#line:1563
            O0OOOO0000000O000 .refresh_attach_table ()#line:1564
    def set_caption (O000O0OO00O0OO00O ):#line:1566
        OO0OO00OO00OO0O0O =O000O0OO00O0OO00O .attach_table .currentRow ()#line:1567
        if 0 <=OO0OO00OO00OO0O0O <len (O000O0OO00O0OO00O .attachments ):#line:1568
            O0O0OO0000OO00OO0 =O000O0OO00O0OO00O .attachments [OO0OO00OO00OO0O0O ]#line:1569
            OO00000O000000000 ,O000000OO0OO00O00 =QInputDialog .getMultiLineText (O000O0OO00O0OO00O ,"تعديل التعليق","التعليق:",O0O0OO0000OO00OO0 .caption )#line:1570
            if O000000OO0OO00O00 :#line:1571
                O0O0OO0000OO00OO0 .caption =OO00000O000000000 #line:1572
                O000O0OO00O0OO00O .refresh_attach_table ()#line:1573
    def refresh_attach_table (OOOO0O00O0O0OO00O ):#line:1575
        OOOO0O00O0O0OO00O .attach_table .setRowCount (len (OOOO0O00O0O0OO00O .attachments ))#line:1576
        for OO00OO0O0000O0OOO ,OO0O00O00OO000O00 in enumerate (OOOO0O00O0O0OO00O .attachments ):#line:1577
            OOOO0O00O0O0OO00O .attach_table .setItem (OO00OO0O0000O0OOO ,0 ,QTableWidgetItem (OO0O00O00OO000O00 .filepath ))#line:1578
            OOOO0O00O0O0OO00O .attach_table .setItem (OO00OO0O0000O0OOO ,1 ,QTableWidgetItem (OO0O00O00OO000O00 .caption ))#line:1579
        OOOO0O00O0O0OO00O .attach_table .resizeColumnsToContents ()#line:1580
    def send_message (OO0000OOOO00OOO0O ):#line:1582
        OO0O0OO000OO0O0O0 =OO0000OOOO00OOO0O .phone_line .text ().strip ()#line:1583
        if not OO0O0OO000OO0O0O0 :#line:1584
            QMessageBox .warning (OO0000OOOO00OOO0O ,"تنبيه","يرجى إدخال رقم الهاتف.")#line:1585
            return #line:1586
        OO00O0OOO0000OO0O =OO0000OOOO00OOO0O .text_edit .toPlainText ().strip ()#line:1587
        O0000O0OOOO0OO00O =[{"filepath":OO00O0000O0O0O0OO .filepath ,"caption":OO00O0000O0O0O0OO .caption }for OO00O0000O0O0O0OO in OO0000OOOO00OOO0O .attachments ]#line:1588
        send_message_to_new_number (OO0O0OO000OO0O0O0 ,OO00O0OOO0000OO0O ,O0000O0OOOO0OO00O )#line:1590
        QMessageBox .information (OO0000OOOO00OOO0O ,"نجاح","تم إرسال الرسالة اليدوية.")#line:1591
        OO0000OOOO00OOO0O .accept ()#line:1592
def main ():#line:1598
    OOO000O0O0O00O0OO =QApplication (sys .argv )#line:1599
    O0O00O0OOOOO00O0O =os .path .join (os .path .dirname (__file__ ),"style_sheet.qss")#line:1600
    if os .path .exists (O0O00O0OOOOO00O0O ):#line:1601
        with open (O0O00O0OOOOO00O0O ,"r",encoding ="utf-8")as O0O00OOOO00OO0O0O :#line:1602
            OOO000O0O0O00O0OO .setStyleSheet (O0O00OOOO00OO0O0O .read ())#line:1603
    O00O0O0OO0OOO0O0O =WhatsAppSenderUI ()#line:1605
    global ui_instance #line:1606
    ui_instance =O00O0O0OO0OOO0O0O #line:1607
    O00O0O0OO0OOO0O0O .show ()#line:1608
    sys .exit (OOO000O0O0O00O0OO .exec_ ())#line:1609
if __name__ =="__main__":#line:1611
    main ()#line:1612
