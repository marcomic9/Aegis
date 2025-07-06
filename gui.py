import os
import customtkinter as ctk
import tkinter.filedialog as fd
from tkinterdnd2 import TkinterDnD, DND_FILES
import db
import keyring
import json

# --- MODERN DARK BLUE & GREY PALETTE ---
DARK_BLUE = "#1a2233"  # main background
MID_BLUE = "#22304a"    # sidebar, cards
LIGHT_GREY = "#f4f6fa"  # content background
MID_GREY = "#b0b8c1"    # accent, icons
WHITE = "#ffffff"       # text
ACCENT_BLUE = "#3a7bd5" # accent
SOFT_SUCCESS = "#6fdc8c"  # softer green
SOFT_ERROR = "#ff8a8a"    # softer red
SUCCESS = SOFT_SUCCESS
ERROR = SOFT_ERROR

# --- Modern App Name Header ---
class ModernHeader(ctk.CTkCanvas):
    def __init__(self, master, text, **kwargs):
        super().__init__(master, highlightthickness=0, bg=DARK_BLUE, **kwargs)
        self.text = text
        self.font = ("Segoe UI", 44, "bold")
        self.bind("<Configure>", self._draw)
    def _draw(self, event=None):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        # Subtle shadow
        self.create_text(
            width // 2 + 2, height // 2 + 2,
            text=self.text,
            font=self.font,
            fill="#000000",
            anchor="center"
        )
        # Main text
        self.create_text(
            width // 2, height // 2,
            text=self.text,
            font=self.font,
            fill=WHITE,
            anchor="center"
        )
        # Underline accent
        self.create_line(
            width // 2 - 90, height // 2 + 32,
            width // 2 + 90, height // 2 + 32,
            fill=ACCENT_BLUE, width=4, capstyle="round"
        )

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# --- Sidebar Tabs ---
PAGES = ["Home", "Excel", "Results", "Virtual Agent", "Stats"]

class AutomateAgentApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        try:
            self.tk.call('package', 'require', 'tkdnd')
        except Exception:
            pass
        self.title("AutomateAgent - PDF Automation Assistant")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        self.configure(bg=DARK_BLUE)
        self.credits = 100  # Example credit count, should be dynamic in real app
        self.app_frame = ctk.CTkFrame(self, fg_color=DARK_BLUE, corner_radius=18)
        self.app_frame.pack(fill="both", expand=True)
        self.app_frame.grid_columnconfigure(0, weight=0)
        self.app_frame.grid_columnconfigure(1, weight=1)
        self.app_frame.grid_rowconfigure(1, weight=1)
        # Modern header
        self.header = ModernHeader(
            self.app_frame,
            text="AutomateAgent",
            width=600,
            height=90
        )
        self.header.grid(row=0, column=0, columnspan=2, pady=(24, 8), sticky="n")
        self.sidebar = ModernSidebar(self.app_frame, self)
        self.sidebar.grid(row=1, column=0, sticky="nswe", padx=(24, 12), pady=(0, 24))
        self.main_content = ModernMainContent(self.app_frame, app=self)
        self.main_content.grid(row=1, column=1, sticky="nsew", padx=(12, 24), pady=(0, 24))
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)
    def handle_drop(self, event):
        if self.main_content.current_page == "Home":
            try:
                files = self.tk.splitlist(event.data)
                pdf_files = [f for f in files if f.lower().endswith('.pdf')]
                if pdf_files:
                    self.main_content.pages["Home"].handle_dropped_files(pdf_files)
                else:
                    self.main_content.pages["Home"].update_status_label("Only PDF files are accepted.", text_color=ERROR)
            except Exception:
                self.main_content.pages["Home"].update_status_label("Error processing dropped files.", text_color=ERROR)

# --- Modern Sidebar Navigation ---
class ModernSidebar(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, width=240, corner_radius=18, fg_color=MID_BLUE)
        self.grid_propagate(False)
        self.grid_rowconfigure(len(PAGES)+1, weight=1)
        self.grid_columnconfigure(0, weight=1)  # Make buttons stretch full width
        ctk.CTkLabel(
            self,
            text="Menu",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=WHITE,
            fg_color="transparent"
        ).grid(row=0, column=0, pady=(28, 18), padx=24, sticky="w")
        for idx, page in enumerate(PAGES, start=1):
            ctk.CTkButton(
                self,
                text=page,
                command=lambda p=page: app.main_content.show_page(p),
                height=64,  # Larger button height
                font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                corner_radius=16,
                fg_color=DARK_BLUE,
                hover_color=ACCENT_BLUE,
                border_width=0,
                text_color=WHITE,
                anchor="w"
            ).grid(row=idx, column=0, pady=12, padx=18, sticky="ew")

