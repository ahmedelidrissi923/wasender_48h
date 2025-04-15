__version__ = "1.2.2"

######################################
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import tkinter.font as tkFont
import json, os, platform

# ==================== إنشاء نافذة الجذر ====================
root = tk.Tk()
root.title("نظام الترقيم الذكي للتوصيلات")
root.geometry("1000x800")
root.minsize(800, 600)

# ==================== المتغيرات العامة ====================
img_path = None
img_original = None
base_preview_img = None
preview_img = None

scale_x = 1.0
scale_y = 1.0

# قائمة التوصيلات؛ كل توصيلة عبارة عن قاموس يحتوي على "x", "y" و"val"
positions = []
undo_stack = []
font_size = 30
padding_rect = 4

zoom_factor = 1.0
pan_offset = [0, 0]
pan_start = (0, 0)

selected_marker_index = None
drag_threshold = 10

# خيار حفظ المشروع
#   "pdf" (PDF فقط - الافتراضي)
#   "images+pdf" (صور + PDF)
#   "images" (صور فقط)
save_option = tk.StringVar(root, value="pdf")

# إعدادات الخط
use_custom_font = tk.BooleanVar(root, value=False)
selected_font_family = tk.StringVar(root, value="Arial")
selected_font_weight = tk.StringVar(root, value="normal")
selected_font_slant = tk.StringVar(root, value="roman")
selected_font_file = None

font_mapping = {
    "Arial": "arial.ttf",
    "Times New Roman": "times.ttf",
    "Courier New": "cour.ttf",
    "Tahoma": "tahoma.ttf",
    "Verdana": "verdana.ttf"
}

# حقول إدخال رقم البداية والنهاية
ent_start = None
ent_end = None

# متغير لتحديد نمط التوزيع (default: التوزيع العادي، layered: توزيع طبقات)
mode_var = tk.StringVar(root, value="default")

# ==================== الدوال المساعدة (عرض معلومات، اختيار صورة ...) ====================

def show_help():
    """
    دالة لإظهار نافذة المساعدة أو معلومات حول الأداة.
    """
    messagebox.showinfo(
        "حول الأداة",
        "هذا برنامج نظام ترقيم ذكي للتوصيلات:\n"
        "- يمكنك اختيار صورة وإضافة مواضع الأرقام عليها.\n"
        "- يمكنك اختيار نمط التوزيع عادي أو على شكل طبقات.\n"
        "- يمكنك توليد صفحات مرقمة (صور أو PDF) متسلسلة أو موزعة.\n"
        "- يدعم حفظ وتحميل مشروع التوصيلات.\n\n"
        "استخدام سعيد!"
    )

def select_image():
    """
    دالة لاختيار صورة من الجهاز وتهيئتها للمعاينة على الـ Canvas.
    """
    global img_path, img_original, base_preview_img, scale_x, scale_y
    chosen = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
    )
    if chosen:
        img_path = chosen
        try:
            tmp_image = Image.open(chosen)
            preview = tmp_image.copy()
            # تصغير الصورة للمعاينة على الـCanvas
            preview.thumbnail((canvas.winfo_width(), canvas.winfo_height()))
            base_preview_img = preview.copy()

            scale_x = tmp_image.width / base_preview_img.width
            scale_y = tmp_image.height / base_preview_img.height

            img_original = tmp_image
            tmp_image.close()

            lbl_status.config(text="✅ تم اختيار الصورة بنجاح")
            update_preview()

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل تحميل الصورة\n{e}")

def reset_view():
    """
    دالة لإعادة تعيين مستوى التكبير/التصغير وإزاحة اللوحة.
    """
    global zoom_factor, pan_offset
    zoom_factor = 1.0
    pan_offset = [0, 0]
    update_preview()

# ==================== الدوال الخاصة بالتوزيع ====================

def calculate_preview_values(start, end, positions):
    """
    توزيع عرض المعاينة للوضع العادي:
    لكل توصيلة يتم حساب الرقم:
      printed_value = start + (فهرس القيمة بين القيم الفريدة) % (end - start + 1)
    """
    total_numbers = end - start + 1
    if total_numbers <= 0 or not positions:
        return []
    unique_vals = sorted({pos['val'] for pos in positions})
    val_to_number = {}
    for i, val in enumerate(unique_vals):
        assigned_number = start + (i % total_numbers)
        val_to_number[val] = assigned_number
    preview_numbers = [val_to_number[pos['val']] for pos in positions]
    return preview_numbers

