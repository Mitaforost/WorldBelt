"""
🎬 YouTube Video Downloader

Этот скрипт позволяет загружать одиночные YouTube-видео в формате mp4 с наилучшим качеством.
Основан на библиотеке `yt_dlp` — форке youtube-dl, который активно поддерживается и обновляется.

🔧 Особенности:
- Загружает только одно видео (без плейлистов)
- Сохраняет файл под названием видео (`%(title)s.%(ext)s`)
- Использует лучший доступный формат в mp4 (если доступен)

📦 Требования:
Установите `yt_dlp`, если ещё не установлен:
    pip install yt-dlp
"""
from yt_dlp import YoutubeDL

def download_video(url):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    url = input("🎥 Введите ссылку на YouTube-видео: ")
    download_video(url)