# --- Modern Main Content/Page Manager ---
class ModernMainContent(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, corner_radius=18, fg_color=LIGHT_GREY)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.pages = {
            "Home": HomePage(self, app),
            "Excel": ExcelPage(self, app),
            "Results": ResultsPage(self),
            "Virtual Agent": VirtualAgentPage(self),
            "Stats": StatsPage(self)
        }
        for page_name, page_widget in self.pages.items():
            page_widget.grid(row=0, column=0, sticky="nsew")
            if page_name != "Home":
                page_widget.grid_remove()
        self.current_page = "Home"
    def show_page(self, page_name_to_show: str):
        if page_name_to_show in self.pages:
            self.pages[self.current_page].grid_remove()
            self.pages[page_name_to_show].grid()
            self.current_page = page_name_to_show
        else:
            print(f"Error: Page '{page_name_to_show}' not found.")

# --- Home Page ---
class HomePage(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        super().__init__(
            master,
            fg_color=LIGHT_GREY,
            corner_radius=16,
            border_width=0
        )
        self.grid_columnconfigure(0, weight=1)
        self.selected_files = []
        self.id_count = 0
        self.status_label = None
        self.file_info_label = None
        self.app = app
        self.selected_agent = ctk.StringVar()
        self.agent_names = self.load_agent_names()
        self._build_ui()
    def load_agent_names(self):
        try:
            with open("agents.json", "r", encoding="utf-8") as f:
                agents = json.load(f)
                return [a["name"] for a in agents]
        except Exception:
            return []
    def _build_ui(self):
        # Credit counter at the top
        self.credit_label = ctk.CTkLabel(
            self,
            text=f"Credits Left: {self.app.credits}",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=ACCENT_BLUE
        )
        self.credit_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="e")
        # Agent selection dropdown
        agent_frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=10)
        agent_frame.grid(row=1, column=0, padx=20, pady=(5, 5), sticky="ew")
        ctk.CTkLabel(agent_frame, text="Select Virtual Agent:", font=ctk.CTkFont(size=14, weight="bold"), text_color=MID_BLUE).pack(side="left", padx=(10, 4))
        self.agent_dropdown = ctk.CTkOptionMenu(agent_frame, variable=self.selected_agent, values=self.agent_names, width=180, font=ctk.CTkFont(size=13))
        self.agent_dropdown.pack(side="left", padx=4, pady=6)
        if self.agent_names:
            self.selected_agent.set(self.agent_names[0])
        ctk.CTkLabel(
            self,
            text="Drag-and-drop or click to upload PDF files",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=MID_BLUE
        ).grid(row=2, column=0, padx=20, pady=(5, 5), sticky="w")
        self.file_drop_frame = ctk.CTkFrame(
            self,
            height=140,
            fg_color=WHITE,
            corner_radius=14,
            border_width=2,
            border_color=ACCENT_BLUE
        )
        self.file_drop_frame.grid(row=3, column=0, padx=20, pady=15, sticky="ew")
        self.file_drop_frame.grid_propagate(False)
        self.file_info_label = ctk.CTkLabel(
            self.file_drop_frame,
            text="Drop PDFs here or click to browse",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=MID_BLUE,
            fg_color="transparent",
            wraplength=600
        )
        self.file_info_label.place(relx=0.5, rely=0.5, anchor="center")
        self.file_drop_frame.bind("<Button-1>", self.browse_files)
        self.file_drop_frame.bind("<Enter>", lambda e: self.file_drop_frame.configure(fg_color=MID_GREY))
        self.file_drop_frame.bind("<Leave>", lambda e: self.file_drop_frame.configure(fg_color=WHITE))
        self.browse_button = ctk.CTkButton(
            self,
            text="📂 Browse Files",
            command=self.browse_files,
            height=44,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            corner_radius=12,
            fg_color=MID_BLUE,
            hover_color=ACCENT_BLUE,
            border_width=0,
            text_color=WHITE
        )
        self.browse_button.grid(row=4, column=0, pady=10, padx=20, sticky="ew")
        self.id_count_label = ctk.CTkLabel(
            self,
            text="IDs found: 0",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=ACCENT_BLUE
        )
        self.id_count_label.grid(row=5, column=0, padx=20, pady=5, sticky="w")
        self.start_button = ctk.CTkButton(
            self,
            text="🚀 Start Automation",
            command=self.start_automation,
            height=44,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            corner_radius=12,
            fg_color=ACCENT_BLUE,
            hover_color=MID_BLUE,
            border_width=0,
            text_color=WHITE
        )
        self.start_button.grid(row=6, column=0, pady=15, padx=20, sticky="ew")
        self.status_label = ctk.CTkLabel(
            self,
            text="Status: Idle",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=MID_BLUE
        )
        self.status_label.grid(row=7, column=0, padx=20, pady=10, sticky="w")
    def browse_files(self, event=None):
        file_paths = fd.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF Files", "*.pdf"), ("All files", "*.*")]
        )
        if file_paths:
            self.selected_files = list(file_paths)
            self.update_file_display_label()
            self.update_status_label(f"{len(self.selected_files)} file(s) selected.", text_color=MID_BLUE)
            self.update_id_count()
    def handle_dropped_files(self, file_paths: list):
        self.selected_files = file_paths
        self.update_file_display_label()
        self.update_status_label(f"{len(self.selected_files)} file(s) dropped.", text_color=MID_BLUE)
        self.update_id_count()
    def update_file_display_label(self):
        if self.selected_files:
            if len(self.selected_files) == 1:
                filename = os.path.basename(self.selected_files[0])
                self.file_info_label.configure(text=f"Selected: {filename}")
            else:
                self.file_info_label.configure(text=f"{len(self.selected_files)} PDF files selected.")
        else:
            self.file_info_label.configure(text="Drop PDFs here or click to browse")
    def update_status_label(self, message: str, text_color=MID_BLUE):
        if self.status_label:
            self.status_label.configure(text=f"Status: {message}", text_color=text_color)
    def update_id_count(self):
        self.id_count = 0
        if self.selected_files:
            self.id_count = len(self.selected_files) * 3
        self.id_count_label.configure(text=f"IDs found: {self.id_count}")
    def start_automation(self):
        if not self.selected_files:
            self.update_status_label("No files selected to process!", text_color=ERROR)
            return
        if not self.selected_agent.get():
            self.update_status_label("No virtual agent selected!", text_color=ERROR)
            return
        self.update_status_label(f"Processing {len(self.selected_files)} file(s) with agent '{self.selected_agent.get()}'...", text_color=MID_BLUE)
        self.app.update()
        self.process_pdfs(self.selected_agent.get())
    def process_pdfs(self, agent_name):
        import pdf_parser  # Import here to avoid circular import
        import virtual_agent_scraper  # Import here to avoid circular import
        total_credits = self.app.credits
        processed_count = 0
        for pdf_path in self.selected_files:
            pdf_filename = os.path.basename(pdf_path)
            # --- 1. Extract records from PDF ---
            try:
                parsed_ids = pdf_parser.parse_pdf(pdf_path)  # Should return a list of dicts
            except Exception as e:
                self.update_status_label(f"Error parsing {pdf_filename}: {e}", text_color=ERROR)
                continue
            # --- 2. Insert records into DB as 'pending' ---
            for rec in parsed_ids:
                db.insert_record(
                    pdf_filename,
                    rec.get("municipality", ""),
                    rec.get("township", ""),
                    rec.get("sectional_scheme_name", ""),
                    rec.get("unit", ""),
                    rec.get("size", ""),
                    rec.get("name", ""),
                    rec.get("identifier", "")
                )
            # --- 3. Process each record with virtual_agent_scraper ---
            pending = db.get_pending_ids(pdf_filename)
            for rec in pending:
                if total_credits <= 0:
                    self.update_status_label("No credits left!", text_color=ERROR)
                    return
                try:
                    result = virtual_agent_scraper.scrape(rec, agent_name)  # Pass agent_name
                    if result:
                        db.update_status(rec["id"], "done")
                        processed_count += 1
                        total_credits -= 1
                        self.app.credits = total_credits
                        self.credit_label.configure(text=f"Credits Left: {self.app.credits}")
                        self.update_status_label(f"Processed ID: {rec['identifier']}", text_color=SUCCESS)
                    else:
                        self.update_status_label(f"Failed: {rec['identifier']}", text_color=ERROR)
                except Exception as e:
                    self.update_status_label(f"Error: {e}", text_color=ERROR)
                self.app.update()
        self.update_status_label(f"Finished! {processed_count} IDs processed.", text_color=SUCCESS)

