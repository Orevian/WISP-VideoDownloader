import os
import requests
from PySide6.QtCore import Qt, QSize, Signal, Slot
from PySide6.QtGui import QIcon, QPixmap, QMovie
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QLineEdit, QComboBox, QStackedWidget, QFrame, QFileDialog,
    QProgressBar, QScrollArea, QListWidget, QListWidgetItem, QSizePolicy,
    QMessageBox
)

from PySide6.QtCore import QThread

from styles import THEME_STYLE
from searcher import SearchWorker
from downloader import MetadataWorker, DownloadWorker

# Helper functions to format search lists and layouts
def clean_duration(seconds):
    if not seconds:
        return "00:00"
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


class ImageDownloader(QThread):
    """
    Downloads thumbnail images in background threads so visual listing doesn't lag.
    """
    loaded = Signal(QPixmap, str)

    def __init__(self, url, video_id):
        super().__init__()
        self.url = url
        self.video_id = video_id

    def run(self):
        try:
            if not self.url:
                self.loaded.emit(QPixmap(), self.video_id)
                return
            response = requests.get(self.url, timeout=5)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.loaded.emit(pixmap, self.video_id)
            else:
                self.loaded.emit(QPixmap(), self.video_id)
        except Exception:
            self.loaded.emit(QPixmap(), self.video_id)


