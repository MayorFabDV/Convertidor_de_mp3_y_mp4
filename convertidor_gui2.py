import customtkinter as ctk
import yt_dlp
import threading
import os
import sys
import webbrowser
import subprocess
import urllib.request
import json
import ssl
import certifi
from datetime import datetime
from tkinter import filedialog

# ============================================================================
# NOTA SOBRE SSL:
# Se usa certifi para manejar los certificados de forma segura.
# Esto evita errores de SSL sin desactivar la verificación.
# ============================================================================

# Configuración visual global
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class UniversalConverter(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Icono de la ventana (funciona en desarrollo, --onefile y --onedir)
        if getattr(sys, 'frozen', False):
            candidate_dirs = [sys._MEIPASS, os.path.dirname(sys.executable)]
        else:
            candidate_dirs = [os.path.dirname(os.path.abspath(__file__))]
        
        for c_dir in candidate_dirs:
            ico_file = os.path.join(c_dir, "ico.ico")
            if os.path.exists(ico_file):
                try:
                    self.iconbitmap(ico_file)
                    break
                except Exception:
                    pass
        
        self.title("Convertidor mp3 y mp4 - Bafyam")
        self.geometry("900x620")
        self.minsize(850, 580)
        
        # Obtención de ruta de ffmpeg
        self.ffmpeg_path = 'ffmpeg'
        for c_dir in candidate_dirs:
            ffmpeg_candidate = os.path.join(c_dir, 'ffmpeg.exe')
            if os.path.exists(ffmpeg_candidate):
                self.ffmpeg_path = ffmpeg_candidate
                break
        
        # Configurar SSL usando los certificados de certifi.
        # Esto es vital para que funcione al compilar con PyInstaller y al descargar.
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        
        self.download_folder = os.getcwd()
        
        # Ruta profesional para el historial (en la carpeta de usuario, no en la del .exe)
        self.history_dir = os.path.join(os.path.expanduser('~'), '.bafyam_media')
        os.makedirs(self.history_dir, exist_ok=True)
        self.history_file = os.path.join(self.history_dir, 'historial.json')
        
        # Control de cancelación y estado
        self.cancel_event = threading.Event()
        self.is_downloading = False
        
        # Configurar grid principal (2 Columnas: Sidebar + Main Content)
        self.grid_columnconfigure(0, weight=0, minsize=230)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._setup_sidebar()
        self._setup_main_panel()
        
        # Verificar actualizaciones de yt-dlp al iniciar (en segundo plano)
        threading.Thread(target=self.check_ytdlp_update, daemon=True).start()
    
    def _setup_sidebar(self):
        """Barra lateral izquierda con marcas, estado, historial y donación."""
        self.sidebar = ctk.CTkFrame(self, corner_radius=0, fg_color="#121216")
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_rowconfigure(4, weight=1)

        title_label = ctk.CTkLabel(self.sidebar, text="Bafyam Media", font=ctk.CTkFont(size=18, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=(25, 2), sticky="w")

        subtitle_label = ctk.CTkLabel(self.sidebar, text="Convertidor mp3 y mp4", font=ctk.CTkFont(size=11), text_color="gray60")
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        self.status_badge = ctk.CTkLabel(
            self.sidebar, text="Verificando sistema...", font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#F39C12", fg_color="#2C2415", corner_radius=8, height=30
        )
        self.status_badge.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        platforms_info = ctk.CTkLabel(
            self.sidebar, text="Soporta:\nYouTube, YT Music, TikTok\nInstagram, Facebook, X\nReddit, Twitch, Vimeo\nSoundCloud, Dailymotion, Bilibili\n¡Y +1000 sitios más!",
            font=ctk.CTkFont(size=11), text_color="gray50", justify="left"
        )
        platforms_info.grid(row=3, column=0, padx=20, pady=(20, 10), sticky="w")

        # Botón de Historial (Fila 5)
        self.history_btn = ctk.CTkButton(
            self.sidebar, text="Ver Historial", command=self.show_history,
            fg_color="gray25", hover_color="gray35", font=ctk.CTkFont(size=13, weight="bold"), height=38, corner_radius=8
        )
        self.history_btn.grid(row=5, column=0, padx=20, pady=(10, 5), sticky="ew")

        # Botón de GitHub (Fila 6)
        self.github_btn = ctk.CTkButton(
            self.sidebar, text="Ver codigo en GitHub", command=self.open_github,
            fg_color="#24292e", hover_color="#40464e", font=ctk.CTkFont(size=13, weight="bold"), height=38, corner_radius=8
        )
        self.github_btn.grid(row=6, column=0, padx=20, pady=(5, 5), sticky="ew")

        # Botón de Donación (Fila 7)
        self.donate_btn = ctk.CTkButton(
            self.sidebar, text="Invítame un café", command=self.open_donation,
            fg_color="#FF5F5F", hover_color="#E04848", font=ctk.CTkFont(size=13, weight="bold"), height=38, corner_radius=8
        )
        self.donate_btn.grid(row=7, column=0, padx=20, pady=(5, 10), sticky="ew")

        self.footer = ctk.CTkLabel(self.sidebar, text="Hecho con cariño y 0 anuncios", text_color="gray40", font=ctk.CTkFont(size=10))
        self.footer.grid(row=8, column=0, padx=20, pady=(0, 15))

    def _setup_main_panel(self):
        """Panel derecho agrupado en Cards modulares."""
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # --- CARD 1: Entrada de URL y Selección de Destino ---
        card_input = ctk.CTkFrame(self.main_frame, corner_radius=12)
        card_input.grid(row=0, column=0, sticky="ew", pady=(0, 15), ipadx=10, ipady=10)
        card_input.grid_columnconfigure(0, weight=1)

        url_title = ctk.CTkLabel(card_input, text="Enlace del Video o Playlist", font=ctk.CTkFont(size=13, weight="bold"))
        url_title.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        url_box = ctk.CTkFrame(card_input, fg_color="transparent")
        url_box.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")
        url_box.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(url_box, placeholder_text="https://...", height=38)
        self.url_entry.grid(row=0, column=0, sticky="ew")

        folder_box = ctk.CTkFrame(card_input, fg_color="transparent")
        folder_box.grid(row=2, column=0, padx=15, pady=(0, 5), sticky="ew")
        folder_box.grid_columnconfigure(1, weight=1)

        folder_icon = ctk.CTkLabel(folder_box, text="Guardar en:", font=ctk.CTkFont(size=12))
        folder_icon.grid(row=0, column=0, padx=(0, 10), sticky="w")

        display_path = self.download_folder if len(self.download_folder) <= 45 else self.download_folder[:42] + "..."
        self.folder_path_label = ctk.CTkLabel(folder_box, text=display_path, font=ctk.CTkFont(size=11), text_color="gray60", anchor="w")
        self.folder_path_label.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        self.folder_btn = ctk.CTkButton(folder_box, text="Elegir", command=self.choose_folder, width=80, height=30, fg_color="gray25", hover_color="gray35")
        self.folder_btn.grid(row=0, column=2, sticky="e")

        # --- CARD 2: Formatos y Ajustes Adicionales ---
        card_options = ctk.CTkFrame(self.main_frame, corner_radius=12)
        card_options.grid(row=1, column=0, sticky="ew", pady=(0, 15), ipadx=10, ipady=10)
        card_options.grid_columnconfigure((0, 1), weight=1)

        fmt_title = ctk.CTkLabel(card_options, text="Formato de Salida", font=ctk.CTkFont(size=13, weight="bold"))
        fmt_title.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        self.format_seg = ctk.CTkSegmentedButton(
            card_options, values=["MP4 (Video + Audio)", "MP4 (Sin Audio)", "MP3 (Solo Audio)"],
            selected_color="#6C5CE7", selected_hover_color="#5A4BD1", height=36
        )
        self.format_seg.set("MP4 (Video + Audio)")
        self.format_seg.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="ew")

        self.subtitles_var = ctk.BooleanVar(value=False)
        self.subtitles_switch = ctk.CTkSwitch(card_options, text="Subtítulos (Si está disponible)", variable=self.subtitles_var)
        self.subtitles_switch.grid(row=2, column=0, padx=15, pady=5, sticky="w")

        self.thumbnail_var = ctk.BooleanVar(value=False)
        self.thumbnail_switch = ctk.CTkSwitch(card_options, text="Miniatura (Si está disponible)", variable=self.thumbnail_var)
        self.thumbnail_switch.grid(row=2, column=1, padx=15, pady=5, sticky="w")

        # --- CARD 3: Control de Descarga y Consola ---
        card_action = ctk.CTkFrame(self.main_frame, corner_radius=12)
        card_action.grid(row=2, column=0, sticky="nsew", pady=(0, 0), ipadx=10, ipady=10)
        card_action.grid_columnconfigure((0, 1), weight=1)

        self.download_btn = ctk.CTkButton(
            card_action, text="INICIAR DESCARGA", command=self.start_download, height=46,
            font=ctk.CTkFont(size=14, weight="bold"), fg_color="#1DB954", hover_color="#179B45", corner_radius=8
        )
        self.download_btn.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")

        self.cancel_btn = ctk.CTkButton(
            card_action, text="CANCELAR", command=self.cancel_download, height=46,
            font=ctk.CTkFont(size=14, weight="bold"), fg_color="#E74C3C", hover_color="#C0392B", corner_radius=8,
            state="disabled"
        )
        self.cancel_btn.grid(row=0, column=1, padx=(0, 15), pady=(15, 10), sticky="ew")

        self.status_text = ctk.CTkTextbox(
            card_action, height=120, font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#0F0F12", border_width=1, border_color="gray20"
        )
        self.status_text.grid(row=1, column=0, columnspan=2, padx=15, pady=(5, 10), sticky="ew")
        self.status_text.insert("end", "[Sistema] Iniciando y verificando componentes...\n")
        self.status_text.configure(state="disabled")

    # --- MÉTODOS DE LÓGICA, HISTORIAL Y ACTUALIZACIÓN ---

    def _insert_log(self, message):
        """Helper privado para insertar texto en la consola (solo desde hilo principal)."""
        try:
            self.status_text.configure(state="normal")
            self.status_text.insert("end", message + "\n")
            self.status_text.see("end")
            self.status_text.configure(state="disabled")
        except Exception:
            pass

    def log(self, message):
        """Thread-safe log. Usa self.after si se llama desde un hilo secundario."""
        if threading.current_thread() is threading.main_thread():
            self._insert_log(message)
        else:
            self.after(0, lambda m=message: self._insert_log(m))

    def save_to_history(self, url, title, platform):
        """Guarda la descarga en el archivo de historial JSON"""
        try:
            history = []
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            new_entry = {
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "plataforma": platform.upper(),
                "titulo": title[:60] + "..." if len(title) > 60 else title,
                "url": url
            }
            
            history.insert(0, new_entry) # Agregar al principio
            history = history[:50] # Mantener solo los últimos 50
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=4, ensure_ascii=False)
        except Exception:
            pass # Si falla, no interrumpimos la descarga

    def show_history(self):
        """Abre una ventana emergente con el historial"""
        history_window = ctk.CTkToplevel(self)
        history_window.title("Historial de Descargas")
        history_window.geometry("500x400")
        history_window.attributes("-topmost", True)
        
        # Centrar ventana respecto a la principal
        history_window.geometry(f"+{self.winfo_rootx() + 50}+{self.winfo_rooty() + 50}")

        textbox = ctk.CTkTextbox(history_window, width=480, height=350, font=ctk.CTkFont(size=11))
        textbox.pack(padx=10, pady=10, fill="both", expand=True)
        
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            if not history:
                textbox.insert("end", "No hay descargas recientes.\n¡Descarga algo para verlo aquí!")
            else:
                for item in history:
                    textbox.insert("end", f"{item['fecha']} | {item['plataforma']}\n", "date")
                    textbox.insert("end", f"{item['titulo']}\n", "title")
                    textbox.insert("end", f"{item['url']}\n", "url")
                    textbox.insert("end", "─" * 45 + "\n")
        else:
            textbox.insert("end", "No hay historial aún.\n¡Descarga algo para verlo aquí!")
            
        textbox.configure(state="disabled")
        # Colores para el texto del historial
        textbox.tag_config("date", foreground="#F39C12")
        textbox.tag_config("title", foreground="#FFFFFF", font=ctk.CTkFont(size=11, weight="bold"))
        textbox.tag_config("url", foreground="#888888")

    def check_ytdlp_update(self):
        try:
            # Usamos certifi para el contexto SSL seguro
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            
            req = urllib.request.Request(
                "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest",
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=5, context=ssl_context) as response:
                data = json.loads(response.read().decode())
                latest_version = data['tag_name']
                current_version = yt_dlp.__version__
                
                if latest_version != current_version:
                    def _notify_update():
                        self.log(f"Nueva versión de yt-dlp disponible: {latest_version} (Tienes la {current_version})")
                        self.status_badge.configure(text="Actualización disponible", text_color="#F39C12", fg_color="#2C2415")
                    self.after(0, _notify_update)
                    
                    if not getattr(sys, 'frozen', False):
                        self.after(0, lambda: self.log("Intentando actualizar yt-dlp en segundo plano..."))
                        threading.Thread(target=self._update_ytdlp_thread, daemon=True).start()
                    else:
                        self.after(0, lambda: self.log("Nota: Estás usando el .exe. Las actualizaciones del motor vienen en cada nueva versión del programa."))
                else:
                    def _ready():
                        self.status_badge.configure(text="Sistema Listo y Actualizado", text_color="#2ECC71", fg_color="#18281E")
                        self.log("yt-dlp está en su última versión.")
                    self.after(0, _ready)
        except Exception:
            def _offline():
                self.status_badge.configure(text="Sistema Listo (Offline)", text_color="#2ECC71", fg_color="#18281E")
            self.after(0, _offline)

    def _update_ytdlp_thread(self):
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.after(0, lambda: self.log("yt-dlp actualizado correctamente! Reinicia el programa para aplicar cambios."))
                self.after(0, lambda: self.status_badge.configure(text="Actualizado", text_color="#2ECC71", fg_color="#18281E"))
            else:
                self.after(0, lambda: self.log("No se pudo actualizar automáticamente."))
        except Exception as e:
            self.after(0, lambda: self.log(f"Error al actualizar: {e}"))

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_folder = folder
            display_path = folder if len(folder) <= 45 else folder[:42] + "..."
            self.folder_path_label.configure(text=display_path)
            self.log(f"Carpeta seleccionada: {folder}")

    def detect_platform(self, url):
        url_lower = url.lower()
        if 'music.youtube.com' in url_lower: return 'youtube_music'
        elif 'tiktok.com' in url_lower: return 'tiktok'
        elif 'instagram.com' in url_lower: return 'instagram'
        elif 'facebook.com' in url_lower or 'fb.watch' in url_lower: return 'facebook'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower: return 'twitter'
        elif 'reddit.com' in url_lower or 'redd.it' in url_lower: return 'reddit'
        elif 'twitch.tv' in url_lower: return 'twitch'
        elif 'vimeo.com' in url_lower: return 'vimeo'
        elif 'soundcloud.com' in url_lower: return 'soundcloud'
        elif 'dailymotion.com' in url_lower: return 'dailymotion'
        elif 'bilibili.com' in url_lower: return 'bilibili'
        elif 'youtube.com' in url_lower or 'youtu.be' in url_lower: return 'youtube'
        else: return 'universal'

    def is_playlist(self, url):
        url_lower = url.lower()
        return 'playlist' in url_lower or 'list=' in url_lower
    
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            self.log("Error: Debes ingresar una URL")
            return
        
        if not url.startswith(('http://', 'https://')):
            self.log("Error: La URL debe comenzar con http:// o https://")
            return
        
        self.cancel_event.clear()
        self.is_downloading = True
        
        self.download_btn.configure(state="disabled", text="Procesando descarga...", fg_color="gray40")
        self.cancel_btn.configure(state="normal")
        self.status_badge.configure(text="Descargando...", text_color="#F1C40F", fg_color="#2C2815")
        
        self.status_text.configure(state="normal")
        self.status_text.delete("1.0", "end")
        self.status_text.configure(state="disabled")
        
        thread = threading.Thread(target=self.download_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def cancel_download(self):
        if self.is_downloading:
            self.log("Solicitando cancelación...")
            self.cancel_event.set()
    
    def download_thread(self, url):
        platform = self.detect_platform(url)
        is_playlist = self.is_playlist(url)
        
        # Actualizar UI desde hilo secundario de forma segura
        self.after(0, lambda: self.download_btn.configure(state="disabled", text="Descargando...", fg_color="gray40"))
        self.after(0, lambda: self.cancel_btn.configure(state="normal"))
        self.after(0, lambda: self.status_badge.configure(text="Descargando...", text_color="#F1C40F", fg_color="#2C2815"))
        
        if is_playlist:
            self.log("PLAYLIST DETECTADA! Descargando lista...")
        else:
            platform_name = platform.upper() if platform != 'universal' else 'SITIO WEB COMPATIBLE'
            self.log(f"Plataforma detectada: {platform_name}")
        
        selected_fmt_str = self.format_seg.get()
        if selected_fmt_str == "MP3 (Solo Audio)":
            format_choice = "mp3"
        elif selected_fmt_str == "MP4 (Sin Audio)":
            format_choice = "mp4_no_audio"
        else:
            format_choice = "mp4_audio"

        want_subtitles = self.subtitles_var.get()
        want_thumbnail = self.thumbnail_var.get()
        
        def progress_hook(d):
            if self.cancel_event.is_set():
                raise Exception("Descarga cancelada por el usuario")
            
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', 'N/A').strip()
                speed = d.get('_speed_str', 'N/A').strip()
                filename = d.get('filename', '').split('/')[-1].split('\\')[-1]
                self.log(f"{filename[:30]}... | {percent} | {speed}")
            elif d['status'] == 'finished':
                self.log("Procesando/Convirtiendo archivo...")
        
        ydl_opts = {
            # --- Formato y Contenedor ---
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',  # Une en MP4 sin postprocesador problemático
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            
            # --- Callbacks y Logs ---
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,

            # --- Configuración de Red y FFmpeg ---
            'ffmpeg_location': self.ffmpeg_path,
            'retries': 5,
            'fragment_retries': 5,
            'http_chunk_size': 10485760,
            'socket_timeout': 30,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        # Lógica de carpetas: solo usar subcarpeta si es playlist o hay archivos extra
        needs_subfolder = is_playlist or want_subtitles or want_thumbnail
        
        if is_playlist:
            ydl_opts['outtmpl'] = os.path.join(self.download_folder, '%(playlist_title)s', '%(title)s', '%(title)s.%(ext)s')
            self.log("Organización: Carpeta de playlist + subcarpetas por video")
        else:
            if needs_subfolder:
                ydl_opts['outtmpl'] = os.path.join(self.download_folder, '%(title)s', '%(title)s.%(ext)s')
                self.log("Organización: Carpeta con el nombre del video para guardar todo junto")
            else:
                ydl_opts['outtmpl'] = os.path.join(self.download_folder, '%(title)s.%(ext)s')
                self.log("Guardando archivo directamente en la carpeta seleccionada")
        
        if want_subtitles:
            self.log("Subtítulos activados")
            ydl_opts['writesubtitles'] = True
            ydl_opts['subtitlesformat'] = 'srt'
            ydl_opts['subtitleslangs'] = ['es', 'en']
        
        if want_thumbnail:
            self.log("Miniaturas activadas")
            ydl_opts['writethumbnail'] = True
            ydl_opts['convertthumbnails'] = 'jpg'
        
        if platform == "youtube_music":
            self.log("YouTube Music detectado - Optimizando para audio...")
            ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio/best'
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '0'}]
            ydl_opts['addmetadata'] = True
        elif platform == "tiktok":
            self.log("TikTok detectado - Descargando SIN marca de agua...")
            ydl_opts['user_agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
            ydl_opts['format'] = 'best'
        elif platform in ["instagram", "facebook", "twitter", "reddit", "twitch", "vimeo", "soundcloud", "dailymotion", "bilibili"]:
            self.log(f"{platform.capitalize()} detectado. Usando formato compatible...")
            ydl_opts['format'] = 'best'
        else:
            if format_choice == "mp3":
                self.log("Preparando MP3 de alta calidad...")
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '0'}]
            elif format_choice == "mp4_audio":
                self.log("Preparando MP4 con audio...")
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            elif format_choice == "mp4_no_audio":
                self.log("Preparando MP4 sin audio...")
                ydl_opts['format'] = 'bestvideo[ext=mp4]/best'
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extraemos info primero para obtener el título real para el historial
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Video desconocido')
                
                # Ahora sí, descargamos
                ydl.download([url])
                
                # Guardamos en el historial al finalizar con éxito
                self.save_to_history(url, title, platform)
            
            # Verificamos si fue cancelado para no mostrar el mensaje de éxito
            if self.cancel_event.is_set():
                self.log("\n" + "="*40)
                self.log("DESCARGA CANCELADA POR EL USUARIO")
                self.log("="*40)
            else:
                self.log("\n" + "="*40)
                self.log("DESCARGA COMPLETADA CON EXITO!")
                self.log(f"Guardado en: {self.download_folder}")
                self.log("="*40)
            
        except Exception as e:
            if self.cancel_event.is_set() or "cancelada" in str(e).lower():
                self.log("\n" + "="*40)
                self.log("DESCARGA CANCELADA POR EL USUARIO")
                self.log("="*40)
            else:
                self.log(f"\nError: {e}")
                if platform in ["instagram", "facebook"]:
                    self.log("Tip: Si es video privado, se requieren cookies del navegador.")
        
        finally:
            self.is_downloading = False
            self.after(0, lambda: self.download_btn.configure(state="normal", text="INICIAR DESCARGA", fg_color="#1DB954"))
            self.after(0, lambda: self.cancel_btn.configure(state="disabled"))
            self.after(0, lambda: self.status_badge.configure(text="Sistema Listo", text_color="#2ECC71", fg_color="#18281E"))

    def open_donation(self):
        url = "https://ko-fi.com/bafyam" 
        webbrowser.open(url)
        self.log("Gracias por considerar apoyar el proyecto!")
        
    def open_github(self):
        url = "https://github.com/MayorFabDV/Convertidor_de_mp3_y_mp4"
        webbrowser.open(url)
        self.log("Abriendo el repositorio en tu navegador! Código 100% abierto y seguro.")    

if __name__ == "__main__":
    app = UniversalConverter()
    app.mainloop()