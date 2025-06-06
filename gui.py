import os
import customtkinter as ctk
import tkinter.filedialog as fd
from tkinterdnd2 import TkinterDnD, DND_FILES

# Set permanent dark theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class AegisApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        try:
            self.tk.call('package', 'require', 'tkdnd')
            print("Successfully loaded 'tkdnd' package.")
        except Exception as e:
            print("⚠️ Failed to load 'tkdnd' package. Drag-and-drop may not work.")
            print("Details:", e)

        self.title("Aegis - PDF Automation Assistant")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        # Main CTkFrame as the app container
        self.app_frame = ctk.CTkFrame(self, fg_color="#1e1e1e")
        self.app_frame.pack(fill="both", expand=True)
        self.app_frame.grid_columnconfigure(0, weight=0)
        self.app_frame.grid_columnconfigure(1, weight=1)
        self.app_frame.grid_rowconfigure(0, weight=1)

        # Sidebar and main content
        self.sidebar = Sidebar(self.app_frame)
        self.sidebar.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)

        self.main_content = MainContent(self.app_frame)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Enable drag-and-drop
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)

    def handle_drop(self, event):
        try:
            files = self.tk.splitlist(event.data)
            pdf_files = [f for f in files if f.lower().endswith('.pdf')]
            if pdf_files:
                self.main_content.process_page.handle_dropped_files(pdf_files)
            else:
                self.main_content.process_page.update_status_label("Only PDF files are accepted.", text_color="#FF4C4C")
        except Exception as e:
            print(f"Error handling drop: {e}")
            self.main_content.process_page.update_status_label("Error processing dropped files.", text_color="#FF4C4C")


class Sidebar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, width=250, corner_radius=12, fg_color="#2f2f2f")
        self.grid_propagate(False)
        self.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            self,
            text="Aegis Menu",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#E0E0E0"
        ).grid(row=0, column=0, pady=(20, 15), padx=20, sticky="w")

        buttons = [
            ("📁 Process Files", lambda: master.master.main_content.show_page("process")),
            ("🔐 Virtual Agents", lambda: master.master.main_content.show_page("credentials")),
            ("📊 Statistics", lambda: master.master.main_content.show_page("stats"))
        ]
        for idx, (text, command) in enumerate(buttons, start=1):
            ctk.CTkButton(
                self,
                text=text,
                command=command,
                height=48,
                font=ctk.CTkFont(family="Segoe UI", size=14),
                corner_radius=12,
                fg_color="#0078D4",
                hover_color="#005EA6",
                border_width=1,
                border_color="#0078D4",
                text_color="#E0E0E0"
            ).grid(row=idx, column=0, pady=8, padx=20, sticky="ew")


class MainContent(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=12, fg_color="#1e1e1e")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.pages = {}
        self.process_page = ProcessPage(self)
        self.credentials_page = CredentialsPage(self, process_page=self.process_page)
        self.stats_page = StatsPage(self)

        self.pages = {
            "process": self.process_page,
            "credentials": self.credentials_page,
            "stats": self.stats_page
        }

        for page_name, page_widget in self.pages.items():
            page_widget.grid(row=0, column=0, sticky="nsew")
            if page_name != "process":
                page_widget.grid_remove()

        self.current_page = "process"

    def show_page(self, page_name_to_show: str):
        if page_name_to_show in self.pages:
            self.pages[self.current_page].grid_remove()
            self.pages[page_name_to_show].grid()
            self.current_page = page_name_to_show
        else:
            print(f"Error: Page '{page_name_to_show}' not found.")


