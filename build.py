import PyInstaller.__main__
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import threading

# ------------------ إعداد ألوان ------------------
BG_COLOR = "#2b2b2b"       # خلفية رئيسية
FG_COLOR = "#f0f0f0"       # لون النصوص
ENTRY_BG = "#3c3f41"       # خلفية الإدخال
BUTTON_BG = "#4CAF50"      # أخضر للأزرار
BUTTON_FG = "white"
BROWSE_BG = "#2196F3"      # أزرق لأزرار Browse
ACCENT_COLOR = "#FF5722"   # لون مميز للعناصر المهمة
TOOLTIP_BG = "#454545"     # خلفية التلميحات

# ------------------ فئة Tooltip ------------------
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip, text=self.text, background=TOOLTIP_BG,
                        foreground=FG_COLOR, relief="solid", borderwidth=1,
                        font=("Arial", 9), justify="left")
        label.pack()

    def leave(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

# ------------------ فئة مؤشر التحميل الدائري ------------------
class LoadingSpinner:
    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, width=40, height=40, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(pady=10)
        
        # إنشاء الدائرة الأساسية
        self.circle = self.canvas.create_oval(5, 5, 35, 35, outline=ACCENT_COLOR, width=2, fill="")
        
        # إنشاء مؤشر التحميل (قوس)
        self.arc = self.canvas.create_arc(5, 5, 35, 35, start=0, extent=45, 
                                         outline=BUTTON_BG, width=3, style=tk.ARC)
        
        self.angle = 0
        self.animation_id = None
        
    def start(self):
        self.angle = 0
        self.animate()
        
    def stop(self):
        if self.animation_id:
            self.canvas.after_cancel(self.animation_id)
            self.animation_id = None
        
    def animate(self):
        self.angle = (self.angle + 10) % 360
        self.canvas.itemconfig(self.arc, start=self.angle)
        self.animation_id = self.canvas.after(50, self.animate)

# ------------------ وظائف الملفات ------------------
def select_file():
    file_path = filedialog.askopenfilename(title="Select Python File", filetypes=[("Python files", "*.py")])
    if file_path:
        py_entry.delete(0, tk.END)
        py_entry.insert(0, file_path)

def select_icon():
    icon_path = filedialog.askopenfilename(title="Select Icon File", filetypes=[("Icon files", "*.ico")])
    if icon_path:
        icon_entry.delete(0, tk.END)
        icon_entry.insert(0, icon_path)

def select_output_dir():
    dir_path = filedialog.askdirectory(title="Select Output Directory")
    if dir_path:
        out_entry.delete(0, tk.END)
        out_entry.insert(0, dir_path)

# ------------------ تحويل الملف ------------------
def start_conversion():
    # تشغيل التحويل في thread منفصل لمنع تجميد الواجهة
    conversion_thread = threading.Thread(target=convert_file)
    conversion_thread.daemon = True
    conversion_thread.start()

def update_loading_message():
    """تحديث رسالة التحميل بشكل دوري"""
    messages = [
        "Compiling Python code...",
        "Packaging dependencies...",
        "Creating executable...",
        "Finalizing conversion...",
        "Almost done...",
        "This might take a while...",
        "Preparing files...",
        "Optimizing executable...",
        "Setting up environment...",
        "Wrapping up..."
    ]
    
    if hasattr(update_loading_message, "current_index"):
        update_loading_message.current_index = (update_loading_message.current_index + 1) % len(messages)
    else:
        update_loading_message.current_index = 0
        
    loading_label.config(text=messages[update_loading_message.current_index])
    
    # استمرار التحديث كل 3 ثواني طالما العملية جارية
    if loading_frame.winfo_ismapped():
        root.after(3000, update_loading_message)

def convert_file():
    filename = py_entry.get().strip()
    icon_path = icon_entry.get().strip()
    out_dir = out_entry.get().strip()
    exe_name = name_entry.get().strip()
    use_noconsole = noconsole_var.get()
    mode = build_mode.get()
    import re
    exe_name = re.sub(r'[<>:"/\\|?*]', '_', exe_name) # إزالة الأحرف غير المسموح بها في أسماء الملفات

    if not filename:
        messagebox.showerror("Error", "Please select a Python file.")
        return
    if not filename.endswith(".py"):
        if not filename.endswith(".pyw"):
            messagebox.showerror("Error", "Invalid file. Please select a .py file or .pyw file.")
            return
    if os.path.basename(filename) == "build.py":
        messagebox.showerror("Error", "You cannot convert the build script itself.")
        return
    if not os.path.exists(filename):
        messagebox.showerror("Error", f"File not found: {filename}")
        return

    # إظهار مؤشر التحميل
    loading_frame.grid(row=8, column=0, columnspan=3, pady=10)
    spinner.start()
    update_loading_message()  # بدء رسائل التحميل المتغيرة

    command = []
    if mode == "onefile": command.append("--onefile")
    if use_noconsole: command.append("--noconsole")
    if icon_path: command.append(f"--icon={icon_path}")
    if out_dir: command.append(f"--distpath={out_dir}")
    if exe_name: command.append(f"--name={exe_name}")
    command.append(filename)

    try:
        # تعطيل زر التحويل أثناء عملية البناء
        convert_button.config(state=tk.DISABLED, text="Converting...")
        
        # تنفيذ الأمر الفعلي
        PyInstaller.__main__.run(command)
        
        # إخفاء مؤشر التحميل بعد الانتهاء
        loading_frame.grid_forget()
        spinner.stop()
        
        messagebox.showinfo(
            "Success",
            f"✅ Conversion of {filename} to exe completed.\n"
            f"Output Folder: {out_dir if out_dir else 'dist/'}\n"
            f"Exe Name: {exe_name if exe_name else os.path.splitext(os.path.basename(filename))[0]}\n"
            f"Mode: {'One File' if mode == 'onefile' else 'One Directory'}"
        )
    except Exception as e:
        messagebox.showerror("Error", str(e))
        loading_frame.pack_forget()
        spinner.stop()
    finally:
        # إعادة تمكين زر التحويل
        convert_button.config(state=tk.NORMAL, text="Convert to EXE")

# تأثيرات تفاعلية للأزرار
def on_enter(e, button, color):
    e.widget.config(bg=color)

def on_leave(e, button, color):
    e.widget.config(bg=color)

# ------------------ واجهة رسومية ------------------
root = tk.Tk()
root.title("Python to EXE Converter")
root.configure(bg=BG_COLOR)
root.geometry("800x650")
root.minsize(750, 600)

# إطار رئيسي مع تمرير
main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# عنوان التطبيق
title_label = tk.Label(main_frame, text="Python to EXE Converter", 
                      font=("Arial", 18, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR)
title_label.pack(pady=(0, 20))

# إطار المحتوى
content_frame = tk.Frame(main_frame, bg=BG_COLOR)
content_frame.pack(fill=tk.BOTH, expand=True)

# جعل الأعمدة قابلة للتمدد
content_frame.grid_columnconfigure(1, weight=1)

# تسهيلات للـ Labels و Entries
def styled_label(master, text):
    return tk.Label(master, text=text, font=("Arial", 11), bg=BG_COLOR, fg=FG_COLOR, anchor="w")
def styled_entry(master, placeholder=""):
    entry = tk.Entry(master, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, 
                    relief="flat", font=("Arial", 10))
    # إضافة نص توضيحي
    if placeholder:
        entry.insert(0, placeholder)
        entry.config(fg="#888888")
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=FG_COLOR)
        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg="#888888")
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
    return entry

