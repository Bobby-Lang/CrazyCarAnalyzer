import customtkinter as ctk
from tkinter import messagebox
from src.utils.config_manager import ConfigManager
from src.core.scraper import CrazyCarScraper

class AccountPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config_manager = ConfigManager()
        
        # Header
        self.header = ctk.CTkLabel(self, text="账号管理", font=("Microsoft YaHei UI", 24, "bold"))
        self.header.pack(pady=20, padx=20, anchor="w")
        
        # Form Area
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(padx=20, fill="x")
        
        self.phone_entry = ctk.CTkEntry(self.form_frame, placeholder_text="手机号")
        self.phone_entry.pack(pady=10, padx=20, fill="x")
        
        self.pwd_entry = ctk.CTkEntry(self.form_frame, placeholder_text="密码", show="*")
        self.pwd_entry.pack(pady=10, padx=20, fill="x")
        
        self.btn_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.btn_frame.pack(pady=10, fill="x")
        
        self.save_btn = ctk.CTkButton(self.btn_frame, text="保存账号", command=self.save_account)
        self.save_btn.pack(side="right", padx=20)
        
        self.test_btn = ctk.CTkButton(self.btn_frame, text="测试登录", fg_color="#E0A800", hover_color="#C69500", command=self.test_login)
        self.test_btn.pack(side="right", padx=20)
        
        # List Area
        ctk.CTkLabel(self, text="已保存账号", font=("Microsoft YaHei UI", 16)).pack(pady=(20, 10), padx=20, anchor="w")
        
        self.list_frame = ctk.CTkScrollableFrame(self, height=300)
        self.list_frame.pack(padx=20, fill="both", expand=True)
        
        self.refresh_list()

    def refresh_list(self):
        # Clear existing
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        accounts = self.config_manager.get("accounts", [])
        curr_idx = self.config_manager.get("current_account_idx", -1)
        
        for i, acc in enumerate(accounts):
            row = ctk.CTkFrame(self.list_frame)
            row.pack(fill="x", pady=5)
            
            lbl_text = f"{acc['phone']} {'(默认)' if i == curr_idx else ''}"
            lbl = ctk.CTkLabel(row, text=lbl_text, anchor="w")
            lbl.pack(side="left", padx=10)
            
            del_btn = ctk.CTkButton(row, text="删除", width=60, fg_color="#DC3545", hover_color="#C82333", command=lambda idx=i: self.delete_account(idx))
            del_btn.pack(side="right", padx=5, pady=5)
            
            use_btn = ctk.CTkButton(row, text="设为默认", width=80, command=lambda idx=i: self.set_default(idx))
            if i != curr_idx:
                use_btn.pack(side="right", padx=5, pady=5)

    def save_account(self):
        phone = self.phone_entry.get().strip()
        pwd = self.pwd_entry.get().strip()
        if not phone or not pwd:
            return
        
        self.config_manager.add_or_update_account(phone, pwd)
        self.phone_entry.delete(0, "end")
        self.pwd_entry.delete(0, "end")
        self.refresh_list()

    def delete_account(self, idx):
        accounts = self.config_manager.get("accounts", [])
        if 0 <= idx < len(accounts):
            del accounts[idx]
            self.config_manager.set("accounts", accounts)
            
            # Update index
            curr = self.config_manager.get("current_account_idx", -1)
            if curr == idx:
                self.config_manager.set("current_account_idx", -1)
            elif curr > idx:
                self.config_manager.set("current_account_idx", curr - 1)
                
            self.refresh_list()

    def set_default(self, idx):
        self.config_manager.set("current_account_idx", idx)
        self.refresh_list()

    def test_login(self):
        phone = self.phone_entry.get().strip()
        pwd = self.pwd_entry.get().strip()
        if not phone:
            acc = self.config_manager.get_current_account()
            if acc:
                phone = acc["phone"]
                pwd = acc["password"]
            else:
                return

        def log_cb(msg):
            print(msg) # Simple print for test

        scraper = CrazyCarScraper(phone, pwd, log_cb)
        if scraper.login():
            messagebox.showinfo("成功", "登录成功！")
        else:
            messagebox.showerror("失败", "登录失败，请检查账号密码或网络")
