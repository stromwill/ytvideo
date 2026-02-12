"""
Modul Downloader - Download video sendiri dari YouTube menggunakan yt-dlp
"""
import os
import yt_dlp
import threading


class VideoDownloader:
    """Download video YouTube (untuk video milik sendiri)."""

    def __init__(self, output_dir="temp"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.progress_callback = None
        self.info = None

    def set_progress_callback(self, callback):
        """Set callback function untuk progress update: callback(percent, status_text)"""
        self.progress_callback = callback

    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', 'N/A').strip()
            eta = d.get('_eta_str', 'N/A').strip()
            status = f"Downloading: {percent} | Speed: {speed} | ETA: {eta}"
            if self.progress_callback:
                try:
                    pct = float(percent.replace('%', ''))
                except ValueError:
                    pct = 0
                self.progress_callback(pct, status)
        elif d['status'] == 'finished':
            if self.progress_callback:
                self.progress_callback(100, "Download selesai! Memproses...")

    def get_video_info(self, url):
        """Ambil informasi video tanpa download."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            self.info = ydl.extract_info(url, download=False)
            return {
                'title': self.info.get('title', 'Unknown'),
                'duration': self.info.get('duration', 0),
                'channel': self.info.get('channel', 'Unknown'),
                'view_count': self.info.get('view_count', 0),
                'description': self.info.get('description', ''),
                'thumbnail': self.info.get('thumbnail', ''),
                'upload_date': self.info.get('upload_date', ''),
                'categories': self.info.get('categories', []),
                'tags': self.info.get('tags', []),
                'like_count': self.info.get('like_count', 0),
                'formats': [
                    {
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'resolution': f.get('resolution', 'N/A'),
                        'filesize': f.get('filesize', 0),
                        'fps': f.get('fps', 0),
                    }
                    for f in self.info.get('formats', [])
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none'
                ],
            }

    def download(self, url, quality="best", filename=None):
        """
        Download video dari URL.
        
        Args:
            url: URL YouTube
            quality: 'best', '1080p', '720p', '480p'
            filename: Nama file output (tanpa ekstensi)
        
        Returns:
            Path ke file yang didownload
        """
        if filename is None:
            filename = "%(title)s"

        format_map = {
            'best': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '1080p': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]',
            '720p': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]',
            '480p': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]',
        }

        output_template = os.path.join(self.output_dir, f"{filename}.%(ext)s")

        ydl_opts = {
            'format': format_map.get(quality, format_map['best']),
            'outtmpl': output_template,
            'progress_hooks': [self._progress_hook],
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Cari file yang didownload
            filename_out = ydl.prepare_filename(info)
            # Pastikan ekstensi mp4
            if not filename_out.endswith('.mp4'):
                base = os.path.splitext(filename_out)[0]
                filename_out = base + '.mp4'
            return filename_out

    def download_audio_only(self, url, filename=None):
        """Download hanya audio (untuk subtitle generation)."""
        if filename is None:
            filename = "audio_%(title)s"

        output_template = os.path.join(self.output_dir, f"{filename}.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'progress_hooks': [self._progress_hook],
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename_out = ydl.prepare_filename(info)
            base = os.path.splitext(filename_out)[0]
            return base + '.wav'

    def download_thumbnail(self, url, filename="thumbnail"):
        """Download thumbnail video."""
        import urllib.request
        
        info = self.get_video_info(url) if not self.info else {
            'thumbnail': self.info.get('thumbnail', '')
        }
        
        thumb_url = info.get('thumbnail', '')
        if not thumb_url:
            return None

        output_path = os.path.join(self.output_dir, f"{filename}.jpg")
        urllib.request.urlretrieve(thumb_url, output_path)
        return output_path