class ProcessPage(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, label_text="Process PDFs", label_font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), fg_color="#1e1e1e")
        self.grid_columnconfigure(0, weight=1)

        self.selected_files = []
        self.animation_id = None
        self.is_processing = False
        self.idle_color_index = 0
        self.processing_dots = 0

        ctk.CTkLabel(
            self,
            text="Select Virtual Agent Profile:",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#E0E0E0"
        ).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        self.profile_values = ["Custom", "Marco's VA", "Admin VA"]
        self.selected_profile = ctk.StringVar(value="Custom")
        self.profile_menu = ctk.CTkOptionMenu(
            self,
            variable=self.selected_profile,
            values=self.profile_values,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            dropdown_font=ctk.CTkFont(family="Segoe UI", size=12),
            corner_radius=12,
            fg_color="#2f2f2f",
            button_color="#0078D4",
            button_hover_color="#005EA6",
            text_color="#E0E0E0"
        )
        self.profile_menu.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.profile_menu.set("Custom")

        self.file_drop_frame = ctk.CTkFrame(
            self,
            height=150,
            fg_color="#2f2f2f",
            corner_radius=12,
            border_width=2,
            border_color="#0078D4"
        )
        self.file_drop_frame.grid(row=2, column=0, padx=20, pady=15, sticky="ew")
        self.file_drop_frame.grid_propagate(False)

        self.file_info_label = ctk.CTkLabel(
            self.file_drop_frame,
            text="Drop PDFs here or click to browse",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#E0E0E0",
            fg_color="transparent",
            wraplength=600
        )
        self.file_info_label.place(relx=0.5, rely=0.5, anchor="center")

        self.file_drop_frame.bind("<Button-1>", self.browse_files)
        self.file_drop_frame.bind("<Enter>", lambda e: self.file_drop_frame.configure(fg_color="#3a3a3a"))
        self.file_drop_frame.bind("<Leave>", lambda e: self.file_drop_frame.configure(fg_color="#2f2f2f"))

        self.browse_button = ctk.CTkButton(
            self,
            text="📂 Browse Files",
            command=self.browse_files,
            height=48,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=12,
            fg_color="#0078D4",
            hover_color="#005EA6",
            border_width=1,
            border_color="#0078D4",
            text_color="#E0E0E0"
        )
        self.browse_button.grid(row=3, column=0, pady=10, padx=20, sticky="ew")

        self.open_excel_var = ctk.BooleanVar()
        self.open_excel_checkbox = ctk.CTkCheckBox(
            self,
            text="Open Excel after processing",
            variable=self.open_excel_var,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#E0E0E0",
            hover_color="#005EA6"
        )
        self.open_excel_checkbox.grid(row=4, column=0, pady=10, padx=20, sticky="w")

        self.start_button = ctk.CTkButton(
            self,
            text="🚀 Start Processing",
            command=self.start_processing,
            height=48,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=12,
            fg_color="#0078D4",
            hover_color="#005EA6",
            border_width=1,
            border_color="#0078D4",
            text_color="#E0E0E0"
        )
        self.start_button.grid(row=5, column=0, pady=15, padx=20, sticky="ew")

        self.status_label = ctk.CTkLabel(
            self,
            text="Status: Idle",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#E0E0E0"
        )
        self.status_label.grid(row=6, column=0, padx=20, pady=10, sticky="w")

        self.start_idle_animation()

    def start_idle_animation(self):
        if self.is_processing or not self.status_label:
            return
        if self.animation_id:
            self.after_cancel(self.animation_id)
        colors = ["#E0E0E0", "#A0A0A0"]
        self.status_label.configure(text_color=colors[self.idle_color_index])
        self.idle_color_index = (self.idle_color_index + 1) % 2
        self.animation_id = self.after(1000, self.start_idle_animation)

    def start_processing_animation(self):
        if not self.status_label:
            return
        if self.animation_id:
            self.after_cancel(self.animation_id)
        dots = "." * (self.processing_dots + 1)
        self.status_label.configure(text=f"Status: Processing{dots}", text_color="#E0E0E0")
        self.processing_dots = (self.processing_dots + 1) % 3
        self.animation_id = self.after(500, self.start_processing_animation)

    def stop_animation(self):
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
        self.idle_color_index = 0
        self.processing_dots = 0

    def browse_files(self, event=None):
        file_paths = fd.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF Files", "*.pdf"), ("All files", "*.*")]
        )
        if file_paths:
            self.selected_files = list(file_paths)
            self.update_file_display_label()
            self.update_status_label(f"{len(self.selected_files)} file(s) selected.", text_color="#E0E0E0")

    def handle_dropped_files(self, file_paths: list):
        self.selected_files = file_paths
        self.update_file_display_label()
        self.update_status_label(f"{len(self.selected_files)} file(s) dropped.", text_color="#E0E0E0")

    def update_file_display_label(self):
        if self.selected_files:
            if len(self.selected_files) == 1:
                filename = os.path.basename(self.selected_files[0])
                self.file_info_label.configure(text=f"Selected: {filename}")
            else:
                self.file_info_label.configure(text=f"{len(self.selected_files)} PDF files selected.")
        else:
            self.file_info_label.configure(text="Drop PDFs here or click to browse")

    def update_status_label(self, message: str, text_color="#E0E0E0"):
        if self.status_label:
            self.stop_animation()
            self.status_label.configure(text=f"Status: {message}", text_color=text_color)
            if message == "Idle":
                self.is_processing = False
                self.start_idle_animation()
            elif "Processing" in message:
                self.is_processing = True
                self.start_processing_animation()

    def start_processing(self):
        if not self.selected_files:
            self.update_status_label("No files selected to process!", text_color="#FF4C4C")
            return
        selected_profile = self.selected_profile.get()
        self.update_status_label(f"Processing {len(self.selected_files)} file(s) with profile: {selected_profile}", text_color="#E0E0E0")
        print(f"Processing files: {self.selected_files}")
        print(f"Selected profile: {selected_profile}")
        print(f"Open Excel after processing: {self.open_excel_var.get()}")
        self.after(2000, self.on_processing_complete)

    def on_processing_complete(self):
        self.update_status_label("Processing complete!", text_color="#00CC00")


