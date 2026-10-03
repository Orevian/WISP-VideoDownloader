import os
import re
import math
from PySide6.QtCore import QThread, Signal
import yt_dlp

class MetadataWorker(QThread):
    """
    Worker thread that quickly loads specific video information/metadata 
    to populate quality selectors and direct-download cards dynamically.
    """
    metadata_loaded = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        ydl_opts = {
            'skip_download': True,
            'quiet': True,
            'no_warnings': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                if not info:
                    raise Exception("Could not extract video metadata.")
                
                self.metadata_loaded.emit(info)
        except Exception as e:
            self.error_occurred.emit(str(e))


class DownloadWorker(QThread):
    """
    Worker running the download task, communicating percentages, 
    speeds, ETA, and progress status updates back to the UI.
    """
    progress_changed = Signal(dict)
    status_changed = Signal(str)
    download_finished = Signal(str)
    download_error = Signal(str)

    def __init__(self, url, output_dir, format_choice):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.format_choice = format_choice # 'MP4_4K', 'MP4_1080P', 'MP4_720P', 'MP3_AUDIO'

    def run(self):
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir, exist_ok=True)
            except Exception as e:
                self.download_error.emit(f"Failed to create directory: {str(e)}")
                return

        # Build proper output template
        out_tmpl = os.path.join(self.output_dir, '%(title)s.%(ext)s')

        # Configure formats for high-end outputs (4K/60fps demands video + audio merging)
        # Note: Merging formats requires ffmpeg installed on the host system.
        if self.format_choice == 'MP4_4K':
            # Target 2160p with fallback, then merge best audio
            format_str = 'bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=2160]+bestaudio/best'
            post_processors = []
        elif self.format_choice == 'MP4_1080P':
            format_str = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best'
            post_processors = []
        elif self.format_choice == 'MP4_720P':
            format_str = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best'
            post_processors = []
        elif self.format_choice == 'MP3_AUDIO':
            format_str = 'bestaudio/best'
            post_processors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }]
        else:
            format_str = 'best'
            post_processors = []

        ydl_opts = {
            'format': format_str,
            'outtmpl': out_tmpl,
            'progress_hooks': [self.progress_hook],
            'postprocessors': post_processors,
            'quiet': True,
            'no_warnings': True,
            # If ffmpeg is present, attempt seamless merge to standard MP4
            'merge_output_format': 'mp4' if self.format_choice != 'MP3_AUDIO' else None
        }

        try:
            self.status_changed.emit("Contacting server and starting stream...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.download_finished.emit("Stream processed and saved successfully!")
        except Exception as e:
            self.download_error.emit(str(e))

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            speed = d.get('speed', 0)
            eta = d.get('eta', 0)

            # Clean styling conversions
            if total > 0:
                percent = (downloaded / total) * 100
            else:
                percent = 0

            # Convert Bytes to MBs
            total_mb = total / (1024 * 1024)
            downloaded_mb = downloaded / (1024 * 1024)
            
            # Format speed
            if speed and speed > 1024 * 1024:
                speed_str = f"{speed / (1024 * 1024):.2f} MB/s"
            elif speed:
                speed_str = f"{speed / 1024:.2f} KB/s"
            else:
                speed_str = "Calculating..."

            # Format ETA
            if eta:
                minutes = int(eta // 60)
                seconds = int(eta % 60)
                eta_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
            else:
                eta_str = "N/A"

            progress_data = {
                'percent': percent,
                'total_size': f"{total_mb:.2f} MB" if total else "Unknown Size",
                'downloaded': f"{downloaded_mb:.2f} MB",
                'speed': speed_str,
                'eta': eta_str
            }
            self.progress_changed.emit(progress_data)
        elif d['status'] == 'finished':
            self.status_changed.emit("Processing format/Merging audio & video channels...")