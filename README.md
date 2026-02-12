# YouTube Video Optimizer — AdSense Ready Tool 🎬

Tool desktop Python untuk **mengoptimasi video YouTube milik sendiri** agar lebih optimal untuk monetisasi AdSense.

> ⚠️ Tool ini HANYA untuk mengedit ulang video milik sendiri. BUKAN untuk reupload video orang lain.

## Fitur

| Fitur | Deskripsi |
|-------|-----------|
| 📥 Download | Download video sendiri dari YouTube |
| 🔤 Auto Subtitle | Generate subtitle otomatis (Whisper AI) & burn ke video |
| ✂️ Remove Silence | Auto-cut bagian diam / dead air |
| 🔊 Audio Enhance | Normalize volume & bersihkan audio |
| 🖼️ Thumbnail | Generate thumbnail dari frame terbaik video |
| 🏷️ SEO | Generate judul viral, deskripsi, dan tags |
| 📤 YouTube Export | Export dengan settings optimal YouTube |
| 📱 Shorts | Auto-crop jadi YouTube Shorts vertikal |

## Requirements

- **Python 3.9+**
- **FFmpeg** — harus terinstall dan ada di PATH

### Install FFmpeg (Windows)
```
winget install FFmpeg
```
Atau download dari https://ffmpeg.org/download.html

## Cara Install

```bash
# Clone/download project ini
cd youtube

# Install dependencies
pip install -r requirements.txt
```

## Cara Pakai

```bash
python main.py
```

1. Masukkan URL YouTube video kamu, atau browse file video lokal
2. Pilih opsi optimasi yang diinginkan
3. Klik **MULAI OPTIMASI**
4. Tunggu proses selesai
5. Cek folder `output/` untuk hasil

## Struktur Project

```
youtube/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── README.md              
├── app/
│   ├── __init__.py
│   ├── gui.py             # GUI (Tkinter)
│   ├── downloader.py      # YouTube downloader (yt-dlp)
│   ├── subtitler.py       # Auto subtitle (Whisper + FFmpeg)
│   ├── editor.py          # Video editor (FFmpeg)
│   ├── thumbnail.py       # Thumbnail generator (Pillow)
│   └── title_generator.py # Title & SEO generator
├── temp/                   # Temporary files
└── output/                 # Output files
```

## Tips Optimasi AdSense

1. **Subtitle WAJIB** — meningkatkan watch time 30-40%
2. **Audio bersih** — penonton langsung skip kalau audio jelek
3. **Hapus dead air** — pacing cepat = retention tinggi
4. **Thumbnail menarik** — CTR naik = lebih banyak views
5. **Judul SEO** — lebih mudah ditemukan di search
6. **Upload Shorts** — gratis exposure dari algorithm YouTube