class CredentialsPage(ctk.CTkScrollableFrame):
    def __init__(self, master, process_page=None):
        super().__init__(master, label_text="Manage Virtual Agent Credentials", label_font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), fg_color="#1e1e1e")
        self.grid_columnconfigure(0, weight=1)
        self._process_page = process_page
        self.agents = []  # List to store agent data: [name, username, password, is_permanent]
        self.selected_agent_index = ctk.IntVar(value=-1)  # Track selected agent for editing
        self.is_editing = False  # Track editing mode

        # Agent Selection
        ctk.CTkLabel(
            self,
            text="Select Agent:",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#E0E0E0"
        ).grid(row=0, column=0, pady=(15, 5), padx=20, sticky="w")

        self.agent_menu = ctk.CTkOptionMenu(
            self,
            values=["Create New Agent"] + [agent[0] for agent in self.agents],
            command=self.on_agent_select,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            dropdown_font=ctk.CTkFont(family="Segoe UI", size=12),
            corner_radius=12,
            fg_color="#2f2f2f",
            button_color="#0078D4",
            button_hover_color="#005EA6",
            text_color="#E0E0E0"
        )
        self.agent_menu.grid(row=1, column=0, pady=5, padx=20, sticky="ew")
        self.agent_menu.set("Create New Agent")

        # Input Fields (corrected to remove text_color_disabled)
        self.entry_agent_name = ctk.CTkEntry(
            self,
            placeholder_text="Agent Name",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#2f2f2f",
            text_color="#E0E0E0",
            corner_radius=12
        )
        self.entry_agent_name.grid(row=2, column=0, pady=5, padx=20, sticky="ew")
        self.entry_agent_name.configure(state="disabled", text_color="#808080")

        self.entry_username = ctk.CTkEntry(
            self,
            placeholder_text="Username",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#2f2f2f",
            text_color="#E0E0E0",
            corner_radius=12
        )
        self.entry_username.grid(row=3, column=0, pady=5, padx=20, sticky="ew")
        self.entry_username.configure(state="disabled", text_color="#808080")

        self.entry_password = ctk.CTkEntry(
            self,
            placeholder_text="Password",
            show="*",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#2f2f2f",
            text_color="#E0E0E0",
            corner_radius=12
        )
        self.entry_password.grid(row=4, column=0, pady=5, padx=20, sticky="ew")
        self.entry_password.configure(state="disabled", text_color="#808080")

        self.save_permanently_var = ctk.BooleanVar()
        self.save_permanently_checkbox = ctk.CTkCheckBox(
            self,
            text="Save Permanently",
            variable=self.save_permanently_var,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#E0E0E0",
            hover_color="#005EA6",
            state="disabled"
        )
        self.save_permanently_checkbox.grid(row=5, column=0, pady=10, padx=20, sticky="w")

        self.edit_button = ctk.CTkButton(
            self,
            text="Edit Agent",
            command=self.enable_edit_mode,
            height=48,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=12,
            fg_color="#0078D4",
            hover_color="#005EA6",
            border_width=1,
            border_color="#0078D4",
            text_color="#E0E0E0",
            state="disabled"
        )
        self.edit_button.grid(row=6, column=0, pady=15, padx=20, sticky="ew")

        self.create_button = ctk.CTkButton(
            self,
            text="Create Agent",
            command=self.create_agent,
            height=48,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=12,
            fg_color="#0078D4",
            hover_color="#005EA6",
            border_width=1,
            border_color="#0078D4",
            text_color="#E0E0E0"
        )
        self.create_button.grid(row=7, column=0, pady=15, padx=20, sticky="ew")

        self.save_changes_button = ctk.CTkButton(
            self,
            text="Save Changes",
            command=self.save_changes,
            height=48,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=12,
            fg_color="#0078D4",
            hover_color="#005EA6",
            border_width=1,
            border_color="#0078D4",
            text_color="#E0E0E0",
            state="disabled"
        )
        self.save_changes_button.grid(row=8, column=0, pady=15, padx=20, sticky="ew")

    def on_agent_select(self, selected_agent):
        self.is_editing = False
        if selected_agent == "Create New Agent":
            self.selected_agent_index.set(-1)
            self.entry_agent_name.delete(0, 'end')
            self.entry_username.delete(0, 'end')
            self.entry_password.delete(0, 'end')
            self.save_permanently_var.set(False)
            self.entry_agent_name.configure(state="normal", text_color="#E0E0E0")
            self.entry_username.configure(state="normal", text_color="#E0E0E0")
            self.entry_password.configure(state="normal", text_color="#E0E0E0")
            self.save_permanently_checkbox.configure(state="normal")
            self.edit_button.configure(state="disabled")
            self.save_changes_button.configure(state="disabled")
        else:
            index = [agent[0] for agent in self.agents].index(selected_agent)
            self.selected_agent_index.set(index)
            agent = self.agents[index]
            self.entry_agent_name.delete(0, 'end')
            self.entry_username.delete(0, 'end')
            self.entry_password.delete(0, 'end')
            self.entry_agent_name.insert(0, agent[0])
            self.entry_username.insert(0, agent[1])
            self.entry_password.insert(0, agent[2])
            self.save_permanently_var.set(agent[3])
            self.entry_agent_name.configure(state="disabled", text_color="#808080")
            self.entry_username.configure(state="disabled", text_color="#808080")
            self.entry_password.configure(state="disabled", text_color="#808080")
            self.save_permanently_checkbox.configure(state="disabled")
            self.edit_button.configure(state="normal")
            self.save_changes_button.configure(state="disabled")

    def enable_edit_mode(self):
        self.is_editing = True
        self.entry_agent_name.configure(state="normal", text_color="#E0E0E0")
        self.entry_username.configure(state="normal", text_color="#E0E0E0")
        self.entry_password.configure(state="normal", text_color="#E0E0E0")
        self.save_permanently_checkbox.configure(state="normal")
        self.save_changes_button.configure(state="normal")

    def create_agent(self):
        agent_name = self.entry_agent_name.get().strip()
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        is_permanent = self.save_permanently_var.get()

        if not agent_name or not username or not password:
            print("Agent Name, Username, and Password are required.")
            if self._process_page:
                self._process_page.update_status_label("All fields are required.", text_color="#FF4C4C")
            return

        if agent_name in [agent[0] for agent in self.agents]:
            print("Agent name already exists.")
            if self._process_page:
                self._process_page.update_status_label("Agent name already exists.", text_color="#FF4C4C")
            return

        self.agents.append([agent_name, username, password, is_permanent])
        self.agent_menu.configure(values=["Create New Agent"] + [agent[0] for agent in self.agents])
        self.agent_menu.set(agent_name)
        self.selected_agent_index.set(len(self.agents) - 1)
        self.entry_agent_name.configure(state="disabled", text_color="#808080")
        self.entry_username.configure(state="disabled", text_color="#808080")
        self.entry_password.configure(state="disabled", text_color="#808080")
        self.save_permanently_checkbox.configure(state="disabled")
        self.edit_button.configure(state="normal")
        self.save_changes_button.configure(state="disabled")
        if self._process_page:
            self._process_page.update_status_label("Agent created successfully.", text_color="#00CC00")

    def save_changes(self):
        if not self.is_editing:
            return
        index = self.selected_agent_index.get()
        if index >= 0:
            agent_name = self.entry_agent_name.get().strip()
            username = self.entry_username.get().strip()
            password = self.entry_password.get().strip()
            is_permanent = self.save_permanently_var.get()

            if not agent_name or not username or not password:
                print("Agent Name, Username, and Password are required.")
                if self._process_page:
                    self._process_page.update_status_label("All fields are required.", text_color="#FF4C4C")
                return

            for i, agent in enumerate(self.agents):
                if i != index and agent[0] == agent_name:
                    print("Agent name already exists.")
                    if self._process_page:
                        self._process_page.update_status_label("Agent name already exists.", text_color="#FF4C4C")
                    return

            self.agents[index] = [agent_name, username, password, is_permanent]
            self.agent_menu.configure(values=["Create New Agent"] + [agent[0] for agent in self.agents])
            self.agent_menu.set(agent_name)
            self.entry_agent_name.configure(state="disabled", text_color="#808080")
            self.entry_username.configure(state="disabled", text_color="#808080")
            self.entry_password.configure(state="disabled", text_color="#808080")
            self.save_permanently_checkbox.configure(state="disabled")
            self.edit_button.configure(state="normal")
            self.save_changes_button.configure(state="disabled")
            self.is_editing = False
            if self._process_page:
                self._process_page.update_status_label("Agent updated successfully.", text_color="#00CC00")
        else:
            print("No agent selected for editing.")
            if self._process_page:
                self._process_page.update_status_label("No agent selected for editing.", text_color="#FF4C4C")