# --- Placeholder Pages ---
class ExcelPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=LIGHT_GREY, corner_radius=16)
        self.app = app
        self.open_excel_var = ctk.BooleanVar(value=True)
        self.save_path_var = ctk.StringVar(value="")
        self._build_ui()
    def _build_ui(self):
        ctk.CTkLabel(
            self,
            text="Excel Export Settings",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=MID_BLUE
        ).pack(pady=(30, 10), anchor="w", padx=30)
        ctk.CTkCheckBox(
            self,
            text="Open Excel after completion",
            variable=self.open_excel_var,
            font=ctk.CTkFont(family="Segoe UI", size=15),
            text_color=MID_BLUE
        ).pack(pady=10, anchor="w", padx=40)
        frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12)
        frame.pack(pady=20, padx=30, fill="x")
        ctk.CTkLabel(
            frame,
            text="Save Excel to:",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=MID_BLUE
        ).pack(side="left", padx=10, pady=10)
        ctk.CTkEntry(
            frame,
            textvariable=self.save_path_var,
            width=320,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=LIGHT_GREY,
            text_color=MID_BLUE,
            corner_radius=8
        ).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(
            frame,
            text="Browse",
            command=self.browse_save_path,
            height=36,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            corner_radius=8,
            fg_color=ACCENT_BLUE,
            hover_color=MID_BLUE,
            border_width=0,
            text_color=WHITE
        ).pack(side="left", padx=10, pady=10)
    def browse_save_path(self):
        file_path = fd.asksaveasfilename(
            title="Save Excel File As",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.save_path_var.set(file_path)

class ResultsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=LIGHT_GREY, corner_radius=16)
        self.selected_pdf = ctk.StringVar()
        self.records = []
        self._build_ui()
    def _build_ui(self):
        ctk.CTkLabel(self, text="Results", font=ctk.CTkFont(size=22, weight="bold"), text_color=ACCENT_BLUE).pack(pady=(24, 10))
        # PDF selector (centered)
        selector_frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12)
        selector_frame.pack(pady=(0, 10), padx=30, fill="x")
        selector_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(selector_frame, text="Select PDF:", font=ctk.CTkFont(size=15, weight="bold"), text_color=MID_BLUE).grid(row=0, column=0, padx=12, pady=(10, 0), sticky="ew")
        self.pdfs_dropdown = ctk.CTkOptionMenu(selector_frame, variable=self.selected_pdf, values=self.get_pdf_list(), command=self.on_pdf_select, width=320, font=ctk.CTkFont(size=14))
        self.pdfs_dropdown.grid(row=1, column=0, padx=12, pady=(2, 10), sticky="ew")
        # Summary
        self.summary_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14, weight="bold"), text_color=MID_BLUE)
        self.summary_label.pack(pady=(0, 8))
        # Scrollable table area
        self.table_scroll = ctk.CTkScrollableFrame(self, fg_color=WHITE, corner_radius=14, width=1200, height=350)  # wider
        self.table_scroll.pack(padx=30, pady=10, fill="both", expand=True)
        self.table_labels = []
        self.selected_pdf.trace_add('write', lambda *a: self.display_table())
        if self.get_pdf_list():
            self.selected_pdf.set(self.get_pdf_list()[0])
            self.display_table()
    def get_pdf_list(self):
        import db
        with db.get_conn() as conn:
            cur = conn.execute('SELECT DISTINCT pdf_filename FROM processed_ids')
            return [row[0] for row in cur.fetchall()]
    def on_pdf_select(self, value):
        self.display_table()
    def display_table(self):
        import db
        for label in self.table_labels:
            label.destroy()
        self.table_labels.clear()
        pdf = self.selected_pdf.get()
        if not pdf:
            self.summary_label.configure(text="")
            return
        records = db.get_all_records(pdf)
        headers = ["municipality", "township", "sectional_scheme_name", "unit", "size", "name", "identifier", "status", "processed_at"]
        # Summary
        total = len(records)
        done = sum(1 for r in records if r.get("status") == "done")
        pending = total - done
        self.summary_label.configure(text=f"Total IDs: {total}   Done: {done}   Pending: {pending}")
        # Header row
        for col, h in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_scroll, text=h.upper(), font=ctk.CTkFont(size=13, weight="bold"), text_color=ACCENT_BLUE, fg_color=LIGHT_GREY, width=22)
            lbl.grid(row=0, column=col, padx=6, pady=4, sticky="nsew")
            self.table_labels.append(lbl)
        # Data rows with alternating colors
        for row, rec in enumerate(records, start=1):
            bg = MID_GREY if row % 2 == 0 else WHITE
            for col, h in enumerate(headers):
                val = rec.get(h, "")
                # Use a label with wraplength for text wrapping
                lbl = ctk.CTkLabel(self.table_scroll, text=str(val), font=ctk.CTkFont(size=12), text_color=MID_BLUE, fg_color=bg, width=22, wraplength=140, anchor="w", justify="left")
                lbl.grid(row=row, column=col, padx=6, pady=2, sticky="nsew")
                self.table_labels.append(lbl)

