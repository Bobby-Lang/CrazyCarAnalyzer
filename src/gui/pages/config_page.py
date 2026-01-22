import customtkinter as ctk
from src.utils.config_manager import ConfigManager

class ConfigPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config_manager = ConfigManager()
        
        self.header = ctk.CTkLabel(self, text="高级配置", font=("Microsoft YaHei UI", 24, "bold"))
        self.header.pack(pady=20, padx=20, anchor="w")

        # Substitution Map Section
        sub_frame = ctk.CTkFrame(self)
        sub_frame.pack(padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(sub_frame, text="角色名称替换表 (原始名称 -> 显示名称)", font=("Microsoft YaHei UI", 16, "bold")).pack(pady=10, padx=10, anchor="w")
        
        # Header Row
        h_row = ctk.CTkFrame(sub_frame, fg_color="transparent")
        h_row.pack(fill="x", padx=10)
        ctk.CTkLabel(h_row, text="原始名称", width=200, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(h_row, text="显示名称", width=200, anchor="w").pack(side="left", padx=5)
        
        # Scroll List
        self.sub_list = ctk.CTkScrollableFrame(sub_frame, height=300)
        self.sub_list.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Add New Row Area
        add_row = ctk.CTkFrame(sub_frame)
        add_row.pack(fill="x", padx=10, pady=10)
        
        self.new_key = ctk.CTkEntry(add_row, placeholder_text="原始名称")
        self.new_key.pack(side="left", fill="x", expand=True, padx=5)
        
        self.new_val = ctk.CTkEntry(add_row, placeholder_text="显示名称")
        self.new_val.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(add_row, text="添加规则", command=self.add_rule).pack(side="right", padx=5)

        self.refresh_list()

    def refresh_list(self):
        for w in self.sub_list.winfo_children():
            w.destroy()
            
        sub_map = self.config_manager.get("substitution_map", {})
        
        for k, v in sub_map.items():
            row = ctk.CTkFrame(self.sub_list, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=k, width=200, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=v, width=200, anchor="w").pack(side="left", padx=5)
            
            ctk.CTkButton(row, text="删除", width=60, fg_color="#DC3545", command=lambda key=k: self.delete_rule(key)).pack(side="right", padx=5)

    def add_rule(self):
        k = self.new_key.get().strip()
        v = self.new_val.get().strip()
        if k and v:
            sub_map = self.config_manager.get("substitution_map", {})
            sub_map[k] = v
            self.config_manager.set("substitution_map", sub_map)
            self.new_key.delete(0, "end")
            self.new_val.delete(0, "end")
            self.refresh_list()

    def delete_rule(self, key):
        sub_map = self.config_manager.get("substitution_map", {})
        if key in sub_map:
            del sub_map[key]
            self.config_manager.set("substitution_map", sub_map)
            self.refresh_list()
