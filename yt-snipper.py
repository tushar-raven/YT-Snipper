import tkinter as tk
from tkinter import messagebox, filedialog
from pytube import YouTube
import os
import threading
import subprocess
import re

def parse_time(hours, minutes, seconds):
    """ Convert hours, minutes, and seconds to total seconds, handling empty fields. """
    try:
        hours = int(hours) if hours.strip() else 0
        minutes = int(minutes) if minutes.strip() else 0
        seconds = int(seconds) if seconds.strip() else 0
        return hours * 3600 + minutes * 60 + seconds
    except ValueError:
        messagebox.showerror("Error", "Please enter valid integer values for hours, minutes, and seconds.")
        return None

def valid_int(s, default=0):
    """ Check if the string s is a valid integer, return default if empty. """
    try:
        return int(s) if s.strip() else default
    except ValueError:
        return None

def extract_start_time(link):
    """ Extract start time from YouTube video URL if provided. """
    match = re.search(r"t=(\d+)", link)
    if match:
        seconds = int(match.group(1))
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return str(hours), str(minutes), str(seconds)
    return '0', '0', '0'

def update_start_time(event=None):
    """ Update start time fields when URL changes. """
    start_hours, start_minutes, start_seconds = extract_start_time(url_entry.get())
    start_hour_entry.delete(0, tk.END)
    start_hour_entry.insert(0, start_hours)
    start_min_entry.delete(0, tk.END)
    start_min_entry.insert(0, start_minutes)
    start_sec_entry.delete(0, tk.END)
    start_sec_entry.insert(0, start_seconds)

def download_and_cut_video_ffmpeg(link, start_hours, start_minutes, start_seconds, duration_seconds, output_path):
    # Validate all inputs and handle empty inputs by setting defaults
    start_hours = valid_int(start_hours)
    start_minutes = valid_int(start_minutes)
    start_seconds = valid_int(start_seconds)
    duration_seconds = valid_int(duration_seconds)

    if None in (start_hours, start_minutes, start_seconds, duration_seconds):
        messagebox.showerror("Error", "Start time and duration must be integers.")
        return

    if duration_seconds <= 0:
        messagebox.showerror("Error", "Duration must be a positive integer.")
        return

    try:
        yt = YouTube(link)
        video_url = yt.streams.get_highest_resolution().url
        start_time = f"{start_hours * 3600 + start_minutes * 60 + start_seconds}"
        
        command = [
            'ffmpeg',
            '-y',  # Automatically overwrite existing files
            '-ss', start_time,  # Start time
            '-i', video_url,    # Input URL
            '-t', str(duration_seconds),  # Duration to cut
            '-c:v', 'libx264',  # Video codec
            '-c:a', 'aac',      # Audio codec
            '-strict', 'experimental',
            '-b:a', '192k',     # Audio bitrate
            output_path
        ]
        
        subprocess.run(command, check=True)
        messagebox.showinfo("Success", "Video has been cut and saved successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to cut video: {str(e)}")

def submit():
    output_filename = filedialog.asksaveasfilename(
        title="Save the cut video as",
        defaultextension=".mp4",
        filetypes=[("MP4 files", "*.mp4")],
        initialfile="cut_video.mp4"
    )
    if not output_filename:
        return
    
    thread = threading.Thread(target=lambda: download_and_cut_video_ffmpeg(
        url_entry.get(),
        start_hour_entry.get(),
        start_min_entry.get(),
        start_sec_entry.get(),
        duration_entry.get(),
        output_filename
    ))
    thread.start()

# Create the main window
root = tk.Tk()
root.title("Video Cutter")

# Create and pack the widgets
tk.Label(root, text="Video Link:").pack()
url_entry = tk.Entry(root, width=50)
url_entry.pack()
url_entry.bind("<FocusOut>", update_start_time)  # Bind the callback to URL entry focus
url_entry.bind("<KeyRelease>", update_start_time)  # Bind the callback to URL entry key release

start_hours, start_minutes, start_seconds = extract_start_time(url_entry.get())

tk.Label(root, text="Start Time (HH:MM:SS):").pack()
start_time_frame = tk.Frame(root)
start_time_frame.pack()
start_hour_entry = tk.Entry(start_time_frame, width=3)
start_hour_entry.pack(side=tk.LEFT)

tk.Label(start_time_frame, text=":").pack(side=tk.LEFT)
start_min_entry = tk.Entry(start_time_frame, width=3)
start_min_entry.pack(side=tk.LEFT)

tk.Label(start_time_frame, text=":").pack(side=tk.LEFT)
start_sec_entry = tk.Entry(start_time_frame, width=3)
start_sec_entry.pack(side=tk.LEFT)

tk.Label(root, text="Clip Duration (seconds):").pack()
duration_entry = tk.Entry(root, width=20)
duration_entry.pack()

submit_button = tk.Button(root, text="Download and Cut", command=submit)
submit_button.pack()

# Run the application
root.mainloop()
