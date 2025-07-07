import customtkinter as ctk
from client.widgets.Popup import Popup

class Generate(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.master = master  
        
        self.button = ctk.CTkButton(
            self, 
            text="Generate", 
            text_color="#FAF9F6",
            font=("Poppins Medium", 25), 
            fg_color="#CAA45D",
            hover_color="#CC922F", 
            width=200, 
            height=40,
            command=self.click
        )
        self.button.pack(padx=20, pady=20)
        self.popup = None
    
    def click(self):
        if hasattr(self.master, 'file_frame') and self.master.file_frame.get_current_path():
            if self.popup is None or not self.popup.winfo_exists():
                self.popup = Popup(self.master) 
                self.popup.grab_set()
                self.popup.focus()
            else:
                self.popup.focus()
        else:
            from client.utils.MssgBox import MessageBox
            MessageBox.show_error("No File Selected", 
                "Please select a video file.")