def distribute_with_duplicates(start, end, positions):
    """
    توزيع الأرقام بالنمط العادي مع احترام التكرارات:
    التوصيلات ذات نفس القيمة تحصل على نفس الرقم.
    ثم توزيع الأرقام حسب عدد القيم الفريدة.
    """
    total_numbers = end - start + 1
    if total_numbers <= 0 or not positions:
        return []
    unique_vals = sorted({pos['val'] for pos in positions})
    val_to_sequence = {val: [] for val in unique_vals}

    # تعبئة التسلسل
    for i in range(total_numbers):
        current = start + i
        idx = i % len(unique_vals)  # توزيع بشكل دوري
        val_to_sequence[unique_vals[idx]].append(current)

    # إنشاء الصفحات (حيث كل صفحة لديها قيمة مرقمة لكل توصيلة)
    distributed = []
    max_len = max(len(seq) for seq in val_to_sequence.values())

    for page in range(max_len):
        page_values = []
        for pos in positions:
            seq = val_to_sequence[pos['val']]
            value = seq[page] if page < len(seq) else None
            page_values.append(value)
        distributed.append(page_values)

    return distributed

def distribute_by_layers(start, end, positions):
    """
    توزيع الأرقام بنمط الطبقات (Layered):
    مثال: إذا كانت التوصيلات 3 (مثلًا: أعلى، وسط، أسفل) والرقم من 1 إلى 9،
    فإننا نحصل على:
       الصفحة 1: 1 (أعلى)، 4 (وسط)، 7 (أسفل)
       الصفحة 2: 2 (أعلى)، 5 (وسط)، 8 (أسفل)
       الصفحة 3: 3 (أعلى)، 6 (وسط)، 9 (أسفل)
    """
    total_numbers = end - start + 1
    if total_numbers <= 0 or not positions:
        return []

    arr = list(range(start, end + 1))
    unique_vals = sorted({p["val"] for p in positions})
    n = len(unique_vals)

    # كل Layer يمسك قيمه بطريقة التدرج (مثلاً: layer[0] = [1, 4, 7], layer[1] = [2, 5, 8], ...)
    layers = [arr[i::n] for i in range(n)]

    # نحتاج أقصى عدد صفحات = أقصى طول لأي layer
    max_len = max(len(layer) for layer in layers)

    # خريطة لمعرفة أي فهرس يعبر عن أي توصيلة فريدة
    val_to_idx = {v: i for i, v in enumerate(unique_vals)}

    pages = []
    for page_index in range(max_len):
        page_vals = []
        for pos in positions:
            # اكتشاف أي Layer خاصة بقيمة هذا الـMarker
            layer_index = val_to_idx[pos["val"]]
            if page_index < len(layers[layer_index]):
                page_vals.append(layers[layer_index][page_index])
            else:
                page_vals.append(None)
        pages.append(page_vals)

    return pages

# ==================== دوال التحكم بالبكرة (تكبير/تصغير) ====================

def on_mouse_wheel_zoom(event):
    global zoom_factor
    if event.delta:
        if event.delta > 0:
            zoom_factor *= 1.1
        else:
            zoom_factor /= 1.1
    else:
        # في بعض الأنظمة قد يأتي الحدث بأرقام مختلفة (num=4 أو num=5)
        if event.num == 4:
            zoom_factor *= 1.1
        elif event.num == 5:
            zoom_factor /= 1.1
    update_preview()

# ==================== دوال المعاينة على الـ Canvas ====================

