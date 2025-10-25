# 🎬 YouTube Video Downloader

A modern, feature-rich desktop application for downloading YouTube videos and audio with a beautiful dark-themed interface.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-Enabled-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### Core Functionality
- **Video Information Fetching**: Automatically retrieves video metadata including:
  - Title
  - Thumbnail preview
  - Duration
  - Uploader name
  - Available quality options
  
- **Video Type Detection**: Identifies:
  - Regular YouTube videos
  - YouTube Shorts
  - Live streams (active or recorded)

### Download Options
- **Multiple Format Support**:
  - Full video download (MP4)
  - Audio-only download (MP3)
  
- **Quality Selection**:
  - Best quality (automatic)
  - Custom resolution selection (1080p, 720p, 480p, 360p, etc.)
  
- **Progress Tracking**:
  - Real-time progress bar
  - Download speed indicator
  - Status updates

### User Experience
- **Modern Dark Theme**: Eye-friendly interface with green/blue accents
- **Clipboard Monitoring**: Automatically detects YouTube URLs copied to clipboard
- **System Notifications**: Desktop notification when download completes
- **Custom Save Location**: Choose where to save your downloads
- **Persistent Settings**: Saves your preferred download folder

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- FFmpeg (for audio conversion and video processing)

### Step 1: Install FFmpeg

#### Windows
1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract the archive
3. Add FFmpeg's `bin` folder to your system PATH

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

### Step 2: Install Python Dependencies

1. Clone or download this repository
2. Open a terminal/command prompt in the project directory
3. Install required packages:

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install yt-dlp PyQt5 Pillow requests pyperclip plyer
```

## 📖 Usage

### Running the Application

#### Option 1: New Modern Interface (Recommended)
```bash
python youtube_downloader_app.py
```

#### Option 2: Legacy Interface
```bash
python main.py
```

### How to Use

1. **Enter URL**:
   - Paste a YouTube video URL in the text field
   - Or simply copy a YouTube URL - it will be auto-detected!

2. **Fetch Video Information**:
   - Click the "🔍 Check" button
   - Wait for video information to load
   - Review title, thumbnail, duration, and video type

3. **Choose Download Options**:
   - Select format: Full Video or Audio Only (MP3)
   - Choose quality from the dropdown menu
   - Optionally change the save location by clicking "Browse"

4. **Download**:
   - Click the "⬇️ Download" button
   - Watch the progress bar for download status
   - Get notified when download completes!

## 🎨 User Interface

### Main Window Components

```
┌─────────────────────────────────────────┐
│     🎬 YouTube Video Downloader         │
├─────────────────────────────────────────┤
│  Video URL                              │
│  [Paste URL here...        ] [🔍 Check] │
├─────────────────────────────────────────┤
│  Video Information                      │
│  ┌───────────────────────────────────┐  │
│  │     [Video Thumbnail]             │  │
│  └───────────────────────────────────┘  │
│  Title: Video Title Here                │
│  Type: Regular Video / Short / Live     │
│  Duration: 00:00:00                     │
│  Uploader: Channel Name                 │
├─────────────────────────────────────────┤
│  Download Options                       │
│  Format: ⚪ Full Video  ⚪ Audio Only   │
│  Quality: [Best Quality ▼]              │
│  Save to: [C:\...\Downloads] [Browse]   │
├─────────────────────────────────────────┤
│  Download Progress                      │
│  [████████████░░░░░░░░░░] 60%          │
│  Downloading... 5.2 MB/s                │
├─────────────────────────────────────────┤
│           [⬇️ Download]                 │
└─────────────────────────────────────────┘
```

## 🛠️ Configuration

The application stores configuration in `configurations/configurations.json`:

```json
{
  "folder_path": "C:/Users/YourName/Downloads",
  "quality": "best",
  "output": "{folder_path}/%(title)s.%(ext)s"
}
```

You can modify this file to change default settings.

## 📋 Supported URLs

- Regular YouTube videos: `https://www.youtube.com/watch?v=VIDEO_ID`
- YouTube Shorts: `https://www.youtube.com/shorts/SHORT_ID`
- Short URLs: `https://youtu.be/VIDEO_ID`
- Live streams: Both active and recorded

## 🔧 Troubleshooting

### Common Issues

#### "Import Error: No module named 'PyQt5'"
**Solution**: Install PyQt5
```bash
pip install PyQt5
```

#### "FFmpeg not found" error
**Solution**: Install FFmpeg and ensure it's in your system PATH

#### Download fails with "Unable to extract video data"
**Solution**: 
- Update yt-dlp: `pip install --upgrade yt-dlp`
- Check if the video is available in your region
- Verify the URL is correct

#### Clipboard detection not working
**Solution**: Install pyperclip dependencies:
- **Windows**: Should work out of the box
- **Linux**: Install xclip or xsel: `sudo apt install xclip`
- **macOS**: Should work out of the box

#### System notification not showing
**Solution**: This is optional and won't affect downloads. To enable:
- **Windows**: Should work with plyer
- **Linux**: Install notify-send: `sudo apt install libnotify-bin`
- **macOS**: Should work with plyer

## 📁 Project Structure

```
dowloadVideos/
├── youtube_downloader_app.py   # Main application (new modern UI)
├── main.py                      # Legacy application entry point
├── baixarVideo.py              # Download functions (legacy)
├── menu.py                     # Menu components (legacy)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── configurations/
    └── configurations.json     # Application settings
```

## 🔐 Legal Notice

This tool is for personal use only. Please respect:
- YouTube's Terms of Service
- Copyright laws in your country
- Content creators' rights

Only download videos that you have the right to download.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📝 License

This project is provided as-is for educational purposes.

## 🙏 Acknowledgments

- **yt-dlp**: The powerful YouTube download engine
- **PyQt5**: For the beautiful GUI framework
- **FFmpeg**: For audio/video processing

## 📞 Support

If you encounter any issues:
1. Check the Troubleshooting section above
2. Update all dependencies: `pip install --upgrade -r requirements.txt`
3. Ensure FFmpeg is properly installed
4. Check yt-dlp issues: [https://github.com/yt-dlp/yt-dlp/issues](https://github.com/yt-dlp/yt-dlp/issues)

---

**Enjoy downloading! 🎉**
