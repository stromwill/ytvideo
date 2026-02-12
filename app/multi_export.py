"""
Multi-Platform Export — Export video untuk TikTok, Instagram Reels, Facebook, dll
Menggunakan FFmpeg untuk resize, crop, dan re-encode sesuai platform specs
"""
import os
import subprocess
from app.ffmpeg_util import get_ffmpeg_path, get_ffprobe_path


class MultiPlatformExporter:
    """Export videos optimized for different social media platforms."""

    # Platform specifications
    PLATFORMS = {
        'youtube': {
            'name': 'YouTube',
            'width': 1920, 'height': 1080,
            'aspect': '16:9',
            'max_duration': 43200,  # 12 hours
            'max_size_mb': 128000,
            'fps': 30,
            'video_bitrate': '8M',
            'audio_bitrate': '192k',
            'format': 'mp4',
            'codec': 'libx264',
        },
        'youtube_shorts': {
            'name': 'YouTube Shorts',
            'width': 1080, 'height': 1920,
            'aspect': '9:16',
            'max_duration': 60,
            'max_size_mb': 128000,
            'fps': 30,
            'video_bitrate': '6M',
            'audio_bitrate': '192k',
            'format': 'mp4',
            'codec': 'libx264',
        },
        'tiktok': {
            'name': 'TikTok',
            'width': 1080, 'height': 1920,
            'aspect': '9:16',
            'max_duration': 600,  # 10 min
            'max_size_mb': 287,
            'fps': 30,
            'video_bitrate': '4M',
            'audio_bitrate': '128k',
            'format': 'mp4',
            'codec': 'libx264',
        },
        'instagram_reels': {
            'name': 'Instagram Reels',
            'width': 1080, 'height': 1920,
            'aspect': '9:16',
            'max_duration': 90,
            'max_size_mb': 250,
            'fps': 30,
            'video_bitrate': '5M',
            'audio_bitrate': '128k',
            'format': 'mp4',
            'codec': 'libx264',
        },
        'instagram_feed': {
            'name': 'Instagram Feed',
            'width': 1080, 'height': 1080,
            'aspect': '1:1',
            'max_duration': 60,
            'max_size_mb': 250,
            'fps': 30,
            'video_bitrate': '5M',
            'audio_bitrate': '128k',
            'format': 'mp4',
            'codec': 'libx264',
        },
        'facebook': {
            'name': 'Facebook',
            'width': 1920, 'height': 1080,
            'aspect': '16:9',
            'max_duration': 14400,  # 4 hours
            'max_size_mb': 10000,
            'fps': 30,
            'video_bitrate': '8M',
            'audio_bitrate': '192k',
            'format': 'mp4',
            'codec': 'libx264',
        },
        'facebook_reels': {
            'name': 'Facebook Reels',
            'width': 1080, 'height': 1920,
            'aspect': '9:16',
            'max_duration': 90,
            'max_size_mb': 4000,
            'fps': 30,
            'video_bitrate': '5M',
            'audio_bitrate': '128k',
            'format': 'mp4',
            'codec': 'libx264',
        },
        'twitter': {
            'name': 'Twitter/X',
            'width': 1920, 'height': 1080,
            'aspect': '16:9',
            'max_duration': 140,
            'max_size_mb': 512,
            'fps': 30,
            'video_bitrate': '6M',
            'audio_bitrate': '128k',
            'format': 'mp4',
            'codec': 'libx264',
        },
    }

    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        self.ffmpeg = get_ffmpeg_path()
        self.ffprobe = get_ffprobe_path()
        os.makedirs(output_dir, exist_ok=True)

    def get_video_duration(self, video_path):
        """Get video duration in seconds."""
        cmd = [
            self.ffprobe, '-v', 'quiet',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return float(result.stdout.strip())
        except Exception:
            return 0

    def export(self, video_path, platform, start_time=0, duration=None,
               crop_mode='smart'):
        """
        Export video for a specific platform.
        
        Args:
            video_path: Input video path
            platform: Platform key (e.g., 'tiktok', 'instagram_reels')
            start_time: Start time in seconds (for trimming)
            duration: Duration in seconds (None = use max or full)
            crop_mode: 'smart' (center crop), 'pad' (add black bars), 'stretch'
        """
        if platform not in self.PLATFORMS:
            raise ValueError(f"Unknown platform: {platform}. Available: {list(self.PLATFORMS.keys())}")

        spec = self.PLATFORMS[platform]
        vid_duration = self.get_video_duration(video_path)

        # Determine output duration
        if duration:
            out_duration = min(duration, spec['max_duration'])
        elif vid_duration > spec['max_duration']:
            out_duration = spec['max_duration']
        else:
            out_duration = None  # Use full duration

        # Build video filter
        tw, th = spec['width'], spec['height']
        if crop_mode == 'smart':
            # Center crop to target aspect ratio
            vf = (
                f"scale=max({tw}\\,iw*{th}/ih):max({th}\\,ih*{tw}/iw),"
                f"crop={tw}:{th}:(iw-{tw})/2:(ih-{th})/2,"
                f"setsar=1"
            )
        elif crop_mode == 'pad':
            # Scale + pad (letterbox/pillarbox)
            vf = (
                f"scale={tw}:{th}:force_original_aspect_ratio=decrease,"
                f"pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2:black,"
                f"setsar=1"
            )
        else:  # stretch
            vf = f"scale={tw}:{th},setsar=1"

        # Build FFmpeg command
        output_name = f"{os.path.splitext(os.path.basename(video_path))[0]}_{platform}.mp4"
        output_path = os.path.join(self.output_dir, output_name)

        cmd = [
            self.ffmpeg, '-y',
            '-ss', str(start_time),
            '-i', video_path,
        ]

        if out_duration:
            cmd.extend(['-t', str(out_duration)])

        cmd.extend([
            '-vf', vf,
            '-r', str(spec['fps']),
            '-c:v', spec['codec'],
            '-b:v', spec['video_bitrate'],
            '-preset', 'medium',
            '-c:a', 'aac',
            '-b:a', spec['audio_bitrate'],
            '-ar', '44100',
            '-ac', '2',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            output_path
        ])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            # Check file size limit
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            if size_mb > spec['max_size_mb']:
                # Re-encode with lower bitrate
                return self._reduce_size(output_path, spec)
            return output_path

        raise RuntimeError(f"Export failed for {spec['name']}: {result.stderr[:500]}")

    def _reduce_size(self, video_path, spec):
        """Re-encode video with lower bitrate to meet size limit."""
        # Calculate target bitrate from max size and duration
        duration = self.get_video_duration(video_path)
        if duration <= 0:
            return video_path

        target_total_kbps = int((spec['max_size_mb'] * 8 * 1024) / duration * 0.9)
        audio_kbps = int(spec['audio_bitrate'].replace('k', ''))
        video_kbps = max(target_total_kbps - audio_kbps, 500)

        output_path = video_path.replace('.mp4', '_resized.mp4')
        cmd = [
            self.ffmpeg, '-y', '-i', video_path,
            '-c:v', spec['codec'], '-b:v', f'{video_kbps}k',
            '-preset', 'slow',
            '-c:a', 'aac', '-b:a', spec['audio_bitrate'],
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            output_path
        ]

        subprocess.run(cmd, capture_output=True, timeout=600)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            # Replace original
            os.remove(video_path)
            os.rename(output_path, video_path)

        return video_path

    def export_multi(self, video_path, platforms=None, start_time=0,
                     duration=None, crop_mode='smart'):
        """Export video to multiple platforms at once."""
        if platforms is None:
            platforms = ['tiktok', 'instagram_reels', 'facebook']

        results = {}
        for platform in platforms:
            try:
                output = self.export(video_path, platform, start_time, duration, crop_mode)
                results[platform] = {
                    'status': 'success',
                    'path': output,
                    'size_mb': round(os.path.getsize(output) / (1024 * 1024), 2),
                    'platform_name': self.PLATFORMS[platform]['name'],
                }
            except Exception as e:
                results[platform] = {
                    'status': 'error',
                    'error': str(e),
                    'platform_name': self.PLATFORMS[platform]['name'],
                }

        return results

    def format_export_report(self, results):
        """Format export results into readable report."""
        lines = []
        lines.append("=" * 50)
        lines.append("📱 MULTI-PLATFORM EXPORT REPORT")
        lines.append("=" * 50)

        success = 0
        for platform, result in results.items():
            if result['status'] == 'success':
                lines.append(f"  ✅ {result['platform_name']}: {result['size_mb']}MB — {result['path']}")
                success += 1
            else:
                lines.append(f"  ❌ {result['platform_name']}: {result['error']}")

        lines.append(f"\n📊 Total: {success}/{len(results)} berhasil")
        lines.append("=" * 50)
        return "\n".join(lines)

    @classmethod
    def get_available_platforms(cls):
        """Return list of available platforms with their specs."""
        return {k: {'name': v['name'], 'resolution': f"{v['width']}x{v['height']}",
                     'aspect': v['aspect'], 'max_duration': v['max_duration']}
                for k, v in cls.PLATFORMS.items()}