class StatsPage(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, label_text="Aegis Statistics", label_font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), fg_color="#1e1e1e")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Processing Stats Header
        ctk.CTkLabel(
            self,
            text="Processing Stats",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#E0E0E0"
        ).grid(row=0, column=0, columnspan=2, pady=(15, 5), padx=20, sticky="w")

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
            frame = ctk.CTkFrame(self, fg_color="#2f2f2f", corner_radius=8)
            frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
            ctk.CTkLabel(
                frame,
                text=f"{key}: {value}",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color="#E0E0E0"
            ).pack(side="left", padx=10)

        # Performance Metrics Header
        performance_row = (len(processing_stats) // 2) + 2
        ctk.CTkLabel(
            self,
            text="Performance Metrics",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#E0E0E0"
        ).grid(row=performance_row, column=0, columnspan=2, pady=(15, 5), padx=20, sticky="w")

        # Performance Metrics Data
        performance_metrics = {
            "Average Time per PDF": "3.2s",
            "Estimated Time Saved": "6.1 minutes",
            "Streak (days processing)": 3
        }

        for idx, (key, value) in enumerate(performance_metrics.items()):
            col = idx % 2
            row = performance_row + 1 + (idx // 2)
            frame = ctk.CTkFrame(self, fg_color="#2f2f2f", corner_radius=8)
            frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
            ctk.CTkLabel(
                frame,
                text=f"{key}: {value}",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color="#E0E0E0"
            ).pack(side="left", padx=10)


if __name__ == "__main__":
    app = AegisApp()
    app.mainloop()