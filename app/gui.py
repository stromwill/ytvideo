"""
YouTube Video Optimizer GUI - Desktop App
Auto-edit video sendiri agar optimal untuk AdSense/monetisasi YouTube
"""
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# Tambah parent dir ke path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class YouTubeOptimizerApp:
    """Main GUI Application."""

    def __init__(self, root):
        self.root = root
        self.root.title("🎬 YouTube Video Optimizer - AdSense Ready")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)
        
        # Colors
        self.BG = "#1e1e2e"
        self.BG2 = "#2a2a3e"
        self.FG = "#ffffff"
        self.ACCENT = "#ff4757"
        self.ACCENT2 = "#2ed573"
        self.BTN_BG = "#3742fa"
        
        self.root.configure(bg=self.BG)
        
        # Variables
        self.url_var = tk.StringVar()
        self.video_path_var = tk.StringVar()
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
        self.temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp")
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self._build_ui()

    def _build_ui(self):
        """Build the main UI."""
        # ===== HEADER =====
        header_frame = tk.Frame(self.root, bg=self.ACCENT, height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame, text="🎬 YouTube Video Optimizer — AdSense Ready Tool",
            bg=self.ACCENT, fg=self.FG, font=("Segoe UI", 16, "bold")
        ).pack(pady=15)

        # ===== MAIN CONTAINER =====
        main_frame = tk.Frame(self.root, bg=self.BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # ===== LEFT PANEL: Input & Controls =====
        left_panel = tk.Frame(main_frame, bg=self.BG2, width=500)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # --- Input Section ---
        self._section_label(left_panel, "📥 INPUT VIDEO")
        
        input_frame = tk.Frame(left_panel, bg=self.BG2)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(input_frame, text="YouTube URL (video kamu sendiri):", 
                bg=self.BG2, fg=self.FG, font=("Segoe UI", 10)).pack(anchor=tk.W)
        
        url_frame = tk.Frame(input_frame, bg=self.BG2)
        url_frame.pack(fill=tk.X, pady=3)
        
        self.url_entry = tk.Entry(url_frame, textvariable=self.url_var, 
                                   font=("Consolas", 11), bg="#3a3a5e", fg=self.FG,
                                   insertbackground=self.FG, relief=tk.FLAT)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        tk.Button(url_frame, text="📥 Download", command=self._download_video,
                 bg=self.BTN_BG, fg=self.FG, font=("Segoe UI", 9, "bold"),
                 relief=tk.FLAT, padx=10, cursor="hand2").pack(side=tk.RIGHT, padx=(5,0))

        tk.Label(input_frame, text="— ATAU —", bg=self.BG2, fg="#888", 
                font=("Segoe UI", 9)).pack(pady=3)

        local_frame = tk.Frame(input_frame, bg=self.BG2)
        local_frame.pack(fill=tk.X, pady=3)
        
        self.local_entry = tk.Entry(local_frame, textvariable=self.video_path_var,
                                     font=("Consolas", 10), bg="#3a3a5e", fg=self.FG,
                                     insertbackground=self.FG, relief=tk.FLAT)
        self.local_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        tk.Button(local_frame, text="📂 Browse", command=self._browse_file,
                 bg="#555", fg=self.FG, font=("Segoe UI", 9),
                 relief=tk.FLAT, padx=10, cursor="hand2").pack(side=tk.RIGHT, padx=(5,0))

        # --- Optimization Options ---
        self._section_label(left_panel, "⚡ OPTIMASI ADSENSE")

        opts_frame = tk.Frame(left_panel, bg=self.BG2)
        opts_frame.pack(fill=tk.X, padx=10, pady=5)

        self.opt_subtitle = tk.BooleanVar(value=True)
        self.opt_silence = tk.BooleanVar(value=True)
        self.opt_audio_enhance = tk.BooleanVar(value=True)
        self.opt_speed = tk.BooleanVar(value=False)
        self.opt_thumbnail = tk.BooleanVar(value=True)
        self.opt_seo = tk.BooleanVar(value=True)
        self.opt_shorts = tk.BooleanVar(value=False)
        self.opt_youtube_export = tk.BooleanVar(value=True)

        options = [
            (self.opt_subtitle, "🔤 Auto Subtitle (Whisper AI)", 
             "Generate & burn subtitle otomatis ke video"),
            (self.opt_silence, "✂️ Hapus Dead Air / Silence",
             "Auto-cut bagian diam yang terlalu lama"),
            (self.opt_audio_enhance, "🔊 Enhance Audio",
             "Normalize volume & bersihkan audio"),
            (self.opt_speed, "⏩ Speed Up 1.05x",
             "Percepat sedikit untuk pacing lebih baik"),
            (self.opt_thumbnail, "🖼️ Generate Thumbnail",
             "Buat thumbnail dari frame terbaik video"),
            (self.opt_seo, "🏷️ Generate Title & Tags SEO",
             "Buat judul, deskripsi, dan tags viral"),
            (self.opt_shorts, "📱 Buat YouTube Shorts",
             "Auto-crop bagian terbaik jadi Shorts vertikal"),
            (self.opt_youtube_export, "📤 Export YouTube-Ready",
             "Export dengan settings optimal YouTube"),
        ]

        for var, text, tooltip in options:
            cb_frame = tk.Frame(opts_frame, bg=self.BG2)
            cb_frame.pack(fill=tk.X, pady=2)
            
            cb = tk.Checkbutton(cb_frame, text=text, variable=var,
                              bg=self.BG2, fg=self.FG, selectcolor="#3a3a5e",
                              activebackground=self.BG2, activeforeground=self.FG,
                              font=("Segoe UI", 10), anchor=tk.W, cursor="hand2")
            cb.pack(side=tk.LEFT)
            
            tk.Label(cb_frame, text=f"  {tooltip}", bg=self.BG2, fg="#888",
                    font=("Segoe UI", 8)).pack(side=tk.LEFT)

        # --- Settings ---
        self._section_label(left_panel, "⚙️ SETTINGS")
        
        settings_frame = tk.Frame(left_panel, bg=self.BG2)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)

        # Whisper model size
        row1 = tk.Frame(settings_frame, bg=self.BG2)
        row1.pack(fill=tk.X, pady=2)
        tk.Label(row1, text="Whisper Model:", bg=self.BG2, fg=self.FG,
                font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.whisper_model = tk.StringVar(value="base")
        whisper_combo = ttk.Combobox(row1, textvariable=self.whisper_model,
                                      values=["tiny", "base", "small", "medium", "large"],
                                      width=10, state="readonly")
        whisper_combo.pack(side=tk.LEFT, padx=5)
        tk.Label(row1, text="(base = recommended)", bg=self.BG2, fg="#888",
                font=("Segoe UI", 8)).pack(side=tk.LEFT)

        # Language
        row2 = tk.Frame(settings_frame, bg=self.BG2)
        row2.pack(fill=tk.X, pady=2)
        tk.Label(row2, text="Bahasa Audio:", bg=self.BG2, fg=self.FG,
                font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.language = tk.StringVar(value="id")
        lang_combo = ttk.Combobox(row2, textvariable=self.language,
                                   values=["id", "en", "auto"],
                                   width=10, state="readonly")
        lang_combo.pack(side=tk.LEFT, padx=5)

        # Resolution
        row3 = tk.Frame(settings_frame, bg=self.BG2)
        row3.pack(fill=tk.X, pady=2)
        tk.Label(row3, text="Resolution:", bg=self.BG2, fg=self.FG,
                font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.resolution = tk.StringVar(value="1080p")
        res_combo = ttk.Combobox(row3, textvariable=self.resolution,
                                  values=["720p", "1080p", "1440p", "2160p"],
                                  width=10, state="readonly")
        res_combo.pack(side=tk.LEFT, padx=5)

        # ===== START BUTTON =====
        tk.Button(
            left_panel, text="🚀  MULAI OPTIMASI  🚀",
            command=self._start_optimization,
            bg=self.ACCENT2, fg="#000", font=("Segoe UI", 14, "bold"),
            relief=tk.FLAT, padx=20, pady=10, cursor="hand2"
        ).pack(fill=tk.X, padx=10, pady=15)

        # ===== RIGHT PANEL: Log & Progress =====
        right_panel = tk.Frame(main_frame, bg=self.BG2, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self._section_label(right_panel, "📊 PROGRESS & LOG")

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(right_panel, variable=self.progress_var,
                                             maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

        self.status_label = tk.Label(right_panel, text="Siap...", bg=self.BG2,
                                      fg=self.ACCENT2, font=("Segoe UI", 10))
        self.status_label.pack(padx=10, anchor=tk.W)

        # Log area
        self.log_text = scrolledtext.ScrolledText(
            right_panel, bg="#1a1a2e", fg="#ccc", font=("Consolas", 9),
            wrap=tk.WORD, relief=tk.FLAT, insertbackground=self.FG
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- SEO Results ---
        self._section_label(right_panel, "🏷️ SEO RESULTS")
        
        self.seo_text = scrolledtext.ScrolledText(
            right_panel, bg="#1a1a2e", fg="#ccc", font=("Consolas", 9),
            wrap=tk.WORD, relief=tk.FLAT, height=8, insertbackground=self.FG
        )
        self.seo_text.pack(fill=tk.X, padx=10, pady=(5, 10))

        # Footer
        tk.Label(
            self.root, text="⚠️ Tool ini hanya untuk mengedit ulang video milik sendiri. Bukan untuk reupload video orang lain.",
            bg=self.BG, fg="#888", font=("Segoe UI", 8)
        ).pack(side=tk.BOTTOM, pady=5)

    def _section_label(self, parent, text):
        """Create a section label."""
        tk.Label(parent, text=text, bg=self.BG2, fg=self.ACCENT,
                font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, padx=10, pady=(10, 3))
        # Separator line
        sep = tk.Frame(parent, bg=self.ACCENT, height=1)
        sep.pack(fill=tk.X, padx=10, pady=(0, 5))

    def _log(self, message, tag=None):
        """Add message to log."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def _update_status(self, percent, text):
        """Update progress bar and status."""
        self.progress_var.set(percent)
        self.status_label.config(text=text)
        self.root.update_idletasks()

    def _browse_file(self):
        """Open file dialog to select local video."""
        path = filedialog.askopenfilename(
            title="Pilih Video",
            filetypes=[
                ("Video files", "*.mp4 *.mkv *.avi *.mov *.webm *.flv"),
                ("All files", "*.*"),
            ]
        )
        if path:
            self.video_path_var.set(path)
            self._log(f"📂 Video dipilih: {path}")

    def _download_video(self):
        """Download video dari URL."""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Masukkan URL YouTube dulu!")
            return

        def _download():
            try:
                self._log(f"📥 Downloading: {url}")
                self._update_status(10, "Downloading video...")

                from app.downloader import VideoDownloader
                dl = VideoDownloader(output_dir=self.temp_dir)
                dl.set_progress_callback(self._update_status)

                # Get info first
                info = dl.get_video_info(url)
                self._log(f"📹 Title: {info['title']}")
                self._log(f"⏱ Duration: {info['duration']}s")
                self._log(f"👁 Views: {info['view_count']:,}")

                # Download
                video_path = dl.download(url, quality=self.resolution.get().replace('p', '') + 'p' 
                                         if self.resolution.get() != 'best' else 'best')
                self.video_path_var.set(video_path)
                self._log(f"✅ Download selesai: {video_path}")
                self._update_status(100, "Download selesai!")

            except Exception as e:
                self._log(f"❌ Error download: {str(e)}")
                self._update_status(0, "Error!")
                messagebox.showerror("Error", f"Gagal download: {str(e)}")

        threading.Thread(target=_download, daemon=True).start()

    def _start_optimization(self):
        """Start the full optimization pipeline."""
        video_path = self.video_path_var.get().strip()
        if not video_path:
            messagebox.showwarning("Warning", "Pilih video dulu! Download dari URL atau browse file lokal.")
            return
        
        if not os.path.exists(video_path):
            messagebox.showerror("Error", f"File tidak ditemukan: {video_path}")
            return

        def _optimize():
            try:
                current_video = video_path
                step = 0
                total_steps = sum([
                    self.opt_audio_enhance.get(),
                    self.opt_silence.get(),
                    self.opt_speed.get(),
                    self.opt_subtitle.get(),
                    self.opt_thumbnail.get(),
                    self.opt_seo.get(),
                    self.opt_shorts.get(),
                    self.opt_youtube_export.get(),
                ])
                
                if total_steps == 0:
                    messagebox.showinfo("Info", "Pilih minimal satu opsi optimasi!")
                    return

                self._log("=" * 50)
                self._log("🚀 MEMULAI OPTIMASI VIDEO...")
                self._log("=" * 50)

                def step_progress(pct, text):
                    overall = ((step / total_steps) + (pct / 100 / total_steps)) * 100
                    self._update_status(overall, text)

                # Step 1: Audio Enhancement
                if self.opt_audio_enhance.get():
                    step += 1
                    self._log(f"\n[{step}/{total_steps}] 🔊 Enhancing audio...")
                    from app.editor import VideoEditor
                    editor = VideoEditor(output_dir=self.output_dir)
                    editor.set_progress_callback(step_progress)
                    current_video = editor.enhance_audio(current_video)
                    self._log(f"✅ Audio enhanced: {current_video}")

                # Step 2: Remove Silence
                if self.opt_silence.get():
                    step += 1
                    self._log(f"\n[{step}/{total_steps}] ✂️ Menghapus dead air...")
                    from app.editor import VideoEditor
                    editor = VideoEditor(output_dir=self.output_dir)
                    editor.set_progress_callback(step_progress)
                    current_video = editor.remove_silence(current_video)
                    self._log(f"✅ Silence dihapus: {current_video}")

                # Step 3: Speed adjustment
                if self.opt_speed.get():
                    step += 1
                    self._log(f"\n[{step}/{total_steps}] ⏩ Adjusting speed 1.05x...")
                    from app.editor import VideoEditor
                    editor = VideoEditor(output_dir=self.output_dir)
                    editor.set_progress_callback(step_progress)
                    current_video = editor.adjust_speed(current_video, speed=1.05)
                    self._log(f"✅ Speed adjusted: {current_video}")

                # Step 4: Auto Subtitle
                if self.opt_subtitle.get():
                    step += 1
                    self._log(f"\n[{step}/{total_steps}] 🔤 Generating subtitle dengan Whisper...")
                    self._log(f"   Model: {self.whisper_model.get()}")
                    self._log(f"   Bahasa: {self.language.get()}")
                    self._log("   ⏳ Ini bisa memakan waktu beberapa menit...")
                    
                    from app.subtitler import AutoSubtitler
                    lang = self.language.get() if self.language.get() != "auto" else None
                    subtitler = AutoSubtitler(
                        model_size=self.whisper_model.get(),
                        output_dir=self.output_dir
                    )
                    subtitler.set_progress_callback(step_progress)
                    
                    result = subtitler.full_pipeline(
                        current_video, 
                        language=lang,
                        subtitle_format="ass",
                        burn_to_video=True,
                        font_size=22,
                        bold=True,
                    )
                    
                    if result['video_output']:
                        current_video = result['video_output']
                    self._log(f"✅ Subtitle generated & burned: {current_video}")
                    self._log(f"   Subtitle file: {result['subtitle_path']}")

                # Step 5: Thumbnail
                if self.opt_thumbnail.get():
                    step += 1
                    self._log(f"\n[{step}/{total_steps}] 🖼️ Generating thumbnail...")
                    from app.thumbnail import ThumbnailGenerator
                    thumb_gen = ThumbnailGenerator(output_dir=self.output_dir)
                    
                    thumbnails = thumb_gen.batch_generate(
                        current_video,
                        title_text="DRAMA PENDEK",
                        num_options=5
                    )
                    self._log(f"✅ {len(thumbnails)} thumbnail options generated:")
                    for t in thumbnails:
                        self._log(f"   📷 {t}")

                # Step 6: SEO
                if self.opt_seo.get():
                    step += 1
                    self._log(f"\n[{step}/{total_steps}] 🏷️ Generating title, description & tags...")
                    from app.title_generator import TitleGenerator
                    seo_gen = TitleGenerator()
                    seo_package = seo_gen.generate_seo_package(theme="drama")
                    
                    # Show in SEO panel
                    self.seo_text.delete('1.0', tk.END)
                    self.seo_text.insert(tk.END, "📌 RECOMMENDED TITLES:\n")
                    for opt in seo_package['title_options']:
                        self.seo_text.insert(tk.END, 
                            f"  [{opt['grade']}] (Score: {opt['score']}) {opt['title']}\n")
                    
                    self.seo_text.insert(tk.END, f"\n📝 TAGS:\n")
                    self.seo_text.insert(tk.END, ", ".join(seo_package['tags'][:15]))
                    
                    # Save description to file
                    desc_path = os.path.join(self.output_dir, "description.txt")
                    with open(desc_path, 'w', encoding='utf-8') as f:
                        f.write(seo_package['description'])
                    
                    tags_path = os.path.join(self.output_dir, "tags.txt")
                    with open(tags_path, 'w', encoding='utf-8') as f:
                        f.write("\n".join(seo_package['tags']))
                    
                    self._log(f"✅ SEO package saved:")
                    self._log(f"   📄 {desc_path}")
                    self._log(f"   🏷️ {tags_path}")

                # Step 7: YouTube Shorts
                if self.opt_shorts.get():
                    step += 1
                    self._log(f"\n[{step}/{total_steps}] 📱 Creating YouTube Shorts clip...")
                    from app.editor import VideoEditor
                    editor = VideoEditor(output_dir=self.output_dir)
                    editor.set_progress_callback(step_progress)
                    # Ambil 60 detik pertama sebagai shorts (hook)
                    shorts_path = editor.create_shorts_clip(current_video, 0, 60)
                    self._log(f"✅ Shorts clip: {shorts_path}")

                # Step 8: YouTube Export
                if self.opt_youtube_export.get():
                    step += 1
                    self._log(f"\n[{step}/{total_steps}] 📤 Exporting YouTube-ready video...")
                    from app.editor import VideoEditor
                    editor = VideoEditor(output_dir=self.output_dir)
                    editor.set_progress_callback(step_progress)
                    final_video = editor.export_for_youtube(
                        current_video, resolution=self.resolution.get()
                    )
                    self._log(f"✅ Final video: {final_video}")
                    current_video = final_video

                # DONE!
                self._log("\n" + "=" * 50)
                self._log("🎉 OPTIMASI SELESAI!")
                self._log(f"📂 Output folder: {self.output_dir}")
                self._log("=" * 50)
                self._update_status(100, "✅ Selesai! Cek folder output.")

                # Open output folder
                if os.name == 'nt':
                    os.startfile(self.output_dir)

            except Exception as e:
                self._log(f"\n❌ ERROR: {str(e)}")
                import traceback
                self._log(traceback.format_exc())
                self._update_status(0, f"Error: {str(e)}")
                messagebox.showerror("Error", f"Terjadi error:\n{str(e)}")

        threading.Thread(target=_optimize, daemon=True).start()


def main():
    root = tk.Tk()
    
    # Style
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TProgressbar", troughcolor="#3a3a5e", background="#2ed573",
                    thickness=20)
    style.configure("TCombobox", fieldbackground="#3a3a5e", background="#3a3a5e",
                    foreground="#ffffff")
    
    app = YouTubeOptimizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
