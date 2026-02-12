"""
Modul Batch Processing - Proses banyak video sekaligus
"""
import os
import json
import threading
from datetime import datetime


class BatchProcessor:
    """Proses banyak video YouTube sekaligus."""

    def __init__(self, output_base_dir="output"):
        self.output_base_dir = output_base_dir
        os.makedirs(output_base_dir, exist_ok=True)
        self.progress_callback = None
        self.results = []
        self.is_running = False
        self.should_stop = False

    def set_progress_callback(self, callback):
        """callback(video_index, total_videos, percent, status_text)"""
        self.progress_callback = callback

    def _update(self, idx, total, pct, text):
        if self.progress_callback:
            self.progress_callback(idx, total, pct, text)

    def stop(self):
        """Stop batch processing."""
        self.should_stop = True

    def process_url_list(self, urls, options):
        """
        Proses list URL video.

        Args:
            urls: List of YouTube URLs
            options: dict dengan opsi optimasi:
                {
                    'subtitle': True/False,
                    'silence': True/False,
                    'audio_enhance': True/False,
                    'speed': False,
                    'thumbnail': True/False,
                    'seo': True/False,
                    'shorts': False,
                    'youtube_export': True/False,
                    'watermark_logo': None or path,
                    'color_grade': None or preset name,
                    'whisper_model': 'base',
                    'language': 'id',
                    'resolution': '1080p',
                }

        Returns:
            List of result dicts
        """
        self.is_running = True
        self.should_stop = False
        self.results = []
        total = len(urls)

        for i, url in enumerate(urls):
            if self.should_stop:
                self._update(i, total, 0, "Batch processing dihentikan!")
                break

            url = url.strip()
            if not url:
                continue

            self._update(i + 1, total, 0, f"Video {i+1}/{total}: Memulai...")

            # Buat output dir per video
            video_dir = os.path.join(self.output_base_dir, f"video_{i+1:03d}")
            os.makedirs(video_dir, exist_ok=True)

            result = {
                'url': url,
                'index': i + 1,
                'status': 'processing',
                'output_dir': video_dir,
                'outputs': {},
                'error': None,
            }

            try:
                # Step 1: Download
                self._update(i + 1, total, 10, f"Video {i+1}/{total}: Downloading...")
                from app.downloader import VideoDownloader
                dl = VideoDownloader(output_dir=video_dir)
                video_path = dl.download(url, quality=options.get('resolution', 'best'))
                result['outputs']['original'] = video_path

                current_video = video_path

                # Step 2: Audio Enhance
                if options.get('audio_enhance', False):
                    self._update(i + 1, total, 25, f"Video {i+1}/{total}: Enhancing audio...")
                    from app.editor import VideoEditor
                    editor = VideoEditor(output_dir=video_dir)
                    current_video = editor.enhance_audio(current_video)
                    result['outputs']['audio_enhanced'] = current_video

                # Step 3: Remove Silence
                if options.get('silence', False):
                    self._update(i + 1, total, 35, f"Video {i+1}/{total}: Removing silence...")
                    from app.editor import VideoEditor
                    editor = VideoEditor(output_dir=video_dir)
                    current_video = editor.remove_silence(current_video)
                    result['outputs']['no_silence'] = current_video

                # Step 4: Speed
                if options.get('speed', False):
                    self._update(i + 1, total, 45, f"Video {i+1}/{total}: Adjusting speed...")
                    from app.editor import VideoEditor
                    editor = VideoEditor(output_dir=video_dir)
                    current_video = editor.adjust_speed(current_video, speed=1.05)
                    result['outputs']['speed_adjusted'] = current_video

                # Step 5: Color Grading
                if options.get('color_grade'):
                    self._update(i + 1, total, 50, f"Video {i+1}/{total}: Color grading...")
                    from app.color_grading import ColorGrading
                    cg = ColorGrading(output_dir=video_dir)
                    current_video = cg.apply_preset(current_video, options['color_grade'])
                    result['outputs']['color_graded'] = current_video

                # Step 6: Subtitle
                if options.get('subtitle', False):
                    self._update(i + 1, total, 55, f"Video {i+1}/{total}: Generating subtitles...")
                    from app.subtitler import AutoSubtitler
                    lang = options.get('language', 'id')
                    if lang == 'auto':
                        lang = None
                    subtitler = AutoSubtitler(
                        model_size=options.get('whisper_model', 'base'),
                        output_dir=video_dir
                    )
                    sub_result = subtitler.full_pipeline(current_video, language=lang)
                    if sub_result['video_output']:
                        current_video = sub_result['video_output']
                    result['outputs']['subtitled'] = current_video
                    result['outputs']['subtitle_file'] = sub_result['subtitle_path']

                # Step 7: Watermark
                if options.get('watermark_logo'):
                    self._update(i + 1, total, 70, f"Video {i+1}/{total}: Adding watermark...")
                    from app.watermark import WatermarkOverlay
                    wm = WatermarkOverlay(output_dir=video_dir)
                    current_video = wm.add_image_watermark(
                        current_video, options['watermark_logo']
                    )
                    result['outputs']['watermarked'] = current_video

                # Step 8: YouTube Export
                if options.get('youtube_export', False):
                    self._update(i + 1, total, 80, f"Video {i+1}/{total}: Exporting...")
                    from app.editor import VideoEditor
                    editor = VideoEditor(output_dir=video_dir)
                    current_video = editor.export_for_youtube(
                        current_video, resolution=options.get('resolution', '1080p')
                    )
                    result['outputs']['final'] = current_video

                # Step 9: Thumbnail
                if options.get('thumbnail', False):
                    self._update(i + 1, total, 85, f"Video {i+1}/{total}: Generating thumbnails...")
                    from app.thumbnail import ThumbnailGenerator
                    tg = ThumbnailGenerator(output_dir=video_dir)
                    thumbs = tg.batch_generate(current_video, "DRAMA PENDEK", num_options=3)
                    result['outputs']['thumbnails'] = thumbs

                # Step 10: SEO
                if options.get('seo', False):
                    self._update(i + 1, total, 90, f"Video {i+1}/{total}: Generating SEO...")
                    from app.title_generator import TitleGenerator
                    tg = TitleGenerator()
                    seo = tg.generate_seo_package()
                    
                    desc_path = os.path.join(video_dir, "description.txt")
                    with open(desc_path, 'w', encoding='utf-8') as f:
                        f.write(seo['description'])
                    tags_path = os.path.join(video_dir, "tags.txt")
                    with open(tags_path, 'w', encoding='utf-8') as f:
                        f.write("\n".join(seo['tags']))
                    
                    result['outputs']['seo_description'] = desc_path
                    result['outputs']['seo_tags'] = tags_path

                # Step 11: Shorts
                if options.get('shorts', False):
                    self._update(i + 1, total, 95, f"Video {i+1}/{total}: Creating Shorts...")
                    from app.editor import VideoEditor
                    editor = VideoEditor(output_dir=video_dir)
                    shorts = editor.create_shorts_clip(current_video, 0, 60)
                    result['outputs']['shorts'] = shorts

                result['status'] = 'success'
                self._update(i + 1, total, 100, f"Video {i+1}/{total}: ✅ Selesai!")

            except Exception as e:
                result['status'] = 'error'
                result['error'] = str(e)
                self._update(i + 1, total, 100, f"Video {i+1}/{total}: ❌ Error: {e}")

            self.results.append(result)

        # Save batch report
        self._save_report()
        self.is_running = False
        return self.results

    def _save_report(self):
        """Save batch processing report."""
        report_path = os.path.join(self.output_base_dir, "batch_report.json")
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_videos': len(self.results),
            'successful': sum(1 for r in self.results if r['status'] == 'success'),
            'failed': sum(1 for r in self.results if r['status'] == 'error'),
            'results': self.results,
        }
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return report_path

    def process_from_file(self, file_path, options):
        """
        Proses URL dari text file (satu URL per baris).

        Args:
            file_path: Path ke file .txt berisi URL
            options: dict opsi optimasi
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return self.process_url_list(urls, options)
