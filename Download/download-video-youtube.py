from yt_dlp import YoutubeDL

def download_video(url):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',  # Пытается сохранить в mp4, если возможно
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegMerger',
            'preferredformat': 'mp4',  # Требует ffmpeg, но если его нет, ytdlp сам выдаст ошибку и предложит fallback
        }],
        'ffmpeg_location': 'none',  # Попробовать без ffmpeg
        'noplaylist': True,
        'quiet': False,
        'no_warnings': False,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("Попробуем скачать самое лучшее совместимое видео без слияния...")
        fallback_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': '%(title)s.%(ext)s',
        }
        with YoutubeDL(fallback_opts) as ydl:
            ydl.download([url])

if __name__ == "__main__":
    url = input("🎥 Введите ссылку на YouTube-видео: ")
    download_video(url)
