"""
Modul Video Editor - Edit video otomatis untuk optimasi AdSense
Menggunakan FFmpeg untuk processing video
"""
import os
import subprocess
import json


class VideoEditor:
    """Auto-edit video untuk optimasi AdSense / monetisasi YouTube."""

    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.progress_callback = None

    def set_progress_callback(self, callback):
        self.progress_callback = callback

    def _update_progress(self, percent, text):
        if self.progress_callback:
            self.progress_callback(percent, text)

    def _run_ffmpeg(self, cmd, description="Processing..."):
        """Run FFmpeg command dengan error handling."""
        self._update_progress(50, description)
        process = subprocess.run(cmd, capture_output=True, text=True)
        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {process.stderr}")
        return True

    def get_video_info(self, video_path):
        """Ambil informasi detail video menggunakan ffprobe."""
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format', '-show_streams',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffprobe error: {result.stderr}")
        return json.loads(result.stdout)

    def detect_silence(self, video_path, noise_threshold="-30dB", min_duration=2.0):
        """
        Deteksi bagian diam/silence di video.
        Berguna untuk cut dead air.
        
        Args:
            video_path: Path ke video
            noise_threshold: Threshold noise (default -30dB)
            min_duration: Durasi minimum silence yang dideteksi (detik)
        
        Returns:
            List of (start, end) silence segments
        """
        self._update_progress(20, "Mendeteksi bagian diam...")

        cmd = [
            'ffmpeg', '-i', video_path,
            '-af', f'silencedetect=noise={noise_threshold}:d={min_duration}',
            '-f', 'null', '-'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        silences = []
        lines = result.stderr.split('\n')
        current_start = None
        
        for line in lines:
            if 'silence_start:' in line:
                try:
                    current_start = float(line.split('silence_start:')[1].strip().split()[0])
                except (ValueError, IndexError):
                    pass
            elif 'silence_end:' in line and current_start is not None:
                try:
                    end = float(line.split('silence_end:')[1].strip().split()[0])
                    silences.append((current_start, end))
                    current_start = None
                except (ValueError, IndexError):
                    pass

        self._update_progress(40, f"Ditemukan {len(silences)} bagian diam")
        return silences

    def remove_silence(self, video_path, output_path=None, 
                       noise_threshold="-30dB", min_duration=2.0, padding=0.3):
        """
        Hapus bagian diam dari video secara otomatis.
        
        Args:
            video_path: Path ke video input
            output_path: Path video output
            noise_threshold: Threshold noise
            min_duration: Durasi minimum silence yang dihapus
            padding: Padding sebelum/sesudah cut (detik)
        
        Returns:
            Path ke video output
        """
        if output_path is None:
            base = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.output_dir, f"{base}_no_silence.mp4")

        # Deteksi silence
        silences = self.detect_silence(video_path, noise_threshold, min_duration)
        
        if not silences:
            self._update_progress(100, "Tidak ada silence yang perlu dihapus")
            # Copy file as-is
            subprocess.run(['ffmpeg', '-y', '-i', video_path, '-c', 'copy', output_path],
                         capture_output=True)
            return output_path

        # Dapatkan durasi video
        info = self.get_video_info(video_path)
        duration = float(info['format']['duration'])

        # Buat segment list (bagian yang DEKEEP, bukan yang dihapus)
        keep_segments = []
        current_pos = 0.0

        for start, end in silences:
            seg_start = current_pos
            seg_end = max(current_pos, start + padding)
            if seg_end > seg_start + 0.1:
                keep_segments.append((seg_start, seg_end))
            current_pos = max(current_pos, end - padding)

        # Tambah segment terakhir
        if current_pos < duration:
            keep_segments.append((current_pos, duration))

        if not keep_segments:
            self._update_progress(100, "Tidak ada segment yang perlu dikeep")
            return video_path

        # Buat filter complex untuk concat segments
        self._update_progress(60, f"Menggabungkan {len(keep_segments)} segment...")

        filter_parts = []
        for i, (start, end) in enumerate(keep_segments):
            filter_parts.append(
                f"[0:v]trim=start={start:.3f}:end={end:.3f},setpts=PTS-STARTPTS[v{i}];"
                f"[0:a]atrim=start={start:.3f}:end={end:.3f},asetpts=PTS-STARTPTS[a{i}];"
            )

        concat_inputs = ''.join(f'[v{i}][a{i}]' for i in range(len(keep_segments)))
        filter_complex = ''.join(filter_parts) + f"{concat_inputs}concat=n={len(keep_segments)}:v=1:a=1[outv][outa]"

        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-filter_complex', filter_complex,
            '-map', '[outv]', '-map', '[outa]',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-c:a', 'aac', '-b:a', '192k',
            output_path
        ]

        self._run_ffmpeg(cmd, "Menghapus silence...")
        self._update_progress(100, f"Silence dihapus! Output: {output_path}")
        return output_path

    def add_intro(self, video_path, intro_path, output_path=None):
        """
        Tambah intro ke awal video.
        
        Args:
            video_path: Path ke video utama
            intro_path: Path ke video intro
            output_path: Path video output
        """
        if output_path is None:
            base = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.output_dir, f"{base}_with_intro.mp4")

        # Buat file list untuk concat
        list_path = os.path.join(self.output_dir, "_concat_list.txt")
        with open(list_path, 'w') as f:
            f.write(f"file '{os.path.abspath(intro_path)}'\n")
            f.write(f"file '{os.path.abspath(video_path)}'\n")

        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat', '-safe', '0',
            '-i', list_path,
            '-c', 'copy',
            output_path
        ]

        self._run_ffmpeg(cmd, "Menambahkan intro...")
        os.remove(list_path)
        self._update_progress(100, "Intro berhasil ditambahkan!")
        return output_path

    def add_outro(self, video_path, outro_path, output_path=None):
        """Tambah outro ke akhir video."""
        if output_path is None:
            base = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.output_dir, f"{base}_with_outro.mp4")

        list_path = os.path.join(self.output_dir, "_concat_list.txt")
        with open(list_path, 'w') as f:
            f.write(f"file '{os.path.abspath(video_path)}'\n")
            f.write(f"file '{os.path.abspath(outro_path)}'\n")

        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat', '-safe', '0',
            '-i', list_path,
            '-c', 'copy',
            output_path
        ]

        self._run_ffmpeg(cmd, "Menambahkan outro...")
        os.remove(list_path)
        self._update_progress(100, "Outro berhasil ditambahkan!")
        return output_path

    def add_background_music(self, video_path, music_path, volume=0.15, output_path=None):
        """
        Tambah background music ke video.
        
        Args:
            video_path: Path ke video
            music_path: Path ke file musik
            volume: Volume musik (0.0 - 1.0, default 0.15 = 15%)
            output_path: Path video output
        """
        if output_path is None:
            base = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.output_dir, f"{base}_with_music.mp4")

        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', music_path,
            '-filter_complex',
            f'[1:a]volume={volume},aloop=loop=-1:size=2e+09[music];'
            f'[0:a][music]amix=inputs=2:duration=first:dropout_transition=3[aout]',
            '-map', '0:v', '-map', '[aout]',
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            output_path
        ]

        self._run_ffmpeg(cmd, "Menambahkan background music...")
        self._update_progress(100, "Background music berhasil ditambahkan!")
        return output_path

    def enhance_audio(self, video_path, output_path=None):
        """
        Enhance audio: normalize volume, reduce noise ringan.
        Penting untuk AdSense — audio jernih = penonton betah.
        """
        if output_path is None:
            base = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.output_dir, f"{base}_enhanced_audio.mp4")

        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11,highpass=f=80,lowpass=f=12000',
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '192k',
            output_path
        ]

        self._run_ffmpeg(cmd, "Enhancing audio...")
        self._update_progress(100, "Audio berhasil di-enhance!")
        return output_path

    def adjust_speed(self, video_path, speed=1.05, output_path=None):
        """
        Adjust kecepatan video sedikit (misal 1.05x).
        Bisa bikin pacing lebih cepat tanpa terasa aneh.
        
        Args:
            speed: Kecepatan (1.0 = normal, 1.05 = 5% lebih cepat)
        """
        if output_path is None:
            base = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.output_dir, f"{base}_speed{speed}x.mp4")

        audio_tempo = speed
        # FFmpeg atempo hanya support 0.5-2.0
        if audio_tempo < 0.5:
            audio_tempo = 0.5
        elif audio_tempo > 2.0:
            audio_tempo = 2.0

        video_pts = 1.0 / speed

        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-filter_complex',
            f'[0:v]setpts={video_pts:.4f}*PTS[v];[0:a]atempo={audio_tempo:.4f}[a]',
            '-map', '[v]', '-map', '[a]',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-c:a', 'aac', '-b:a', '192k',
            output_path
        ]

        self._run_ffmpeg(cmd, f"Adjusting speed ke {speed}x...")
        self._update_progress(100, f"Speed berhasil diubah ke {speed}x!")
        return output_path

    def create_hook_cut(self, video_path, hook_start, hook_end, output_path=None):
        """
        Pindahkan scene paling menarik ke awal video (hook).
        Penting untuk retention rate dan AdSense!
        
        Args:
            video_path: Path ke video
            hook_start: Waktu mulai scene hook (detik)
            hook_end: Waktu akhir scene hook (detik)
        """
        if output_path is None:
            base = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.output_dir, f"{base}_hooked.mp4")

        info = self.get_video_info(video_path)
        duration = float(info['format']['duration'])

        # Segment: hook + before_hook + after_hook
        filter_complex = (
            f"[0:v]trim=start={hook_start}:end={hook_end},setpts=PTS-STARTPTS[hookv];"
            f"[0:a]atrim=start={hook_start}:end={hook_end},asetpts=PTS-STARTPTS[hooka];"
            f"[0:v]trim=start=0:end={hook_start},setpts=PTS-STARTPTS[prev];"
            f"[0:a]atrim=start=0:end={hook_start},asetpts=PTS-STARTPTS[prea];"
            f"[0:v]trim=start={hook_end}:end={duration},setpts=PTS-STARTPTS[postv];"
            f"[0:a]atrim=start={hook_end}:end={duration},asetpts=PTS-STARTPTS[posta];"
            f"[hookv][hooka][prev][prea][postv][posta]concat=n=3:v=1:a=1[outv][outa]"
        )

        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-filter_complex', filter_complex,
            '-map', '[outv]', '-map', '[outa]',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-c:a', 'aac', '-b:a', '192k',
            output_path
        ]

        self._run_ffmpeg(cmd, "Membuat hook cut...")
        self._update_progress(100, "Hook cut berhasil dibuat!")
        return output_path

    def export_for_youtube(self, video_path, output_path=None, resolution="1080p"):
        """
        Export video dengan settings optimal untuk YouTube.
        Bitrate, codec, dan format yang direkomendasikan YouTube.
        """
        if output_path is None:
            base = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.output_dir, f"{base}_youtube_ready.mp4")

        res_map = {
            '2160p': ('3840', '2160', '40M'),
            '1440p': ('2560', '1440', '24M'),
            '1080p': ('1920', '1080', '12M'),
            '720p': ('1280', '720', '7.5M'),
        }

        width, height, bitrate = res_map.get(resolution, res_map['1080p'])

        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,'
                   f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',
            '-c:v', 'libx264', '-preset', 'slow', '-b:v', bitrate,
            '-c:a', 'aac', '-b:a', '320k', '-ar', '48000',
            '-movflags', '+faststart',
            '-pix_fmt', 'yuv420p',
            output_path
        ]

        self._run_ffmpeg(cmd, f"Exporting untuk YouTube ({resolution})...")
        self._update_progress(100, f"Video YouTube-ready berhasil di-export!")
        return output_path

    def create_shorts_clip(self, video_path, start_time, end_time, output_path=None):
        """
        Buat YouTube Shorts clip dari video (vertikal 9:16, max 60 detik).
        
        Args:
            video_path: Path ke video
            start_time: Waktu mulai (detik)
            end_time: Waktu akhir (detik, max start+60)
        """
        if output_path is None:
            base = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.output_dir, f"{base}_shorts.mp4")

        # Max 60 detik untuk Shorts
        duration = min(end_time - start_time, 60)

        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-ss', str(start_time),
            '-t', str(duration),
            '-vf', 'crop=ih*(9/16):ih,scale=1080:1920',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-c:a', 'aac', '-b:a', '192k',
            output_path
        ]

        self._run_ffmpeg(cmd, "Membuat Shorts clip...")
        self._update_progress(100, "Shorts clip berhasil dibuat!")
        return output_path
