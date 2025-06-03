import os
import customtkinter as ctk
import tkinter.filedialog as fd
from tkinterdnd2 import TkinterDnD, DND_FILES # Ensure TkinterDnD is imported correctly

# Set default appearance and theme
ctk.set_appearance_mode("System") # Options: "System", "Light", "Dark"
ctk.set_default_color_theme("blue") # Options: "blue", "green", "dark-blue"

class AegisApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        # --- TkinterDnD Initialization ---
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
        self.app_frame = ctk.CTkFrame(self)
        self.app_frame.pack(fill="both", expand=True)
        self.app_frame.grid_columnconfigure(0, weight=0)
        self.app_frame.grid_columnconfigure(1, weight=1)
        self.app_frame.grid_rowconfigure(0, weight=1)
        self.app_frame.grid_rowconfigure(1, weight=0)

        # Initialize UI components in the CTkFrame
        self.sidebar = Sidebar(self.app_frame)
        self.sidebar.grid(row=0, column=0, sticky="nswe", padx=10, pady=(10, 0))

        self.settings_sidebar = SettingsSidebar(self.app_frame)
        self.settings_sidebar.grid(row=1, column=0, sticky="nswe", padx=10, pady=(0, 10))

        self.main_content = MainContent(self.app_frame)
        self.main_content.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)

        # Enable drag-and-drop on the main app window (or specific widgets if preferred)
        # The DND_FILES type means it will accept file drops.
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)

    def handle_drop(self, event):
        # Use self.tk.splitlist to correctly parse the dropped file paths.
        # event.data is a string containing a Tcl-formatted list of file paths.
        try:
            files = self.tk.splitlist(event.data)
            pdf_files = [f for f in files if f.lower().endswith('.pdf')]
            if pdf_files:
                # Pass the actual list of PDF file paths
                self.main_content.process_page.handle_dropped_files(pdf_files)
            else:
                # Optionally provide feedback if non-PDFs are dropped
                self.main_content.process_page.update_status_label("Only PDF files are accepted via drag & drop.")

        except Exception as e:
            print(f"Error handling drop: {e}")
            if hasattr(self.main_content, 'process_page') and self.main_content.process_page:
                self.main_content.process_page.update_status_label("Error processing dropped files.")


class Sidebar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, width=200, corner_radius=10, fg_color="#2b2b2b") # Darker sidebar
        self.grid_propagate(False) # Prevent resizing based on content
        self.grid_rowconfigure(5, weight=1) # Push button to bottom if needed / Add empty space

        ctk.CTkLabel(
            self,
            text="Aegis Menu",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold")
        ).grid(row=0, column=0, pady=(20, 10), padx=20, sticky="w")

        buttons = [
            ("📁 Process Files", lambda: master.main_content.show_page("process")),
            ("🔐 Virtual Agents", lambda: master.main_content.show_page("credentials")),
            ("📊 Statistics", lambda: master.main_content.show_page("stats"))
        ]
        for idx, (text, command) in enumerate(buttons, start=1):
            ctk.CTkButton(
                self,
                text=text,
                command=command,
                height=40,
                font=ctk.CTkFont(size=14),
                corner_radius=8,
                fg_color="#3a3a3a",
                hover_color="#4a4a4a"
            ).grid(row=idx, column=0, pady=5, padx=20, sticky="ew")

class SettingsSidebar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, width=200, corner_radius=10, fg_color="#2b2b2b")
        self.grid_propagate(False)
        self.grid_rowconfigure(3, weight=1) # Pushes content up

        ctk.CTkLabel(
            self,
            text="Settings",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold")
        ).grid(row=0, column=0, pady=(20, 10), padx=10, sticky="w")

        ctk.CTkLabel(
            self,
            text="Theme",
            font=ctk.CTkFont(size=14)
        ).grid(row=1, column=0, pady=(10, 5), padx=10, sticky="w")

        self.theme_menu = ctk.CTkOptionMenu(
            self,
            values=["System", "Light", "Dark"],
            command=self.change_theme,
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=12),
            corner_radius=8
        )
        self.theme_menu.grid(row=2, column=0, pady=5, padx=10, sticky="ew")
        self.theme_menu.set(ctk.get_appearance_mode()) # Set current mode

    def change_theme(self, new_mode: str):
        ctk.set_appearance_mode(new_mode)

