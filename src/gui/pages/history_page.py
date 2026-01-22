import customtkinter as ctk
import os
import webbrowser
from pathlib import Path
from tkinter import messagebox
from src.utils.paths import get_data_dir

class HistoryPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.header = ctk.CTkLabel(self, text="历史记录", font=("Microsoft YaHei UI", 24, "bold"))
        self.header.pack(pady=20, padx=20, anchor="w")
        
        # Toolbar
        tool_frame = ctk.CTkFrame(self, fg_color="transparent")
        tool_frame.pack(fill="x", padx=20)
        
        ctk.CTkButton(tool_frame, text="刷新列表", width=100, command=self.refresh_list).pack(side="left")
        ctk.CTkButton(tool_frame, text="打开文件夹", width=100, fg_color="gray", command=self.open_folder).pack(side="left", padx=10)

        # List
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.on_show()

    def on_show(self):
        self.refresh_list()

    def open_folder(self):
        d = get_data_dir()
        if not d.exists():
            d.mkdir(parents=True)
        os.startfile(d)

    def refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
            
        d = get_data_dir()
        if not d.exists():
            return

        files = sorted(list(d.glob("Report_*.html")), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not files:
            ctk.CTkLabel(self.list_frame, text="暂无历史报表").pack(pady=20)
            return

        for f in files:
            row = ctk.CTkFrame(self.list_frame)
            row.pack(fill="x", pady=5)
            
            # Icon or Name
            ctk.CTkLabel(row, text="📄", font=("Arial", 20)).pack(side="left", padx=10)
            
            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left", padx=5)
            
            ctk.CTkLabel(info_frame, text=f.name, font=("Microsoft YaHei UI", 14, "bold")).pack(anchor="w")
            
            # Buttons
            ctk.CTkButton(row, text="删除", width=60, fg_color="#DC3545", command=lambda p=f: self.delete_file(p)).pack(side="right", padx=10)
            ctk.CTkButton(row, text="查看", width=80, command=lambda p=f: self.open_report(p)).pack(side="right", padx=5)

    def open_report(self, path):
        webbrowser.open(f"file://{path.absolute()}")

    def delete_file(self, path):
        if messagebox.askyesno("确认", f"确定要删除 {path.name} 吗？"):
            try:
                os.remove(path)
                self.refresh_list()
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {e}")