class SearchResultWidget(QFrame):
    """
    Custom widget for each Search Card with modern design and Select capability.
    """
    selected = Signal(str) # Emits Video URL when selected

    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.setObjectName("ResultCard")
        self.url = item_data['url']
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Video Thumbnail Label (Fixed dimensions with rounded fallback)
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(140, 80)
        self.thumb_label.setStyleSheet("background-color: #10101F; border-radius: 6px;")
        self.thumb_label.setScaledContents(True)
        main_layout.addWidget(self.thumb_label)

        # Video Information Container
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(5)

        self.title_label = QLabel(item_data['title'])
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #FFFFFF;")
        self.title_label.setWordWrap(True)
        info_layout.addWidget(self.title_label)

        details_label = QLabel(f"By: {item_data['uploader']}  |  Duration: {clean_duration(item_data['duration'])}")
        details_label.setStyleSheet("color: #94A3B8; font-size: 12px;")
        info_layout.addWidget(details_label)

        main_layout.addWidget(info_widget, 1)

        # Load details button
        self.select_btn = QPushButton("Convert")
        self.select_btn.setObjectName("PrimaryButton")
        self.select_btn.setFixedSize(100, 36)
        self.select_btn.clicked.connect(self.on_select_clicked)
        main_layout.addWidget(self.select_btn)

        # Trigger background image load
        self.loader = ImageDownloader(item_data['thumbnail'], item_data['id'])
        self.loader.loaded.connect(self.on_image_loaded)
        self.loader.start()

    def on_image_loaded(self, pixmap, video_id):
        if not pixmap.isNull():
            self.thumb_label.setPixmap(pixmap.scaled(self.thumb_label.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        else:
            self.thumb_label.setText("No Image")

    def on_select_clicked(self):
        self.selected.emit(self.url)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VibeStreamer PRO - YouTube Link & Keyword Downloader")
        self.resize(980, 680)
        self.setStyleSheet(THEME_STYLE)
        
        # Core active objects and variables
        self.default_download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.active_download_url = ""
        self.active_download_worker = None
        self.active_search_worker = None
        self.active_metadata_worker = None

        self.init_ui()

    def init_ui(self):
        # Master Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ------------------- SIDEBAR -------------------
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 20)
        sidebar_layout.setSpacing(10)

        # Brand Title Header
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        brand_label = QLabel("VibeStreamer")
        brand_label.setObjectName("BrandLabel")
        brand_pro = QLabel("PRO")
        brand_pro.setStyleSheet("font-size: 11px; font-weight: 800; color: #10B981; background: #0F2D24; padding: 2px 6px; border-radius: 4px;")
        
        logo_layout.addWidget(brand_label)
        logo_layout.addWidget(brand_pro)
        logo_layout.addStretch()
        sidebar_layout.addWidget(logo_container)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #23233B; margin: 15px 0px;")
        sidebar_layout.addWidget(divider)

        # Nav Buttons
        self.nav_direct_btn = QPushButton(" Direct Downloader")
        self.nav_direct_btn.setObjectName("NavButton")
        self.nav_direct_btn.setCheckable(True)
        self.nav_direct_btn.setChecked(True)
        self.nav_direct_btn.clicked.connect(lambda: self.switch_tab(0))
        sidebar_layout.addWidget(self.nav_direct_btn)

        self.nav_search_btn = QPushButton(" Search YouTube")
        self.nav_search_btn.setObjectName("NavButton")
        self.nav_search_btn.setCheckable(True)
        self.nav_search_btn.clicked.connect(lambda: self.switch_tab(1))
        sidebar_layout.addWidget(self.nav_search_btn)

        self.nav_settings_btn = QPushButton(" Settings")
        self.nav_settings_btn.setObjectName("NavButton")
        self.nav_settings_btn.setCheckable(True)
        self.nav_settings_btn.clicked.connect(lambda: self.switch_tab(2))
        sidebar_layout.addWidget(self.nav_settings_btn)

        sidebar_layout.addStretch()

        # Small brand indicator
        version_label = QLabel("v1.2.0 Stable  |  Powered by yt-dlp")
        version_label.setStyleSheet("color: #4B5563; font-size: 11px; font-weight: 600;")
        sidebar_layout.addWidget(version_label)

        main_layout.addWidget(sidebar)

        # ------------------- CONTENT STACK -------------------
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)

        # Setup individual pages
        self.setup_direct_tab()
        self.setup_search_tab()
        self.setup_settings_tab()

    # ------------------ DIRECT DOWNLOAD TAB ------------------
    def setup_direct_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 40, 30, 30)
        layout.setSpacing(25)

        # Header Title
        head_label = QLabel("Direct Stream Downloader")
        head_label.setStyleSheet("font-size: 24px; font-weight: 800; color: #FFFFFF;")
        layout.addWidget(head_label)

        # Link Input Area
        input_card = QFrame()
        input_card.setObjectName("Card")
        input_card_layout = QHBoxLayout(input_card)
        input_card_layout.setContentsMargins(15, 15, 15, 15)
        input_card_layout.setSpacing(10)

        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("Paste YouTube Video URL here (e.g. https://www.youtube.com/watch?v=...)")
        input_card_layout.addWidget(self.link_input, 1)

        self.parse_btn = QPushButton("Analyze Link")
        self.parse_btn.setObjectName("PrimaryButton")
        self.parse_btn.clicked.connect(self.parse_url)
        input_card_layout.addWidget(self.parse_btn)

        layout.addWidget(input_card)

        # Analytical View Card (Initially hidden or minimalized)
        self.info_card = QFrame()
        self.info_card.setObjectName("Card")
        self.info_card.setVisible(False)
        info_card_layout = QHBoxLayout(self.info_card)
        info_card_layout.setContentsMargins(15, 15, 15, 15)
        info_card_layout.setSpacing(20)

        self.info_thumbnail = QLabel()
        self.info_thumbnail.setFixedSize(160, 90)
        self.info_thumbnail.setStyleSheet("background-color: #0F0F1A; border-radius: 6px;")
        self.info_thumbnail.setScaledContents(True)
        info_card_layout.addWidget(self.info_thumbnail)

        info_details_widget = QWidget()
        info_details_layout = QVBoxLayout(info_details_widget)
        info_details_layout.setContentsMargins(0, 0, 0, 0)
        info_details_layout.setSpacing(5)

        self.info_title = QLabel("Video Title")
        self.info_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        self.info_title.setWordWrap(True)
        info_details_layout.addWidget(self.info_title)

        self.info_author = QLabel("Author / Channel")
        self.info_author.setStyleSheet("font-size: 13px; color: #94A3B8;")
        info_details_layout.addWidget(self.info_author)

        info_card_layout.addWidget(info_details_widget, 1)
        layout.addWidget(self.info_card)

        # Control Panel Configuration (Format options & Path)
        options_row = QHBoxLayout()
        options_row.setSpacing(20)

        # Target Quality Selector
        quality_widget = QWidget()
        quality_layout = QVBoxLayout(quality_widget)
        quality_layout.setContentsMargins(0, 0, 0, 0)
        quality_layout.setSpacing(6)
        
        quality_lbl = QLabel("Target Resolution / Format")
        quality_lbl.setStyleSheet("font-weight: 700; color: #94A3B8; font-size: 12px;")
        quality_layout.addWidget(quality_lbl)

        self.quality_combo = QComboBox()
        self.quality_combo.addItem("Best Video (MP4 4K / 60 FPS)", "MP4_4K")
        self.quality_combo.addItem("Full HD (MP4 1080P)", "MP4_1080P")
        self.quality_combo.addItem("HD (MP4 720P)", "MP4_720P")
        self.quality_combo.addItem("High Quality Audio (MP3 320kbps)", "MP3_AUDIO")
        quality_layout.addWidget(self.quality_combo)
        options_row.addWidget(quality_widget, 1)

        # Custom Path Picker
        path_widget = QWidget()
        path_layout = QVBoxLayout(path_widget)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(6)

        path_lbl = QLabel("Destination Directory")
        path_lbl.setStyleSheet("font-weight: 700; color: #94A3B8; font-size: 12px;")
        path_layout.addWidget(path_lbl)

        path_input_row = QHBoxLayout()
        path_input_row.setSpacing(8)
        
        self.path_input = QLineEdit()
        self.path_input.setText(self.default_download_dir)
        path_input_row.addWidget(self.path_input, 1)

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setObjectName("SecondaryButton")
        self.browse_btn.clicked.connect(self.browse_directory)
        path_input_row.addWidget(self.browse_btn)

        path_layout.addLayout(path_input_row)
        options_row.addWidget(path_widget, 1.2)

        layout.addLayout(options_row)

        # Progress Section
        self.progress_container = QFrame()
        self.progress_container.setObjectName("Card")
        self.progress_container.setVisible(False)
        prog_layout = QVBoxLayout(self.progress_container)
        prog_layout.setContentsMargins(15, 15, 15, 15)
        prog_layout.setSpacing(10)

        # Top row: State indicator & Speed values
        prog_info_row = QHBoxLayout()
        self.progress_status = QLabel("Preparing Stream Downloader...")
        self.progress_status.setStyleSheet("font-weight: bold; color: #E2E8F0;")
        
        self.speed_label = QLabel("0.0 MB/s")
        self.speed_label.setStyleSheet("color: #10B981; font-weight: bold;")
        
        prog_info_row.addWidget(self.progress_status)
        prog_info_row.addStretch()
        prog_info_row.addWidget(self.speed_label)
        prog_layout.addLayout(prog_info_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        prog_layout.addWidget(self.progress_bar)

        # Bottom row: ETA & Size indicator
        prog_details_row = QHBoxLayout()
        self.eta_label = QLabel("ETA: Calculating...")
        self.eta_label.setStyleSheet("color: #94A3B8; font-size: 12px;")
        
        self.size_label = QLabel("0.0 MB / 0.0 MB")
        self.size_label.setStyleSheet("color: #94A3B8; font-size: 12px;")

        prog_details_row.addWidget(self.eta_label)
        prog_details_row.addStretch()
        prog_details_row.addWidget(self.size_label)
        prog_layout.addLayout(prog_details_row)

        layout.addWidget(self.progress_container)

        # Trigger download button
        self.download_btn = QPushButton("Start High Speed Stream Download")
        self.download_btn.setObjectName("PrimaryButton")
        self.download_btn.setStyleSheet("font-size: 15px; padding: 14px;")
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        layout.addStretch()
        self.stack.addWidget(page)

    # ------------------ SEARCH TAB ------------------
    def setup_search_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 40, 30, 30)
        layout.setSpacing(20)

        # Header Title
        head_label = QLabel("Keyword Search Engine")
        head_label.setStyleSheet("font-size: 24px; font-weight: 800; color: #FFFFFF;")
        layout.addWidget(head_label)

        # Search Bar Box
        search_card = QFrame()
        search_card.setObjectName("Card")
        search_card_layout = QHBoxLayout(search_card)
        search_card_layout.setContentsMargins(15, 15, 15, 15)
        search_card_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter video title or search term (e.g. Lofi hip hop mix 4k)...")
        self.search_input.returnPressed.connect(self.run_search)
        search_card_layout.addWidget(self.search_input, 1)

        self.search_btn = QPushButton("Search YouTube")
        self.search_btn.setObjectName("PrimaryButton")
        self.search_btn.clicked.connect(self.run_search)
        search_card_layout.addWidget(self.search_btn)

        layout.addWidget(search_card)

        # Loader/No results label
        self.status_feedback = QLabel("")
        self.status_feedback.setStyleSheet("color: #94A3B8; font-size: 13px; font-weight: 500;")
        self.status_feedback.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_feedback)

        # Scrollable area of results
        self.scroll_results = QScrollArea()
        self.scroll_results.setWidgetResizable(True)
        self.scroll_results.setStyleSheet("background-color: transparent; border: none;")
        
        self.results_container = QWidget()
        self.results_container_layout = QVBoxLayout(self.results_container)
        self.results_container_layout.setContentsMargins(0, 0, 0, 0)
        self.results_container_layout.setSpacing(10)
        self.results_container_layout.addStretch() # bottom stretch space

        self.scroll_results.setWidget(self.results_container)
        layout.addWidget(self.scroll_results, 1)

        self.stack.addWidget(page)

    # ------------------ SETTINGS TAB ------------------
    def setup_settings_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 40, 30, 30)
        layout.setSpacing(25)

        # Header Title
        head_label = QLabel("Settings & Diagnostics")
        head_label.setStyleSheet("font-size: 24px; font-weight: 800; color: #FFFFFF;")
        layout.addWidget(head_label)

        # Info Box Card
        info_card = QFrame()
        info_card.setObjectName("Card")
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(20, 20, 20, 20)
        info_layout.setSpacing(15)

        card_title = QLabel("System Requirements & Features")
        card_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        info_layout.addWidget(card_title)

        desc_label = QLabel(
            "<b>4K 60FPS Support:</b> To properly merge high-resolution video tracks (1080p, 1440p, 4K, 8K) with "
            "independent high-fidelity audio streams, <i>FFmpeg</i> must be configured and installed on your system's "
            "PATH variables.<br><br>"
            "<b>Output Formats:</b><br>"
            "• MP4 High-Quality presets will maintain native structural streams.<br>"
            "• MP3 conversion generates isolated audio extracted at 320kbps."
        )
        desc_label.setStyleSheet("color: #94A3B8; font-size: 13px; line-height: 20px;")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)

        layout.addWidget(info_card)

        # About block
        about_card = QFrame()
        about_card.setObjectName("Card")
        about_layout = QVBoxLayout(about_card)
        about_layout.setContentsMargins(20, 20, 20, 20)
        about_layout.setSpacing(10)

        about_title = QLabel("About VibeStreamer PRO")
        about_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        about_layout.addWidget(about_title)

        about_text = QLabel(
            "VibeStreamer PRO is a non-commercial utility designed as a clean interface to demonstrate multi-threaded "
            "media extraction directly to your local workspace. Ensure download behaviors comply with original content provider licenses."
        )
        about_text.setStyleSheet("color: #64748B; font-size: 12px;")
        about_text.setWordWrap(True)
        about_layout.addWidget(about_text)

        layout.addWidget(about_card)
        layout.addStretch()

        self.stack.addWidget(page)

    # ------------------ EVENT ROUTERS / ACTIONS ------------------
    def switch_tab(self, index):
        # Update Nav checked state visual cues
        self.nav_direct_btn.setChecked(index == 0)
        self.nav_search_btn.setChecked(index == 1)
        self.nav_settings_btn.setChecked(index == 2)
        
        self.stack.setCurrentIndex(index)

    def browse_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Download Destination", self.path_input.text())
        if dir_path:
            self.path_input.setText(dir_path)

    def parse_url(self):
        url = self.link_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Invalid Request", "Please specify a valid stream URL link.")
            return

        self.parse_btn.setEnabled(False)
        self.parse_btn.setText("Parsing...")
        
        # Kill running metadata thread if necessary
        if self.active_metadata_worker and self.active_metadata_worker.isRunning():
            self.active_metadata_worker.terminate()
            self.active_metadata_worker.wait()

        self.active_metadata_worker = MetadataWorker(url)
        self.active_metadata_worker.metadata_loaded.connect(self.on_metadata_loaded)
        self.active_metadata_worker.error_occurred.connect(self.on_metadata_failed)
        self.active_metadata_worker.start()

    def on_metadata_loaded(self, info):
        self.parse_btn.setEnabled(True)
        self.parse_btn.setText("Analyze Link")
        self.active_download_url = info.get('webpage_url', self.link_input.text().strip())

        # Populating Analytical Card UI
        self.info_title.setText(info.get('title', 'Unknown Title'))
        self.info_author.setText(f"Channel: {info.get('uploader', 'Unknown Source')}  |  Duration: {clean_duration(info.get('duration', 0))}")
        self.info_card.setVisible(True)

        thumbnail_url = info.get('thumbnail')
        if thumbnail_url:
            self.metadata_thumb_loader = ImageDownloader(thumbnail_url, "DIRECT_PREVIEW")
            self.metadata_thumb_loader.loaded.connect(self.on_preview_image_loaded)
            self.metadata_thumb_loader.start()

    def on_preview_image_loaded(self, pixmap, video_id):
        if not pixmap.isNull():
            self.info_thumbnail.setPixmap(pixmap.scaled(self.info_thumbnail.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

    def on_metadata_failed(self, error):
        self.parse_btn.setEnabled(True)
        self.parse_btn.setText("Analyze Link")
        QMessageBox.critical(self, "Extraction Error", f"Failed to index streams safely:\n{error}")

    def run_search(self):
        query = self.search_input.text().strip()
        if not query:
            return

        # Clear results container
        # Note: We must carefully destroy existing widgets safely
        for i in reversed(range(self.results_container_layout.count())):
            item = self.results_container_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        self.status_feedback.setText("Searching YouTube databases. Please hold...")
        self.search_btn.setEnabled(False)

        # Start Async search
        if self.active_search_worker and self.active_search_worker.isRunning():
            self.active_search_worker.terminate()
            self.active_search_worker.wait()

        self.active_search_worker = SearchWorker(query)
        self.active_search_worker.results_found.connect(self.on_search_completed)
        self.active_search_worker.error_occurred.connect(self.on_search_failed)
        self.active_search_worker.start()

    def on_search_completed(self, results):
        self.search_btn.setEnabled(True)
        self.status_feedback.setText("")

        if not results:
            self.status_feedback.setText("No matching results found.")
            return

        for index, item in enumerate(results):
            widget = SearchResultWidget(item)
            widget.selected.connect(self.load_from_search_result)
            self.results_container_layout.insertWidget(index, widget)

    def on_search_failed(self, err_msg):
        self.search_btn.setEnabled(True)
        self.status_feedback.setText("")
        QMessageBox.critical(self, "Search Error", f"Search extraction triggered an error:\n{err_msg}")

    @Slot(str)
    def load_from_search_result(self, url):
        # Populate Direct URL field and jump to tab
        self.link_input.setText(url)
        self.switch_tab(0)
        # Automatically trigger parsing on click
        self.parse_url()

    def start_download(self):
        url = self.link_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Invalid URL", "Please specify a stream source URL before starting.")
            return

        # Verify output directory
        out_dir = self.path_input.text().strip()
        if not out_dir:
            out_dir = self.default_download_dir
            self.path_input.setText(out_dir)

        # Form choice parameters
        idx = self.quality_combo.currentIndex()
        format_val = self.quality_combo.itemData(idx)

        # Prepare elements
        self.download_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_container.setVisible(True)

        if self.active_download_worker and self.active_download_worker.isRunning():
            self.active_download_worker.terminate()
            self.active_download_worker.wait()

        self.active_download_worker = DownloadWorker(url, out_dir, format_val)
        self.active_download_worker.progress_changed.connect(self.on_download_progress)
        self.active_download_worker.status_changed.connect(self.on_download_status)
        self.active_download_worker.download_finished.connect(self.on_download_success)
        self.active_download_worker.download_error.connect(self.on_download_failed)
        self.active_download_worker.start()

    def on_download_progress(self, progress_data):
        self.progress_bar.setValue(int(progress_data['percent']))
        self.speed_label.setText(progress_data['speed'])
        self.eta_label.setText(f"ETA: {progress_data['eta']}")
        self.size_label.setText(f"{progress_data['downloaded']} / {progress_data['total_size']}")

    def on_download_status(self, status):
        self.progress_status.setText(status)

    def on_download_success(self, msg):
        self.download_btn.setEnabled(True)
        self.progress_status.setText("Done!")
        self.progress_bar.setValue(100)
        QMessageBox.information(self, "VibeStreamer Pro", f"Success!\n{msg}")

    def on_download_failed(self, error):
        self.download_btn.setEnabled(True)
        self.progress_status.setText("Process Failed")
        QMessageBox.critical(self, "Download Execution Failed", f"A processing error halted completion:\n{error}")