class MainContent(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=10, fg_color="transparent") # Transparent bg
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.pages = {}

        # Instantiate pages and store them
        self.process_page = ProcessPage(self)
        self.credentials_page = CredentialsPage(self)
        self.stats_page = StatsPage(self)

        self.pages = {
            "process": self.process_page,
            "credentials": self.credentials_page,
            "stats": self.stats_page
        }

        for page_name, page_widget in self.pages.items():
            page_widget.grid(row=0, column=0, sticky="nsew") # Add all pages initially
            if page_name != "process": # Then hide non-default pages
                page_widget.grid_remove()

        self.current_page = "process" # Keep track of the current page

    def show_page(self, page_name_to_show: str):
        if page_name_to_show in self.pages:
            self.pages[self.current_page].grid_remove() # Hide current page
            self.pages[page_name_to_show].grid() # Show new page
            self.current_page = page_name_to_show
        else:
            print(f"Error: Page '{page_name_to_show}' not found.")


class ProcessPage(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, label_text="Process PDFs", label_font=ctk.CTkFont(size=16, weight="bold"))
        self.grid_columnconfigure(0, weight=1)
        self.selected_files = [] # To store paths of selected/dropped files

        # --- Profile selection for processing ---
        ctk.CTkLabel(
            self,
            text="Select Virtual Agent Profile:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(10, 2), sticky="w")
        self.profile_values = ["Custom", "Marco's VA", "Admin VA"]
        self.selected_profile = ctk.StringVar(value="Custom")
        self.profile_menu = ctk.CTkOptionMenu(
            self,
            variable=self.selected_profile,
            values=self.profile_values,
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=12),
            corner_radius=8
        )
        self.profile_menu.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        # File drop/info area
        self.file_info_label = ctk.CTkLabel(
            self,
            text="Drop PDFs here or click to browse",
            height=150,
            fg_color=("gray75", "gray25"), # Light/Dark mode colors
            text_color=("gray10", "gray90"),
            font=ctk.CTkFont(size=14),
            corner_radius=10
        )
        self.file_info_label.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        self.file_info_label.bind("<Button-1>", self.browse_files) # Make label clickable

        # Browse button
        ctk.CTkButton(
            self,
            text="📂 Browse Files",
            command=self.browse_files,
            height=40,
            font=ctk.CTkFont(size=14),
            corner_radius=8
        ).grid(row=3, column=0, pady=10, padx=20, sticky="ew")

        # Checkbox for opening Excel
        self.open_excel_var = ctk.BooleanVar()
        ctk.CTkCheckBox(
            self,
            text="Open Excel after processing",
            variable=self.open_excel_var,
            font=ctk.CTkFont(size=12)
        ).grid(row=4, column=0, pady=10, padx=20, sticky="w")

        # Start button
        ctk.CTkButton(
            self,
            text="🚀 Start Processing",
            command=self.start_processing,
            height=40,
            font=ctk.CTkFont(size=14),
            corner_radius=8
        ).grid(row=5, column=0, pady=20, padx=20, sticky="ew")

        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="Status: Idle",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=6, column=0, padx=20, pady=10, sticky="w")

    def browse_files(self, event=None):
        file_paths = fd.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF Files", "*.pdf"), ("All files", "*.*")]
        )
        if file_paths:
            self.selected_files = list(file_paths) # Store as a list
            self.update_file_display_label()
            self.update_status_label(f"{len(self.selected_files)} file(s) selected. Ready to process!")

    def handle_dropped_files(self, file_paths: list):
        self.selected_files = file_paths
        self.update_file_display_label()
        self.update_status_label(f"{len(self.selected_files)} file(s) dropped. Ready to process!")

    def update_file_display_label(self):
        if self.selected_files:
            if len(self.selected_files) == 1:
                # Show filename if only one file, or just the count
                filename = os.path.basename(self.selected_files[0])
                self.file_info_label.configure(text=f"Selected: {filename}")
            else:
                self.file_info_label.configure(text=f"{len(self.selected_files)} PDF files selected.")
        else:
            self.file_info_label.configure(text="Drop PDFs here or click to browse")

    def update_status_label(self, message: str):
        self.status_label.configure(text=f"Status: {message}")

    def start_processing(self):
        if not self.selected_files:
            self.update_status_label("No files selected to process!")
            return
        selected_profile = self.selected_profile.get()
        self.update_status_label(f"Processing {len(self.selected_files)} file(s) with profile: {selected_profile}...")
        # --- Placeholder for actual processing logic ---
        print(f"Processing files: {self.selected_files}")
        print(f"Selected profile: {selected_profile}")
        print(f"Open Excel after processing: {self.open_excel_var.get()}")
        # Simulate processing
        self.after(2000, self.on_processing_complete)

    def on_processing_complete(self):
        self.update_status_label("✅ Processing complete!")
        # self.selected_files = [] # Optionally clear selection
        # self.update_file_display_label() # Update display if cleared


