import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD

class SimpleDnDApp(TkinterDnD.Tk): # Inherit from TkinterDnD.Tk
    def __init__(self):
        super().__init__()
        self.title("Drag and Drop Test")
        self.geometry("400x250")

        self.label = tk.Label(self, text="Drag files onto this window!", relief="solid", bd=2, padx=10, pady=10)
        self.label.pack(expand=True, fill="both", padx=20, pady=20)

        # Register this window as a drop target for files
        try:
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self.on_drop)
            self.label.config(text="Drag files onto this window! (DnD Ready)")
        except Exception as e:
            self.label.config(text=f"Error initializing DnD: {e}")
            print(f"Error initializing DnD: {e}")


    def on_drop(self, event):
        # event.data contains the path(s) of the dropped file(s)
        # On Windows, it's typically a string like "{C:/path/to/file1} {C:/path/to/file2}"
        # On Linux/macOS, it might be space-separated or a list-like string

        dropped_paths = event.data.strip()
        # Handle multiple files in case of spaces in paths
        if dropped_paths.startswith('{') and dropped_paths.endswith('}'):
            # This is a common format for multiple paths with spaces on Windows
            files = [p.strip('{}') for p in dropped_paths.split('} {')]
        else:
            files = [dropped_paths] # Assume a single path or space-separated without braces

        print("Dropped files:")
        for f in files:
            print(f"-", f)

        self.label.config(text=f"Dropped:\n{', '.join([file.split('/')[-1] for file in files])}")
        tk.messagebox.showinfo("Files Dropped", f"Successfully dropped:\n{', '.join(files)}")

if __name__ == "__main__":
    app = SimpleDnDApp()
    app.mainloop()