def update_preview():
    """
    دالة لرسم الصورة على الـ Canvas ووضع الأرقام عليها للمعاينة.
    """
    canvas.delete("all")
    if base_preview_img is None:
        return

    # تكبير/تصغير الصورة وفق zoom_factor
    new_w = int(base_preview_img.width * zoom_factor)
    new_h = int(base_preview_img.height * zoom_factor)
    resized_img = base_preview_img.resize((new_w, new_h), Image.LANCZOS)

    global preview_img
    preview_img = ImageTk.PhotoImage(resized_img)
    canvas.create_image(pan_offset[0], pan_offset[1], anchor=tk.NW, image=preview_img, tags="image")

    try:
        current_font_size = int(ent_font_size.get())
    except:
        current_font_size = font_size

    # الخط الخاص بالمعاينة (tkFont)
    if use_custom_font.get():
        preview_font_family = "Arial"  # عند استخدام ملف خط مخصص، نضبط خطًا افتراضيًا للمعاينة
    else:
        preview_font_family = selected_font_family.get()

    preview_font = tkFont.Font(
        family=preview_font_family,
        size=current_font_size,
        weight=selected_font_weight.get() if not use_custom_font.get() else "normal",
        slant=selected_font_slant.get() if not use_custom_font.get() else "roman"
    )

    # أرقام البداية والنهاية
    try:
        start_num = int(ent_start.get().strip())
        end_num = int(ent_end.get().strip())
    except:
        start_num = 1
        end_num = len(positions)

    # عند اختيار توزيع الطبقات، نستخدم الصفحة الأولى كمعاينة
    if mode_var.get() == "layered":
        pages_values = distribute_by_layers(start_num, end_num, positions)
        preview_vals = list(pages_values[0]) if pages_values else []
    else:
        # توزيع عادي للمعاينة
        preview_vals = calculate_preview_values(start_num, end_num, positions)

    # رسم مربعات النصوص
    for idx, (marker, text_val) in enumerate(zip(positions, preview_vals)):
        if text_val is None:
            continue

        dx = marker["x"] * zoom_factor + pan_offset[0]
        dy = marker["y"] * zoom_factor + pan_offset[1]
        text = str(text_val)

        text_w = preview_font.measure(text)
        text_h = preview_font.metrics("linespace")

        left = dx - (text_w/2 + padding_rect)
        top = dy - (text_h/2 + padding_rect)
        right = dx + (text_w/2 + padding_rect)
        bottom = dy + (text_h/2 + padding_rect)

        # إذا كانت التوصيلة محددة
        if selected_marker_index == idx:
            canvas.create_rectangle(left-2, top-2, right+2, bottom+2,
                                    outline="orange", width=3, tags="mark")

        # رسم الإطار الأحمر
        canvas.create_rectangle(left, top, right, bottom, outline="red", width=2, tags="mark")
        # رسم النص
        canvas.create_text(dx, dy, text=text, fill="blue", font=preview_font, tags="mark")

# ==================== دوال التعامل مع التوصيلات في الـ Canvas ====================

def move_selected_marker(dx, dy):
    """
    تحريك التوصيلة المحددة بمقدار (dx, dy) على الصورة (بالمقاييس الحقيقية).
    """
    global selected_marker_index
    if selected_marker_index is not None and 0 <= selected_marker_index < len(positions):
        marker = positions[selected_marker_index]
        # نحول dx, dy إلى قيم على الصورة قبل التكبير
        marker["x"] += dx / zoom_factor
        marker["y"] += dy / zoom_factor
        update_preview()

def handle_arrow_keys(event):
    if event.keysym == "Up":
        move_selected_marker(0, -5)
    elif event.keysym == "Down":
        move_selected_marker(0, 5)
    elif event.keysym == "Left":
        move_selected_marker(-5, 0)
    elif event.keysym == "Right":
        move_selected_marker(5, 0)

def repeat_marker():
    """
    نسخ (تكرار) التوصيلة المحددة وإزاحتها قليلًا.
    """
    global selected_marker_index
    if selected_marker_index is not None:
        save_undo_state()
        new_marker = positions[selected_marker_index].copy()
        new_marker["x"] -= 15  # إزاحة 15px لليسار
        positions.append(new_marker)
        selected_marker_index = len(positions) - 1
        update_preview()
        lbl_status.config(text=f"🔁 تمت تكرار التوصيلة رقم {new_marker['val']}")

def get_marker_at_in_base(x, y):
    """
    إرجاع فهرس التوصيلة (positions) إذا تم النقر عليها (بهامش معيّن drag_threshold).
    """
    tol = drag_threshold / zoom_factor
    for idx, marker in enumerate(positions):
        if abs(marker["x"] - x) <= tol and abs(marker["y"] - y) <= tol:
            return idx
    return None

def save_undo_state():
    """
    حفظ حالة من أجل التراجع (undo).
    """
    undo_stack.append([m.copy() for m in positions])
    if len(undo_stack) > 20:
        undo_stack.pop(0)

