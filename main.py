import tkinter as tk
from tkinter import messagebox, filedialog
from pytube import YouTube
from moviepy.editor import VideoFileClip
import os
import threading
import re

def parse_time(hours, minutes, seconds):
    """ Convert hours, minutes, and seconds to total seconds. """
    try:
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
    except ValueError:
        messagebox.showerror("Error", "Please enter valid integer values for hours, minutes, and seconds.")
        return None

def extract_start_time(link):
    """ Extract start time from YouTube video URL if provided. """
    match = re.search(r"&t=(\d+)", link)
    if match:
        seconds = int(match.group(1))
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return hours, minutes, seconds
    else:
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

def download_video(link, path):
    """ Download the video from YouTube and return the path and video length. """
    yt = YouTube(link)
    video = yt.streams.get_highest_resolution()
    video.download(output_path=path, filename='temp_video.mp4')
    return os.path.join(path, 'temp_video.mp4'), yt.length

def cut_video(video_path, start_cut, end_cut, output_path):
    """ Cut the specified portion from the video. """
    clip = VideoFileClip(video_path)
    cut_clip = clip.subclip(start_cut, end_cut)
    cut_clip.write_videofile(output_path, codec='libx264')
    clip.close()

def download_and_cut_video(link, start_hours, start_minutes, start_seconds, duration_seconds, output_path):
    if not link:
        messagebox.showerror("Error", "Please provide a valid YouTube video link.")
        return

    start_cut = parse_time(start_hours, start_minutes, start_seconds)
    if start_cut is None:
        return

    duration_seconds = int(duration_seconds)
    if duration_seconds <= 0:
        messagebox.showerror("Error", "Clip duration must be greater than zero.")
        return

    try:
        temp_path = filedialog.askdirectory(title="Select Download Folder")
        if not temp_path:
            return
        video_path, video_length = download_video(link, temp_path)
        end_cut = start_cut + duration_seconds
        
        if end_cut > video_length:
            messagebox.showerror("Error", "The selected clip duration exceeds the video length.")
            return

        output_filename = filedialog.asksaveasfilename(
            title="Save the cut video as",
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4")],
            initialfile="cut_video.mp4"
        )
        if not output_filename:
            return
        
        cut_video(video_path, start_cut, end_cut, output_filename)
        os.remove(video_path)
        messagebox.showinfo("Success", "Video has been cut and saved successfully.")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number for duration.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def submit():
    thread = threading.Thread(target=lambda: download_and_cut_video(
        url_entry.get(),
        start_hour_entry.get(),
        start_min_entry.get(),
        start_sec_entry.get(),
        duration_entry.get(),
        "cut_video.mp4"
    ))
    thread.start()

# Create the main window
root = tk.Tk()
root.title("Video Cutter")

# Create and pack the widgets
tk.Label(root, text="Video Link:").pack()
url_entry = tk.Entry(root, width=50)
url_entry.pack()
url_entry.bind("<FocusIn>", update_start_time)  # Bind the callback to URL entry focus
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
