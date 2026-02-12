"""
YouTube Video Optimizer - AdSense Ready Tool
=============================================

Tool desktop untuk mengoptimasi video YouTube milik sendiri
agar lebih optimal untuk monetisasi AdSense.

Fitur:
- Download video sendiri dari YouTube
- Auto subtitle menggunakan Whisper AI
- Hapus dead air / silence otomatis
- Enhance audio (normalize volume)
- Generate thumbnail dari frame terbaik
- Generate judul, deskripsi, dan tags SEO
- Export YouTube-ready format
- Buat YouTube Shorts clip

Requirements:
- Python 3.9+
- FFmpeg (harus terinstall & ada di PATH)

Cara install:
    pip install -r requirements.txt

Cara jalankan:
    python main.py
"""
import sys
import os

# Tambah project root ke path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.gui import main

if __name__ == "__main__":
    main()
