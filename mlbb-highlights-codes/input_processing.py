from server.utils.getModel import get_model, get_lrcn_model, get_yolo_model
from server.utils.mainUtils import see_progressBar, detect_teamfight, detect_banner, extract_initial_highlights
from client.utils.MssgBox import MessageBox
import shared_state
import os

from dataclasses import dataclass
@dataclass
class HighlightClip:
    start_time: float
    end_time: float
    banners: list
    priority: int


def InputProcess(file_path=None, sort_type=None, parent_window=None, callback=None):

    progress = see_progressBar(parent_window, "Initializing...", 'Initalization Process')

    if progress: 
        try:
            progress.update_progress(0.50, "Loading models...")  
        except:
            pass  

    lrcn_model = get_lrcn_model()
    yolo_model = get_yolo_model()
    if lrcn_model is None or yolo_model is None:
        MessageBox.show_error("Error", "Failed to load models. Please check the model paths.")
        return


    if not os.path.exists(file_path):
        print(f"Video file not found: {file_path}")
        MessageBox.show_error("Error", f"Video file not found: {file_path}")
        return
    
    if progress: 
        try:
            progress.update_progress(0.80, "Preparing video...")  
        except:
            pass  

    input_video_path = file_path
    output_path = f'highlight_clips/{os.path.basename(file_path)}-{sort_type}_output'
    
    if progress: 
        try:
            progress.update_progress(0.1, "Preparing video...")
            progress.destroy()  
        except:
            pass  

    teamfights = detect_teamfight(parent_window, input_video_path, lrcn_model)

    results, mean_priority_score = detect_banner(parent_window, input_video_path, yolo_model, sort_type, teamfights)

    extract_initial_highlights(parent_window, input_video_path, output_path, results, mean_priority_score)
    
    shared_state.output_folder = output_path

    if callback and callable(callback):
        callback()

    return
    




