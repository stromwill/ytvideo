"""
Modul Color Grading - Preset filter warna untuk video
Bikin video terlihat lebih sinematik/profesional
"""
import os
import subprocess
from app.ffmpeg_util import get_ffmpeg_path


class ColorGrading:
    """Apply color grading presets ke video menggunakan FFmpeg."""

    # Semua preset menggunakan FFmpeg filter
    PRESETS = {
        'cinematic_warm': {
            'name': 'Cinematic Warm',
            'description': 'Warm tone, sedikit orange-teal — cocok untuk drama',
            'filter': 'eq=contrast=1.1:brightness=0.02:saturation=1.2,'
                      'colorbalance=rs=0.05:gs=-0.02:bs=-0.05:'
                      'rm=0.03:gm=0.0:bm=-0.03:'
                      'rh=0.02:gh=-0.01:bh=-0.03',
        },
        'cinematic_cool': {
            'name': 'Cinematic Cool',
            'description': 'Cool blue undertone — cocok untuk scene tegang',
            'filter': 'eq=contrast=1.15:brightness=-0.01:saturation=0.9,'
                      'colorbalance=rs=-0.03:gs=-0.01:bs=0.06:'
                      'rm=-0.02:gm=0.0:bm=0.04:'
                      'rh=-0.03:gh=0.0:bh=0.05',
        },
        'dramatic': {
            'name': 'Dramatic',
            'description': 'High contrast, desaturated — cocok untuk scene konflik',
            'filter': 'eq=contrast=1.3:brightness=-0.03:saturation=0.7,'
                      'curves=m=0/0 0.25/0.15 0.5/0.5 0.75/0.85 1/1,'
                      'unsharp=5:5:0.5',
        },
        'vintage': {
            'name': 'Vintage / Retro',
            'description': 'Faded look, warm highlights — cocok untuk flashback',
            'filter': 'eq=contrast=0.95:brightness=0.03:saturation=0.75,'
                      'colorbalance=rs=0.06:gs=0.02:bs=-0.04:'
                      'rh=0.08:gh=0.04:bh=-0.02,'
                      'curves=m=0/0.05 0.5/0.55 1/0.95',
        },
        'bright_pop': {
            'name': 'Bright & Vibrant',
            'description': 'Warna terang & vivid — cocok untuk scene happy/sukses',
            'filter': 'eq=contrast=1.05:brightness=0.05:saturation=1.4,'
                      'curves=m=0/0 0.5/0.55 1/1',
        },
        'dark_moody': {
            'name': 'Dark & Moody',
            'description': 'Gelap, misterius — cocok untuk scene malam/rahasia',
            'filter': 'eq=contrast=1.2:brightness=-0.08:saturation=0.8,'
                      'colorbalance=rs=-0.02:gs=-0.03:bs=0.02:'
                      'rm=-0.01:gm=-0.02:bm=0.01,'
                      'curves=m=0/0 0.3/0.2 0.7/0.7 1/0.92',
        },
        'golden_hour': {
            'name': 'Golden Hour',
            'description': 'Warm golden glow — cocok untuk scene romantis/sukses',
            'filter': 'eq=contrast=1.05:brightness=0.03:saturation=1.15,'
                      'colorbalance=rs=0.08:gs=0.04:bs=-0.06:'
                      'rm=0.05:gm=0.02:bm=-0.04',
        },
        'bw_dramatic': {
            'name': 'Black & White (Dramatic)',
            'description': 'Hitam putih high contrast — cocok untuk flashback/kenangan',
            'filter': 'hue=s=0,eq=contrast=1.3:brightness=-0.02,'
                      'curves=m=0/0 0.25/0.1 0.5/0.5 0.75/0.9 1/1',
        },
        'teal_orange': {
            'name': 'Teal & Orange',
            'description': 'Look film Hollywood — paling populer untuk drama',
            'filter': 'eq=contrast=1.1:saturation=1.1,'
                      'colorbalance=rs=0.07:gs=-0.03:bs=-0.07:'
                      'rm=0.04:gm=-0.02:bm=-0.04:'
                      'rh=-0.03:gh=0.0:bh=0.06',
        },
        'enhance_only': {
            'name': 'Auto Enhance',
            'description': 'Hanya perbaikan otomatis — tidak mengubah mood',
            'filter': 'eq=contrast=1.05:saturation=1.05,'
                      'unsharp=5:5:0.3',
        },
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

    def get_presets(self):
        """Return list of available presets."""
        return [
            {
                'id': preset_id,
                'name': preset['name'],
                'description': preset['description'],
            }
            for preset_id, preset in self.PRESETS.items()
        ]

    def apply_preset(self, video_path, preset_id, output_path=None):
        """
        Apply color grading preset ke video.

        Args:
            video_path: Path ke video
            preset_id: ID preset (key dari PRESETS dict)
            output_path: Path output (default: auto)

        Returns:
            Path ke video output
        """
        if preset_id not in self.PRESETS:
            available = ', '.join(self.PRESETS.keys())
            raise ValueError(f"Preset '{preset_id}' tidak ditemukan. Available: {available}")

        preset = self.PRESETS[preset_id]

        if output_path is None:
            base = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.output_dir, f"{base}_{preset_id}.mp4")

        self._update(20, f"Applying preset: {preset['name']}...")

        cmd = [
            self.ffmpeg, '-y',
            '-i', video_path,
            '-vf', preset['filter'],
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-c:a', 'copy',
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {result.stderr}")

        self._update(100, f"Color grading '{preset['name']}' berhasil!")
        return output_path

    def apply_custom(self, video_path, contrast=1.0, brightness=0.0,
                      saturation=1.0, hue=0, output_path=None):
        """
        Apply custom color adjustment.

        Args:
            contrast: 0.0 - 2.0 (1.0 = normal)
            brightness: -1.0 to 1.0 (0.0 = normal)
            saturation: 0.0 - 3.0 (1.0 = normal, 0 = grayscale)
            hue: Hue rotation in degrees
        """
        if output_path is None:
            base = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.output_dir, f"{base}_custom_grade.mp4")

        self._update(20, "Applying custom color grading...")

        vf = f"eq=contrast={contrast}:brightness={brightness}:saturation={saturation}"
        if hue != 0:
            vf += f",hue=h={hue}"

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

        self._update(100, "Custom color grading berhasil!")
        return output_path

    def preview_all_presets(self, video_path, timestamp=5):
        """
        Generate preview frame dari semua presets.
        Berguna untuk memilih preset yang cocok.

        Args:
            video_path: Path ke video
            timestamp: Waktu frame yang diambil (detik)

        Returns:
            dict of {preset_id: preview_image_path}
        """
        previews = {}
        preview_dir = os.path.join(self.output_dir, "color_previews")
        os.makedirs(preview_dir, exist_ok=True)

        total = len(self.PRESETS)
        for i, (preset_id, preset) in enumerate(self.PRESETS.items()):
            self._update(int((i / total) * 100), f"Generating preview: {preset['name']}...")

            output = os.path.join(preview_dir, f"preview_{preset_id}.jpg")
            cmd = [
                self.ffmpeg, '-y',
                '-ss', str(timestamp),
                '-i', video_path,
                '-vf', f"{preset['filter']},scale=640:-1",
                '-vframes', '1',
                '-q:v', '2',
                output
            ]
            subprocess.run(cmd, capture_output=True)

            if os.path.exists(output):
                previews[preset_id] = output

        self._update(100, f"Preview {len(previews)} presets selesai!")
        return previews
