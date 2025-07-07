import customtkinter as ctk
import tkinter as tk
import cv2
import os
from PIL import Image, ImageTk
from tkinter import filedialog
import shutil
from moviepy import VideoFileClip, concatenate_videoclips
import threading
import time
import shared_state
from client.utils.MssgBox import MessageBox

ctk.set_appearance_mode("light")

class EditClips(ctk.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        print('Edit Clips widget')
        output_folder = shared_state.output_folder
        print(f"Output path: {output_folder}")
        if not output_folder:
            raise RuntimeError("Output path not set. Please run the video processing first.")
        
        self.title("Video Editor")
        self.iconpath = tk.PhotoImage(file=os.path.join("client/assets/miniicon.png"))
        self.iconphoto(False, self.iconpath)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.minsize(800, 700)

        x = (screen_width // 2) - (800 // 2) 
        y = (screen_height // 2) - (700 // 2) 
        self.geometry(f"800x700+{x}+{y}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.video_folder = ""
        self.video_files = []
        self.current_video_index = 0
        self.videos_to_keep = []
        self.videos_to_delete = []
        
        self.cap = None
        self.is_playing = False
        self.playback_thread = None
        self.frame_rate = 30
        self.playback_speed = 1.0
        self.current_frame = 0
        self.total_frames = 0
        self.should_stop = False
        
        self.playback_lock = threading.RLock()
        
        self.title_label = ctk.CTkLabel(self, text="Edit Clips", font=('Poppins SemiBold', 30), 
                                  text_color='#0A2749', bg_color="transparent")
        self.title_label.grid(row=0, column=0, pady=(30, 0), sticky="ew")

        self.desc = ctk.CTkLabel(self, text="Select video clips to keep or delete.", font=('Poppins Regular', 20), 
                                 text_color='#0A2749',bg_color="transparent")
        self.desc.grid(row=1, column=0, sticky="ew")
        
        self.video_nav = ctk.CTkFrame(self, fg_color="transparent")
        self.video_nav.grid(row=2, column=0, sticky="nsew")
        self.video_nav.grid_columnconfigure(0, weight=1)
        self.video_nav.grid_columnconfigure(1, weight=3)
        self.video_nav.grid_columnconfigure(2, weight=1)
        self.video_nav.grid_rowconfigure(0, weight=1)

        left = ctk.CTkImage(Image.open("client/assets/LeftArrow.png"), size=(15, 25))
        self.left_arrow = ctk.CTkButton(self.video_nav, image=left, text="", fg_color="transparent",
                                      corner_radius=30, hover_color="#E6F0FF", width=60, height=60,
                                      command=self.previous_video, state="disabled")
        self.left_arrow.grid(row=0, column=0, padx=10, sticky="e")
        
        self.video_frame = ctk.CTkFrame(self.video_nav, fg_color="transparent")
        self.video_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.video_frame.grid_columnconfigure(0, weight=1)
        self.video_frame.grid_rowconfigure(0, weight=1)
        self.video_frame.grid_rowconfigure(1, weight=0)

        self.video_label = tk.Label(self.video_frame, bg="#F0F0F0")
        self.video_label.grid(row=0, column=0, sticky="nsew")
        
        self.control_frame = ctk.CTkFrame(self.video_frame, fg_color="#F0F0F0")
        self.control_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        
        self.control_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.play_button = ctk.CTkButton(self.control_frame, text="▶️", width=40, height=30,
                                       corner_radius=5, fg_color="#2B5D95", text_color="#FFFFFF",
                                       command=self.toggle_play)
        self.play_button.grid(row=0, column=1, padx=5)
        
        self.speed_button = ctk.CTkButton(self.control_frame, text="1.0x", width=40, height=30,
                                        corner_radius=5, fg_color="#2B5D95", text_color="#FFFFFF",
                                        command=self.change_speed)
        self.speed_button.grid(row=0, column=2, padx=5)
        
        self.restart_button = ctk.CTkButton(self.control_frame, text="⟲", width=40, height=30,
                                          corner_radius=5, fg_color="#2B5D95", text_color="#FFFFFF",
                                          command=self.restart_video)
        self.restart_button.grid(row=0, column=0, padx=5)

        right = ctk.CTkImage(Image.open("client/assets/RightArrow.png"), size=(15, 25))
        self.right_arrow = ctk.CTkButton(self.video_nav, image=right, text="", fg_color="transparent",
                                       corner_radius=30, hover_color="#E6F0FF", width=60, height=60,
                                       command=self.next_video, state="disabled")
        self.right_arrow.grid(row=0, column=2, padx=10, sticky="w")

        self.status_bar = ctk.CTkLabel(self, text="Initializing...", 
                                     height=25, font=("Poppins Regular", 13))
        self.status_bar.grid(row=3, column=0, sticky="ew", pady=(5, 0))
        
        self.counter_label = ctk.CTkLabel(self, text="", height=25, 
                                        font=("Poppins Medium", 14), text_color="#2B5D95")
        self.counter_label.grid(row=4, column=0, sticky="ew", pady=(5, 0))
        
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=5, column=0, pady=(20, 30), sticky="ew")
        
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=0)
        self.button_frame.grid_columnconfigure(2, weight=0)
        self.button_frame.grid_columnconfigure(3, weight=1)

        self.button_delete = ctk.CTkButton(self.button_frame, text="Delete Clip", corner_radius=10, fg_color="#FAF9F6", 
                                           text_color="#0A2749", font=("Poppins Medium", 15), border_width=1, border_color="#2B5D95",
                                           hover_color="#E6E6E6", width=200, height=40, command=self.delete_clip)
        self.button_delete.grid(row=0, column=1, padx=20)

        self.button_keep = ctk.CTkButton(self.button_frame, text="Keep Clip", corner_radius=10, 
                                       fg_color="#CAA45D", text_color="#FAF9F6", 
                                       font=("Poppins Medium", 15), hover_color="#CC922F",
                                       width=200, height=40, command=self.keep_clip)
        self.button_keep.grid(row=0, column=2, padx=20)
        
        self.button_concatenate = ctk.CTkButton(self, text="Concatenate Selected Clips", 
                                             corner_radius=10, fg_color="#2B5D95", 
                                             text_color="#FAF9F6", font=("Poppins Medium", 15), 
                                             hover_color="#1A4980", width=300, height=40, 
                                             command=self.concatenate_clips, state="disabled")
        self.button_concatenate.grid(row=6, column=0, pady=(0, 20))
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        if output_folder:
            self.video_folder = output_folder
            self.load_videos_from_folder()
            return
        else:
            MessageBox.show_error("Error", "No generated highlight clips.")
            self.on_closing()
            return
    
    def load_videos_from_folder(self):
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
        
        self.video_files = []
        try:
            for file in os.listdir(self.video_folder):
                if any(file.lower().endswith(ext) for ext in video_extensions):
                    self.video_files.append(os.path.join(self.video_folder, file))
        except Exception as e:
            if MessageBox.show_error("Error", "No generated highlight clips."):
                self.on_closing()
        
        if not self.video_files:
            return
        
        self.videos_to_keep = [False] * len(self.video_files)
        self.videos_to_delete = [False] * len(self.video_files)
        
        self.current_video_index = 0
        self.load_current_video()
        
        self.status_bar.configure(text=f"Loaded {len(self.video_files)} videos from folder")
        self.update_counter_label()
    
    def load_current_video(self):
        if not self.video_files or self.current_video_index >= len(self.video_files):
            return
        
        video_path = self.video_files[self.current_video_index]
        
        try:
            self.stop_playback()
            
            with self.playback_lock:
                self.cap = cv2.VideoCapture(video_path)
                
                if not self.cap.isOpened():
                    raise Exception(f"Failed to open video file: {video_path}")
                
                width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                self.frame_rate = self.cap.get(cv2.CAP_PROP_FPS)
                self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.current_frame = 0
                
                if self.frame_rate <= 0:
                    self.frame_rate = 30  
            
            max_width = 700
            max_height = 550
            
            if width > max_width or height > max_height:
                width_ratio = max_width / width
                height_ratio = max_height / height
                scale_factor = min(width_ratio, height_ratio)
                
                self.display_width = int(width * scale_factor)
                self.display_height = int(height * scale_factor)
            else:
                self.display_width = width
                self.display_height = height
            
            self.video_label.config(width=self.display_width, height=self.display_height)
            
            ret, first_frame = self.cap.read()
            if ret:
                self.display_frame(first_frame)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            self.should_stop = False
            self.start_playback()
            
            self.play_button.configure(text="⏸️", state="normal")
            
            filename = os.path.basename(video_path)
            self.status_bar.configure(text=f"Playing: {filename}")
            
            self.update_button_state()
            
        except Exception as e:
            if MessageBox.show_error("Error", "No generated highlight clips."):
                self.on_closing()
            
    def display_frame(self, frame):
        if frame is None:
            return
            
        try:
            frame = cv2.resize(frame, (self.display_width, self.display_height))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image=image)
            
            self.video_label.config(image=photo)
            self.video_label.image = photo  
        except Exception as e:
            print(f"Error displaying frame: {e}")
        
    def playback_loop(self):
        while not self.should_stop:
            with self.playback_lock:
                if not self.is_playing or not self.cap or not self.cap.isOpened():
                    time.sleep(0.1)
                    continue
                    
                try:
                    ret, frame = self.cap.read()
                    
                    if not ret: 
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        self.current_frame = 0
                        continue
                        
                    self.current_frame += 1
                    
                    frame_copy = frame.copy()
                except Exception as e:
                    print(f"Error reading frame: {e}")
                    time.sleep(0.1)
                    continue
            
            self.display_frame(frame_copy)
            
            sleep_time = 1.0 / (self.frame_rate * self.playback_speed)
            time.sleep(max(0.001, sleep_time))  
            
    def start_playback(self):
        self.is_playing = True
        
        if self.playback_thread is None or not self.playback_thread.is_alive():
            self.should_stop = False
            self.playback_thread = threading.Thread(target=self.playback_loop)
            self.playback_thread.daemon = True
            self.playback_thread.start()
            
    def stop_playback(self):
        self.should_stop = True
        self.is_playing = False
        
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(1.0)
            
        with self.playback_lock:
            if self.cap and self.cap.isOpened():
                self.cap.release()
                
            self.cap = None
            self.playback_thread = None
        
    def toggle_play(self):
        if not self.cap:
            return
            
        if self.is_playing:
            self.is_playing = False
            self.play_button.configure(text="▶️")
        else:
            self.is_playing = True
            self.play_button.configure(text="⏸️")
            
    def restart_video(self):
        if not self.cap:
            return
        
        with self.playback_lock:
            if self.cap and self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.current_frame = 0
                
                ret, frame = self.cap.read()
                if ret:
                    self.display_frame(frame)
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
    def change_speed(self):
        speeds = [0.5, 1.0, 1.5, 2.0]
        
        current_index = speeds.index(self.playback_speed) if self.playback_speed in speeds else 0
        next_index = (current_index + 1) % len(speeds)
        self.playback_speed = speeds[next_index]
        
        self.speed_button.configure(text=f"{self.playback_speed}x")
    
    def next_video(self):
        if self.current_video_index < len(self.video_files) - 1:
            self.current_video_index += 1
            self.load_current_video()
            self.update_counter_label()
            self.update_button_state()
    
    def previous_video(self):
        if self.current_video_index > 0:
            self.current_video_index -= 1
            self.load_current_video()
            self.update_counter_label()
            self.update_button_state()
    
    def keep_clip(self):
        if self.video_files and 0 <= self.current_video_index < len(self.video_files):
            self.videos_to_keep[self.current_video_index] = True
            self.videos_to_delete[self.current_video_index] = False
            self.update_button_state()
            self.update_counter_label()
            self.left_arrow.configure(state="normal")
            self.right_arrow.configure(state="normal")

            self.button_keep.configure(fg_color="green", hover_color="green")
            self.button_delete.configure(fg_color="#FAF9F6", text_color="#0A2749")
            
            if self.current_video_index >= len(self.video_files) - 1:
                self.button_concatenate.configure(state="normal")
                MessageBox.show_checkmark("End of Videos", "You've reached the last video. You can now concatenate all selected clips.")
    
    def delete_clip(self):
        if self.video_files and 0 <= self.current_video_index < len(self.video_files):
            self.videos_to_keep[self.current_video_index] = False
            self.videos_to_delete[self.current_video_index] = True
            self.update_button_state()
            self.update_counter_label()
            self.left_arrow.configure(state="normal")
            self.right_arrow.configure(state="normal")
            
            if self.current_video_index >= len(self.video_files) - 1:
                self.button_concatenate.configure(state="normal")
                MessageBox.show_checkmark("End of Videos", "You've reached the last video. You can now concatenate all selected clips.")
    
    def update_button_state(self):
        if not self.video_files:
            return

        if self.videos_to_keep[self.current_video_index]:
            self.button_keep.configure(fg_color="green", hover_color="green")
            self.button_delete.configure(fg_color="#FAF9F6", hover_color="#E6E6E6", 
                                       text_color="#0A2749", border_width=1)
        elif self.videos_to_delete[self.current_video_index]:
            self.button_delete.configure(fg_color="red", hover_color="red", 
                                       text_color="#FAF9F6", border_width=0)
            self.button_keep.configure(fg_color="#CAA45D", hover_color="#CC922F")
        else:
            self.button_keep.configure(fg_color="#CAA45D", text_color="#FAF9F6")
            self.button_delete.configure(fg_color="#FAF9F6", text_color="#0A2749")
            self.left_arrow.configure(state="disabled")
            self.right_arrow.configure(state="disabled")
        
    
    def update_counter_label(self):
        if self.video_files:
            total_videos = len(self.video_files)
            selected_videos = sum(self.videos_to_keep)
            self.counter_label.configure(
                text=f"Video {self.current_video_index + 1} of {total_videos} | {selected_videos} clips selected for concatenation"
            )

    def concatenate_clips(self):
        """Concatenate all selected video clips into a single video file"""
        selected_videos = [self.video_files[i] for i in range(len(self.video_files)) if self.videos_to_keep[i]]
        
        if not selected_videos:
            MessageBox.show_error("No Clips Selected", "Please select at least one clip to concatenate.")
            return
        
        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
            title="Save Concatenated Video As"
        )
        
        if not output_path:
            return
        
        try:
            self.status_bar.configure(text="Concatenating videos... This may take a while.")
            self.update()
            
            clips = [VideoFileClip(video) for video in selected_videos]
            
            final_clip = concatenate_videoclips(clips)
            
            final_clip.write_videofile(output_path, codec="libx264")
            
            final_clip.close()
            for clip in clips:
                clip.close()
            
            self.status_bar.configure(text=f"Successfully saved concatenated video to: {output_path}")
            MessageBox.show_checkmark("Success", "Video clips have been successfully concatenated!")
            self.on_closing()
            
        except Exception as e:
            MessageBox.show_error("Error", f"An error occurred during concatenation: {str(e)}")
            self.status_bar.configure(text=f"Error during concatenation: {str(e)}")
  
    def on_closing(self):
        self.stop_playback()
        time.sleep(0.5)
        self.destroy()