def undo_action():
    global selected_marker_index
    if undo_stack:
        last_state = undo_stack.pop()
        positions.clear()
        positions.extend(last_state)
        selected_marker_index = None
        update_preview()
        lbl_status.config(text="↩️ تم التراجع عن آخر تعديل")

def on_left_button_press(event):
    """
    حدث النقر بالزر الأيسر لتحديد توصيلة إذا كانت تحته.
    """
    global selected_marker_index
    bx = (event.x - pan_offset[0]) / zoom_factor
    by = (event.y - pan_offset[1]) / zoom_factor
    idx = get_marker_at_in_base(bx, by)
    if idx is not None:
        selected_marker_index = idx
        lbl_status.config(text=f"✅ التوصيلة رقم {positions[idx]['val']} محددة")
    else:
        selected_marker_index = None
        lbl_status.config(text="لم يتم تحديد توصيلة")
    update_preview()

def on_marker_drag(event):
    """
    سحب التوصيلة المحددة بالماوس.
    """
    if selected_marker_index is not None:
        bx = (event.x - pan_offset[0]) / zoom_factor
        by = (event.y - pan_offset[1]) / zoom_factor
        positions[selected_marker_index]["x"] = bx
        positions[selected_marker_index]["y"] = by
        update_preview()

def on_marker_release(event):
    lbl_status.config(text="✅ تم تعديل المواقع")

def on_right_button_press(event):
    """
    بدأ السحب بالزر الأيمن للفأرة من أجل التحريك (pan).
    """
    global pan_start
    pan_start = (event.x, event.y)

def on_pan_motion(event):
    """
    السحب بالزر الأيمن للفأرة لتحريك الصورة.
    """
    global pan_offset, pan_start
    dx = event.x - pan_start[0]
    dy = event.y - pan_start[1]
    pan_offset[0] += dx
    pan_offset[1] += dy
    pan_start = (event.x, event.y)
    update_preview()

def on_pan_release(event):
    pass

# ==================== إضافة وحساب قيمة توصيلة جديدة ====================

def next_marker_value_func():
    """
    الحصول على رقم توصيلة جديد غير مستخدم في positions.
    """
    used = {marker["val"] for marker in positions}
    i = 1
    while i in used:
        i += 1
    return i

def add_marker():
    global selected_marker_index
    new_val = next_marker_value_func()
    cw = canvas.winfo_width()
    ch = canvas.winfo_height()
    center_x = (cw/2 - pan_offset[0]) / zoom_factor
    center_y = (ch/2 - pan_offset[1]) / zoom_factor
    save_undo_state()
    positions.append({"x": center_x, "y": center_y, "val": new_val})
    selected_marker_index = len(positions) - 1
    update_preview()
    lbl_status.config(text=f"➕ تمت إضافة التوصيلة رقم {new_val}")

# ==================== توليد الصفحات المرقمة ====================

