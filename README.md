# 🌍 Universal Converter - Bafyam Media

Convertidor/descargador de videos multi-plataforma, gratuito, sin anuncios y de código abierto.

¡¡¡ADVERTENCIA EL ANTIVIRUS PUEDE MARVAR DE FALSO POSITIVO EL PROGRAMA POR EL METODO DE yt-dlp EN VIRUS TOTAL SOLO DOS DE 67 (six seven xd) ANTIVIRUS COMO LO SON MICROSOFT DEFENDER LO MARCAN DE VIRUS!!!

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Ads](https://img.shields.io/badge/Ads-0-red)

## ✨ Características

- 🎬 **Multi-plataforma**: YouTube, TikTok (sin marca de agua), Instagram, Facebook, X/Twitter, Reddit, Twitch, Vimeo, SoundCloud, YouTube Music y +1000 sitios más
- 📋 **Soporte para Playlists**: Descarga listas completas organizadas en carpetas
- 🎨 **Formatos flexibles**: MP4 (con/sin audio), MP3 de alta calidad
- 📝 **Subtítulos**: Descarga subtítulos en SRT (español e inglés)
- 🖼️ **Miniaturas**: Guarda la imagen de portada en JPG
- 📁 **Organización automática**: Crea carpetas por video/playlist
- 🛡️ **Blindaje anti-fallos**: Reintentos automáticos, manejo de redes inestables
- 🔄 **Auto-actualización**: Detecta nuevas versiones de yt-dlp
- ☕ **100% gratis y sin anuncios**

## 🚀 Instalación

### Opción 1: Ejecutable 
1. Descarga el `.exe` desde [Releases](https://github.com/MayorFabDV/Convertidor_de_mp3_y_mp4/releases)
2. Ejecútalo. No requiere instalación.

### Opción 2: Desde el código fuente
```bash
# Clonar el repositorio
git clone https://github.com/MayorFabDV/Convertidor_de_mp3_y_mp4
.git
cd TU_REPO

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Descargar ffmpeg.exe y colocarlo en la carpeta del proyecto
# (Descarga desde: https://github.com/BtbN/FFmpeg-Builds/releases)

# Ejecutar
python convertidor_gui2.py

Compila tu propio exe como quieras
pyinstaller --onefile --windowed --add-binary "ffmpeg.exe;." --name "Nombre XD" convertidor_gui2.py

¿Como usar?
Pega el link del video o playlist
Elige el formato (MP4, MP3)
Activa las opciones que necesites (subtítulos, miniatura)
Elige la carpeta de destino
¡Click en "INICIAR DESCARGA"!

La estructura de descarga es así
📁 Carpeta_Destino/
   └── 📁 Nombre_del_Video/
       ├── 🎬 video.mp4
       ├── 📝 subtitulos.srt
       └── 🖼️ miniatura.jpg

Contribuciones
¿Tienes una idea o encontraste un bug? ¡Abre un Issue o un Pull Request!

☕ Apoya el proyecto
https://ko-fi.com/bafyam 

MIT License - Libre para usar, modificar y distribuir.

Hecho con <3 por Bafyam
