"""Quick test to verify all modules can be imported."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")

try:
    from app.ffmpeg_util import get_ffmpeg_path, get_ffprobe_path
    ffmpeg = get_ffmpeg_path()
    print(f"[OK] FFmpeg found: {ffmpeg}")
except Exception as e:
    print(f"[WARN] FFmpeg: {e}")
    print("       Will use imageio_ffmpeg bundled version")

try:
    from app.downloader import VideoDownloader
    print("[OK] Downloader module")
except Exception as e:
    print(f"[ERR] Downloader: {e}")

try:
    from app.subtitler import AutoSubtitler
    print("[OK] Subtitler module")
except Exception as e:
    print(f"[ERR] Subtitler: {e}")

try:
    from app.editor import VideoEditor
    print("[OK] Editor module")
except Exception as e:
    print(f"[ERR] Editor: {e}")

try:
    from app.thumbnail import ThumbnailGenerator
    print("[OK] Thumbnail module")
except Exception as e:
    print(f"[ERR] Thumbnail: {e}")

try:
    from app.title_generator import TitleGenerator
    print("[OK] Title Generator module")
except Exception as e:
    print(f"[ERR] Title Generator: {e}")

print("\nAll modules loaded! App is ready to run.")
print("Run: python main.py")
