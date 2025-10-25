"""
Modern YouTube Video Downloader Application
A desktop application with dark theme for downloading YouTube videos and audio.
"""

import sys
import os
import json
import threading
import requests
from io import BytesIO
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QRadioButton,
    QButtonGroup, QProgressBar, QFileDialog, QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PIL import Image
import yt_dlp
import pyperclip
from plyer import notification


class VideoInfoFetcher(QThread):
    """Thread for fetching video information without blocking the UI"""
    info_fetched = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                
                # Determine video type
                video_type = "Regular Video"
                if '/shorts/' in self.url:
                    video_type = "YouTube Short"
                elif info.get('is_live'):
                    video_type = "Live Stream (Active)"
                elif info.get('was_live'):
                    video_type = "Live Stream (Recorded)"
                
                # Get available formats
                formats = []
                if info.get('formats'):
                    for fmt in info['formats']:
                        if fmt.get('height'):
                            formats.append(fmt['height'])
                    formats = sorted(list(set(formats)), reverse=True)
                
                video_data = {
                    'title': info.get('title', 'Unknown'),
                    'thumbnail': info.get('thumbnail', ''),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'video_type': video_type,
                    'formats': formats,
                    'url': self.url
                }
                
                self.info_fetched.emit(video_data)
                
        except Exception as e:
            self.error_occurred.emit(str(e))


