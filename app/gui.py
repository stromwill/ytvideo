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
        self.root.geometry("1200x850")
        self.root.minsize(1000, 700)
        
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

        # ===== LEFT PANEL: Input & Controls (Scrollable) =====
        left_outer = tk.Frame(main_frame, bg=self.BG2, width=520)
        left_outer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        left_canvas = tk.Canvas(left_outer, bg=self.BG2, highlightthickness=0)
        left_scrollbar = ttk.Scrollbar(left_outer, orient="vertical", command=left_canvas.yview)
        left_panel = tk.Frame(left_canvas, bg=self.BG2)

        left_panel.bind("<Configure>", lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all")))
        left_canvas.create_window((0, 0), window=left_panel, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scrollbar.set)

        left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        left_canvas.bind_all("<MouseWheel>", _on_mousewheel)

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
        self.opt_watermark = tk.BooleanVar(value=False)
        self.opt_color_grade = tk.BooleanVar(value=False)
        self.opt_chapters = tk.BooleanVar(value=False)
        self.opt_adsense_check = tk.BooleanVar(value=True)
        self.opt_translate = tk.BooleanVar(value=False)
        self.opt_intro_outro = tk.BooleanVar(value=False)
        self.opt_analytics = tk.BooleanVar(value=True)
        self.opt_multi_export = tk.BooleanVar(value=False)

        options = [
            (self.opt_subtitle, "🔤 Auto Subtitle (Whisper AI)", 
             "Generate & burn subtitle otomatis ke video"),
            (self.opt_translate, "🌍 Translate Subtitle",
             "Terjemahkan subtitle ke bahasa lain"),
            (self.opt_silence, "✂️ Hapus Dead Air / Silence",
             "Auto-cut bagian diam yang terlalu lama"),
            (self.opt_audio_enhance, "🔊 Enhance Audio",
             "Normalize volume & bersihkan audio"),
            (self.opt_speed, "⏩ Speed Up 1.05x",
             "Percepat sedikit untuk pacing lebih baik"),
            (self.opt_watermark, "💧 Watermark / Logo",
             "Tambah watermark teks atau gambar ke video"),
            (self.opt_color_grade, "🎨 Color Grading",
             "Terapkan preset warna sinematik ke video"),
            (self.opt_intro_outro, "🎬 Intro / Outro",
             "Sisipkan intro & outro branded otomatis"),
            (self.opt_thumbnail, "🖼️ Generate Thumbnail",
             "Buat thumbnail dari frame terbaik video"),
            (self.opt_seo, "🏷️ Generate Title & Tags SEO",
             "Buat judul, deskripsi, dan tags viral"),
            (self.opt_chapters, "📑 Auto Generate Chapters",
             "Buat timestamp chapter otomatis dari subtitle"),
            (self.opt_shorts, "📱 Buat YouTube Shorts",
             "Auto-crop bagian terbaik jadi Shorts vertikal"),
            (self.opt_youtube_export, "📤 Export YouTube-Ready",
             "Export dengan settings optimal YouTube"),
            (self.opt_multi_export, "📱 Multi-Platform Export",
             "Export untuk TikTok, IG Reels, Facebook"),
            (self.opt_analytics, "📊 Video Analytics",
             "Analisis detail video (bitrate, fps, codec)"),
            (self.opt_adsense_check, "✅ AdSense Readiness Check",
             "Cek apakah video siap untuk monetisasi"),
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

        # Watermark text
        row4 = tk.Frame(settings_frame, bg=self.BG2)
        row4.pack(fill=tk.X, pady=2)
        tk.Label(row4, text="Watermark Text:", bg=self.BG2, fg=self.FG,
                font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.watermark_text = tk.StringVar(value="")
        wm_entry = tk.Entry(row4, textvariable=self.watermark_text,
                            font=("Segoe UI", 10), bg="#3a3a5e", fg=self.FG,
                            insertbackground=self.FG, relief=tk.FLAT, width=18)
        wm_entry.pack(side=tk.LEFT, padx=5, ipady=2)
        tk.Label(row4, text="(nama channel)", bg=self.BG2, fg="#888",
                font=("Segoe UI", 8)).pack(side=tk.LEFT)

        # Watermark logo file
        row4b = tk.Frame(settings_frame, bg=self.BG2)
        row4b.pack(fill=tk.X, pady=2)
        tk.Label(row4b, text="Watermark Logo:", bg=self.BG2, fg=self.FG,
                font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.watermark_logo = tk.StringVar(value="")
        wm_logo_entry = tk.Entry(row4b, textvariable=self.watermark_logo,
                                  font=("Segoe UI", 9), bg="#3a3a5e", fg=self.FG,
                                  insertbackground=self.FG, relief=tk.FLAT, width=12)
        wm_logo_entry.pack(side=tk.LEFT, padx=5, ipady=2)
        tk.Button(row4b, text="📂", command=self._browse_logo,
                 bg="#555", fg=self.FG, font=("Segoe UI", 9),
                 relief=tk.FLAT, padx=5, cursor="hand2").pack(side=tk.LEFT)

        # Color grading preset
        row5 = tk.Frame(settings_frame, bg=self.BG2)
        row5.pack(fill=tk.X, pady=2)
        tk.Label(row5, text="Color Preset:", bg=self.BG2, fg=self.FG,
                font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.color_preset = tk.StringVar(value="cinematic_warm")
        color_combo = ttk.Combobox(row5, textvariable=self.color_preset,
                                    values=["cinematic_warm", "cinematic_cool", "dramatic",
                                            "vintage", "bright_pop", "dark_moody",
                                            "golden_hour", "bw_dramatic", "teal_orange",
                                            "enhance_only"],
                                    width=16, state="readonly")
        color_combo.pack(side=tk.LEFT, padx=5)

        # Batch URLs file
        row6 = tk.Frame(settings_frame, bg=self.BG2)
        row6.pack(fill=tk.X, pady=2)
        tk.Label(row6, text="Batch URLs File:", bg=self.BG2, fg=self.FG,
                font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.batch_file = tk.StringVar(value="")
        batch_entry = tk.Entry(row6, textvariable=self.batch_file,
                               font=("Segoe UI", 9), bg="#3a3a5e", fg=self.FG,
                               insertbackground=self.FG, relief=tk.FLAT, width=12)
        batch_entry.pack(side=tk.LEFT, padx=5, ipady=2)
        tk.Button(row6, text="📂", command=self._browse_batch_file,
                 bg="#555", fg=self.FG, font=("Segoe UI", 9),
                 relief=tk.FLAT, padx=5, cursor="hand2").pack(side=tk.LEFT)
        tk.Button(row6, text="▶ Batch", command=self._start_batch,
                 bg="#e67e22", fg=self.FG, font=("Segoe UI", 9, "bold"),
                 relief=tk.FLAT, padx=8, cursor="hand2").pack(side=tk.LEFT, padx=3)

        # Translate target language
        row7 = tk.Frame(settings_frame, bg=self.BG2)
        row7.pack(fill=tk.X, pady=2)
        tk.Label(row7, text="Translate ke:", bg=self.BG2, fg=self.FG,
                font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.translate_target = tk.StringVar(value="en")
        trans_combo = ttk.Combobox(row7, textvariable=self.translate_target,
                                    values=["en", "id", "ms", "zh-CN", "ja", "ko",
                                            "hi", "ar", "es", "fr", "de", "pt",
                                            "ru", "th", "vi", "tl"],
                                    width=10, state="readonly")
        trans_combo.pack(side=tk.LEFT, padx=5)
        tk.Label(row7, text="(bahasa tujuan)", bg=self.BG2, fg="#888",
                font=("Segoe UI", 8)).pack(side=tk.LEFT)

        # Intro/Outro channel name
        row8 = tk.Frame(settings_frame, bg=self.BG2)
        row8.pack(fill=tk.X, pady=2)
        tk.Label(row8, text="Channel Name:", bg=self.BG2, fg=self.FG,
                font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.channel_name = tk.StringVar(value="Film Pendek Pahm")
        ch_entry = tk.Entry(row8, textvariable=self.channel_name,
                            font=("Segoe UI", 10), bg="#3a3a5e", fg=self.FG,
                            insertbackground=self.FG, relief=tk.FLAT, width=18)
        ch_entry.pack(side=tk.LEFT, padx=5, ipady=2)

        # Custom intro/outro file
        row8b = tk.Frame(settings_frame, bg=self.BG2)
        row8b.pack(fill=tk.X, pady=2)
        tk.Label(row8b, text="Intro Video:", bg=self.BG2, fg=self.FG,
                font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.intro_file = tk.StringVar(value="")
        intro_entry = tk.Entry(row8b, textvariable=self.intro_file,
                               font=("Segoe UI", 9), bg="#3a3a5e", fg=self.FG,
                               insertbackground=self.FG, relief=tk.FLAT, width=12)
        intro_entry.pack(side=tk.LEFT, padx=5, ipady=2)
        tk.Button(row8b, text="📂", command=lambda: self._browse_video_to(self.intro_file),
                 bg="#555", fg=self.FG, font=("Segoe UI", 9),
                 relief=tk.FLAT, padx=5, cursor="hand2").pack(side=tk.LEFT)

        row8c = tk.Frame(settings_frame, bg=self.BG2)
        row8c.pack(fill=tk.X, pady=2)
        tk.Label(row8c, text="Outro Video:", bg=self.BG2, fg=self.FG,
                font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.outro_file = tk.StringVar(value="")
        outro_entry = tk.Entry(row8c, textvariable=self.outro_file,
                               font=("Segoe UI", 9), bg="#3a3a5e", fg=self.FG,
                               insertbackground=self.FG, relief=tk.FLAT, width=12)
        outro_entry.pack(side=tk.LEFT, padx=5, ipady=2)
        tk.Button(row8c, text="📂", command=lambda: self._browse_video_to(self.outro_file),
                 bg="#555", fg=self.FG, font=("Segoe UI", 9),
                 relief=tk.FLAT, padx=5, cursor="hand2").pack(side=tk.LEFT)

        # Multi-platform export targets
        row9 = tk.Frame(settings_frame, bg=self.BG2)
        row9.pack(fill=tk.X, pady=2)
        tk.Label(row9, text="Export Platforms:", bg=self.BG2, fg=self.FG,
                font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.export_platforms_var = tk.StringVar(value="tiktok,instagram_reels,facebook")
        plat_entry = tk.Entry(row9, textvariable=self.export_platforms_var,
                              font=("Segoe UI", 9), bg="#3a3a5e", fg=self.FG,
                              insertbackground=self.FG, relief=tk.FLAT, width=25)
        plat_entry.pack(side=tk.LEFT, padx=5, ipady=2)

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

    def _browse_video_to(self, target_var):
        """Browse for a video file and set to target StringVar."""
        path = filedialog.askopenfilename(
            title="Pilih Video",
            filetypes=[
                ("Video files", "*.mp4 *.mkv *.avi *.mov *.webm"),
                ("All files", "*.*"),
            ]
        )
        if path:
            target_var.set(path)
            self._log(f"📂 File dipilih: {path}")

    def _browse_logo(self):
        """Open file dialog to select watermark logo image."""
        path = filedialog.askopenfilename(
            title="Pilih Logo Watermark",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.webp"),
                ("All files", "*.*"),
            ]
        )
        if path:
            self.watermark_logo.set(path)
            self._log(f"📂 Logo dipilih: {path}")

    def _browse_batch_file(self):
        """Open file dialog to select batch URLs text file."""
        path = filedialog.askopenfilename(
            title="Pilih File Batch URLs",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ]
        )
        if path:
            self.batch_file.set(path)
            self._log(f"📂 Batch file dipilih: {path}")

    def _start_batch(self):
        """Start batch processing from a URLs file."""
        batch_path = self.batch_file.get().strip()
        if not batch_path or not os.path.exists(batch_path):
            messagebox.showwarning("Warning", "Pilih file .txt berisi daftar URL YouTube dulu!")
            return

        def _run_batch():
            try:
                self._log("=" * 50)
                self._log("🔄 BATCH PROCESSING DIMULAI...")
                self._log("=" * 50)
                self._update_status(5, "Starting batch...")

                from app.batch import BatchProcessor
                processor = BatchProcessor(output_dir=self.output_dir)

                # Build options dict from current GUI settings
                options = {
                    'subtitle': self.opt_subtitle.get(),
                    'silence_removal': self.opt_silence.get(),
                    'audio_enhance': self.opt_audio_enhance.get(),
                    'speed': self.opt_speed.get(),
                    'thumbnail': self.opt_thumbnail.get(),
                    'seo': self.opt_seo.get(),
                    'shorts': self.opt_shorts.get(),
                    'youtube_export': self.opt_youtube_export.get(),
                    'whisper_model': self.whisper_model.get(),
                    'language': self.language.get(),
                    'resolution': self.resolution.get(),
                }

                results = processor.process_from_file(batch_path, options)
                
                success = sum(1 for r in results if r.get('status') == 'success')
                total = len(results)
                
                self._log(f"\n🔄 Batch selesai: {success}/{total} berhasil")
                self._update_status(100, f"Batch done: {success}/{total}")
                
                if os.name == 'nt':
                    os.startfile(self.output_dir)
                    
            except Exception as e:
                self._log(f"❌ Batch error: {str(e)}")
                import traceback
                self._log(traceback.format_exc())
                messagebox.showerror("Error", f"Batch error:\n{str(e)}")

        threading.Thread(target=_run_batch, daemon=True).start()

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
                    self.opt_watermark.get(),
                    self.opt_color_grade.get(),
                    self.opt_intro_outro.get(),
                    self.opt_subtitle.get(),
                    self.opt_translate.get(),
                    self.opt_thumbnail.get(),
                    self.opt_seo.get(),
                    self.opt_chapters.get(),
                    self.opt_shorts.get(),
                    self.opt_youtube_export.get(),
                    self.opt_multi_export.get(),
                    self.opt_analytics.get(),
                    self.opt_adsense_check.get(),
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

                # Step 3b: Watermark
                if self.opt_watermark.get():
                    step += 1
                    self._log(f"\n[{step}/{total_steps}] 💧 Adding watermark...")
                    from app.watermark import WatermarkOverlay
                    wm = WatermarkOverlay(output_dir=self.output_dir)
                    wm_text = self.watermark_text.get().strip()
                    wm_logo = self.watermark_logo.get().strip()
                    
                    if wm_logo and os.path.exists(wm_logo):
                        current_video = wm.add_image_watermark(
                            current_video, wm_logo, position="top-right", opacity=0.7, scale=0.12
                        )
                        self._log(f"✅ Logo watermark added: {current_video}")
                    elif wm_text:
                        current_video = wm.add_text_watermark(
                            current_video, wm_text, position="top-right", font_size=28, opacity=0.6
                        )
                        self._log(f"✅ Text watermark added: {current_video}")
                    else:
                        self._log("⚠️ Watermark diaktifkan tapi tidak ada teks/logo. Dilewati.")

                # Step 3c: Color Grading
                if self.opt_color_grade.get():
                    step += 1
                    preset_name = self.color_preset.get()
                    self._log(f"\n[{step}/{total_steps}] 🎨 Applying color grading: {preset_name}...")
                    from app.color_grading import ColorGrading
                    cg = ColorGrading(output_dir=self.output_dir)
                    current_video = cg.apply_preset(current_video, preset_name)
                    self._log(f"✅ Color grading applied: {current_video}")

                # Step 3d: Intro / Outro
                if self.opt_intro_outro.get():
                    step += 1
                    self._log(f"\n[{step}/{total_steps}] 🎬 Adding intro/outro...")
                    from app.intro_outro import IntroOutroManager
                    io_mgr = IntroOutroManager(output_dir=self.output_dir)
                    
                    intro_p = self.intro_file.get().strip() or None
                    outro_p = self.outro_file.get().strip() or None
                    ch_name = self.channel_name.get().strip() or "Film Pendek Pahm"
                    
                    if intro_p and not os.path.exists(intro_p):
                        intro_p = None
                    if outro_p and not os.path.exists(outro_p):
                        outro_p = None
                    
                    current_video = io_mgr.full_pipeline(
                        current_video, channel_name=ch_name,
                        intro_path=intro_p, outro_path=outro_p,
                        auto_generate=(not intro_p or not outro_p)
                    )
                    self._log(f"✅ Intro/outro added: {current_video}")

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

                # Step 4b: Translate Subtitle
                if self.opt_translate.get():
                    step += 1
                    target_lang = self.translate_target.get()
                    self._log(f"\n[{step}/{total_steps}] 🌍 Translating subtitle to {target_lang}...")
                    from app.translator import SubtitleTranslator
                    translator = SubtitleTranslator(output_dir=self.output_dir)
                    
                    # Find subtitle file from previous step or output dir
                    sub_file = None
                    for ext in ['.srt', '.ass']:
                        candidate = os.path.join(self.output_dir, f"subtitle{ext}")
                        if os.path.exists(candidate):
                            sub_file = candidate
                            break
                    
                    if sub_file:
                        src_lang = self.language.get() if self.language.get() != 'auto' else 'id'
                        translated_path = translator.translate_subtitle(
                            sub_file, source_lang=src_lang, target_lang=target_lang
                        )
                        self._log(f"✅ Subtitle translated: {translated_path}")
                    else:
                        self._log("⚠️ Tidak ada file subtitle ditemukan. Aktifkan Auto Subtitle dulu.")

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

                # Step 7b: Auto Chapters
                if self.opt_chapters.get():
                    step += 1
                    self._log(f"\n[{step}/{total_steps}] 📑 Generating chapter timestamps...")
                    from app.chapter_generator import ChapterGenerator
                    ch_gen = ChapterGenerator(output_dir=self.output_dir)
                    
                    # Try to use SRT from subtitle step
                    srt_path = os.path.join(self.output_dir, "subtitle.srt")
                    if os.path.exists(srt_path):
                        chapters = ch_gen.generate_from_srt(srt_path)
                        self._log(f"✅ {len(chapters)} chapters generated from SRT")
                    else:
                        chapters = ch_gen.generate_from_transcription(current_video,
                            language=self.language.get() if self.language.get() != "auto" else None)
                        self._log(f"✅ {len(chapters)} chapters generated from audio analysis")
                    
                    ch_path = ch_gen.save_chapters(chapters)
                    formatted = ch_gen.format_timestamps(chapters)
                    self._log(f"📑 Chapters saved: {ch_path}")
                    self._log(f"   Preview:\n{formatted[:500]}")
                    
                    # Add to SEO text
                    self.seo_text.insert(tk.END, f"\n\n📑 CHAPTERS:\n{formatted}")

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

                # Step 8b: Multi-Platform Export
                if self.opt_multi_export.get():
                    step += 1
                    platforms_str = self.export_platforms_var.get().strip()
                    platforms = [p.strip() for p in platforms_str.split(',') if p.strip()]
                    self._log(f"\n[{step}/{total_steps}] 📱 Multi-platform export: {', '.join(platforms)}...")
                    from app.multi_export import MultiPlatformExporter
                    exporter = MultiPlatformExporter(output_dir=self.output_dir)
                    results = exporter.export_multi(current_video, platforms=platforms)
                    report_text = exporter.format_export_report(results)
                    self._log(report_text)
                    
                    self.seo_text.insert(tk.END, f"\n\n📱 MULTI-PLATFORM EXPORT:\n")
                    for plat, res in results.items():
                        if res['status'] == 'success':
                            self.seo_text.insert(tk.END, f"  ✅ {res['platform_name']}: {res['size_mb']}MB\n")
                        else:
                            self.seo_text.insert(tk.END, f"  ❌ {res['platform_name']}: {res['error']}\n")

                # Step 8c: Video Analytics
                if self.opt_analytics.get():
                    step += 1
                    self._log(f"\n[{step}/{total_steps}] 📊 Analyzing video...")
                    from app.analytics import VideoAnalytics
                    analyzer = VideoAnalytics()
                    stats = analyzer.analyze(current_video)
                    report_text = analyzer.format_report(stats)
                    self._log(report_text)
                    
                    self.seo_text.insert(tk.END, f"\n\n📊 VIDEO ANALYTICS:\n")
                    v = stats.get('video', {})
                    a = stats.get('audio', {})
                    self.seo_text.insert(tk.END, f"  Duration: {stats['duration_formatted']}\n")
                    self.seo_text.insert(tk.END, f"  Size: {stats['file_size_mb']}MB\n")
                    if v:
                        self.seo_text.insert(tk.END, f"  Video: {v.get('resolution','')} {v.get('fps','')}fps {v.get('codec','')}\n")
                    if a:
                        self.seo_text.insert(tk.END, f"  Audio: {a.get('codec','')} {a.get('bitrate_kbps','')}kbps\n")

                # Step 8d: AdSense Readiness Check
                if self.opt_adsense_check.get():
                    step += 1
                    self._log(f"\n[{step}/{total_steps}] ✅ Running AdSense readiness check...")
                    from app.adsense_checker import AdSenseChecker
                    checker = AdSenseChecker()
                    report = checker.check_video(current_video)
                    formatted_report = checker.format_report(report)
                    self._log(formatted_report)
                    
                    # Show in SEO panel
                    self.seo_text.insert(tk.END, f"\n\n✅ ADSENSE CHECK:\n")
                    self.seo_text.insert(tk.END, f"Score: {report['score']}/100 ({report['grade']})\n")
                    if report.get('recommendations'):
                        for rec in report['recommendations']:
                            self.seo_text.insert(tk.END, f"  💡 {rec}\n")

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
