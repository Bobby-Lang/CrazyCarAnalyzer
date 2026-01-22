import customtkinter as ctk
import os
from src.utils.config_manager import ConfigManager
from src.gui.pages.home_page import HomePage
from src.gui.pages.account_page import AccountPage
from src.gui.pages.config_page import ConfigPage
from src.gui.pages.history_page import HistoryPage

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Config
        self.config_manager = ConfigManager()
        
        # Window Setup
        self.title("CrazyCarAnalyzer Pro")
        self.geometry("900x700")
        
        # Theme
        ctk.set_appearance_mode(self.config_manager.get("app_settings", {}).get("theme", "Dark"))
        ctk.set_default_color_theme("blue")

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="🏎️ CrazyCar", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation Buttons
        self.btn_home = self.create_nav_btn("📊 主页", "home", 1)
        self.btn_account = self.create_nav_btn("🔐 账号", "account", 2)
        self.btn_config = self.create_nav_btn("⚙️ 配置", "config", 3)
        self.btn_history = self.create_nav_btn("📜 历史", "history", 4)
        
        # Version Info
        self.version_label = ctk.CTkLabel(self.sidebar_frame, text="v1.0.0", text_color="gray")
        self.version_label.grid(row=6, column=0, padx=20, pady=20)

        # 2. Content Area
        self.frames = {}
        for F, name in [(HomePage, "home"), (AccountPage, "account"), (ConfigPage, "config"), (HistoryPage, "history")]:
            frame = F(parent=self, controller=self)
            self.frames[name] = frame
            frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Start at home
        self.show_frame("home")

    def create_nav_btn(self, text, name, row):
        btn = ctk.CTkButton(self.sidebar_frame, text=text, fg_color="transparent", text_color=("gray10", "#DCE4EE"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.show_frame(name))
        btn.grid(row=row, column=0, padx=20, pady=10, sticky="ew")
        return btn

    def show_frame(self, name):
        # Reset buttons style
        for btn in [self.btn_home, self.btn_account, self.btn_config, self.btn_history]:
            btn.configure(fg_color="transparent")
        
        # Highlight current
        if name == "home": self.btn_home.configure(fg_color=("gray75", "gray25"))
        elif name == "account": self.btn_account.configure(fg_color=("gray75", "gray25"))
        elif name == "config": self.btn_config.configure(fg_color=("gray75", "gray25"))
        elif name == "history": self.btn_history.configure(fg_color=("gray75", "gray25"))

        frame = self.frames[name]
        frame.tkraise()
        # Optional: trigger on_show if exists
        if hasattr(frame, "on_show"):
            frame.on_show()

if __name__ == "__main__":
    app = App()
    app.mainloop()