class VideoDownloader(QThread):
    """Thread for downloading videos without blocking the UI"""
    progress_update = pyqtSignal(float, str)
    download_complete = pyqtSignal(str)
    download_error = pyqtSignal(str)

    def __init__(self, url, download_path, quality, download_type):
        super().__init__()
        self.url = url
        self.download_path = download_path
        self.quality = quality
        self.download_type = download_type

    def check_ffmpeg(self):
        """Check if FFmpeg is available in the system"""
        try:
            import subprocess
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, 
                         check=True, 
                         timeout=5)
            return True
        except:
            return False

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    percent = (downloaded / total) * 100
                    speed = d.get('speed', 0)
                    speed_str = f"{speed / 1024 / 1024:.2f} MB/s" if speed else "calculating..."
                    self.progress_update.emit(percent, speed_str)
            except:
                pass
        elif d['status'] == 'finished':
            self.progress_update.emit(100, "Processing...")

    def run(self):
        try:
            # Check if FFmpeg is available
            ffmpeg_available = self.check_ffmpeg()
            
            # Configure download options based on type
            if self.download_type == 'audio':
                if ffmpeg_available:
                    # With FFmpeg: convert to MP3
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                        'progress_hooks': [self.progress_hook],
                    }
                else:
                    # Without FFmpeg: download best audio format (usually m4a/webm)
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                        'progress_hooks': [self.progress_hook],
                    }
            else:  # video
                if self.quality == 'best':
                    format_str = 'bestvideo+bestaudio/best' if ffmpeg_available else 'best'
                else:
                    if ffmpeg_available:
                        format_str = f'bestvideo[height<={self.quality}]+bestaudio/best[height<={self.quality}]'
                    else:
                        format_str = f'best[height<={self.quality}]'
                
                ydl_opts = {
                    'format': format_str,
                    'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                }
                
                # Only merge if FFmpeg is available
                if ffmpeg_available:
                    ydl_opts['merge_output_format'] = 'mp4'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                filename = ydl.prepare_filename(info)
                if self.download_type == 'audio':
                    # Change extension to mp3
                    filename = os.path.splitext(filename)[0] + '.mp3'
                self.download_complete.emit(filename)
                
        except Exception as e:
            self.download_error.emit(str(e))


class YouTubeDownloaderApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.video_info = None
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.last_clipboard = ""
        self.ffmpeg_available = self.check_ffmpeg_status()
        
        # Load configuration
        self.load_config()
        
        # Initialize UI
        self.init_ui()
        
        # Start clipboard monitoring timer
        self.clipboard_timer = QTimer()
        self.clipboard_timer.timeout.connect(self.check_clipboard)
        self.clipboard_timer.start(1000)  # Check every second

    def check_ffmpeg_status(self):
        """Check if FFmpeg is installed"""
        try:
            import subprocess
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, 
                         check=True, 
                         timeout=5)
            return True
        except:
            return False

    def load_config(self):
        """Load configuration from JSON file"""
        config_path = 'configurations/configurations.json'
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.download_path = config.get('folder_path', self.download_path)
            except:
                pass

    def save_config(self):
        """Save configuration to JSON file"""
        config_path = 'configurations/configurations.json'
        os.makedirs('configurations', exist_ok=True)
        config = {
            'folder_path': self.download_path,
            'quality': 'best',
            'output': '{folder_path}/%(title)s.%(ext)s'
        }
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("YouTube Video Downloader")
        self.setGeometry(100, 100, 900, 750)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("YouTube Video Downloader")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #E53935; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # FFmpeg Status Warning
        if not self.ffmpeg_available:
            ffmpeg_warning = QLabel(
                "⚠️ FFmpeg not detected - Audio will be downloaded in original format (M4A/WEBM)\n"
                "Videos will be downloaded in single-file format (may have lower quality)"
            )
            ffmpeg_warning.setStyleSheet("""
                background-color: #FFA726;
                color: #000000;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            """)
            ffmpeg_warning.setAlignment(Qt.AlignCenter)
            ffmpeg_warning.setWordWrap(True)
            main_layout.addWidget(ffmpeg_warning)
        else:
            ffmpeg_ok = QLabel("✓ FFmpeg detected - Full functionality enabled")
            ffmpeg_ok.setStyleSheet("""
                background-color: #66BB6A;
                color: #000000;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            """)
            ffmpeg_ok.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(ffmpeg_ok)
        
        # URL Input Section
        url_group = QGroupBox("Video URL")
        url_layout = QVBoxLayout()
        
        url_input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube URL here...")
        self.url_input.setMinimumHeight(40)
        url_input_layout.addWidget(self.url_input)
        
        self.check_button = QPushButton("Check")
        self.check_button.setMinimumHeight(40)
        self.check_button.setMinimumWidth(120)
        self.check_button.clicked.connect(self.fetch_video_info)
        url_input_layout.addWidget(self.check_button)
        
        url_layout.addLayout(url_input_layout)
        url_group.setLayout(url_layout)
        main_layout.addWidget(url_group)
        
        # Video Info Section
        info_group = QGroupBox("Video Information")
        info_layout = QVBoxLayout()
        
        # Thumbnail
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setMinimumHeight(200)
        self.thumbnail_label.setStyleSheet("background-color: #1e1e1e; border-radius: 5px;")
        self.thumbnail_label.setText("No video loaded")
        info_layout.addWidget(self.thumbnail_label)
        
        # Video details
        self.title_label = QLabel("Title: -")
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        info_layout.addWidget(self.title_label)
        
        self.type_label = QLabel("Type: -")
        info_layout.addWidget(self.type_label)
        
        self.duration_label = QLabel("Duration: -")
        info_layout.addWidget(self.duration_label)
        
        self.uploader_label = QLabel("Uploader: -")
        info_layout.addWidget(self.uploader_label)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
        
        # Download Options Section
        options_group = QGroupBox("Download Options")
        options_layout = QVBoxLayout()
        
        # Format selection
        format_layout = QHBoxLayout()
        format_label = QLabel("Format:")
        format_layout.addWidget(format_label)
        
        self.format_group = QButtonGroup()
        self.video_radio = QRadioButton("Full Video")
        self.video_radio.setChecked(True)
        
        # Update audio label based on FFmpeg availability
        audio_label = "Audio Only (MP3)" if self.ffmpeg_available else "Audio Only (M4A/WEBM)"
        self.audio_radio = QRadioButton(audio_label)
        
        self.format_group.addButton(self.video_radio)
        self.format_group.addButton(self.audio_radio)
        
        format_layout.addWidget(self.video_radio)
        format_layout.addWidget(self.audio_radio)
        format_layout.addStretch()
        options_layout.addLayout(format_layout)
        
        # Quality selection
        quality_layout = QHBoxLayout()
        quality_label = QLabel("Quality:")
        quality_layout.addWidget(quality_label)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItem("Best Quality", "best")
        self.quality_combo.setMinimumWidth(200)
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()
        options_layout.addLayout(quality_layout)
        
        # Download path
        path_layout = QHBoxLayout()
        path_label = QLabel("Save to:")
        path_layout.addWidget(path_label)
        
        self.path_display = QLineEdit(self.download_path)
        self.path_display.setReadOnly(True)
        path_layout.addWidget(self.path_display)
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_folder)
        path_layout.addWidget(self.browse_button)
        options_layout.addLayout(path_layout)
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # Progress Section
        progress_group = QGroupBox("Download Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # Download Button
        self.download_button = QPushButton("Download")
        self.download_button.setMinimumHeight(50)
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #E53935;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #C62828;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        main_layout.addWidget(self.download_button)

    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        dark_stylesheet = """
            QMainWindow {
                background-color: #121212;
            }
            QWidget {
                background-color: #121212;
                color: #E0E0E0;
                font-family: Arial;
                font-size: 12px;
            }
            QGroupBox {
                border: 2px solid #333333;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: #E53935;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit {
                background-color: #1e1e1e;
                border: 2px solid #333333;
                border-radius: 5px;
                padding: 8px;
                color: #E0E0E0;
            }
            QLineEdit:focus {
                border: 2px solid #E53935;
            }
            QPushButton {
                background-color: #E53935;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C62828;
            }
            QPushButton:pressed {
                background-color: #B71C1C;
            }
            QComboBox {
                background-color: #1e1e1e;
                border: 2px solid #333333;
                border-radius: 5px;
                padding: 5px;
                color: #E0E0E0;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #E0E0E0;
                margin-right: 5px;
            }
            QRadioButton {
                color: #E0E0E0;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #555555;
                border-radius: 9px;
                background-color: #1e1e1e;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #E53935;
                border-radius: 9px;
                background-color: #E53935;
            }
            QProgressBar {
                border: 2px solid #333333;
                border-radius: 5px;
                text-align: center;
                background-color: #1e1e1e;
                color: #E0E0E0;
            }
            QProgressBar::chunk {
                background-color: #E53935;
                border-radius: 3px;
            }
            QLabel {
                color: #E0E0E0;
            }
        """
        self.setStyleSheet(dark_stylesheet)

    def check_clipboard(self):
        """Check clipboard for YouTube URLs"""
        try:
            clipboard_content = pyperclip.paste()
            if clipboard_content != self.last_clipboard:
                self.last_clipboard = clipboard_content
                # Check if it's a YouTube URL
                if 'youtube.com' in clipboard_content or 'youtu.be' in clipboard_content:
                    if not self.url_input.text():  # Only auto-fill if empty
                        self.url_input.setText(clipboard_content)
                        self.status_label.setText("YouTube URL detected in clipboard!")
        except:
            pass

    def fetch_video_info(self):
        """Fetch video information from URL"""
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL")
            return
        
        # Validate URL
        if 'youtube.com' not in url and 'youtu.be' not in url:
            QMessageBox.warning(self, "Error", "Please enter a valid YouTube URL")
            return
        
        # Disable buttons and show loading
        self.check_button.setEnabled(False)
        self.download_button.setEnabled(False)
        self.status_label.setText("Fetching video information...")
        
        # Start fetching in background thread
        self.fetcher_thread = VideoInfoFetcher(url)
        self.fetcher_thread.info_fetched.connect(self.on_info_fetched)
        self.fetcher_thread.error_occurred.connect(self.on_fetch_error)
        self.fetcher_thread.start()

    def on_info_fetched(self, video_data):
        """Handle successfully fetched video information"""
        self.video_info = video_data
        
        # Update UI with video info
        self.title_label.setText(f"Title: {video_data['title']}")
        self.type_label.setText(f"Type: {video_data['video_type']}")
        
        # Format duration
        duration_sec = video_data['duration']
        hours = duration_sec // 3600
        minutes = (duration_sec % 3600) // 60
        seconds = duration_sec % 60
        
        if hours > 0:
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            duration_str = f"{minutes:02d}:{seconds:02d}"
        
        self.duration_label.setText(f"Duration: {duration_str}")
        self.uploader_label.setText(f"Uploader: {video_data['uploader']}")
        
        # Load thumbnail
        self.load_thumbnail(video_data['thumbnail'])
        
        # Update quality options
        self.quality_combo.clear()
        self.quality_combo.addItem("Best Quality", "best")
        for resolution in video_data['formats']:
            self.quality_combo.addItem(f"{resolution}p", str(resolution))
        
        # Enable download button
        self.download_button.setEnabled(True)
        self.check_button.setEnabled(True)
        self.status_label.setText("Video information loaded successfully!")

    def on_fetch_error(self, error_msg):
        """Handle error when fetching video information"""
        QMessageBox.critical(self, "Error", f"Failed to fetch video information:\n{error_msg}")
        self.check_button.setEnabled(True)
        self.status_label.setText("Error fetching video information")

    def load_thumbnail(self, thumbnail_url):
        """Load and display video thumbnail"""
        try:
            response = requests.get(thumbnail_url)
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            
            # Resize to fit label
            image.thumbnail((400, 300), Image.Resampling.LANCZOS)
            
            # Convert to QPixmap
            image_data = BytesIO()
            image.save(image_data, format='PNG')
            pixmap = QPixmap()
            pixmap.loadFromData(image_data.getvalue())
            
            self.thumbnail_label.setPixmap(pixmap)
        except Exception as e:
            self.thumbnail_label.setText("Could not load thumbnail")

    def browse_folder(self):
        """Open folder browser dialog"""
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.download_path)
        if folder:
            self.download_path = folder
            self.path_display.setText(folder)
            self.save_config()

    def start_download(self):
        """Start downloading the video"""
        if not self.video_info:
            QMessageBox.warning(self, "Error", "Please fetch video information first")
            return
        
        # Get download options
        download_type = 'audio' if self.audio_radio.isChecked() else 'video'
        quality = self.quality_combo.currentData()
        
        # Disable buttons
        self.download_button.setEnabled(False)
        self.check_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting download...")
        
        # Start download in background thread
        self.downloader_thread = VideoDownloader(
            self.video_info['url'],
            self.download_path,
            quality,
            download_type
        )
        self.downloader_thread.progress_update.connect(self.on_progress_update)
        self.downloader_thread.download_complete.connect(self.on_download_complete)
        self.downloader_thread.download_error.connect(self.on_download_error)
        self.downloader_thread.start()

    def on_progress_update(self, percent, speed):
        """Update progress bar and status"""
        self.progress_bar.setValue(int(percent))
        self.status_label.setText(f"Downloading... {percent:.1f}% - {speed}")

    def on_download_complete(self, filename):
        """Handle successful download completion"""
        self.progress_bar.setValue(100)
        self.status_label.setText("Download completed successfully!")
        self.download_button.setEnabled(True)
        self.check_button.setEnabled(True)
        
        # Show system notification
        try:
            notification.notify(
                title="Download Complete",
                message=f"Video downloaded successfully!\n{os.path.basename(filename)}",
                app_name="YouTube Downloader",
                timeout=10
            )
        except:
            pass
        
        # Show success message
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Download Complete")
        msg.setText("Video downloaded successfully!")
        msg.setInformativeText(f"Saved to: {filename}")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def on_download_error(self, error_msg):
        """Handle download error"""
        self.progress_bar.setValue(0)
        self.status_label.setText("Download failed")
        self.download_button.setEnabled(True)
        self.check_button.setEnabled(True)
        
        QMessageBox.critical(self, "Download Error", f"Failed to download video:\n{error_msg}")


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("YouTube Video Downloader")
    
    # Set application icon (optional)
    # app.setWindowIcon(QIcon('icon.png'))
    
    window = YouTubeDownloaderApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