class CredentialsPage(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, label_text="Manage Virtual Agent Credentials", label_font=ctk.CTkFont(size=16, weight="bold"))
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Select Profile:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, pady=(10, 5), padx=20, sticky="w")

        # Profile values: 'Custom' for manual entry, others for saved profiles
        self.profile_values = ["Custom", "Marco's VA", "Admin VA"]
        self.profile_menu = ctk.CTkOptionMenu(
            self,
            values=self.profile_values,
            command=self.on_profile_select,
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=12),
            corner_radius=8
        )
        self.profile_menu.grid(row=1, column=0, pady=5, padx=20, sticky="ew")
        self.profile_menu.set("Custom")

        # Profile inputs - store them as instance attributes to access their values
        self.entry_profile_name = ctk.CTkEntry(
            self,
            placeholder_text="Profile Name (e.g., Marco's VA)",
            font=ctk.CTkFont(size=12)
        )
        self.entry_profile_name.grid(row=2, column=0, pady=5, padx=20, sticky="ew")

        self.entry_username = ctk.CTkEntry(
            self,
            placeholder_text="Username",
            font=ctk.CTkFont(size=12)
        )
        self.entry_username.grid(row=3, column=0, pady=5, padx=20, sticky="ew")

        self.entry_password = ctk.CTkEntry(
            self,
            placeholder_text="Password",
            show="*",
            font=ctk.CTkFont(size=12)
        )
        self.entry_password.grid(row=4, column=0, pady=5, padx=20, sticky="ew")

        # Save credentials checkbox
        self.remember_var = ctk.BooleanVar()
        ctk.CTkCheckBox(
            self,
            text="Save credentials securely (placeholder)",
            variable=self.remember_var,
            font=ctk.CTkFont(size=12)
        ).grid(row=5, column=0, pady=10, padx=20, sticky="w")

        ctk.CTkButton(
            self,
            text="💾 Save Credentials",
            command=self.save_credentials,
            height=40,
            font=ctk.CTkFont(size=14),
            corner_radius=8
        ).grid(row=6, column=0, pady=10, padx=20, sticky="ew")

    def on_profile_select(self, selected_profile: str):
        if selected_profile == "Custom":
            self.entry_profile_name.configure(state="normal")
            self.entry_username.configure(state="normal")
            self.entry_password.configure(state="normal")
            self.entry_profile_name.delete(0, 'end')
            self.entry_username.delete(0, 'end')
            self.entry_password.delete(0, 'end')
        else:
            # Example: fill with dummy data, disable editing
            self.entry_profile_name.configure(state="normal")
            self.entry_username.configure(state="normal")
            self.entry_password.configure(state="normal")
            self.entry_profile_name.delete(0, 'end')
            self.entry_profile_name.insert(0, selected_profile)
            self.entry_profile_name.configure(state="disabled")
            self.entry_username.delete(0, 'end')
            self.entry_username.insert(0, f"{selected_profile.split()[0].lower()}_user")
            self.entry_username.configure(state="disabled")
            self.entry_password.delete(0, 'end')
            self.entry_password.insert(0, "dummyPassword")
            self.entry_password.configure(state="disabled")

    def save_credentials(self):
        profile_name = self.entry_profile_name.get()
        username = self.entry_username.get()
        password = self.entry_password.get() # Remember to handle securely!
        remember = self.remember_var.get()

        if not profile_name or not username: # Basic validation
            print("Profile Name and Username are required.")
            return

        print(f"Saving Credentials for Profile: {profile_name}")
        print(f"  Username: {username}")
        print(f"  Password: {'*' * len(password) if password else '(empty)'}")
        print(f"  Save Securely: {remember}")
        # Add to profile_values if new and not 'Custom'
        if profile_name not in self.profile_values and profile_name != "Custom":
            self.profile_values.append(profile_name)
            self.profile_menu.configure(values=self.profile_values)
        if profile_name != "Custom":
            self.profile_menu.set(profile_name)
        else:
            self.profile_menu.set("Custom")


class StatsPage(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, label_text="📊 Aegis Statistics", label_font=ctk.CTkFont(size=16, weight="bold"))
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="🎉 Performance Metrics (Sample Data)",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold")
        ).grid(row=0, column=0, pady=10, padx=20, sticky="w")

        # Sample statistics data
        self.stats_data = {
            "PDFs Processed": 128,
            "IDs Retrieved": 114,
            "Average Time per PDF": "3.2s",
            "Estimated Time Saved": "6.1 minutes",
            "Successful Runs": 56,
            "Failed Runs": 2,
            "Streak (days processing)": 3
        }
        for idx, (key, value) in enumerate(self.stats_data.items(), start=1):
            ctk.CTkLabel(
                self,
                text=f"{key}: {value}",
                anchor="w", # Aligns text to the west (left)
                font=ctk.CTkFont(size=14)
            ).grid(row=idx, column=0, padx=20, pady=5, sticky="ew")

if __name__ == "__main__":
    app = AegisApp()
    app.mainloop()