def generate_numbered_pages():
    # 1) قراءة رقم البداية والنهاية
    try:
        start_str = ent_start.get().strip()
        end_str = ent_end.get().strip()
        start_num = int(start_str)
        end_num = int(end_str)
        if start_num > end_num:
            raise ValueError
        total = end_num - start_num + 1
    except:
        messagebox.showerror("خطأ", "يرجى إدخال أرقام بداية ونهاية صحيحة (مثلاً 001 و0010)")
        return

    if not positions:
        messagebox.showerror("خطأ", "لم يتم تحديد أي توصيلة على الصورة")
        return

    # 2) الحصول على حجم الخط
    try:
        current_font_size = int(ent_font_size.get())
    except:
        current_font_size = font_size

    # 3) تحديد ملف الخط
    if use_custom_font.get():
        if not selected_font_file:
            messagebox.showerror("خطأ", "يرجى اختيار ملف الخط المخصص")
            return
        export_font_file = selected_font_file
    else:
        export_font_file = font_mapping.get(selected_font_family.get(), "arial.ttf")

    export_font_size = int(current_font_size * scale_x)
    try:
        font_used = ImageFont.truetype(export_font_file, export_font_size)
    except Exception as e:
        messagebox.showerror("خطأ", f"تعذر تحميل الخط\n{e}")
        return

    # 4) فتح الصورة الأصلية
    if not img_path or not os.path.exists(img_path):
        messagebox.showerror("خطأ", "الصورة الأصلية غير متوفرة")
        return
    try:
        base_image = Image.open(img_path)
    except Exception as e:
        messagebox.showerror("خطأ", f"تعذر فتح الصورة الأصلية\n{e}")
        return

    # 5) تحديد اسم المجلد والملف بناءً على خيار الحفظ
    base_name = os.path.splitext(os.path.basename(img_path))[0]
    if save_option.get() == "pdf":
        out_dir = filedialog.askdirectory(title="اختر مجلد الحفظ")
        if not out_dir:
            return
        new_dir = out_dir
    else:
        out_dir = filedialog.askdirectory(title="اختر مجلد الحفظ")
        if not out_dir:
            return
        new_dir = os.path.join(out_dir, base_name)
        os.makedirs(new_dir, exist_ok=True)

    # 6) إعداد tkFont لتصحيح مركز النص (لأخذ قياسات النص وقت الرسم)
    if use_custom_font.get():
        preview_font_family = "Arial"
    else:
        preview_font_family = selected_font_family.get()

    tk_font_temp = tkFont.Font(
        family=preview_font_family,
        size=current_font_size,
        weight=selected_font_weight.get() if not use_custom_font.get() else "normal",
        slant=selected_font_slant.get() if not use_custom_font.get() else "roman"
    )

    # 7) توزيع الأرقام وفق وضع التوزيع المحدد
    if mode_var.get() == "layered":
        pages_values = distribute_by_layers(start_num, end_num, positions)
    else:
        pages_values = distribute_with_duplicates(start_num, end_num, positions)

    pages = len(pages_values)
    progress_bar["maximum"] = pages
    progress_bar["value"] = 0

    saved_images = []
    width_str = len(start_str)  # لتنسيق النص (عدد الأصفار في البداية مثلاً)

    for page_index, page_vals in enumerate(pages_values):
        new_img = base_image.copy()
        draw = ImageDraw.Draw(new_img)
        for marker, printed_value in zip(positions, page_vals):
            if printed_value is None:
                continue

            text_formatted = f"{printed_value:0{width_str}d}"  # تنسيق بالأصفار بناءً على طول start_str
            actual_x = marker["x"] * scale_x
            actual_y = marker["y"] * scale_y

            tk_w = tk_font_temp.measure(text_formatted)
            tk_h = tk_font_temp.metrics("linespace")

            pil_bbox = font_used.getbbox(text_formatted)
            pil_w = pil_bbox[2] - pil_bbox[0]
            pil_h = pil_bbox[3] - pil_bbox[1]

            # فروق تعويض لاختلاف قياس PIL عن قياس tkFont
            corr_x = (tk_w - pil_w) / 2
            corr_y = (tk_h - pil_h) / 2

            text_x = actual_x - pil_w/2 + corr_x
            text_y = actual_y - pil_h/2 + corr_y

            draw.text((text_x, text_y), text_formatted, font=font_used, fill="blue")

        page_name = os.path.join(new_dir, f"page_{page_index + 1:03}.png")
        new_img.save(page_name)
        saved_images.append(page_name)

        progress_bar["value"] += 1
        root.update_idletasks()

    # توليد ملف PDF إن لزم
    if save_option.get() in ("pdf", "images+pdf"):
        pdf_path = os.path.join(new_dir, base_name + ".pdf")
        try:
            images_for_pdf = [Image.open(p).convert("RGB") for p in saved_images]
            images_for_pdf[0].save(pdf_path, save_all=True, append_images=images_for_pdf[1:])
        except Exception as e:
            messagebox.showerror("خطأ", f"تعذر حفظ ملف PDF\n{e}")
            return

    # في حال حفظ PDF فقط، نحذف الصور المؤقتة
    if save_option.get() == "pdf":
        for p in saved_images:
            if os.path.exists(p):
                os.remove(p)
        msg = f"تم توليد الملف PDF: {os.path.join(out_dir, base_name + '.pdf')}"
    elif save_option.get() == "images+pdf":
        msg = f"تم توليد الصور وملف PDF في المجلد: {new_dir}"
    else:
        msg = f"تم توليد الصور في المجلد: {new_dir}"

    messagebox.showinfo("تم", msg)

# ==================== دوال حفظ واستعادة المشروع ====================