AGENTS_FILE = "agents.json"

class VirtualAgentPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=LIGHT_GREY, corner_radius=16)
        self.agents = self.load_agents()
        self.selected_agent = ctk.StringVar()
        self.is_editing = False
        self.status_label = None
        self._build_ui()
    def _build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self, text="Virtual Agent Credentials", font=ctk.CTkFont(size=24, weight="bold"), text_color=ACCENT_BLUE).pack(pady=(32, 16))
        main_frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=18)
        main_frame.pack(padx=40, pady=20, fill="both", expand=True)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)
        # Left: Card-style agent list
        left_panel = ctk.CTkFrame(main_frame, fg_color=LIGHT_GREY, corner_radius=14, width=340)
        left_panel.grid(row=0, column=0, padx=24, pady=24, sticky="nsew")
        left_panel.grid_propagate(False)
        left_panel.grid_rowconfigure(3, weight=1)  # Make agent list expand
        # Add Agent button at the top, more prominent, more space below
        self.add_agent_btn = ctk.CTkButton(left_panel, text="＋ Add Agent", command=self.add_agent, fg_color=ACCENT_BLUE, text_color=WHITE, font=ctk.CTkFont(size=16, weight="bold"), height=48, corner_radius=14)
        self.add_agent_btn.grid(row=0, column=0, padx=18, pady=(18, 12), sticky="ew")
        # Saved Agents label with more space
        ctk.CTkLabel(left_panel, text="Saved Agents", font=ctk.CTkFont(size=17, weight="bold"), text_color=MID_BLUE).grid(row=1, column=0, pady=(0, 14), padx=20, sticky="w")
        # Scrollable agent list with more padding
        self.agent_list_frame = ctk.CTkScrollableFrame(left_panel, fg_color=LIGHT_GREY, corner_radius=14, width=300, height=420)
        self.agent_list_frame.grid(row=3, column=0, padx=16, pady=(0, 10), sticky="nsew")
        # Right: Agent details form
        right_panel = ctk.CTkFrame(main_frame, fg_color=WHITE, corner_radius=14)
        right_panel.grid(row=0, column=1, padx=24, pady=24, sticky="nsew")
        right_panel.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(right_panel, text="Agent Details", font=ctk.CTkFont(size=16, weight="bold"), text_color=MID_BLUE).grid(row=0, column=0, columnspan=2, pady=(16, 12))
        ctk.CTkLabel(right_panel, text="Agent Name", font=ctk.CTkFont(size=13), text_color=MID_BLUE).grid(row=1, column=0, padx=12, pady=10, sticky="e")
        self.entry_name = ctk.CTkEntry(right_panel, placeholder_text="Agent Name", font=ctk.CTkFont(size=15))
        self.entry_name.grid(row=1, column=1, padx=12, pady=10, sticky="ew")
        ctk.CTkLabel(right_panel, text="Username", font=ctk.CTkFont(size=13), text_color=MID_BLUE).grid(row=2, column=0, padx=12, pady=10, sticky="e")
        self.entry_username = ctk.CTkEntry(right_panel, placeholder_text="Username", font=ctk.CTkFont(size=15))
        self.entry_username.grid(row=2, column=1, padx=12, pady=10, sticky="ew")
        ctk.CTkLabel(right_panel, text="Password", font=ctk.CTkFont(size=13), text_color=MID_BLUE).grid(row=3, column=0, padx=12, pady=10, sticky="e")
        self.entry_password = ctk.CTkEntry(right_panel, placeholder_text="Password", show="*", font=ctk.CTkFont(size=15))
        self.entry_password.grid(row=3, column=1, padx=12, pady=10, sticky="ew")
        # Buttons
        btn_frame = ctk.CTkFrame(right_panel, fg_color=WHITE)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(18, 8))
        self.save_button = ctk.CTkButton(btn_frame, text="Save", command=self.save_agent, fg_color=SUCCESS, text_color=WHITE, width=120, font=ctk.CTkFont(size=15, weight="bold"))
        self.save_button.pack(side="left", padx=10)
        self.cancel_button = ctk.CTkButton(btn_frame, text="Cancel", command=self.cancel_edit, fg_color=ERROR, text_color=WHITE, width=120, font=ctk.CTkFont(size=15, weight="bold"))
        self.cancel_button.pack(side="left", padx=10)
        self.status_label = ctk.CTkLabel(right_panel, text="", font=ctk.CTkFont(size=12), text_color=ERROR)
        self.status_label.grid(row=5, column=0, columnspan=2, pady=(6, 0))
        self.set_fields_state("disabled")
        self.display_agent_list()
    def display_agent_list(self):
        for widget in self.agent_list_frame.winfo_children():
            widget.destroy()
        if not self.agents:
            ctk.CTkLabel(self.agent_list_frame, text="No agents saved yet. Click '＋ Add Agent' to create one.", font=ctk.CTkFont(size=13), text_color=MID_BLUE, wraplength=260, justify="left").pack(pady=30)
            return
        for idx, agent in enumerate(self.agents):
            card = ctk.CTkFrame(self.agent_list_frame, fg_color=WHITE, corner_radius=14, border_width=2, border_color=MID_GREY, height=64)
            card.pack(fill="x", pady=(0, 14), padx=4)
            card.pack_propagate(False)
            # Agent name larger and centered vertically
            name_lbl = ctk.CTkLabel(card, text=agent["name"], font=ctk.CTkFont(size=16, weight="bold"), text_color=MID_BLUE)
            name_lbl.pack(side="left", padx=24, pady=8, anchor="center")
            # Edit and Delete buttons with more space
            btn_frame = ctk.CTkFrame(card, fg_color=WHITE)
            btn_frame.pack(side="right", padx=16, pady=8)
            edit_btn = ctk.CTkButton(btn_frame, text="✏️", width=36, height=32, fg_color=ACCENT_BLUE, text_color=WHITE, command=lambda a=agent: self.edit_agent(a), font=ctk.CTkFont(size=14))
            edit_btn.pack(side="left", padx=4)
            edit_btn._text_label.configure(cursor="hand2")
            edit_btn._text_label.bind("<Enter>", lambda e, b=edit_btn: b._text_label.configure(text="✏️ Edit"))
            edit_btn._text_label.bind("<Leave>", lambda e, b=edit_btn: b._text_label.configure(text="✏️"))
            del_btn = ctk.CTkButton(btn_frame, text="🗑️", width=36, height=32, fg_color=ERROR, text_color=WHITE, command=lambda a=agent: self.delete_agent(a), font=ctk.CTkFont(size=14))
            del_btn.pack(side="left", padx=4)
            del_btn._text_label.configure(cursor="hand2")
            del_btn._text_label.bind("<Enter>", lambda e, b=del_btn: b._text_label.configure(text="🗑️ Delete"))
            del_btn._text_label.bind("<Leave>", lambda e, b=del_btn: b._text_label.configure(text="🗑️"))
            # Divider line below each card except last
            if idx < len(self.agents) - 1:
                divider = ctk.CTkFrame(self.agent_list_frame, fg_color=MID_GREY, height=1)
                divider.pack(fill="x", padx=8, pady=(0, 8))
    def set_fields_state(self, state):
        self.entry_name.configure(state=state)
        self.entry_username.configure(state=state)
        self.entry_password.configure(state=state)
        self.save_button.configure(state=state)
        self.cancel_button.configure(state=state)
    def add_agent(self):
        self.entry_name.delete(0, "end")
        self.entry_username.delete(0, "end")
        self.entry_password.delete(0, "end")
        self.set_fields_state("normal")
        self.is_editing = True
        self.status_label.configure(text="")
        self.selected_agent.set("")
    def edit_agent(self, agent):
        self.entry_name.delete(0, "end")
        self.entry_name.insert(0, agent["name"])
        self.entry_username.delete(0, "end")
        self.entry_username.insert(0, agent["username"])
        self.entry_password.delete(0, "end")
        self.entry_password.insert(0, self.get_password(agent["name"]))
        self.set_fields_state("normal")
        self.is_editing = True
        self.selected_agent.set(agent["name"])
        self.status_label.configure(text="")
    def delete_agent(self, agent):
        self.agents = [a for a in self.agents if a["name"] != agent["name"]]
        self.save_agents()
        self.display_agent_list()
        self.add_agent()  # Clear form
    def save_agent(self):
        name = self.entry_name.get().strip()
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        if not name or not username or not password:
            self.status_label.configure(text="All fields are required!")
            return
        # Save to keyring
        keyring.set_password("AutomateAgent", f"{name}_username", username)
        keyring.set_password("AutomateAgent", f"{name}_password", password)
        # Update local list
        found = False
        for agent in self.agents:
            if agent["name"] == name:
                agent["username"] = username
                found = True
        if not found:
            self.agents.append({"name": name, "username": username})
        self.save_agents()
        self.display_agent_list()
        self.set_fields_state("disabled")
        self.is_editing = False
        self.status_label.configure(text="Saved!", text_color=SUCCESS)
    def cancel_edit(self):
        self.set_fields_state("disabled")
        self.status_label.configure(text="Cancelled.", text_color=ERROR)
    def load_agents(self):
        if os.path.exists(AGENTS_FILE):
            try:
                with open(AGENTS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    def save_agents(self):
        with open(AGENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.agents, f, indent=2)
    def get_password(self, name):
        return keyring.get_password("AutomateAgent", f"{name}_password") or ""

class StatsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=LIGHT_GREY, corner_radius=16)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        # Modern, visually separated card layout
        card_bg = MID_BLUE
        card_fg = WHITE
        card_border = ACCENT_BLUE
        # Headers
        ctk.CTkLabel(
            self,
            text="Processing Stats",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=ACCENT_BLUE
        ).grid(row=0, column=0, columnspan=2, pady=(24, 8), padx=20, sticky="w")
        # Processing Stats Data
        processing_stats = {
            "PDFs Processed": 128,
            "IDs Retrieved": 114,
            "Successful Runs": 56,
            "Failed Runs": 2
        }
        for idx, (key, value) in enumerate(processing_stats.items()):
            col = idx % 2
            row = (idx // 2) + 1
            frame = ctk.CTkFrame(self, fg_color=card_bg, corner_radius=16, border_width=2, border_color=card_border)
            frame.grid(row=row, column=col, padx=18, pady=10, sticky="ew")
            ctk.CTkLabel(
                frame,
                text=key,
                font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                text_color=ACCENT_BLUE
            ).pack(anchor="w", padx=16, pady=(10, 0))
            ctk.CTkLabel(
                frame,
                text=str(value),
                font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                text_color=card_fg
            ).pack(anchor="w", padx=16, pady=(0, 10))
        # Performance Metrics Header
        performance_row = (len(processing_stats) // 2) + 2
        ctk.CTkLabel(
            self,
            text="Performance Metrics",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=ACCENT_BLUE
        ).grid(row=performance_row, column=0, columnspan=2, pady=(24, 8), padx=20, sticky="w")
        # Performance Metrics Data
        performance_metrics = {
            "Average Time per PDF": "3.2s",
            "Estimated Time Saved": "6.1 minutes",
            "Streak (days processing)": 3
        }
        for idx, (key, value) in enumerate(performance_metrics.items()):
            col = idx % 2
            row = performance_row + 1 + (idx // 2)
            frame = ctk.CTkFrame(self, fg_color=card_bg, corner_radius=16, border_width=2, border_color=card_border)
            frame.grid(row=row, column=col, padx=18, pady=10, sticky="ew")
            ctk.CTkLabel(
                frame,
                text=key,
                font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                text_color=ACCENT_BLUE
            ).pack(anchor="w", padx=16, pady=(10, 0))
            ctk.CTkLabel(
                frame,
                text=str(value),
                font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                text_color=card_fg
            ).pack(anchor="w", padx=16, pady=(0, 10))


if __name__ == "__main__":
    db.ensure_db()  # Initialize the database at app startup
    app = AutomateAgentApp()
    app.mainloop()