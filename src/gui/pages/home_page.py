import customtkinter as ctk
import threading
import queue
import webbrowser
import os
from tkinter import messagebox
from src.utils.config_manager import ConfigManager
from src.utils.constants import OFFICIAL_MAP_ORDER, GAME_MODES
from src.core.scraper import CrazyCarScraper
from src.core.report_gen import ReportGenerator
from src.utils.paths import get_data_dir

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config_manager = ConfigManager()
        self.log_queue = queue.Queue()
        self.is_running = False
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 1. Control Panel (Top)
        self.ctrl_frame = ctk.CTkFrame(self)
        self.ctrl_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        # Row 1: Status & Mode
        r1 = ctk.CTkFrame(self.ctrl_frame, fg_color="transparent")
        r1.pack(fill="x", padx=10, pady=5)
        
        self.acc_label = ctk.CTkLabel(r1, text="当前账号: 未登录", font=("Microsoft YaHei UI", 14))
        self.acc_label.pack(side="left")
        
        self.mode_var = ctk.StringVar(value="组队竞速")
        self.mode_menu = ctk.CTkOptionMenu(r1, values=GAME_MODES, variable=self.mode_var)
        self.mode_menu.pack(side="right")
        ctk.CTkLabel(r1, text="模式:").pack(side="right", padx=5)

        # Row 2: Maps Selection
        r2 = ctk.CTkFrame(self.ctrl_frame, fg_color="transparent")
        r2.pack(fill="x", padx=10, pady=5)
        
        # End Map (Start Trigger)
        ctk.CTkLabel(r2, text="结束地图 (最新):").pack(side="left")
        self.end_map_var = ctk.StringVar(value="")
        # Add empty option for "Immediate"
        map_opts = ["(不限制/直接开始)"] + OFFICIAL_MAP_ORDER
        self.end_map_menu = ctk.CTkOptionMenu(r2, values=map_opts, variable=self.end_map_var)
        self.end_map_menu.pack(side="left", padx=10)
        
        # Start Map (Stop Trigger)
        ctk.CTkLabel(r2, text="起始地图 (最旧):").pack(side="left", padx=(20, 0))
        self.start_map_var = ctk.StringVar(value=OFFICIAL_MAP_ORDER[0])
        self.start_map_menu = ctk.CTkComboBox(r2, values=OFFICIAL_MAP_ORDER, variable=self.start_map_var)
        self.start_map_menu.pack(side="left", padx=10)
        
        self.add_map_btn = ctk.CTkButton(r2, text="+ 添加备选", width=80, command=self.add_start_map)
        self.add_map_btn.pack(side="left")

        # Start Maps List Display
        self.start_maps = [OFFICIAL_MAP_ORDER[0]]
        self.maps_display = ctk.CTkTextbox(self.ctrl_frame, height=40, fg_color="transparent", text_color="gray")
        self.maps_display.pack(fill="x", padx=10, pady=5)
        self.maps_display.insert("1.0", f"停止条件(遇到即停): {self.start_maps}")
        self.maps_display.configure(state="disabled")

        # Row 3: Action
        r3 = ctk.CTkFrame(self.ctrl_frame, fg_color="transparent")
        r3.pack(fill="x", padx=10, pady=10)
        
        self.auto_open_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(r3, text="完成后自动打开报表", variable=self.auto_open_var).pack(side="left")
        
        self.run_btn = ctk.CTkButton(r3, text="🚀 开始抓取并分析", font=("Microsoft YaHei UI", 16, "bold"), height=40, fg_color="#28A745", hover_color="#218838", command=self.start_process)
        self.run_btn.pack(side="right", fill="x", expand=True, padx=(20, 0))

        # 2. Log Area (Bottom)
        self.log_box = ctk.CTkTextbox(self, font=("Consolas", 12))
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.log_box.configure(state="disabled")

        # Check logs
        self.after(100, self.check_log_queue)

    def on_show(self):
        acc = self.config_manager.get_current_account()
        if acc:
            self.acc_label.configure(text=f"当前账号: {acc['phone']}")
        else:
            self.acc_label.configure(text="当前账号: 未登录 (请前往账号页设置)")

    def add_start_map(self):
        val = self.start_map_var.get()
        if val not in self.start_maps:
            self.start_maps.append(val)
            self.update_maps_display()

    def update_maps_display(self):
        self.maps_display.configure(state="normal")
        self.maps_display.delete("1.0", "end")
        self.maps_display.insert("1.0", f"停止条件(遇到即停): {self.start_maps}")
        self.maps_display.configure(state="disabled")

    def log(self, msg):
        self.log_queue.put(msg)

    def check_log_queue(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.log_box.configure(state="normal")
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.after(100, self.check_log_queue)

    def start_process(self):
        if self.is_running:
            return

        acc = self.config_manager.get_current_account()
        if not acc:
            messagebox.showwarning("提示", "请先配置账号！")
            self.controller.show_frame("account")
            return

        self.is_running = True
        self.run_btn.configure(state="disabled", text="⏳ 正在运行...")
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        
        thread = threading.Thread(target=self.worker, args=(acc,))
        thread.start()

    def worker(self, acc):
        try:
            self.log("🚀 初始化爬虫...")
            scraper = CrazyCarScraper(acc['phone'], acc['password'], self.log)
            
            if not scraper.login():
                self.log("❌ 登录失败，终止任务")
                return

            end_map = self.end_map_var.get()
            if "不限制" in end_map: end_map = ""
            
            mode = self.mode_var.get()
            
            # Scrape
            header, data = scraper.start_crawl(mode, self.start_maps, end_map, self.config_manager.get("substitution_map"))
            
            # Save CSV
            csv_path = scraper.save_to_csv(header, data, str(get_data_dir()))
            
            if csv_path:
                self.log("📊 正在生成报表...")
                gen = ReportGenerator()
                
                # Load custom pages from config
                custom_pages = self.config_manager.get("custom_pages", [])
                sub_map = self.config_manager.get("substitution_map", {})
                
                report_path = gen.generate_report(csv_path, sub_map, custom_pages, get_data_dir())
                
                if report_path:
                    self.log(f"✅ 报表生成成功: {report_path.name}")
                    if self.auto_open_var.get():
                        self.log("🌍 打开浏览器...")
                        webbrowser.open(f"file://{os.path.abspath(report_path)}")
                else:
                    self.log("❌ 报表生成失败")
            else:
                self.log("❌ 未抓取到数据或保存失败")

        except Exception as e:
            self.log(f"❌ 发生未捕获异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_running = False
            self.after(0, lambda: self.run_btn.configure(state="normal", text="🚀 开始抓取并分析"))
