"""
Auto Translate Subtitle — Terjemahkan subtitle ke bahasa lain
Menggunakan deep-translator (Google Translate gratis, tanpa API key)
"""
import os
import re
import time


class SubtitleTranslator:
    """Translate SRT/ASS subtitle files to other languages."""

    # Supported languages (common ones)
    LANGUAGES = {
        'id': 'Indonesian',
        'en': 'English',
        'ms': 'Malay',
        'zh-CN': 'Chinese (Simplified)',
        'zh-TW': 'Chinese (Traditional)',
        'ja': 'Japanese',
        'ko': 'Korean',
        'hi': 'Hindi',
        'ar': 'Arabic',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'th': 'Thai',
        'vi': 'Vietnamese',
        'tl': 'Filipino',
    }

    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _parse_srt(self, srt_path):
        """Parse SRT file into list of subtitle entries."""
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        entries = []
        blocks = re.split(r'\n\s*\n', content.strip())

        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                index = lines[0].strip()
                timestamp = lines[1].strip()
                text = '\n'.join(lines[2:]).strip()
                entries.append({
                    'index': index,
                    'timestamp': timestamp,
                    'text': text
                })

        return entries

    def _parse_ass(self, ass_path):
        """Parse ASS file, extract dialogue lines."""
        with open(ass_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        header_lines = []
        dialogue_lines = []

        for line in lines:
            if line.strip().startswith('Dialogue:'):
                dialogue_lines.append(line)
            else:
                header_lines.append(line)

        return header_lines, dialogue_lines

    def _extract_ass_text(self, dialogue_line):
        """Extract text portion from ASS Dialogue line."""
        # Dialogue: 0,0:00:01.00,0:00:05.00,Default,,0,0,0,,Text here
        parts = dialogue_line.split(',', 9)
        if len(parts) >= 10:
            text = parts[9].strip()
            # Remove ASS override tags like {\b1} {\an8} etc.
            clean_text = re.sub(r'\{\\[^}]*\}', '', text)
            return clean_text, parts[:9]
        return dialogue_line, []

    def _rebuild_ass_dialogue(self, parts, translated_text):
        """Rebuild ASS Dialogue line with translated text."""
        return ','.join(parts) + ',' + translated_text + '\n'

    def translate_text_batch(self, texts, source_lang='id', target_lang='en', batch_size=30):
        """Translate a list of texts using deep-translator (Google)."""
        try:
            from deep_translator import GoogleTranslator
        except ImportError:
            raise ImportError(
                "deep-translator belum terinstall.\n"
                "Jalankan: pip install deep-translator"
            )

        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = []

        # Translate in batches to avoid rate limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            # Filter empty strings
            non_empty_indices = [j for j, t in enumerate(batch) if t.strip()]
            non_empty_texts = [batch[j] for j in non_empty_indices]

            if non_empty_texts:
                try:
                    # deep-translator supports batch via translate_batch
                    results = translator.translate_batch(non_empty_texts)
                except Exception:
                    # Fallback: translate one by one
                    results = []
                    for text in non_empty_texts:
                        try:
                            results.append(translator.translate(text))
                        except Exception:
                            results.append(text)  # Keep original on failure
                        time.sleep(0.1)

                # Rebuild full batch with empty strings preserved
                batch_result = list(batch)
                for idx, j in enumerate(non_empty_indices):
                    if idx < len(results) and results[idx]:
                        batch_result[j] = results[idx]

                translated.extend(batch_result)
            else:
                translated.extend(batch)

            # Rate limit pause between batches
            if i + batch_size < len(texts):
                time.sleep(0.5)

        return translated

    def translate_srt(self, srt_path, source_lang='id', target_lang='en'):
        """Translate an SRT subtitle file."""
        entries = self._parse_srt(srt_path)
        if not entries:
            raise ValueError(f"No subtitle entries found in {srt_path}")

        # Extract all texts
        texts = [e['text'] for e in entries]

        # Translate
        translated_texts = self.translate_text_batch(texts, source_lang, target_lang)

        # Rebuild SRT
        output_lines = []
        for i, entry in enumerate(entries):
            output_lines.append(entry['index'])
            output_lines.append(entry['timestamp'])
            if i < len(translated_texts):
                output_lines.append(translated_texts[i])
            else:
                output_lines.append(entry['text'])
            output_lines.append('')  # Blank line separator

        # Save
        base = os.path.splitext(os.path.basename(srt_path))[0]
        output_path = os.path.join(self.output_dir, f"{base}_{target_lang}.srt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))

        return output_path

    def translate_ass(self, ass_path, source_lang='id', target_lang='en'):
        """Translate an ASS subtitle file."""
        header_lines, dialogue_lines = self._parse_ass(ass_path)

        if not dialogue_lines:
            raise ValueError(f"No dialogue entries found in {ass_path}")

        # Extract texts and parts
        texts = []
        parts_list = []
        for line in dialogue_lines:
            text, parts = self._extract_ass_text(line)
            texts.append(text)
            parts_list.append(parts)

        # Translate
        translated_texts = self.translate_text_batch(texts, source_lang, target_lang)

        # Rebuild ASS
        output_lines = list(header_lines)
        for i, parts in enumerate(parts_list):
            if parts and i < len(translated_texts):
                output_lines.append(self._rebuild_ass_dialogue(parts, translated_texts[i]))
            else:
                output_lines.append(dialogue_lines[i])

        # Save
        base = os.path.splitext(os.path.basename(ass_path))[0]
        output_path = os.path.join(self.output_dir, f"{base}_{target_lang}.ass")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(output_lines)

        return output_path

    def translate_subtitle(self, subtitle_path, source_lang='id', target_lang='en'):
        """Auto-detect format and translate subtitle file."""
        ext = os.path.splitext(subtitle_path)[1].lower()

        if ext == '.srt':
            return self.translate_srt(subtitle_path, source_lang, target_lang)
        elif ext == '.ass':
            return self.translate_ass(subtitle_path, source_lang, target_lang)
        else:
            raise ValueError(f"Unsupported subtitle format: {ext}. Use .srt or .ass")

    def translate_multi(self, subtitle_path, source_lang='id', target_langs=None):
        """Translate subtitle to multiple languages at once."""
        if target_langs is None:
            target_langs = ['en']

        results = {}
        for lang in target_langs:
            if lang == source_lang:
                continue
            try:
                output = self.translate_subtitle(subtitle_path, source_lang, lang)
                results[lang] = {'status': 'success', 'path': output}
            except Exception as e:
                results[lang] = {'status': 'error', 'error': str(e)}

        return results

    @classmethod
    def get_supported_languages(cls):
        """Return dict of supported language codes and names."""
        return cls.LANGUAGES.copy()
