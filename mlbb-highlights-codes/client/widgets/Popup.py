import customtkinter as ctk
from PIL import ImageTk
import os
from client.utils.connectToBackend import ConnectToServer

class Popup(ctk.CTkToplevel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent_window = parent

        self.title("Sort Options")

        self.iconpath = ImageTk.PhotoImage(file=os.path.join("client/assets/miniicon.png"))
        self.wm_iconbitmap()
        self.after(300, lambda: self.iconphoto(False, self.iconpath))

        self.resizable(False, False)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (200) 
        y = (screen_height // 2) - (150) 
        self.geometry(f"400x300+{x}+{y}")

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Choose output type:", font=("Poppins Medium", 15),
                                  text_color="#0A2749")
        self.title_label.grid(row=0, column=0)
        
        self.container_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.container_frame.grid(row=1, column=0)
        self.container_frame.grid_columnconfigure(0, weight=1)
        self.container_frame.grid_columnconfigure(1, weight=1)


        self.button1 = ctk.CTkButton(self.container_frame, text="Sort highlights\nchronologically.",
                                     font=("Poppins", 13), text_color="#0A2749", fg_color="transparent",
                                     border_color="#0A2749", border_width=1, hover_color="#E6E6E6", 
                                     command=lambda: self.connect_to_server("chronological"))
        self.button1.grid(row=0, column=0, padx=10)


        self.button2 = ctk.CTkButton(self.container_frame, text="Sort highlights by priority.\nex. Top 1-10",
                                     font=("Poppins", 13), text_color="#0A2749", fg_color="transparent",
                                     border_color="#0A2749", border_width=1, hover_color="#E6E6E6", 
                                     command=lambda: self.connect_to_server("priority"))
        self.button2.grid(row=0, column=1, padx=10)

    def connect_to_server(self, sort_type):
        self.withdraw()
        ConnectToServer(self.parent_window, sort_type)