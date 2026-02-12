"""
Intro/Outro Template — Auto-sisipkan intro & outro branded ke video
Menggunakan FFmpeg untuk concat video segments
"""
import os
import subprocess
from app.ffmpeg_util import get_ffmpeg_path, get_ffprobe_path


class IntroOutroManager:
    """Manage and apply intro/outro templates to videos."""

    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        self.ffmpeg = get_ffmpeg_path()
        self.ffprobe = get_ffprobe_path()
        os.makedirs(output_dir, exist_ok=True)

    def get_video_info(self, video_path):
        """Get video resolution, fps, codec info."""
        cmd = [
            self.ffprobe, '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams', '-show_format',
            video_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            import json
            data = json.loads(result.stdout)
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    return {
                        'width': int(stream.get('width', 1920)),
                        'height': int(stream.get('height', 1080)),
                        'fps': eval(stream.get('r_frame_rate', '30/1')),
                        'codec': stream.get('codec_name', 'h264'),
                    }
        except Exception:
            pass
        return {'width': 1920, 'height': 1080, 'fps': 30, 'codec': 'h264'}

    def _normalize_video(self, input_path, output_path, width=1920, height=1080, fps=30):
        """Normalize a video to consistent resolution/fps/codec for safe concatenation."""
        cmd = [
            self.ffmpeg, '-y', '-i', input_path,
            '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,'
                   f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black',
            '-r', str(fps),
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
            '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            output_path
        ]
        subprocess.run(cmd, capture_output=True, timeout=300)
        return output_path

    def create_text_intro(self, text="Film Pendek Pahm", subtitle="",
                          duration=4, width=1920, height=1080,
                          bg_color="black", text_color="white",
                          font_size=72, subtitle_size=36):
        """Create a simple branded text intro using FFmpeg."""
        output_path = os.path.join(self.output_dir, "intro_generated.mp4")

        # Build drawtext filter
        drawtext = (
            f"drawtext=text='{text}':fontsize={font_size}:fontcolor={text_color}:"
            f"x=(w-text_w)/2:y=(h-text_h)/2-30:"
            f"font='Segoe UI':enable='between(t,0,{duration})'"
        )

        if subtitle:
            drawtext += (
                f",drawtext=text='{subtitle}':fontsize={subtitle_size}:"
                f"fontcolor=gray:x=(w-text_w)/2:y=(h/2)+40:"
                f"font='Segoe UI':enable='between(t,0,{duration})'"
            )

        # Fade in/out
        fade = f"fade=t=in:st=0:d=1,fade=t=out:st={duration - 1}:d=1"

        cmd = [
            self.ffmpeg, '-y',
            '-f', 'lavfi', '-i',
            f'color=c={bg_color}:s={width}x{height}:d={duration}:r=30',
            '-f', 'lavfi', '-i',
            f'anullsrc=channel_layout=stereo:sample_rate=44100',
            '-vf', f'{drawtext},{fade}',
            '-t', str(duration),
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
            '-c:a', 'aac', '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            output_path
        ]

        subprocess.run(cmd, capture_output=True, timeout=120)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        raise RuntimeError("Failed to create text intro")

    def create_text_outro(self, text="Terima Kasih Sudah Menonton!",
                          subscribe_text="SUBSCRIBE & LIKE 👍",
                          duration=5, width=1920, height=1080,
                          bg_color="black", text_color="white"):
        """Create a branded text outro."""
        output_path = os.path.join(self.output_dir, "outro_generated.mp4")

        drawtext = (
            f"drawtext=text='{text}':fontsize=64:fontcolor={text_color}:"
            f"x=(w-text_w)/2:y=(h/2)-60:"
            f"font='Segoe UI':enable='between(t,0,{duration})',"
            f"drawtext=text='{subscribe_text}':fontsize=48:"
            f"fontcolor=red:x=(w-text_w)/2:y=(h/2)+30:"
            f"font='Segoe UI':enable='between(t,0.5,{duration})',"
            f"fade=t=in:st=0:d=1,fade=t=out:st={duration - 1}:d=1"
        )

        cmd = [
            self.ffmpeg, '-y',
            '-f', 'lavfi', '-i',
            f'color=c={bg_color}:s={width}x{height}:d={duration}:r=30',
            '-f', 'lavfi', '-i',
            f'anullsrc=channel_layout=stereo:sample_rate=44100',
            '-vf', drawtext,
            '-t', str(duration),
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
            '-c:a', 'aac', '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            output_path
        ]

        subprocess.run(cmd, capture_output=True, timeout=120)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        raise RuntimeError("Failed to create text outro")

    def add_intro(self, video_path, intro_path):
        """Prepend intro video to main video."""
        return self._concat_videos([intro_path, video_path], "with_intro.mp4")

    def add_outro(self, video_path, outro_path):
        """Append outro video to main video."""
        return self._concat_videos([video_path, outro_path], "with_outro.mp4")

    def add_intro_outro(self, video_path, intro_path=None, outro_path=None):
        """Add both intro and outro to video."""
        segments = []
        if intro_path and os.path.exists(intro_path):
            segments.append(intro_path)
        segments.append(video_path)
        if outro_path and os.path.exists(outro_path):
            segments.append(outro_path)

        if len(segments) == 1:
            return video_path  # Nothing to concat

        return self._concat_videos(segments, "with_intro_outro.mp4")

    def _concat_videos(self, video_paths, output_name):
        """Concatenate multiple videos using FFmpeg concat demuxer."""
        # Get target specs from main video (longest one)
        main_info = self.get_video_info(video_paths[-1] if len(video_paths) > 1 else video_paths[0])
        w, h, fps = main_info['width'], main_info['height'], int(main_info['fps'])

        # Normalize all segments
        temp_files = []
        for i, vpath in enumerate(video_paths):
            temp_path = os.path.join(self.output_dir, f"_concat_temp_{i}.mp4")
            self._normalize_video(vpath, temp_path, w, h, fps)
            temp_files.append(temp_path)

        # Create concat list file
        list_path = os.path.join(self.output_dir, "_concat_list.txt")
        with open(list_path, 'w', encoding='utf-8') as f:
            for tf in temp_files:
                # FFmpeg concat needs forward slashes or escaped backslashes
                safe_path = tf.replace('\\', '/')
                f.write(f"file '{safe_path}'\n")

        output_path = os.path.join(self.output_dir, output_name)
        cmd = [
            self.ffmpeg, '-y',
            '-f', 'concat', '-safe', '0',
            '-i', list_path,
            '-c', 'copy',
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        # Cleanup temp files
        for tf in temp_files:
            try:
                os.remove(tf)
            except OSError:
                pass
        try:
            os.remove(list_path)
        except OSError:
            pass

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path

        raise RuntimeError(f"Failed to concatenate videos: {result.stderr[:500]}")

    def full_pipeline(self, video_path, channel_name="Film Pendek Pahm",
                      tagline="", intro_path=None, outro_path=None,
                      auto_generate=True):
        """
        Full intro/outro pipeline.
        If intro_path/outro_path provided: use those files.
        If auto_generate=True and no files: generate text-based intro/outro.
        """
        info = self.get_video_info(video_path)
        w, h = info['width'], info['height']

        # Generate if needed
        if auto_generate and not intro_path:
            intro_path = self.create_text_intro(
                text=channel_name,
                subtitle=tagline or "Presents",
                duration=4, width=w, height=h
            )

        if auto_generate and not outro_path:
            outro_path = self.create_text_outro(
                text="Terima Kasih Sudah Menonton!",
                subscribe_text="SUBSCRIBE & LIKE 👍",
                duration=5, width=w, height=h
            )

        return self.add_intro_outro(video_path, intro_path, outro_path)
