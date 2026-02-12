"""
Modul AdSense Compliance Checker
Analisis video apakah sudah memenuhi syarat monetisasi YouTube
"""
import os
import json
import subprocess
from app.ffmpeg_util import get_ffmpeg_path, get_ffprobe_path


class AdSenseChecker:
    """Cek apakah video memenuhi syarat AdSense/monetisasi YouTube."""

    # YouTube recommended specs
    YOUTUBE_SPECS = {
        'min_duration': 60,           # Minimum 1 menit
        'ideal_min_duration': 480,    # 8+ menit ideal (mid-roll ads)
        'ideal_max_duration': 1200,   # 20 menit max ideal
        'min_resolution_w': 1280,     # Minimum 720p
        'min_resolution_h': 720,
        'ideal_resolution_w': 1920,   # Ideal 1080p
        'ideal_resolution_h': 1080,
        'min_bitrate': 2_000_000,     # 2 Mbps minimum
        'ideal_bitrate': 8_000_000,   # 8 Mbps ideal
        'min_audio_bitrate': 128_000, # 128 kbps minimum
        'ideal_fps': 30,
        'max_fps': 60,
        'ideal_audio_sample_rate': 48000,
        'accepted_formats': ['mp4', 'mkv', 'avi', 'mov', 'webm'],
        'ideal_format': 'mp4',
        'ideal_codec': 'h264',
        'ideal_audio_codec': 'aac',
    }

    def __init__(self):
        self.ffmpeg = get_ffmpeg_path()
        self.ffprobe = get_ffprobe_path()

    def _get_video_info(self, video_path):
        """Get detailed video info via ffprobe."""
        if self.ffprobe:
            cmd = [
                self.ffprobe, '-v', 'quiet',
                '-print_format', 'json',
                '-show_format', '-show_streams',
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)

        # Fallback: parse ffmpeg -i output
        cmd = [self.ffmpeg, '-i', video_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return self._parse_ffmpeg_output(result.stderr)

    def _parse_ffmpeg_output(self, stderr):
        """Parse ffmpeg -i output as fallback."""
        import re
        info = {'format': {}, 'streams': []}

        # Duration
        dur_match = re.search(r'Duration:\s*(\d+):(\d+):(\d+)\.(\d+)', stderr)
        if dur_match:
            h, m, s, cs = dur_match.groups()
            info['format']['duration'] = str(int(h)*3600 + int(m)*60 + int(s) + int(cs)/100)

        # Bitrate
        br_match = re.search(r'bitrate:\s*(\d+)\s*kb/s', stderr)
        if br_match:
            info['format']['bit_rate'] = str(int(br_match.group(1)) * 1000)

        # Video stream
        vid_match = re.search(r'Video:\s*(\w+).*?,\s*(\d+)x(\d+).*?,\s*([\d.]+)\s*fps', stderr)
        if vid_match:
            info['streams'].append({
                'codec_type': 'video',
                'codec_name': vid_match.group(1),
                'width': int(vid_match.group(2)),
                'height': int(vid_match.group(3)),
                'r_frame_rate': f"{vid_match.group(4)}/1",
            })

        # Audio stream
        aud_match = re.search(r'Audio:\s*(\w+).*?,\s*(\d+)\s*Hz.*?,.*?,\s*(\d+)\s*kb/s', stderr)
        if aud_match:
            info['streams'].append({
                'codec_type': 'audio',
                'codec_name': aud_match.group(1),
                'sample_rate': aud_match.group(2),
                'bit_rate': str(int(aud_match.group(3)) * 1000),
            })

        return info

    def check_video(self, video_path):
        """
        Full compliance check untuk video.

        Returns:
            dict: {
                'score': 0-100,
                'grade': 'A'/'B'/'C'/'D'/'F',
                'passed': True/False,
                'checks': [...],
                'recommendations': [...],
                'video_info': {...},
            }
        """
        info = self._get_video_info(video_path)
        checks = []
        recommendations = []
        score = 0

        # Parse info
        fmt = info.get('format', {})
        video_stream = None
        audio_stream = None
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'video' and not video_stream:
                video_stream = stream
            elif stream.get('codec_type') == 'audio' and not audio_stream:
                audio_stream = stream

        # ===== 1. DURASI =====
        duration = float(fmt.get('duration', 0))
        if duration >= self.YOUTUBE_SPECS['ideal_min_duration']:
            score += 20
            checks.append({
                'name': 'Durasi Video',
                'status': 'excellent',
                'value': f"{duration/60:.1f} menit",
                'message': '✅ Durasi ideal! Bisa pasang mid-roll ads.'
            })
        elif duration >= self.YOUTUBE_SPECS['min_duration']:
            score += 12
            checks.append({
                'name': 'Durasi Video',
                'status': 'ok',
                'value': f"{duration/60:.1f} menit",
                'message': '⚠️ Video pendek. 8+ menit lebih baik untuk mid-roll ads.'
            })
            recommendations.append("Perpanjang video ke 8+ menit untuk mid-roll ads")
        else:
            checks.append({
                'name': 'Durasi Video',
                'status': 'fail',
                'value': f"{duration:.0f} detik",
                'message': '❌ Terlalu pendek. Minimum 1 menit untuk monetisasi.'
            })
            recommendations.append("Video harus minimal 1 menit")

        # ===== 2. RESOLUSI =====
        if video_stream:
            w = video_stream.get('width', 0)
            h = video_stream.get('height', 0)
            if w >= self.YOUTUBE_SPECS['ideal_resolution_w'] and h >= self.YOUTUBE_SPECS['ideal_resolution_h']:
                score += 20
                checks.append({
                    'name': 'Resolusi',
                    'status': 'excellent',
                    'value': f"{w}x{h}",
                    'message': '✅ Full HD atau lebih tinggi.'
                })
            elif w >= self.YOUTUBE_SPECS['min_resolution_w']:
                score += 12
                checks.append({
                    'name': 'Resolusi',
                    'status': 'ok',
                    'value': f"{w}x{h}",
                    'message': '⚠️ HD tapi bukan Full HD. 1080p lebih baik.'
                })
                recommendations.append("Upgrade ke 1080p untuk kualitas lebih baik")
            else:
                score += 3
                checks.append({
                    'name': 'Resolusi',
                    'status': 'warning',
                    'value': f"{w}x{h}",
                    'message': '⚠️ Resolusi rendah. Minimum 720p.'
                })
                recommendations.append("Resolusi terlalu rendah, upgrade ke minimal 720p")

            # ===== 3. CODEC =====
            codec = video_stream.get('codec_name', '').lower()
            if codec in ['h264', 'avc']:
                score += 10
                checks.append({
                    'name': 'Video Codec',
                    'status': 'excellent',
                    'value': codec.upper(),
                    'message': '✅ H.264 — codec paling compatible.'
                })
            elif codec in ['h265', 'hevc', 'vp9', 'av1']:
                score += 8
                checks.append({
                    'name': 'Video Codec',
                    'status': 'ok',
                    'value': codec.upper(),
                    'message': '✅ Codec modern, didukung YouTube.'
                })
            else:
                score += 3
                checks.append({
                    'name': 'Video Codec',
                    'status': 'warning',
                    'value': codec.upper() if codec else 'Unknown',
                    'message': '⚠️ Codec kurang umum. Re-encode ke H.264.'
                })
                recommendations.append("Re-encode video ke H.264 (libx264)")

            # ===== 4. FPS =====
            fps_str = video_stream.get('r_frame_rate', '30/1')
            try:
                num, den = fps_str.split('/')
                fps = float(num) / float(den)
            except (ValueError, ZeroDivisionError):
                fps = 30

            if 24 <= fps <= 60:
                score += 10
                checks.append({
                    'name': 'Frame Rate',
                    'status': 'excellent',
                    'value': f"{fps:.0f} fps",
                    'message': '✅ Frame rate normal.'
                })
            else:
                score += 3
                checks.append({
                    'name': 'Frame Rate',
                    'status': 'warning',
                    'value': f"{fps:.0f} fps",
                    'message': '⚠️ Frame rate tidak standar.'
                })
                recommendations.append(f"Ubah frame rate ke 30 atau 60 fps")

        # ===== 5. AUDIO =====
        if audio_stream:
            audio_codec = audio_stream.get('codec_name', '').lower()
            sample_rate = int(audio_stream.get('sample_rate', 0))
            audio_br = int(audio_stream.get('bit_rate', 0))

            if audio_codec in ['aac', 'mp3', 'opus', 'vorbis']:
                score += 10
                checks.append({
                    'name': 'Audio Codec',
                    'status': 'excellent',
                    'value': audio_codec.upper(),
                    'message': '✅ Audio codec didukung.'
                })
            else:
                score += 3
                checks.append({
                    'name': 'Audio Codec',
                    'status': 'warning',
                    'value': audio_codec.upper() if audio_codec else 'Unknown',
                    'message': '⚠️ Re-encode audio ke AAC.'
                })
                recommendations.append("Re-encode audio ke AAC")

            if sample_rate >= 44100:
                score += 5
                checks.append({
                    'name': 'Audio Sample Rate',
                    'status': 'excellent',
                    'value': f"{sample_rate} Hz",
                    'message': '✅ Sample rate standar.'
                })
            elif sample_rate > 0:
                score += 2
                checks.append({
                    'name': 'Audio Sample Rate',
                    'status': 'warning',
                    'value': f"{sample_rate} Hz",
                    'message': '⚠️ Sample rate rendah. 48000 Hz ideal.'
                })
                recommendations.append("Set audio sample rate ke 48000 Hz")

            if audio_br >= self.YOUTUBE_SPECS['min_audio_bitrate']:
                score += 5
                checks.append({
                    'name': 'Audio Bitrate',
                    'status': 'excellent',
                    'value': f"{audio_br//1000} kbps",
                    'message': '✅ Audio bitrate cukup.'
                })
            elif audio_br > 0:
                score += 2
                checks.append({
                    'name': 'Audio Bitrate',
                    'status': 'warning',
                    'value': f"{audio_br//1000} kbps",
                    'message': '⚠️ Audio bitrate rendah. 192+ kbps recommended.'
                })
                recommendations.append("Tingkatkan audio bitrate ke 192 kbps")
        else:
            checks.append({
                'name': 'Audio',
                'status': 'fail',
                'value': 'Tidak ada',
                'message': '❌ Tidak ada audio! Video tanpa suara sulit monetisasi.'
            })
            recommendations.append("Tambahkan audio ke video")

        # ===== 6. BITRATE =====
        total_br = int(fmt.get('bit_rate', 0))
        if total_br >= self.YOUTUBE_SPECS['ideal_bitrate']:
            score += 10
            checks.append({
                'name': 'Total Bitrate',
                'status': 'excellent',
                'value': f"{total_br//1_000_000} Mbps",
                'message': '✅ Bitrate tinggi — kualitas bagus.'
            })
        elif total_br >= self.YOUTUBE_SPECS['min_bitrate']:
            score += 6
            checks.append({
                'name': 'Total Bitrate',
                'status': 'ok',
                'value': f"{total_br//1000} kbps",
                'message': '⚠️ Bitrate cukup, tapi bisa lebih tinggi.'
            })
        elif total_br > 0:
            score += 2
            checks.append({
                'name': 'Total Bitrate',
                'status': 'warning',
                'value': f"{total_br//1000} kbps",
                'message': '⚠️ Bitrate rendah — video mungkin terlihat buram.'
            })
            recommendations.append("Tingkatkan video bitrate saat export")

        # ===== 7. FORMAT =====
        ext = os.path.splitext(video_path)[1].lower().replace('.', '')
        if ext == 'mp4':
            score += 10
            checks.append({
                'name': 'Format File',
                'status': 'excellent',
                'value': ext.upper(),
                'message': '✅ MP4 — format paling compatible.'
            })
        elif ext in self.YOUTUBE_SPECS['accepted_formats']:
            score += 6
            checks.append({
                'name': 'Format File',
                'status': 'ok',
                'value': ext.upper(),
                'message': f'⚠️ {ext.upper()} diterima, tapi MP4 lebih baik.'
            })
        else:
            checks.append({
                'name': 'Format File',
                'status': 'fail',
                'value': ext.upper(),
                'message': f'❌ Format {ext.upper()} tidak didukung YouTube.'
            })
            recommendations.append("Convert video ke format MP4")

        # ===== FINAL SCORE =====
        score = min(score, 100)

        if score >= 85:
            grade = 'A'
        elif score >= 70:
            grade = 'B'
        elif score >= 50:
            grade = 'C'
        elif score >= 30:
            grade = 'D'
        else:
            grade = 'F'

        passed = score >= 50

        # Add general recommendations
        if not any('subtitle' in r.lower() for r in recommendations):
            recommendations.append("💡 Tambahkan subtitle — meningkatkan watch time 30-40%")
        if duration < 480:
            recommendations.append("💡 Video 8+ menit bisa pasang mid-roll ads (pendapatan lebih)")
        if not any('thumbnail' in r.lower() for r in recommendations):
            recommendations.append("💡 Buat thumbnail yang menarik untuk CTR tinggi")

        return {
            'score': score,
            'grade': grade,
            'passed': passed,
            'checks': checks,
            'recommendations': recommendations,
            'video_info': {
                'path': video_path,
                'duration': duration,
                'duration_str': f"{int(duration//60)}:{int(duration%60):02d}",
                'resolution': f"{video_stream.get('width', '?')}x{video_stream.get('height', '?')}" if video_stream else 'Unknown',
                'format': ext.upper(),
            }
        }

    def format_report(self, result):
        """Format check result ke teks yang mudah dibaca."""
        lines = []
        lines.append("=" * 55)
        lines.append("📊 ADSENSE COMPLIANCE CHECK REPORT")
        lines.append("=" * 55)
        lines.append(f"📁 File: {result['video_info']['path']}")
        lines.append(f"⏱ Durasi: {result['video_info']['duration_str']}")
        lines.append(f"📐 Resolusi: {result['video_info']['resolution']}")
        lines.append(f"📦 Format: {result['video_info']['format']}")
        lines.append("")
        lines.append(f"🏆 SCORE: {result['score']}/100 (Grade: {result['grade']})")
        lines.append(f"{'✅ LULUS' if result['passed'] else '❌ BELUM LULUS'} — "
                     f"{'Video siap monetisasi!' if result['passed'] else 'Perlu perbaikan.'}")
        lines.append("")
        lines.append("─" * 55)
        lines.append("DETAIL CHECKS:")
        lines.append("─" * 55)

        for check in result['checks']:
            lines.append(f"  {check['message']}")
            lines.append(f"    → {check['name']}: {check['value']}")

        if result['recommendations']:
            lines.append("")
            lines.append("─" * 55)
            lines.append("REKOMENDASI:")
            lines.append("─" * 55)
            for i, rec in enumerate(result['recommendations'], 1):
                lines.append(f"  {i}. {rec}")

        lines.append("")
        lines.append("=" * 55)
        return "\n".join(lines)
