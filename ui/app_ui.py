import customtkinter as ctk
import threading
import webbrowser
from tkinter import messagebox
import os
from datetime import datetime
from core.scraper import InstagramScraper
from core.report_generator import ReportGenerator

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Instagram Downloader (Guest Mode)")
        self.geometry("600x600") # ارتفاع را کمی زیاد کردم تا فوتر جا شود
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.scraper = InstagramScraper(download_path="output")
        self.reporter = ReportGenerator()
        self.running_task = False 
        
        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) 
        self.grid_rowconfigure(4, weight=0) # ردیف فوتر

        self.lbl_title = ctk.CTkLabel(self, text="INSTAGRAM DOWNLOADER", font=("Roboto", 24, "bold"), text_color="#3B8ED0")
        self.lbl_title.grid(row=0, column=0, pady=(30, 20))

        # --- ورودی ---
        self.frame_input = ctk.CTkFrame(self)
        self.frame_input.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.frame_input, text="Target Username (No @):", font=("Roboto", 14)).pack(pady=5)
        
        self.entry_target = ctk.CTkEntry(self.frame_input, placeholder_text="e.g. natgeo", width=300, height=35)
        self.entry_target.pack(pady=10)

        self.btn_start = ctk.CTkButton(self.frame_input, text="START 🚀", fg_color="#3B8ED0", hover_color="#206a9c", command=self.start_thread, width=200, height=40, font=("Roboto", 14, "bold"))
        self.btn_start.pack(pady=(5, 10))

        # --- تنظیمات ---
        self.chk_skip_existing = ctk.CTkCheckBox(self.frame_input, text="Skip Existing Files")
        self.chk_skip_existing.select()
        self.chk_skip_existing.pack(pady=2)

        self.chk_urls_only = ctk.CTkCheckBox(self.frame_input, text="Get URLs Only (No Download) 🔗", fg_color="#D97706")
        self.chk_urls_only.pack(pady=2)
        
        # پیام هشدار محدودیت
        ctk.CTkLabel(self.frame_input, text="⚠️ Note: Guest Mode Limit is ~12 Posts", text_color="#EAB308", font=("Roboto", 12, "bold")).pack(pady=10)

        # --- لاگ ---
        self.frame_log = ctk.CTkFrame(self)
        self.frame_log.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        
        self.textbox_log = ctk.CTkTextbox(self.frame_log, font=("Consolas", 12))
        self.textbox_log.pack(expand=True, fill="both", padx=5, pady=5)

        # --- Footer (بازگردانی شده) ---
        self.frame_footer = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_footer.grid(row=4, column=0, pady=15, sticky="ew")
        
        self.lbl_credit = ctk.CTkLabel(self.frame_footer, text="Developed by Ahmad Salami Far", font=("Roboto", 12, "bold"), text_color="gray")
        self.lbl_credit.pack()
        
        self.btn_github = ctk.CTkButton(self.frame_footer, text="https://github.com/ahmadsalamifar", command=lambda: webbrowser.open("https://github.com/ahmadsalamifar"), fg_color="transparent", text_color="#3B8ED0", height=20, hover=False)
        self.btn_github.pack()

    def log(self, message):
        self.textbox_log.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.textbox_log.see("end")

    def start_thread(self):
        target = self.entry_target.get()
        if not target:
            messagebox.showwarning("Warning", "Please enter a username!")
            return
        
        t = threading.Thread(target=self.run_process, args=(target,))
        t.start()
        self.btn_start.configure(state="disabled", text="Running...")

    def run_process(self, target):
        self.running_task = True
        try:
            self.log(f"🚀 Started: {target}")
            urls_only = bool(self.chk_urls_only.get())
            if urls_only: self.log("🔗 Mode: URLs Only")

            def update(msg, val):
                self.log(msg)

            new_posts = []
            
            # ارسال تعداد 50 برای اینکه تا جایی که اینستاگرام اجازه می‌دهد (حدود 12) دانلود کند
            for item, msg in self.scraper.scrape_profile(
                target, 
                count=50, 
                skip_existing=bool(self.chk_skip_existing.get()), 
                urls_only=urls_only,
                progress_callback=update
            ):
                if not self.running_task: break
                
                if item is None:
                    self.log(msg)
                elif isinstance(item, list): 
                    self.log(msg)
                else:
                    new_posts.append(item)
                    self.log(msg)

            if new_posts:
                self.log("Done.")
                if urls_only:
                     messagebox.showinfo("Done", f"Extracted {len(new_posts)} links.")
                else:
                    self.log("Generating HTML Report...")
                    os.makedirs(f"output/{target}", exist_ok=True)
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    path = f"output/{target}/report_{ts}.html"
                    self.reporter.generate_html_report(new_posts, path)
                    messagebox.showinfo("Done", f"Downloaded {len(new_posts)} posts.")
            else:
                self.log("Finished (No new items).")

        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            self.btn_start.configure(state="normal", text="START 🚀")
            self.running_task = False