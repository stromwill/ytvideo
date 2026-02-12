"""
Modul Auto Subtitle - Generate subtitle otomatis menggunakan OpenAI Whisper
Lalu burn subtitle ke video menggunakan FFmpeg
"""
import os
import json
import subprocess


class AutoSubtitler:
    """Generate subtitle otomatis dari audio/video menggunakan Whisper."""

    def __init__(self, model_size="base", output_dir="temp"):
        """
        Args:
            model_size: Ukuran model Whisper - 'tiny', 'base', 'small', 'medium', 'large'
                       'tiny'  = Paling cepat, kurang akurat
                       'base'  = Cukup cepat, lumayan akurat (RECOMMENDED)
                       'small' = Lebih lambat, lebih akurat
                       'medium'= Lambat, akurat
                       'large' = Paling lambat, paling akurat (butuh GPU bagus)
        """
        self.model_size = model_size
        self.output_dir = output_dir
        self.model = None
        self.progress_callback = None
        os.makedirs(output_dir, exist_ok=True)

    def set_progress_callback(self, callback):
        self.progress_callback = callback

    def _update_progress(self, percent, text):
        if self.progress_callback:
            self.progress_callback(percent, text)

    def load_model(self):
        """Load Whisper model (download otomatis kalau belum ada)."""
        import whisper
        self._update_progress(10, f"Loading Whisper model '{self.model_size}'...")
        self.model = whisper.load_model(self.model_size)
        self._update_progress(20, "Model loaded!")
        return self.model

    def transcribe(self, audio_path, language="id"):
        """
        Transcribe audio/video ke teks + timestamp.
        
        Args:
            audio_path: Path ke file audio/video
            language: Bahasa ('id' untuk Indonesia, 'en' untuk English, None untuk auto-detect)
        
        Returns:
            dict dengan segments dan full text
        """
        if self.model is None:
            self.load_model()

        self._update_progress(30, "Mulai transcription...")

        options = {
            'verbose': False,
            'word_timestamps': True,
        }
        if language:
            options['language'] = language

        result = self.model.transcribe(audio_path, **options)

        self._update_progress(80, "Transcription selesai!")

        return {
            'text': result['text'],
            'language': result.get('language', language),
            'segments': [
                {
                    'id': seg['id'],
                    'start': seg['start'],
                    'end': seg['end'],
                    'text': seg['text'].strip(),
                }
                for seg in result['segments']
            ]
        }

    def generate_srt(self, transcription, output_filename="subtitle.srt"):
        """
        Generate file SRT dari hasil transcription.
        
        Args:
            transcription: Hasil dari self.transcribe()
            output_filename: Nama file SRT output
        
        Returns:
            Path ke file SRT
        """
        output_path = os.path.join(self.output_dir, output_filename)

        def format_time(seconds):
            hrs = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            ms = int((seconds % 1) * 1000)
            return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"

        with open(output_path, 'w', encoding='utf-8') as f:
            for i, seg in enumerate(transcription['segments'], 1):
                f.write(f"{i}\n")
                f.write(f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n")
                f.write(f"{seg['text']}\n\n")

        self._update_progress(90, f"SRT file berhasil dibuat: {output_path}")
        return output_path

    def generate_ass(self, transcription, output_filename="subtitle.ass",
                     font_name="Arial", font_size=20, 
                     primary_color="&H00FFFFFF", outline_color="&H00000000",
                     bold=True, outline_width=2, shadow=1,
                     position="bottom"):
        """
        Generate file ASS (Advanced SubStation Alpha) dengan styling lengkap.
        Lebih bagus dari SRT karena bisa di-style.
        
        Args:
            transcription: Hasil dari self.transcribe()
            font_name: Font yang dipakai
            font_size: Ukuran font
            primary_color: Warna teks (format ASS: &HAABBGGRR)
            outline_color: Warna outline
            bold: Bold atau tidak
            outline_width: Ketebalan outline
            shadow: Shadow depth
            position: 'bottom', 'top', 'middle'
        
        Returns:
            Path ke file ASS
        """
        output_path = os.path.join(self.output_dir, output_filename)

        alignment_map = {
            'bottom': 2,   # Bottom center
            'top': 8,      # Top center
            'middle': 5,   # Middle center
        }
        alignment = alignment_map.get(position, 2)
        bold_val = -1 if bold else 0

        def format_time_ass(seconds):
            hrs = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            cs = int((seconds % 1) * 100)
            return f"{hrs}:{mins:02d}:{secs:02d}.{cs:02d}"

        header = f"""[Script Info]
Title: Auto Generated Subtitle
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{primary_color},&H000000FF,{outline_color},&H80000000,{bold_val},0,0,0,100,100,0,0,1,{outline_width},{shadow},{alignment},20,20,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(header)
            for seg in transcription['segments']:
                start = format_time_ass(seg['start'])
                end = format_time_ass(seg['end'])
                text = seg['text'].replace('\n', '\\N')
                f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n")

        self._update_progress(90, f"ASS file berhasil dibuat: {output_path}")
        return output_path

    def burn_subtitle_to_video(self, video_path, subtitle_path, output_path=None,
                                subtitle_style=None):
        """
        Burn (hardcode) subtitle ke video menggunakan FFmpeg.
        
        Args:
            video_path: Path ke video input
            subtitle_path: Path ke file SRT atau ASS
            output_path: Path video output (default: video_subtitled.mp4)
            subtitle_style: Style override untuk SRT (diabaikan untuk ASS)
        
        Returns:
            Path ke video output
        """
        if output_path is None:
            base = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.output_dir, f"{base}_subtitled.mp4")

        self._update_progress(50, "Burning subtitle ke video...")

        # Escape path untuk FFmpeg filter (Windows)
        sub_path_escaped = subtitle_path.replace('\\', '/').replace(':', '\\:')

        if subtitle_path.endswith('.ass'):
            # ASS sudah punya styling sendiri
            vf = f"ass='{sub_path_escaped}'"
        else:
            # SRT - tambahkan styling
            if subtitle_style is None:
                subtitle_style = (
                    "FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,"
                    "OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1"
                )
            vf = f"subtitles='{sub_path_escaped}':force_style='{subtitle_style}'"

        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', vf,
            '-c:a', 'copy',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '18',
            output_path
        ]

        process = subprocess.run(cmd, capture_output=True, text=True)

        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {process.stderr}")

        self._update_progress(100, f"Video dengan subtitle berhasil dibuat: {output_path}")
        return output_path

    def full_pipeline(self, video_path, language="id", subtitle_format="ass",
                      burn_to_video=True, **style_kwargs):
        """
        Pipeline lengkap: Video → Transcribe → Subtitle → Burn ke video.
        
        Args:
            video_path: Path ke video
            language: Bahasa audio
            subtitle_format: 'srt' atau 'ass'
            burn_to_video: Burn subtitle ke video atau hanya generate file subtitle
            **style_kwargs: Keyword arguments untuk styling subtitle ASS
        
        Returns:
            dict dengan paths ke semua output
        """
        self._update_progress(5, "Memulai pipeline subtitle...")

        # Step 1: Transcribe
        transcription = self.transcribe(video_path, language=language)

        # Step 2: Generate subtitle file
        if subtitle_format == 'ass':
            sub_path = self.generate_ass(transcription, **style_kwargs)
        else:
            sub_path = self.generate_srt(transcription)

        result = {
            'transcription': transcription,
            'subtitle_path': sub_path,
            'video_output': None,
        }

        # Step 3: Burn to video
        if burn_to_video:
            video_out = self.burn_subtitle_to_video(video_path, sub_path)
            result['video_output'] = video_out

        self._update_progress(100, "Pipeline subtitle selesai!")
        return result
