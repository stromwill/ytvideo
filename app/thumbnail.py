"""
Modul Thumbnail Generator - Buat thumbnail YouTube yang menarik
menggunakan Pillow (PIL)
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import subprocess
import json


class ThumbnailGenerator:
    """Generate thumbnail YouTube yang eye-catching."""

    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.YOUTUBE_SIZE = (1280, 720)  # Standard YouTube thumbnail

    def extract_best_frames(self, video_path, num_frames=10, output_prefix="frame"):
        """
        Extract frame-frame terbaik dari video.
        Menggunakan scene detection FFmpeg.
        
        Args:
            video_path: Path ke video
            num_frames: Jumlah frame yang di-extract
            output_prefix: Prefix nama file output
        
        Returns:
            List path ke frame images
        """
        frames_dir = os.path.join(self.output_dir, "frames")
        os.makedirs(frames_dir, exist_ok=True)

        # Dapatkan durasi video
        probe_cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', video_path
        ]
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        info = json.loads(result.stdout)
        duration = float(info['format']['duration'])

        # Extract frames di interval yang merata
        interval = duration / (num_frames + 1)
        frame_paths = []

        for i in range(1, num_frames + 1):
            timestamp = interval * i
            output_path = os.path.join(frames_dir, f"{output_prefix}_{i:03d}.jpg")
            
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(timestamp),
                '-i', video_path,
                '-vframes', '1',
                '-q:v', '2',
                output_path
            ]
            subprocess.run(cmd, capture_output=True)
            
            if os.path.exists(output_path):
                frame_paths.append(output_path)

        return frame_paths

    def _get_font(self, font_size, bold=True):
        """Coba load font, fallback ke default."""
        font_candidates = [
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/impact.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
        
        for font_path in font_candidates:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, font_size)
        
        # Fallback
        try:
            return ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            return ImageFont.load_default()

    def create_thumbnail(self, background_path, title_text, 
                         output_filename="thumbnail.jpg",
                         text_color=(255, 255, 255),
                         outline_color=(0, 0, 0),
                         overlay_color=(0, 0, 0, 120),
                         text_position="center",
                         font_size=72,
                         add_vignette=True,
                         add_color_boost=True):
        """
        Buat thumbnail YouTube dari gambar background + teks.
        
        Args:
            background_path: Path ke gambar background (frame dari video)
            title_text: Teks utama di thumbnail
            output_filename: Nama file output
            text_color: Warna teks (RGB)
            outline_color: Warna outline teks (RGB)
            overlay_color: Warna overlay gelap (RGBA)
            text_position: 'center', 'bottom', 'top'
            font_size: Ukuran font
            add_vignette: Tambah efek vignette
            add_color_boost: Boost saturation & contrast
        
        Returns:
            Path ke thumbnail
        """
        output_path = os.path.join(self.output_dir, output_filename)

        # Load & resize background
        img = Image.open(background_path).convert('RGBA')
        img = img.resize(self.YOUTUBE_SIZE, Image.LANCZOS)

        # Color boost
        if add_color_boost:
            rgb_img = img.convert('RGB')
            enhancer = ImageEnhance.Color(rgb_img)
            rgb_img = enhancer.enhance(1.3)  # Saturation boost
            enhancer = ImageEnhance.Contrast(rgb_img)
            rgb_img = enhancer.enhance(1.2)  # Contrast boost
            enhancer = ImageEnhance.Brightness(rgb_img)
            rgb_img = enhancer.enhance(1.05)
            img = rgb_img.convert('RGBA')

        # Vignette effect
        if add_vignette:
            vignette = Image.new('RGBA', self.YOUTUBE_SIZE, (0, 0, 0, 0))
            vignette_draw = ImageDraw.Draw(vignette)
            for i in range(80):
                alpha = int(i * 2.5)
                vignette_draw.rectangle(
                    [i, i, self.YOUTUBE_SIZE[0]-i, self.YOUTUBE_SIZE[1]-i],
                    outline=(0, 0, 0, alpha)
                )
            img = Image.alpha_composite(img, vignette)

        # Semi-transparent overlay
        overlay = Image.new('RGBA', self.YOUTUBE_SIZE, overlay_color)
        img = Image.alpha_composite(img, overlay)

        # Draw text
        draw = ImageDraw.Draw(img)
        font = self._get_font(font_size, bold=True)

        # Word wrap
        words = title_text.split()
        lines = []
        current_line = ""
        max_width = self.YOUTUBE_SIZE[0] - 100  # 50px padding each side

        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        # Calculate text position
        line_height = font_size + 10
        total_text_height = len(lines) * line_height

        if text_position == "center":
            y_start = (self.YOUTUBE_SIZE[1] - total_text_height) // 2
        elif text_position == "bottom":
            y_start = self.YOUTUBE_SIZE[1] - total_text_height - 60
        else:  # top
            y_start = 60

        # Draw text with outline
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.YOUTUBE_SIZE[0] - text_width) // 2
            y = y_start + i * line_height

            # Outline (draw text in 8 directions)
            outline_width = 3
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill=outline_color)

            # Main text
            draw.text((x, y), line, font=font, fill=text_color)

        # Convert to RGB and save
        final_img = img.convert('RGB')
        final_img.save(output_path, 'JPEG', quality=95)

        return output_path

    def create_split_thumbnail(self, left_image_path, right_image_path,
                                title_text="", output_filename="thumbnail_split.jpg",
                                divider_color=(255, 0, 0)):
        """
        Buat thumbnail split (2 gambar side by side) — populer untuk drama.
        Misal: kiri = MC miskin, kanan = MC kaya.
        """
        output_path = os.path.join(self.output_dir, output_filename)
        
        canvas = Image.new('RGB', self.YOUTUBE_SIZE, (0, 0, 0))
        
        half_width = self.YOUTUBE_SIZE[0] // 2
        
        # Left image
        left_img = Image.open(left_image_path).convert('RGB')
        left_img = left_img.resize((half_width, self.YOUTUBE_SIZE[1]), Image.LANCZOS)
        canvas.paste(left_img, (0, 0))
        
        # Right image
        right_img = Image.open(right_image_path).convert('RGB')
        right_img = right_img.resize((half_width, self.YOUTUBE_SIZE[1]), Image.LANCZOS)
        canvas.paste(right_img, (half_width, 0))
        
        # Divider line
        draw = ImageDraw.Draw(canvas)
        draw.line(
            [(half_width, 0), (half_width, self.YOUTUBE_SIZE[1])],
            fill=divider_color, width=6
        )
        
        # Title text overlay
        if title_text:
            canvas_rgba = canvas.convert('RGBA')
            # Dark bar at bottom
            overlay = Image.new('RGBA', self.YOUTUBE_SIZE, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle(
                [0, self.YOUTUBE_SIZE[1] - 120, self.YOUTUBE_SIZE[0], self.YOUTUBE_SIZE[1]],
                fill=(0, 0, 0, 180)
            )
            canvas_rgba = Image.alpha_composite(canvas_rgba, overlay)
            
            draw = ImageDraw.Draw(canvas_rgba)
            font = self._get_font(52, bold=True)
            bbox = draw.textbbox((0, 0), title_text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.YOUTUBE_SIZE[0] - text_width) // 2
            y = self.YOUTUBE_SIZE[1] - 95
            
            # Outline
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    draw.text((x+dx, y+dy), title_text, font=font, fill=(0, 0, 0))
            draw.text((x, y), title_text, font=font, fill=(255, 255, 255))
            
            canvas = canvas_rgba.convert('RGB')
        
        canvas.save(output_path, 'JPEG', quality=95)
        return output_path

    def batch_generate(self, video_path, title_text, num_options=5):
        """
        Generate beberapa opsi thumbnail sekaligus dari frame-frame video.
        
        Returns:
            List of thumbnail paths
        """
        frames = self.extract_best_frames(video_path, num_frames=num_options)
        thumbnails = []
        
        positions = ["center", "bottom", "center", "top", "bottom"]
        overlays = [
            (0, 0, 0, 120),
            (20, 0, 0, 140),
            (0, 0, 30, 100),
            (0, 0, 0, 80),
            (30, 0, 0, 160),
        ]
        
        for i, frame_path in enumerate(frames):
            pos = positions[i % len(positions)]
            overlay = overlays[i % len(overlays)]
            
            thumb_path = self.create_thumbnail(
                background_path=frame_path,
                title_text=title_text,
                output_filename=f"thumbnail_option_{i+1}.jpg",
                text_position=pos,
                overlay_color=overlay,
            )
            thumbnails.append(thumb_path)
        
        return thumbnails
