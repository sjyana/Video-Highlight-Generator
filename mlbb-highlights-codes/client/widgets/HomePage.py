import customtkinter as ctk
import os
from PIL import Image, ImageTk
from client.utils.InsertFile import Tk
from client.utils.InsertFile import Dropzone
from client.widgets.Generate import Generate

ctk.set_appearance_mode("light")

class Header(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.logo = ctk.CTkImage(light_image=Image.open('client/assets/logo.png'), size=(409,255))

        self.image = ctk.CTkLabel(self, text="", image = self.logo)
        self.image.grid(row=0, column=0, padx=20, pady=(15,0))

        self.title = ctk.CTkLabel(self,  text="HIGHLIGHT GENERATOR", 
                                        font=('Poppins SemiBold', 30), 
                                        text_color='#0A2749',
                                        bg_color="transparent")
        self.title.grid(row=1, column=0, padx=20)


class App(Tk):
    def __init__(self):
        super().__init__()

        self.title("MLBB Highlight Generator") 
        self.iconpath = ImageTk.PhotoImage(file=os.path.join("client/assets/miniicon.png"))
        self.wm_iconbitmap()
        self.iconphoto(False, self.iconpath)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.minsize(800, 700)

        x = (screen_width // 2) - (600 // 2) 
        y = (screen_height // 2) - (775 // 2) 
        self.geometry(f"800x700+{x}+{y}")


        self.header_frame = Header(master=self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20,0))

        self.file_frame = Dropzone(self, fg_color="transparent")
        self.file_frame.grid(row=1, column=0, padx=20)

        self.generate_frame = Generate(self, fg_color="transparent")
        self.generate_frame.grid(row=2, column=0, padx=20, pady=(0,20))
