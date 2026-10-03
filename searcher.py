import os
from PySide6.QtCore import QThread, Signal
import yt_dlp

class SearchWorker(QThread):
    """
    Search worker running on a secondary thread to prevent UI freezing
    while searching keywords on YouTube using yt-dlp.
    """
    results_found = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, query, limit=8):
        super().__init__()
        self.query = query
        self.limit = limit

    def run(self):
        # Prevent yt-dlp from attempting to download during flat extraction search
        ydl_opts = {
            'extract_flat': True,
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'playlist_items': f'1-{self.limit}'
        }
        
        try:
            # Check if input is empty
            if not self.query.strip():
                self.results_found.emit([])
                return
                
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Direct ytsearch setup
                search_query = f"ytsearch{self.limit}:{self.query}"
                search_results = ydl.extract_info(search_query, download=False)
                
                results_list = []
                if 'entries' in search_results:
                    for entry in search_results['entries']:
                        if not entry:
                            continue
                        
                        # Populate standardized parameters
                        video_id = entry.get('id', '')
                        results_list.append({
                            'id': video_id,
                            'title': entry.get('title', 'Unknown Title'),
                            'url': f"https://www.youtube.com/watch?v={video_id}" if video_id else entry.get('url', ''),
                            'uploader': entry.get('uploader', 'Unknown Channel'),
                            'duration': entry.get('duration', 0),
                            'view_count': entry.get('view_count', 0),
                            'thumbnail': entry.get('thumbnail', f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg") if video_id else ""
                        })
                        
                self.results_found.emit(results_list)
        except Exception as e:
            self.error_occurred.emit(str(e))