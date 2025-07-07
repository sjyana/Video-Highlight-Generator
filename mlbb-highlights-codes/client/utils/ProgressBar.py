import customtkinter as ctk
from PIL import ImageTk
import os

class ProgressBar(ctk.CTkToplevel):
    def __init__(self, master, upload_text=None, **kwargs, ):
        super().__init__(master, **kwargs)
        
        self.title("Input Processing Progress")
        self.transient(master) 

        self.geometry("400x200")
        self.resizable(False, False)
        
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.winfo_width() // 2)
        y = (screen_height // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        self.iconpath = ImageTk.PhotoImage(file=os.path.join("client/assets/miniicon.png"))
        self.wm_iconbitmap()
        self.after(300, lambda: self.iconphoto(False, self.iconpath))
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        
        self.title_label = ctk.CTkLabel(
            self, 
            text=upload_text, 
            font=("Poppins Medium", 15),
            text_color="#0A2749"
        )
        self.title_label.grid(row=0, column=0, pady=(20, 10))
        
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=300,
            height=20,
            corner_radius=10,
            progress_color="#1F6AA5"
        )
        self.progress_bar.grid(row=1, column=0, pady=10)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            self,
            text="Starting upload...",
            text_color="#666666"
        )
        self.status_label.grid(row=2, column=0, pady=(10, 20))
        
        self.attributes('-topmost', True)
        self.after(100, lambda: self.attributes('-topmost', False))
    
    def update_progress(self, value, message=None):
        """Update progress bar and optionally status message"""
        self.progress_bar.set(value)
        if message:
            self.status_label.configure(text=message)
        self.update()