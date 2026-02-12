"""
Modul Auto Chapter Generator
Generate timestamps/chapters otomatis dari subtitle/transcription
YouTube suka video dengan chapters — meningkatkan SEO & engagement
"""
import os
import re


class ChapterGenerator:
    """Generate YouTube chapters otomatis dari transcription."""

    # Keywords yang menandai perubahan scene/topik
    SCENE_KEYWORDS = {
        'id': [
            # Intro patterns
            'selamat datang', 'halo', 'hai', 'perkenalkan',
            # Transition patterns
            'sementara itu', 'kemudian', 'setelah itu', 'beberapa', 'tahun kemudian',
            'hari berikutnya', 'esok hari', 'malam itu', 'pagi hari',
            'di sisi lain', 'di tempat lain',
            # Conflict patterns
            'tapi', 'namun', 'akan tetapi', 'sayangnya', 'tiba-tiba',
            'ternyata', 'rupanya',
            # Climax patterns
            'akhirnya', 'pada akhirnya', 'sekarang',
            # Ending patterns
            'terima kasih', 'subscribe', 'jangan lupa', 'sampai jumpa',
        ],
        'en': [
            'welcome', 'hello', 'hi everyone',
            'meanwhile', 'later', 'after that', 'years later', 'next day',
            'however', 'but', 'suddenly', 'unfortunately',
            'it turns out', 'the truth is',
            'finally', 'in the end',
            'thank you', 'subscribe', 'see you',
        ]
    }

    CHAPTER_LABELS = {
        'id': {
            'intro': 'Pembuka',
            'conflict_start': 'Konflik Dimulai',
            'rising_action': 'Masalah Semakin Besar',
            'turning_point': 'Titik Balik',
            'climax': 'Klimaks',
            'resolution': 'Penyelesaian',
            'ending': 'Ending',
        },
        'en': {
            'intro': 'Introduction',
            'conflict_start': 'Conflict Begins',
            'rising_action': 'Rising Action',
            'turning_point': 'Turning Point',
            'climax': 'Climax',
            'resolution': 'Resolution',
            'ending': 'Ending',
        }
    }

    def __init__(self, language='id'):
        self.language = language
        self.keywords = self.SCENE_KEYWORDS.get(language, self.SCENE_KEYWORDS['id'])
        self.labels = self.CHAPTER_LABELS.get(language, self.CHAPTER_LABELS['id'])

    def generate_from_transcription(self, transcription, min_chapter_duration=60,
                                      max_chapters=8):
        """
        Generate chapters dari hasil transcription Whisper.

        Args:
            transcription: dict dari AutoSubtitler.transcribe()
                           {'segments': [{'start': float, 'end': float, 'text': str}]}
            min_chapter_duration: Minimum durasi per chapter (detik)
            max_chapters: Maximum jumlah chapters

        Returns:
            List of {'time': seconds, 'label': str}
        """
        segments = transcription.get('segments', [])
        if not segments:
            return []

        total_duration = segments[-1]['end']
        chapters = []

        # Method 1: Keyword-based detection
        keyword_chapters = self._detect_by_keywords(segments)

        # Method 2: Time-based structure (drama structure)
        structure_chapters = self._generate_drama_structure(total_duration)

        # Method 3: Silence/pause-based (long pauses = scene change)
        pause_chapters = self._detect_by_pauses(segments, min_pause=2.0)

        # Merge & deduplicate
        all_chapters = keyword_chapters + structure_chapters + pause_chapters
        chapters = self._merge_chapters(all_chapters, min_chapter_duration, max_chapters)

        # Pastikan chapter pertama ada di 00:00
        if not chapters or chapters[0]['time'] > 1:
            chapters.insert(0, {'time': 0, 'label': self.labels['intro']})

        return chapters

    def _detect_by_keywords(self, segments):
        """Detect scene changes based on keywords in transcript."""
        chapters = []
        for seg in segments:
            text_lower = seg['text'].lower()
            for keyword in self.keywords:
                if keyword in text_lower:
                    chapters.append({
                        'time': seg['start'],
                        'label': self._guess_label_from_keyword(keyword),
                        'confidence': 0.7,
                    })
                    break
        return chapters

    def _guess_label_from_keyword(self, keyword):
        """Guess chapter label from keyword."""
        intro_kw = ['selamat datang', 'halo', 'hai', 'welcome', 'hello']
        conflict_kw = ['tapi', 'namun', 'however', 'but', 'sayangnya', 'unfortunately']
        climax_kw = ['tiba-tiba', 'ternyata', 'suddenly', 'it turns out']
        end_kw = ['akhirnya', 'finally', 'in the end', 'pada akhirnya']
        outro_kw = ['terima kasih', 'subscribe', 'thank you', 'sampai jumpa']

        if keyword in intro_kw:
            return self.labels['intro']
        elif keyword in conflict_kw:
            return self.labels['conflict_start']
        elif keyword in climax_kw:
            return self.labels['turning_point']
        elif keyword in end_kw:
            return self.labels['resolution']
        elif keyword in outro_kw:
            return self.labels['ending']
        else:
            return self.labels['rising_action']

    def _generate_drama_structure(self, total_duration):
        """Generate chapters based on typical drama story structure."""
        chapters = []

        if total_duration < 120:
            # Video pendek: 3 chapters
            chapters = [
                {'time': 0, 'label': self.labels['intro'], 'confidence': 0.5},
                {'time': total_duration * 0.3, 'label': self.labels['conflict_start'], 'confidence': 0.5},
                {'time': total_duration * 0.75, 'label': self.labels['resolution'], 'confidence': 0.5},
            ]
        elif total_duration < 600:
            # Video medium: 5 chapters
            chapters = [
                {'time': 0, 'label': self.labels['intro'], 'confidence': 0.5},
                {'time': total_duration * 0.15, 'label': self.labels['conflict_start'], 'confidence': 0.5},
                {'time': total_duration * 0.4, 'label': self.labels['rising_action'], 'confidence': 0.5},
                {'time': total_duration * 0.65, 'label': self.labels['turning_point'], 'confidence': 0.5},
                {'time': total_duration * 0.85, 'label': self.labels['resolution'], 'confidence': 0.5},
            ]
        else:
            # Video panjang: 7 chapters
            chapters = [
                {'time': 0, 'label': self.labels['intro'], 'confidence': 0.5},
                {'time': total_duration * 0.1, 'label': self.labels['conflict_start'], 'confidence': 0.5},
                {'time': total_duration * 0.25, 'label': self.labels['rising_action'], 'confidence': 0.5},
                {'time': total_duration * 0.45, 'label': self.labels['turning_point'], 'confidence': 0.5},
                {'time': total_duration * 0.6, 'label': self.labels['climax'], 'confidence': 0.5},
                {'time': total_duration * 0.78, 'label': self.labels['resolution'], 'confidence': 0.5},
                {'time': total_duration * 0.92, 'label': self.labels['ending'], 'confidence': 0.5},
            ]

        return chapters

    def _detect_by_pauses(self, segments, min_pause=2.0):
        """Detect scene changes based on long pauses between segments."""
        chapters = []
        for i in range(1, len(segments)):
            gap = segments[i]['start'] - segments[i - 1]['end']
            if gap >= min_pause:
                chapters.append({
                    'time': segments[i]['start'],
                    'label': f"Scene {len(chapters) + 2}",
                    'confidence': 0.6,
                })
        return chapters

    def _merge_chapters(self, chapters, min_duration, max_count):
        """Merge nearby chapters and limit total count."""
        if not chapters:
            return []

        # Sort by time
        chapters.sort(key=lambda c: c['time'])

        # Remove chapters too close together
        merged = [chapters[0]]
        for ch in chapters[1:]:
            if ch['time'] - merged[-1]['time'] >= min_duration:
                # Prefer higher confidence
                merged.append(ch)
            elif ch.get('confidence', 0) > merged[-1].get('confidence', 0):
                merged[-1] = ch

        # Limit count — keep highest confidence
        if len(merged) > max_count:
            merged.sort(key=lambda c: c.get('confidence', 0), reverse=True)
            merged = merged[:max_count]
            merged.sort(key=lambda c: c['time'])

        # Clean up
        for ch in merged:
            ch.pop('confidence', None)

        return merged

    def format_timestamps(self, chapters):
        """
        Format chapters ke teks timestamps untuk deskripsi YouTube.

        Format yang dikenali YouTube:
        00:00 - Title
        01:30 - Next Chapter
        """
        lines = []
        for ch in chapters:
            t = ch['time']
            mins = int(t // 60)
            secs = int(t % 60)
            if t >= 3600:
                hrs = int(t // 3600)
                mins = int((t % 3600) // 60)
                lines.append(f"{hrs}:{mins:02d}:{secs:02d} - {ch['label']}")
            else:
                lines.append(f"{mins:02d}:{secs:02d} - {ch['label']}")
        return "\n".join(lines)

    def generate_from_srt(self, srt_path, min_chapter_duration=60, max_chapters=8):
        """
        Generate chapters dari file SRT.

        Args:
            srt_path: Path ke file .srt
        """
        segments = self._parse_srt(srt_path)
        transcription = {'segments': segments}
        return self.generate_from_transcription(
            transcription, min_chapter_duration, max_chapters
        )

    def _parse_srt(self, srt_path):
        """Parse SRT file ke format segments."""
        segments = []
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        blocks = content.strip().split('\n\n')
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                # Parse timestamp line
                time_match = re.match(
                    r'(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)',
                    lines[1]
                )
                if time_match:
                    g = time_match.groups()
                    start = int(g[0])*3600 + int(g[1])*60 + int(g[2]) + int(g[3])/1000
                    end = int(g[4])*3600 + int(g[5])*60 + int(g[6]) + int(g[7])/1000
                    text = ' '.join(lines[2:])
                    segments.append({
                        'start': start,
                        'end': end,
                        'text': text,
                    })

        return segments

    def save_chapters(self, chapters, output_path):
        """Save chapters ke file teks."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("YOUTUBE CHAPTERS / TIMESTAMPS\n")
            f.write("=" * 40 + "\n")
            f.write("Copy-paste ke deskripsi video:\n\n")
            f.write(self.format_timestamps(chapters))
            f.write("\n\n")
            f.write("=" * 40 + "\n")
            f.write("Note: Chapter pertama HARUS mulai dari 00:00\n")
            f.write("Minimum 3 chapters, minimum 10 detik per chapter\n")
        return output_path
