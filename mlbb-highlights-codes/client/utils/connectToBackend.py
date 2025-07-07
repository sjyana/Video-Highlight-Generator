from client.utils.MssgBox import MessageBox
from input_processing import InputProcess
from client.widgets.EditClips import EditClips
import customtkinter as ctk  

class ConnectToServer(ctk.CTkToplevel):  
    def __init__(self, master, sort_type, **kwargs):
        super().__init__(master, **kwargs)  
        
        self.master = master
        self.parent_window = master 
        
        if not hasattr(self.parent_window, 'file_frame'):
            MessageBox.show_error("Error",
                "Could not access the file upload area. Parent window structure might be incorrect.")
            return

        try:
            file_path = self.parent_window.file_frame.get_current_path()

            if not file_path:
                MessageBox.show_error("No File Selected",
                    "Please select a file to upload first.")
                return
            
            self.withdraw()
            
            self.editclips = None
            def on_processing_complete(result=None):
                self.parent_window.withdraw()
                if hasattr(self.master, 'file_frame'):
                    if self.editclips is None or not self.editclips.winfo_exists():
                        self.editclips = EditClips(self.master) 
                        self.editclips.grab_set()
                        self.editclips.focus()
                    else:
                        self.editclips.focus()
            
            InputProcess(file_path, sort_type, parent_window=self.parent_window, 
                        callback=on_processing_complete)
            
        except Exception as e:
            MessageBox.show_error("Error",
                f"Could not access file path: {str(e)}")

def connectToServer(parent_window, sort_type):
    if not hasattr(parent_window, 'file_frame'):
        MessageBox.show_error("Error",
            "Could not access the file upload area. Parent window structure might be incorrect.")
        return

    try:
        file_path = parent_window.file_frame.get_current_path()

        if not file_path:
            MessageBox.show_error("No File Selected",
                "Please select a file to upload first.")
            return
        
        if hasattr(parent_window, 'withdraw'):
            parent_window.withdraw()
        
        def on_processing_complete(result=None):
            if hasattr(parent_window, 'master'):
                master = parent_window.master
                editclips = EditClips(master)
                if hasattr(editclips, 'grab_set'):
                    editclips.grab_set()
                editclips.focus()
        
        InputProcess(file_path, sort_type, parent_window=parent_window, 
                    callback=on_processing_complete)
        
    except Exception as e:
        MessageBox.show_error("Error",
            f"Could not access file path: {str(e)}")