def save_project():
    if not img_path:
        messagebox.showerror("خطأ", "لا توجد صورة حالية")
        return
    project = {
        "img_path": img_path,
        "positions": positions,
        "font_size": ent_font_size.get(),
        "use_custom_font": use_custom_font.get(),
        "selected_font_file": selected_font_file,
        "font_family": selected_font_family.get(),
        "font_weight": selected_font_weight.get(),
        "font_slant": selected_font_slant.get(),
        "save_option": save_option.get(),
        "start_num": ent_start.get(),
        "end_num": ent_end.get()
    }
    path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("Project file", "*.json")]
    )
    if path:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(project, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("تم", "تم حفظ المشروع")

def load_project():
    global img_path, img_original, base_preview_img, scale_x, scale_y, selected_font_file
    chosen = filedialog.askopenfilename(filetypes=[("Project file", "*.json")])
    if not chosen:
        return
    with open(chosen, "r", encoding="utf-8") as f:
        project = json.load(f)

    path_img = project.get("img_path")
    if not path_img or not os.path.exists(path_img):
        messagebox.showerror("خطأ", "تعذر العثور على الصورة الأصلية")
        return

    try:
        tmp_image = Image.open(path_img)
        preview = tmp_image.copy()
        preview.thumbnail((canvas.winfo_width(), canvas.winfo_height()))
        base_preview_img = preview.copy()

        scale_x = tmp_image.width / base_preview_img.width
        scale_y = tmp_image.height / base_preview_img.height

        img_original = tmp_image
        tmp_image.close()
        img_path = path_img
    except Exception as e:
        messagebox.showerror("خطأ", f"فشل تحميل الصورة\n{e}")
        return

    positions.clear()
    positions.extend(project.get("positions", []))

    ent_font_size.delete(0, tk.END)
    ent_font_size.insert(0, project.get("font_size", "30"))
    use_custom_font.set(project.get("use_custom_font", False))
    selected_font_file = project.get("selected_font_file")
    selected_font_family.set(project.get("font_family", "Arial"))
    selected_font_weight.set(project.get("font_weight", "normal"))
    selected_font_slant.set(project.get("font_slant", "roman"))
    lbl_font_file.config(
        text=f"ملف الخط: {os.path.basename(selected_font_file) if selected_font_file else 'لم يتم اختيار ملف'}"
    )
    save_option.set(project.get("save_option", "pdf"))

    ent_start.delete(0, tk.END)
    ent_start.insert(0, project.get("start_num", "00001"))

    ent_end.delete(0, tk.END)
    ent_end.insert(0, project.get("end_num", "01000"))

    update_preview()
    messagebox.showinfo("تم", "تم تحميل المشروع")

# ==================== اختصارات الكيبورد ====================

def bind_shortcuts():
    root.bind("<Control-z>", lambda e: undo_action())
    root.bind("<Control-s>", lambda e: save_project())
    root.bind("<Control-o>", lambda e: load_project())
    root.bind("<Control-r>", lambda e: repeat_marker())
    root.bind("<Control-n>", lambda e: add_marker())
    root.bind("<Up>", handle_arrow_keys)
    root.bind("<Down>", handle_arrow_keys)
    root.bind("<Left>", handle_arrow_keys)
    root.bind("<Right>", handle_arrow_keys)

# ==================== واجهة المستخدم (Layout) ====================

# نستخدم PanedWindow لتقسيم النافذة
paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief="raised", sashwidth=5)
paned.pack(fill=tk.BOTH, expand=True)

# اللوحة اليسرى للمعاينة
frame_preview = tk.Frame(paned, bg="#f0f0f0")
paned.add(frame_preview, minsize=600)

canvas = tk.Canvas(frame_preview, bg="gray")
canvas.pack(fill=tk.BOTH, expand=True)
canvas.bind("<ButtonPress-1>", on_left_button_press)
canvas.bind("<B1-Motion>", on_marker_drag)
canvas.bind("<ButtonRelease-1>", on_marker_release)
canvas.bind("<ButtonPress-3>", on_right_button_press)
canvas.bind("<B3-Motion>", on_pan_motion)
canvas.bind("<ButtonRelease-3>", on_pan_release)

if platform.system() == "Windows":
    canvas.bind("<MouseWheel>", on_mouse_wheel_zoom)
else:
    canvas.bind("<Button-4>", on_mouse_wheel_zoom)
    canvas.bind("<Button-5>", on_mouse_wheel_zoom)

# اللوحة اليمنى (إطار رئيسي) - نضيف عليها سكروول بار
frame_options = tk.Frame(paned, bg="#e0e0e0")
paned.add(frame_options, minsize=300)

