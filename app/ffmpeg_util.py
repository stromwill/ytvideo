"""
Utility untuk mendapatkan path FFmpeg.
Menggunakan imageio_ffmpeg yang sudah include FFmpeg binary.
"""
import shutil
import os


def get_ffmpeg_path():
    """Dapatkan path ke FFmpeg executable."""
    # 1. Coba dari PATH sistem
    ffmpeg_system = shutil.which("ffmpeg")
    if ffmpeg_system:
        return ffmpeg_system

    # 2. Coba dari imageio_ffmpeg (bundled)
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_path and os.path.exists(ffmpeg_path):
            return ffmpeg_path
    except ImportError:
        pass

    # 3. Common Windows locations
    common_paths = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
    ]
    for p in common_paths:
        if os.path.exists(p):
            return p

    raise FileNotFoundError(
        "FFmpeg tidak ditemukan!\n"
        "Install FFmpeg: pip install imageio-ffmpeg\n"
        "Atau download dari: https://ffmpeg.org/download.html"
    )


def get_ffprobe_path():
    """Dapatkan path ke ffprobe executable."""
    # ffprobe biasanya di folder yang sama dengan ffmpeg
    ffmpeg_path = get_ffmpeg_path()
    ffprobe_path = ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe").replace("ffmpeg", "ffprobe", 1)
    
    if os.path.exists(ffprobe_path):
        return ffprobe_path
    
    # Coba dari PATH
    ffprobe_system = shutil.which("ffprobe")
    if ffprobe_system:
        return ffprobe_system
    
    # Fallback: gunakan ffmpeg -i untuk probe
    return None


# Test saat import
if __name__ == "__main__":
    try:
        print(f"FFmpeg: {get_ffmpeg_path()}")
        probe = get_ffprobe_path()
        print(f"FFprobe: {probe if probe else 'Tidak tersedia (akan pakai ffmpeg -i)'}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