def styled_button(master, text, command, bg_color=BUTTON_BG, hover_color=None, tooltip_text=""):
    if hover_color is None:
        hover_color = bg_color
    btn = tk.Button(master, text=text, command=command, bg=bg_color, fg=BUTTON_FG, 
                   font=("Arial", 10), relief="flat", cursor="hand2")
    btn.bind("<Enter>", lambda e: on_enter(e, btn, hover_color))
    btn.bind("<Leave>", lambda e: on_leave(e, btn, bg_color))
    
    # إضافة tooltip إذا كان هناك نص
    if tooltip_text:
        ToolTip(btn, tooltip_text)
    
    return btn

# --- صف اختيار ملف py ---
styled_label(content_frame, "Python File:").grid(row=0, column=0, sticky="w", pady=8)
py_entry = styled_entry(content_frame)
py_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=8)
browse_py_btn = styled_button(content_frame, "Browse", select_file, bg_color=BROWSE_BG, 
                             hover_color="#1976D2", tooltip_text="Select the Python file you want to convert to EXE")
browse_py_btn.grid(row=0, column=2, padx=5, pady=8)

# --- صف اختيار الأيقونة ---
styled_label(content_frame, "Icon File (.ico) [Optional]:").grid(row=1, column=0, sticky="w", pady=8)
icon_entry = styled_entry(content_frame)
icon_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=8)
browse_icon_btn = styled_button(content_frame, "Browse", select_icon, bg_color=BROWSE_BG, 
                               hover_color="#1976D2", tooltip_text="Select an icon file for your EXE (optional)")
