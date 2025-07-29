import requests
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

NUM_THREADS = 8
downloaded = 0
downloaded_lock = threading.Lock()

def get_file_size(url):
    headers = {'Range': 'bytes=0-0'}
    r = requests.get(url, headers=headers, stream=True)
    if 'Content-Range' in r.headers:
        return int(r.headers.get('Content-Range').split('/')[1])
    else:
        return int(r.headers.get('Content-Length'))

def download_part(url, start, end, part_num, temp_dir):
    global downloaded
    headers = {'Range': f'bytes={start}-{end}'}
    r = requests.get(url, headers=headers, stream=True)
    part_path = os.path.join(temp_dir, f'part{part_num}')
    with open(part_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                with downloaded_lock:
                    downloaded += len(chunk)

def combine_parts(temp_dir, total_parts, output_path):
    with open(output_path, 'wb') as outfile:
        for i in range(total_parts):
            part_path = os.path.join(temp_dir, f'part{i}')
            with open(part_path, 'rb') as part_file:
                outfile.write(part_file.read())
            os.remove(part_path)

def show_progress(total_size):
    global downloaded
    last_downloaded = 0
    start_time = time.time()
    while downloaded < total_size:
        time.sleep(1)
        with downloaded_lock:
            current = downloaded
        delta = current - last_downloaded
        last_downloaded = current
        speed = delta / 1024 / 1024  # MB/s
        percent = current / total_size * 100
        print(f"\r🔄 Прогресс: {percent:.2f}% — {current / 1024 / 1024:.2f} MB / {total_size / 1024 / 1024:.2f} MB — 🔽 {speed:.2f} MB/s", end='', flush=True)
    print("\n✅ Скачивание завершено.")

def main():
    global downloaded

    # Запрос ввода от пользователя
    url = input("🔗 Вставьте ссылку на ISO файл: ").strip()
    if not url:
        print("❌ Ошибка: ссылка не может быть пустой.")
        return

    output_name = input("💾 Введите имя для выходного файла (например, Windows10.iso): ").strip()
    if not output_name.endswith('.iso'):
        output_name += '.iso'

    output_path = os.path.abspath(output_name)
    temp_dir = os.path.join(os.path.dirname(output_path), 'temp_parts')

    os.makedirs(temp_dir, exist_ok=True)

    print("⏳ Получаю размер файла...")
    file_size = get_file_size(url)
    print(f"✅ Размер файла: {file_size / (1024 * 1024):.2f} МБ")

    part_size = file_size // NUM_THREADS
    futures = []

    print(f"🚀 Начинаю загрузку ({NUM_THREADS} потоков)...")
    progress_thread = threading.Thread(target=show_progress, args=(file_size,))
    progress_thread.start()

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        for i in range(NUM_THREADS):
            start = i * part_size
            end = (start + part_size - 1) if i < NUM_THREADS - 1 else file_size - 1
            futures.append(executor.submit(download_part, url, start, end, i, temp_dir))

    for future in futures:
        future.result()

    progress_thread.join()

    print("\n🔧 Объединяю части...")
    combine_parts(temp_dir, NUM_THREADS, output_path)
    os.rmdir(temp_dir)

    print(f"🎉 Файл сохранён: {output_path}")

if __name__ == "__main__":
    main()
