from tkinter import StringVar, filedialog
from tkinterdnd2 import TkinterDnD, DND_ALL
import customtkinter as ctk
from PIL import Image
import os

class Tk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class Dropzone(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.input_filepath = None

        self.valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.nameVar = StringVar()

        
        self.drop_frame = ctk.CTkFrame(self, width=500, height=250, 
                                corner_radius=20, fg_color="#F2F2F0",
                                border_width=1, border_color="#2B5D95")
        self.drop_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.drop_frame.grid_propagate(False)
        
        self.drop_frame.grid_rowconfigure(0, weight=1)
        self.drop_frame.grid_rowconfigure(1, weight=2)
        self.drop_frame.grid_columnconfigure(0, weight=1)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_icon = ctk.CTkImage(
            light_image=Image.open("client/assets/upload.png"),
            size=(20, 28))
        
       
        self.file_button = ctk.CTkButton(self.drop_frame, 
                                text="  Choose Video",
                                font=("Poppins Medium", 25),
                                corner_radius=10, 
                                fg_color="#FAF9F6", 
                                text_color="#0A2749",
                                border_width=1,
                                border_color="#2B5D95",
                                hover_color="#E6E6E6",
                                command=self.choose_file,
                                width=200, height=40)
        
        self.file_button.configure(image=file_icon, compound="left")    
        self.file_button.grid(row=0, column=0, pady=(40, 10))

        self.instruction_label = ctk.CTkLabel(
            self.drop_frame, 
            text="Insert raw clip of your game play\nto be summarized here!", 
            font=("Poppins Medium", 15),
            text_color="#0A2749")
        self.instruction_label.grid(row=1, column=0, pady=(0, 40))

        self.drop_frame.drop_target_register(DND_ALL)
        self.drop_frame.dnd_bind("<<Drop>>", self.get_path)


    def choose_file(self):
        filetypes = [("Video Files", "*.mp4 *.avi *.mov *.mkv *.wmv")]
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            if self.is_valid_video(filepath):
                self.nameVar.set(filepath)
                self.instruction_label.configure(text=os.path.basename(filepath))
                self.update_dropzone_status(True)
                self.input_filepath = filepath  
            else:
                self.instruction_label.configure(
                    text="Invalid file type. Please select a video file (MP4, AVI, MOV, MKV, WMV).",
                    text_color="#FF0000")
                self.update_dropzone_status(False)

    def get_path(self, event):
        filepath = event.data.strip('{}')
        if self.is_valid_video(filepath):
            self.nameVar.set(filepath)
            self.instruction_label.configure(text=filepath)
            self.update_dropzone_status(True)
            self.input_filepath = filepath 
        else:
            self.instruction_label.configure(
                text="Invalid file type. Please select a video file\n(MP4, AVI, MOV, MKV, WMV).",
                text_color="#FF0000")
            self.update_dropzone_status(False)
    
    def get_current_path(self):
        if self.input_filepath and os.path.exists(self.input_filepath):
            return self.input_filepath
        return None

    def is_valid_video(self, filepath):
        _, extension = os.path.splitext(filepath)
        return extension.lower() in self.valid_extensions
    
    def update_dropzone_status(self, valid):
        if valid:
            self.drop_frame.configure(border_color="#2B5D95")
            self.instruction_label.configure(text_color="#0A2749")
        else:
            self.drop_frame.configure(border_color="#FF0000")
            self.after(2000, self.reset_dropzone)
    
    def reset_dropzone(self):
        self.drop_frame.configure(border_color="#2B5D95")
        self.instruction_label.configure(
            text="Insert raw clip of your game play\nto be summarized here!", 
            text_color="#0A2749")
        self.input_filepath = None  