browse_icon_btn.grid(row=1, column=2, padx=5, pady=8)

# --- صف اختيار مجلد الإخراج ---
styled_label(content_frame, "Output Folder [Optional]:").grid(row=2, column=0, sticky="w", pady=8)
out_entry = styled_entry(content_frame, "Default: dist folder in current directory")
out_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=8)
browse_out_btn = styled_button(content_frame, "Browse", select_output_dir, bg_color=BROWSE_BG, 
                              hover_color="#1976D2", tooltip_text="Select where to save the converted EXE file")
browse_out_btn.grid(row=2, column=2, padx=5, pady=8)

# --- صف اسم exe النهائي ---
styled_label(content_frame, "Exe File Name [Optional]:").grid(row=3, column=0, sticky="w", pady=8)
name_entry = styled_entry(content_frame, "Default: same as Python file name")
name_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=8)
ToolTip(name_entry, "Set a custom name for the output EXE file (without extension)")

# --- خيار noconsole ---
noconsole_var = tk.BooleanVar()
noconsole_check = tk.Checkbutton(content_frame, text="No Console (Hide terminal window)", 
                                variable=noconsole_var, bg=BG_COLOR, fg=FG_COLOR, 
                                selectcolor=ENTRY_BG, activebackground=BG_COLOR,
                                activeforeground=FG_COLOR, font=("Arial", 10))
noconsole_check.grid(row=4, column=1, sticky="w", pady=12)
ToolTip(noconsole_check, "Check this to hide the console window when the EXE runs (for GUI applications)")

# --- وضع التحويل ---
build_frame = tk.Frame(content_frame, bg=BG_COLOR)
build_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=10)

styled_label(build_frame, "Build Mode:").pack(side=tk.LEFT)

mode_frame = tk.Frame(build_frame, bg=BG_COLOR)
mode_frame.pack(side=tk.RIGHT, expand=True)

build_mode = tk.StringVar(value="onefile")
onefile_radio = tk.Radiobutton(mode_frame, text="One File (.exe)", variable=build_mode, 
                              value="onefile", bg=BG_COLOR, fg=FG_COLOR, 
                              selectcolor=ENTRY_BG, activebackground=BG_COLOR,
                              font=("Arial", 10))
onefile_radio.pack(side=tk.LEFT, padx=10)
ToolTip(onefile_radio, "Create a single executable file (larger but easier to distribute)")

onedir_radio = tk.Radiobutton(mode_frame, text="One Directory (Folder)", variable=build_mode, 
                             value="onedir", bg=BG_COLOR, fg=FG_COLOR, 
                             selectcolor=ENTRY_BG, activebackground=BG_COLOR,
                             font=("Arial", 10))
onedir_radio.pack(side=tk.LEFT, padx=10)
ToolTip(onedir_radio, "Create a folder with all dependencies (smaller executable but multiple files)")

# فاصل
separator = tk.Frame(content_frame, height=2, bg=ENTRY_BG)
separator.grid(row=6, column=0, columnspan=3, sticky="ew", pady=20)

# --- زر التحويل ---
convert_button = styled_button(content_frame, "Convert to EXE", start_conversion, 
                              bg_color=BUTTON_BG, hover_color="#45a049",
                              tooltip_text="Start the conversion process")
convert_button.config(font=("Arial", 14, "bold"), width=25, height=2)
convert_button.grid(row=7, column=0, columnspan=3, pady=20)

# إطار مؤشر التحميل (مخفي في البداية)
loading_frame = tk.Frame(content_frame, bg=BG_COLOR)
spinner = LoadingSpinner(loading_frame)
loading_label = tk.Label(loading_frame, text="", bg=BG_COLOR, fg=FG_COLOR, font=("Arial", 10))
loading_label.pack(pady=5)

# معلومات إضافية في الأسفل
info_text = """
Note: 
- The conversion process may take several minutes depending on your project size
- Make sure all dependencies are installed before converting
- For best results, use a virtual environment
"""
info_label = tk.Label(main_frame, text=info_text, font=("Arial", 9), 
                     bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT)
info_label.pack(side=tk.BOTTOM, pady=(10, 0))

# إضافة tooltips إضافية
ToolTip(py_entry, "Path to the Python file you want to convert")
ToolTip(icon_entry, "Optional: Custom icon for your executable (.ico format)")
ToolTip(out_entry, "Optional: Custom output directory for the executable")

root.mainloop()