# عمل Canvas داخلي للتمرير
options_canvas = tk.Canvas(frame_options, bg="#e0e0e0")
options_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame_options, orient="vertical", command=options_canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

options_canvas.configure(yscrollcommand=scrollbar.set)

# إطار داخلي نضع عليه عناصر الضبط
frame_options_inner = tk.Frame(options_canvas, bg="#e0e0e0")
options_canvas.create_window((0, 0), window=frame_options_inner, anchor="nw")

def on_frame_options_configure(event):
    options_canvas.configure(scrollregion=options_canvas.bbox("all"))

frame_options_inner.bind("<Configure>", on_frame_options_configure)

# ===== في الإطار الداخلي نضع كل الأدوات =====

# تقسيمه إلى قسمين علوي وسفلي
frame_top = tk.Frame(frame_options_inner, bg="#e0e0e0")
frame_top.grid(row=0, column=0, sticky="ew")
frame_top.grid_columnconfigure(0, weight=1)
frame_top.grid_columnconfigure(1, weight=1)

frame_bottom = tk.Frame(frame_options_inner, bg="#e0e0e0")
frame_bottom.grid(row=1, column=0, sticky="nsew", pady=(20,0))
frame_bottom.grid_columnconfigure(0, weight=1)

# 1) القسم العلوي
btn_select_img = tk.Button(
    frame_top, text="📷 تغيير/اختيار صورة", command=select_image, bg="#d1e7dd", width=15
)
btn_select_img.grid(row=0, column=0, columnspan=2, pady=(0,10), sticky="ew")

tk.Label(frame_top, text="🔠 حجم الخط:", bg="#e0e0e0").grid(row=1, column=0, sticky="e")
ent_font_size = tk.Entry(frame_top, width=10)
ent_font_size.insert(0, str(font_size))
ent_font_size.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
ent_font_size.bind("<KeyRelease>", lambda event: update_preview())

tk.Label(frame_top, text="🚦 رقم البداية:", bg="#e0e0e0").grid(row=2, column=0, sticky="e")
ent_start = tk.Entry(frame_top, width=10)
ent_start.insert(0, "01")
ent_start.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

tk.Label(frame_top, text="🚦 رقم النهاية:", bg="#e0e0e0").grid(row=3, column=0, sticky="e")
ent_end = tk.Entry(frame_top, width=10)
ent_end.insert(0, "010")
ent_end.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

tk.Button(
    frame_top, text="🔁 إعادة العرض", command=reset_view, bg="#c9cbc9", width=15
).grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")

chk_custom_font = tk.Checkbutton(
    frame_top, text="📝 استخدام خط مخصص", variable=use_custom_font, command=update_preview, bg="#e0e0e0"
)
chk_custom_font.grid(row=5, column=0, columnspan=2, pady=5, sticky="w")

def select_font_file():
    global selected_font_file
    chosen = filedialog.askopenfilename(filetypes=[("Font files", "*.ttf *.otf")])
    if chosen:
        selected_font_file = chosen
        lbl_font_file.config(text=f"ملف الخط: {os.path.basename(chosen)}")
        update_preview()

btn_select_font = tk.Button(
    frame_top, text="📂 اختر ملف خط", command=select_font_file, bg="#f8d7da", width=15
)
btn_select_font.grid(row=6, column=0, columnspan=2, pady=5, sticky="ew")

lbl_font_file = tk.Label(frame_top, text="لم يتم اختيار ملف الخط", bg="#e0e0e0")
lbl_font_file.grid(row=7, column=0, columnspan=2, sticky="w", pady=2)

tk.Label(frame_top, text="📚 خط النظام:", bg="#e0e0e0").grid(row=8, column=0, columnspan=2, pady=(10,0))
om_font_family = tk.OptionMenu(frame_top, selected_font_family, *tkFont.families(), command=lambda _: update_preview())
om_font_family.config(bg="#fceabb")
om_font_family.grid(row=9, column=0, columnspan=2, sticky="ew")

tk.Label(frame_top, text="الوزن:", bg="#e0e0e0").grid(row=10, column=0, sticky="e")
tk.OptionMenu(frame_top, selected_font_weight, "normal", "bold", command=lambda _: update_preview())\
    .grid(row=10, column=1, sticky="ew")

