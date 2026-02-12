"""
Modul Watermark - Tambah logo/watermark ke video
"""
import os
import subprocess
from app.ffmpeg_util import get_ffmpeg_path


class WatermarkOverlay:
    """Tambah watermark/logo channel ke video."""

    POSITIONS = {
        'top-left':     'x=20:y=20',
        'top-right':    'x=W-w-20:y=20',
        'bottom-left':  'x=20:y=H-h-20',
        'bottom-right': 'x=W-w-20:y=H-h-20',
        'center':       'x=(W-w)/2:y=(H-h)/2',
    }

    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.ffmpeg = get_ffmpeg_path()
        self.progress_callback = None

    def set_progress_callback(self, callback):
        self.progress_callback = callback

    def _update(self, pct, text):
        if self.progress_callback:
            self.progress_callback(pct, text)

    def add_image_watermark(self, video_path, logo_path, position="bottom-right",
                             opacity=0.7, scale_percent=10, output_path=None):
        """
        Tambah logo/gambar sebagai watermark.

        Args:
            video_path: Path ke video
            logo_path: Path ke gambar logo (PNG dengan transparency recommended)
            position: 'top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'
            opacity: Transparansi (0.0 - 1.0)
            scale_percent: Ukuran logo relatif terhadap lebar video (%)
            output_path: Path output
        """
        if output_path is None:
            base = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.output_dir, f"{base}_watermarked.mp4")

        self._update(20, "Menambahkan watermark...")

        pos = self.POSITIONS.get(position, self.POSITIONS['bottom-right'])
        scale_w = f"iw*{scale_percent}/100"

        # Filter: scale logo lalu overlay dengan opacity
        filter_complex = (
            f"[1:v]scale={scale_w}:-1,format=rgba,"
            f"colorchannelmixer=aa={opacity}[logo];"
            f"[0:v][logo]overlay={pos}[out]"
        )

        cmd = [
            self.ffmpeg, '-y',
            '-i', video_path,
            '-i', logo_path,
            '-filter_complex', filter_complex,
            '-map', '[out]', '-map', '0:a',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-c:a', 'copy',
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {result.stderr}")

        self._update(100, f"Watermark ditambahkan: {output_path}")
        return output_path

    def add_text_watermark(self, video_path, text="Channel Name",
                            position="bottom-right", font_size=24,
                            font_color="white", opacity=0.5, output_path=None):
        """
        Tambah teks sebagai watermark (jika belum punya logo).

        Args:
            text: Teks watermark (nama channel, dll)
            font_color: Warna teks
            opacity: Transparansi
        """
        if output_path is None:
            base = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.output_dir, f"{base}_text_wm.mp4")

        self._update(20, "Menambahkan text watermark...")

        pos_map = {
            'top-left':     f"x=20:y=20",
            'top-right':    f"x=w-tw-20:y=20",
            'bottom-left':  f"x=20:y=h-th-20",
            'bottom-right': f"x=w-tw-20:y=h-th-20",
            'center':       f"x=(w-tw)/2:y=(h-th)/2",
        }
        pos = pos_map.get(position, pos_map['bottom-right'])

        # Escape teks untuk FFmpeg
        safe_text = text.replace("'", "\\'").replace(":", "\\:")

        vf = (
            f"drawtext=text='{safe_text}':{pos}:"
            f"fontsize={font_size}:fontcolor={font_color}@{opacity}:"
            f"borderw=2:bordercolor=black@{opacity * 0.5}"
        )

        cmd = [
            self.ffmpeg, '-y',
            '-i', video_path,
            '-vf', vf,
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-c:a', 'copy',
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {result.stderr}")

        self._update(100, f"Text watermark ditambahkan: {output_path}")
        return output_path
