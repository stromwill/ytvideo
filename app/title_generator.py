"""
Modul Title & SEO Generator - Generate judul, deskripsi, dan tags viral
untuk optimasi YouTube AdSense
"""
import random


class TitleGenerator:
    """Generate judul, deskripsi, dan tags YouTube yang viral & SEO-friendly."""

    # Template judul drama pendek yang terbukti viral
    TITLE_TEMPLATES = [
        # Pola: Konflik → Resolusi
        "{conflict}, {resolution}",
        "{conflict}! {resolution}",
        "{conflict}, Ternyata {twist}",
        "{setting}: {conflict}, {resolution}",
        
        # Pola: Emotional hook
        "Semua Menghina {mc}, Tapi {twist}",
        "{antagonist} {action_jahat}, Tapi Tidak Tahu Kalau {twist}",
        "Dikira {status_rendah}, Ternyata {status_tinggi}",
        "{mc} {disakiti}, {timeframe} Kemudian {balas_dendam}",
    ]

    CONFLICTS = [
        "Dibuang Pacar Matre",
        "Dihina Keluarga Pacar",
        "Diusir dari Rumah",
        "Dipecat dari Perusahaan",
        "Direndahkan di Depan Umum",
        "Ditolak Mertua Karena Miskin",
        "Dikhianati Sahabat Sendiri",
        "Ditipu Partner Bisnis",
        "Diceraikan Tanpa Alasan",
        "Dicampakkan Saat Paling Butuh",
    ]

    RESOLUTIONS = [
        "Dia Aktifkan Sistem dan Jadi Miliarder",
        "Ternyata Dia Pewaris Perusahaan Terbesar",
        "Identitas Aslinya Terungkap",
        "5 Tahun Kemudian Dia Kembali Sebagai CEO",
        "Dia Buktikan Semuanya Salah",
        "Sekarang Semua Orang Menyesal",
        "Pria Ini Balas dengan Cara Tak Terduga",
        "Dia Jadi Orang Terkaya di Kota",
    ]

    TAGS_BASE = [
        "drama pendek", "film pendek", "film pendek indonesia",
        "drama indonesia", "short film", "drama terbaru",
        "film pendek terbaru", "drama viral", "cerita pendek",
        "kisah inspiratif", "drama keluarga", "film pendek sedih",
    ]

    def generate_titles(self, theme=None, count=10):
        """
        Generate beberapa opsi judul viral.
        
        Args:
            theme: Tema spesifik (misal 'matre', 'mertua', 'CEO')
            count: Jumlah judul yang digenerate
        
        Returns:
            List of judul
        """
        titles = []
        
        for _ in range(count):
            conflict = random.choice(self.CONFLICTS)
            resolution = random.choice(self.RESOLUTIONS)
            template = random.choice(self.TITLE_TEMPLATES[:4])  # Basic templates
            
            title = template.format(
                conflict=conflict,
                resolution=resolution,
                twist=random.choice(self.RESOLUTIONS),
                setting="Drama Pendek",
                mc="Pria Ini",
            )
            
            if theme:
                # Prioritas judul yang mengandung tema
                if theme.lower() in title.lower():
                    titles.insert(0, title)
                else:
                    titles.append(title)
            else:
                titles.append(title)

        # Deduplicate
        seen = set()
        unique = []
        for t in titles:
            if t not in seen:
                seen.add(t)
                unique.append(t)

        return unique[:count]

    def generate_description(self, title, video_duration_minutes=10):
        """
        Generate deskripsi video yang SEO-friendly.
        
        Args:
            title: Judul video
            video_duration_minutes: Durasi video dalam menit
        """
        timestamps = self._generate_timestamps(video_duration_minutes)
        
        description = f"""{title}

Drama pendek Indonesia tentang perjuangan, pengkhianatan, dan pembalasan.
Kisah yang akan membuat kamu terharu dan terinspirasi.

⏱️ TIMESTAMPS:
{timestamps}

🎬 SINOPSIS:
Seorang pria biasa yang direndahkan oleh orang-orang terdekatnya.
Namun takdir berkata lain. Dengan tekad yang kuat, ia membuktikan
bahwa orang yang dianggap rendah bisa menjadi yang paling tinggi.

📌 Video ini adalah karya fiksi / drama pendek untuk hiburan.
Semua karakter dan kejadian dalam video ini fiktif.

🔔 Jangan lupa SUBSCRIBE dan nyalakan notifikasi untuk drama pendek terbaru!

#dramapendek #filmpendek #dramaindonesia #filmpendekIndonesia
#dramaViral #kisahInspiratif #ceritaPendek #dramaTerbaru
"""
        return description.strip()

    def _generate_timestamps(self, duration_minutes):
        """Generate timestamps otomatis."""
        timestamps = ["00:00 - Awal Cerita"]
        
        if duration_minutes >= 3:
            timestamps.append("01:30 - Konflik Dimulai")
        if duration_minutes >= 5:
            timestamps.append("03:00 - Titik Balik")
        if duration_minutes >= 7:
            timestamps.append(f"05:00 - Pembalasan")
        if duration_minutes >= 10:
            timestamps.append(f"08:00 - Klimaks")
            timestamps.append(f"{duration_minutes-1:02d}:00 - Ending")
        elif duration_minutes >= 5:
            timestamps.append(f"{duration_minutes-1:02d}:00 - Ending")
        
        return "\n".join(timestamps)

    def generate_tags(self, title, additional_keywords=None):
        """
        Generate tags YouTube yang optimal.
        YouTube merekomendasikan 3-5 tags utama + beberapa long-tail.
        
        Returns:
            List of tags
        """
        tags = list(self.TAGS_BASE)
        
        # Extract keywords dari judul
        title_words = title.lower().split()
        stop_words = {'di', 'dan', 'yang', 'ini', 'itu', 'dari', 'ke', 'untuk',
                      'dengan', 'dia', 'nya', 'tapi', 'oleh', 'dalam', 'pria',
                      'saat', 'jadi', 'karena', 'adalah', 'akan', 'bisa'}
        
        keywords = [w for w in title_words if w not in stop_words and len(w) > 3]
        
        # Tambah keyword-based tags
        for kw in keywords:
            tags.append(f"drama {kw}")
            tags.append(f"film pendek {kw}")

        if additional_keywords:
            tags.extend(additional_keywords)

        # Deduplicate & limit
        seen = set()
        unique = []
        for t in tags:
            if t.lower() not in seen:
                seen.add(t.lower())
                unique.append(t)

        return unique[:30]  # YouTube max ~500 chars total

    def analyze_title_score(self, title):
        """
        Analisis seberapa viral-worthy sebuah judul.
        
        Returns:
            dict dengan score dan saran
        """
        score = 0
        feedback = []

        # Panjang judul
        if 40 <= len(title) <= 70:
            score += 20
            feedback.append("✅ Panjang judul ideal (40-70 karakter)")
        elif len(title) < 40:
            score += 10
            feedback.append("⚠️ Judul terlalu pendek, tambahkan detail")
        else:
            score += 5
            feedback.append("⚠️ Judul terlalu panjang, potong yang tidak perlu")

        # Emotional triggers
        emotional_words = ['dibuang', 'dihina', 'diusir', 'dipecat', 'dikhianati',
                          'ditolak', 'dicampakkan', 'direndahkan', 'disakiti',
                          'miliarder', 'kaya', 'ceo', 'sultan', 'menyesal',
                          'ternyata', 'rahasia', 'terkejut', 'balas']
        
        title_lower = title.lower()
        found_emotions = [w for w in emotional_words if w in title_lower]
        if len(found_emotions) >= 2:
            score += 30
            feedback.append(f"✅ Mengandung emotional trigger: {', '.join(found_emotions)}")
        elif len(found_emotions) >= 1:
            score += 15
            feedback.append(f"⚠️ Hanya 1 emotional trigger, tambahkan lagi")
        else:
            feedback.append("❌ Tidak ada emotional trigger — judul kurang menarik")

        # Contrast/conflict pattern
        conflict_words = ['dibuang', 'dihina', 'miskin', 'rendah', 'gagal']
        success_words = ['miliarder', 'kaya', 'ceo', 'sukses', 'sultan', 'pewaris']
        
        has_conflict = any(w in title_lower for w in conflict_words)
        has_success = any(w in title_lower for w in success_words)
        
        if has_conflict and has_success:
            score += 30
            feedback.append("✅ Ada kontras konflik → sukses (pola viral)")
        elif has_conflict or has_success:
            score += 15
            feedback.append("⚠️ Butuh kontras — tambahkan sisi berlawanan")
        else:
            feedback.append("❌ Tidak ada pola konflik → sukses")

        # Angka / spesifik
        if any(char.isdigit() for char in title):
            score += 10
            feedback.append("✅ Ada angka — membuat judul lebih spesifik")

        # Tanda baca
        if '!' in title or '?' in title:
            score += 10
            feedback.append("✅ Ada tanda seru/tanya — meningkatkan urgency")

        return {
            'score': min(score, 100),
            'grade': 'A' if score >= 80 else 'B' if score >= 60 else 'C' if score >= 40 else 'D',
            'feedback': feedback,
        }

    def generate_seo_package(self, theme=None, video_duration=10):
        """
        Generate paket SEO lengkap: judul + deskripsi + tags.
        
        Returns:
            dict dengan title options, description, dan tags
        """
        titles = self.generate_titles(theme=theme, count=5)
        
        # Analisis semua judul
        analyzed = []
        for title in titles:
            analysis = self.analyze_title_score(title)
            analyzed.append({
                'title': title,
                'score': analysis['score'],
                'grade': analysis['grade'],
            })
        
        # Sort by score
        analyzed.sort(key=lambda x: x['score'], reverse=True)
        
        best_title = analyzed[0]['title']
        
        return {
            'title_options': analyzed,
            'recommended_title': best_title,
            'description': self.generate_description(best_title, video_duration),
            'tags': self.generate_tags(best_title),
        }
