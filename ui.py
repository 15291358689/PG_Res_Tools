import tkinter as tk
from tkinter import ttk, filedialog
import threading
from config import RESOURCE_TYPES
from processor import Processor

class ToolApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cocos资源整理工具")
        self.root.geometry("800x500")

        self.source_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.progress = tk.DoubleVar()
        self.progress_label = tk.StringVar(value="准备就绪")

        self.type_vars = {rtype: tk.BooleanVar(value=True) for rtype in RESOURCE_TYPES}

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        ttk.Label(frame, text="源路径").grid(row=0, column=0)
        ttk.Entry(frame, textvariable=self.source_path, width=60).grid(row=0, column=1)
        ttk.Button(frame, text="浏览", command=self.browse_source).grid(row=0, column=2)

        ttk.Label(frame, text="输出路径").grid(row=1, column=0)
        ttk.Entry(frame, textvariable=self.output_path, width=60).grid(row=1, column=1)
        ttk.Button(frame, text="浏览", command=self.browse_output).grid(row=1, column=2)

        type_frame = ttk.LabelFrame(frame, text="资源类型")
        type_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")

        for i, rtype in enumerate(RESOURCE_TYPES):
            ttk.Checkbutton(type_frame, text=rtype, variable=self.type_vars[rtype]).grid(row=i // 4, column=i % 4, sticky="w")

        self.progress_bar = ttk.Progressbar(frame, variable=self.progress, maximum=100)
        self.progress_bar.grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)
        ttk.Label(frame, textvariable=self.progress_label).grid(row=4, column=0, columnspan=3)

        ttk.Button(frame, text="开始整理", command=self.start_thread).grid(row=5, column=0, columnspan=3, pady=10)

    def browse_source(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_path.set(folder)
            self.output_path.set(folder + "/整理结果")

    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.set(folder)

    def start_thread(self):
        threading.Thread(target=self.run).start()

    def update_progress(self, current, total, success, error):
        percent = (current / total) * 100 if total else 0
        self.progress.set(percent)
        self.progress_label.set(f"已处理: {current}/{total} 成功: {success} 失败: {error}")
        self.root.update_idletasks()

    def run(self):
        selected = [rtype for rtype, var in self.type_vars.items() if var.get()]
        proc = Processor(
            self.source_path.get(),
            self.output_path.get(),
            selected,
            self.update_progress
            )
        proc.process_resources()