tk.Label(frame_top, text="الميل:", bg="#e0e0e0").grid(row=11, column=0, sticky="e")
tk.OptionMenu(frame_top, selected_font_slant, "roman", "italic", command=lambda _: update_preview())\
    .grid(row=11, column=1, sticky="ew")

# 2) القسم السفلي (عمليات التوصيلات)
tk.Label(frame_bottom, text="📊 نمط التوزيع:", bg="#e0e0e0")\
    .grid(row=0, column=0, sticky="w", pady=(15,0))

tk.Radiobutton(frame_bottom, text="📐 توزيع عادي", variable=mode_var, value="default", bg="#e0e0e0")\
    .grid(row=1, column=0, sticky="w", padx=2)

tk.Radiobutton(frame_bottom, text="🧱 توزيع طبقات", variable=mode_var, value="layered", bg="#e0e0e0")\
    .grid(row=2, column=0, sticky="w", padx=2)

tk.Button(frame_bottom, text="➕ إضافة توصيلة", command=add_marker, bg="#d9ead3", width=15)\
    .grid(row=3, column=0, pady=5, sticky="ew")

tk.Button(frame_bottom, text="🔁 تكرار التوصيلة", command=repeat_marker, bg="#d1e7dd", width=15)\
    .grid(row=4, column=0, pady=5, sticky="ew")

tk.Button(frame_bottom, text="↩️ تراجع", command=undo_action, bg="#ffe5d9", width=15)\
    .grid(row=5, column=0, pady=5, sticky="ew")

# ===== قسم خيارات حفظ المشروع =====
frame_save = tk.Frame(frame_bottom, bg="#e0e0e0")
frame_save.grid(row=6, column=0, sticky="ew", pady=(20,0))
tk.Label(frame_save, text="طريقة الحفظ:", bg="#e0e0e0")\
    .grid(row=0, column=0, columnspan=3, pady=(0,5))

tk.Radiobutton(frame_save, text="PDF فقط", variable=save_option, value="pdf", bg="#e0e0e0")\
    .grid(row=1, column=0, sticky="w", padx=2)

tk.Radiobutton(frame_save, text="صور + PDF", variable=save_option, value="images+pdf", bg="#e0e0e0")\
    .grid(row=1, column=1, sticky="w", padx=2)

tk.Radiobutton(frame_save, text="صور فقط", variable=save_option, value="images", bg="#e0e0e0")\
    .grid(row=1, column=2, sticky="w", padx=2)

# ===== قسم الإجراءات =====
frame_actions = tk.Frame(frame_bottom, bg="#e0e0e0")
frame_actions.grid(row=7, column=0, sticky="ew", pady=(20,0))
for col in range(3):
    frame_actions.grid_columnconfigure(col, weight=1)

tk.Button(frame_actions, text="🚀 توليد الصفحات", command=generate_numbered_pages, bg="#cff4fc", width=15)\
    .grid(row=0, column=0, sticky="ew", padx=5, pady=5)

tk.Button(frame_actions, text="💾 حفظ المشروع", command=save_project, bg="#d1e7dd", width=15)\
    .grid(row=0, column=1, sticky="ew", padx=5, pady=5)

tk.Button(frame_actions, text="📂 تحميل مشروع", command=load_project, bg="#d1e7dd", width=15)\
    .grid(row=0, column=2, sticky="ew", padx=5, pady=5)

# ===== قسم الحالة =====
frame_status = tk.Frame(frame_bottom, bg="#e0e0e0")
frame_status.grid(row=8, column=0, sticky="ew", pady=(10,0))
frame_status.grid_columnconfigure(0, weight=1)

progress_bar = ttk.Progressbar(frame_status, orient="horizontal", mode="determinate")
progress_bar.grid(row=0, column=0, sticky="ew", pady=5)

lbl_status = tk.Label(frame_status, text="حدد توصيلة على الصورة للتعديل", bg="#e0e0e0", fg="black")
lbl_status.grid(row=1, column=0, sticky="ew", pady=5)

# زر عرض حول الأداة
tk.Button(frame_bottom, text="حول الأداة", command=show_help, bg="#f8d7da", width=15)\
    .grid(row=9, column=0, columnspan=1, pady=5, sticky="ew")

frame_bottom.grid_rowconfigure(9, weight=0)

# ==================== ربط الاختصارات وتشغيل النافذة ====================
bind_shortcuts()
root.mainloop()
