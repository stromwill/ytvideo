"""
Video Analytics Dashboard — Analisis detail video (durasi, bitrate, resolution, fps, codec, dll)
Menggunakan FFprobe untuk extract metadata
"""
import os
import json
import subprocess
from app.ffmpeg_util import get_ffprobe_path


class VideoAnalytics:
    """Analyze video files and provide detailed statistics."""

    def __init__(self):
        self.ffprobe = get_ffprobe_path()

    def analyze(self, video_path):
        """Full video analysis — returns comprehensive stats dict."""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")

        cmd = [
            self.ffprobe, '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams', '-show_format',
            video_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            raise RuntimeError(f"FFprobe error: {result.stderr[:300]}")

        data = json.loads(result.stdout)

        stats = {
            'file': os.path.basename(video_path),
            'file_path': video_path,
            'file_size_bytes': os.path.getsize(video_path),
            'file_size_mb': round(os.path.getsize(video_path) / (1024 * 1024), 2),
            'format': None,
            'duration_seconds': 0,
            'duration_formatted': '00:00:00',
            'overall_bitrate_kbps': 0,
            'video': None,
            'audio': None,
            'subtitle_streams': 0,
            'youtube_ready': True,
            'youtube_issues': [],
        }

        # Format info
        fmt = data.get('format', {})
        stats['format'] = fmt.get('format_long_name', fmt.get('format_name', 'unknown'))
        duration = float(fmt.get('duration', 0))
        stats['duration_seconds'] = round(duration, 2)
        stats['duration_formatted'] = self._format_duration(duration)
        stats['overall_bitrate_kbps'] = int(int(fmt.get('bit_rate', 0)) / 1000)

        # Stream analysis
        sub_count = 0
        for stream in data.get('streams', []):
            codec_type = stream.get('codec_type', '')

            if codec_type == 'video' and stats['video'] is None:
                width = int(stream.get('width', 0))
                height = int(stream.get('height', 0))
                fps_str = stream.get('r_frame_rate', '0/1')
                try:
                    fps = round(eval(fps_str), 2)
                except Exception:
                    fps = 0

                bitrate = int(stream.get('bit_rate', 0)) / 1000 if stream.get('bit_rate') else 0

                stats['video'] = {
                    'codec': stream.get('codec_name', 'unknown'),
                    'codec_long': stream.get('codec_long_name', ''),
                    'profile': stream.get('profile', ''),
                    'width': width,
                    'height': height,
                    'resolution': f"{width}x{height}",
                    'resolution_label': self._resolution_label(height),
                    'fps': fps,
                    'bitrate_kbps': round(bitrate),
                    'pixel_format': stream.get('pix_fmt', ''),
                    'aspect_ratio': stream.get('display_aspect_ratio', ''),
                    'total_frames': int(stream.get('nb_frames', 0)),
                    'color_space': stream.get('color_space', ''),
                    'hdr': stream.get('color_transfer', '') in ['smpte2084', 'arib-std-b67'],
                }

            elif codec_type == 'audio' and stats['audio'] is None:
                bitrate = int(stream.get('bit_rate', 0)) / 1000 if stream.get('bit_rate') else 0
                stats['audio'] = {
                    'codec': stream.get('codec_name', 'unknown'),
                    'codec_long': stream.get('codec_long_name', ''),
                    'sample_rate': int(stream.get('sample_rate', 0)),
                    'channels': int(stream.get('channels', 0)),
                    'channel_layout': stream.get('channel_layout', ''),
                    'bitrate_kbps': round(bitrate),
                }

            elif codec_type == 'subtitle':
                sub_count += 1

        stats['subtitle_streams'] = sub_count

        # YouTube readiness check
        stats['youtube_ready'], stats['youtube_issues'] = self._check_youtube_ready(stats)

        return stats

    def _resolution_label(self, height):
        """Get human-readable resolution label."""
        if height >= 2160:
            return "4K UHD"
        elif height >= 1440:
            return "2K QHD"
        elif height >= 1080:
            return "Full HD"
        elif height >= 720:
            return "HD"
        elif height >= 480:
            return "SD"
        elif height >= 360:
            return "Low"
        return "Very Low"

    def _format_duration(self, seconds):
        """Format seconds to HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def _check_youtube_ready(self, stats):
        """Check if video meets YouTube recommended specs."""
        issues = []
        ready = True

        v = stats.get('video')
        a = stats.get('audio')

        if v:
            # Resolution check
            if v['height'] < 720:
                issues.append(f"Resolution terlalu rendah ({v['resolution']}). Minimal 720p untuk HD.")
                ready = False

            # FPS check
            if v['fps'] < 24:
                issues.append(f"FPS terlalu rendah ({v['fps']}). Minimal 24 fps.")
                ready = False

            # Codec check
            if v['codec'] not in ['h264', 'hevc', 'h265', 'vp9', 'av1']:
                issues.append(f"Codec '{v['codec']}' mungkin tidak optimal. Gunakan H.264 atau H.265.")

            # Pixel format
            if v['pixel_format'] and v['pixel_format'] != 'yuv420p':
                issues.append(f"Pixel format '{v['pixel_format']}'. Recommended: yuv420p.")

        else:
            issues.append("Tidak ada video stream terdeteksi!")
            ready = False

        if a:
            # Audio codec
            if a['codec'] not in ['aac', 'mp3', 'opus', 'vorbis', 'flac']:
                issues.append(f"Audio codec '{a['codec']}' mungkin tidak optimal. Gunakan AAC.")

            # Sample rate
            if a['sample_rate'] < 44100:
                issues.append(f"Sample rate {a['sample_rate']}Hz. Recommended: 44100Hz atau 48000Hz.")

            # Audio bitrate
            if a['bitrate_kbps'] > 0 and a['bitrate_kbps'] < 128:
                issues.append(f"Audio bitrate rendah ({a['bitrate_kbps']}kbps). Minimal 128kbps.")
        else:
            issues.append("Tidak ada audio stream! Video tanpa audio tidak bisa monetisasi.")
            ready = False

        # Duration check
        if stats['duration_seconds'] < 60:
            issues.append(f"Durasi terlalu pendek ({stats['duration_formatted']}). Minimal 1 menit untuk mid-roll ads.")
        elif stats['duration_seconds'] < 480:
            issues.append(f"Durasi {stats['duration_formatted']}. Video 8+ menit bisa pasang mid-roll ads.")

        # File size check
        if stats['file_size_mb'] > 12000:
            issues.append(f"File terlalu besar ({stats['file_size_mb']}MB). Maksimal YouTube 128GB.")

        if not issues:
            issues.append("Semua parameter sudah optimal untuk YouTube!")

        return ready, issues

    def format_report(self, stats):
        """Format analysis into readable text report."""
        lines = []
        lines.append("=" * 55)
        lines.append("📊 VIDEO ANALYTICS REPORT")
        lines.append("=" * 55)
        lines.append(f"📁 File: {stats['file']}")
        lines.append(f"📦 Size: {stats['file_size_mb']} MB")
        lines.append(f"⏱  Duration: {stats['duration_formatted']} ({stats['duration_seconds']}s)")
        lines.append(f"📡 Overall Bitrate: {stats['overall_bitrate_kbps']} kbps")
        lines.append(f"📦 Format: {stats['format']}")

        v = stats.get('video')
        if v:
            lines.append("")
            lines.append("🎥 VIDEO STREAM:")
            lines.append(f"   Codec: {v['codec']} ({v['profile']})")
            lines.append(f"   Resolution: {v['resolution']} ({v['resolution_label']})")
            lines.append(f"   FPS: {v['fps']}")
            lines.append(f"   Bitrate: {v['bitrate_kbps']} kbps")
            lines.append(f"   Pixel Format: {v['pixel_format']}")
            lines.append(f"   Aspect Ratio: {v['aspect_ratio']}")
            lines.append(f"   Total Frames: {v['total_frames']:,}")
            if v['hdr']:
                lines.append(f"   HDR: Yes")

        a = stats.get('audio')
        if a:
            lines.append("")
            lines.append("🔊 AUDIO STREAM:")
            lines.append(f"   Codec: {a['codec']}")
            lines.append(f"   Sample Rate: {a['sample_rate']} Hz")
            lines.append(f"   Channels: {a['channels']} ({a['channel_layout']})")
            lines.append(f"   Bitrate: {a['bitrate_kbps']} kbps")

        lines.append("")
        lines.append(f"📝 Subtitle Streams: {stats['subtitle_streams']}")

        lines.append("")
        yt_status = "✅ READY" if stats['youtube_ready'] else "⚠️ PERLU PERBAIKAN"
        lines.append(f"🎯 YouTube Readiness: {yt_status}")
        for issue in stats['youtube_issues']:
            prefix = "  ✅" if "optimal" in issue.lower() else "  ⚠️"
            lines.append(f"{prefix} {issue}")

        lines.append("=" * 55)
        return "\n".join(lines)

    def compare_videos(self, original_path, optimized_path):
        """Compare original vs optimized video stats."""
        original = self.analyze(original_path)
        optimized = self.analyze(optimized_path)

        comparison = {
            'original': original,
            'optimized': optimized,
            'changes': {}
        }

        # Size change
        size_diff = optimized['file_size_mb'] - original['file_size_mb']
        size_pct = (size_diff / original['file_size_mb'] * 100) if original['file_size_mb'] > 0 else 0
        comparison['changes']['file_size'] = {
            'diff_mb': round(size_diff, 2),
            'diff_percent': round(size_pct, 1),
        }

        # Duration change
        dur_diff = optimized['duration_seconds'] - original['duration_seconds']
        comparison['changes']['duration'] = {
            'diff_seconds': round(dur_diff, 2),
            'original': original['duration_formatted'],
            'optimized': optimized['duration_formatted'],
        }

        # Resolution change
        if original.get('video') and optimized.get('video'):
            comparison['changes']['resolution'] = {
                'original': original['video']['resolution'],
                'optimized': optimized['video']['resolution'],
                'changed': original['video']['resolution'] != optimized['video']['resolution'],
            }

        return comparison

    def format_comparison(self, comparison):
        """Format comparison into readable text."""
        lines = []
        lines.append("=" * 55)
        lines.append("📊 BEFORE vs AFTER COMPARISON")
        lines.append("=" * 55)

        o = comparison['original']
        n = comparison['optimized']
        c = comparison['changes']

        lines.append(f"📦 Size: {o['file_size_mb']}MB → {n['file_size_mb']}MB ({c['file_size']['diff_percent']:+.1f}%)")
        lines.append(f"⏱  Duration: {c['duration']['original']} → {c['duration']['optimized']} ({c['duration']['diff_seconds']:+.1f}s)")

        if 'resolution' in c:
            r = c['resolution']
            status = "→ " + r['optimized'] if r['changed'] else "(sama)"
            lines.append(f"📐 Resolution: {r['original']} {status}")

        lines.append(f"\n🎯 YouTube Ready: {'❌ → ✅' if not o['youtube_ready'] and n['youtube_ready'] else '✅' if n['youtube_ready'] else '⚠️'}")
        lines.append("=" * 55)

        return "\n".join(lines)
