import os
from PIL import Image

INPUT_FOLDER = 'input_images'
OUTPUT_FOLDER = 'output_images'
TARGET_SIZE = 600  # размер итогового изображения
ASPECT_RATIO = 1.0  # отношение сторон: ширина / высота

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def crop_to_aspect(img, aspect_ratio):
    width, height = img.size
    current_ratio = width / height

    if current_ratio > aspect_ratio:
        # слишком широкое — обрежем по бокам
        new_width = int(height * aspect_ratio)
        left = (width - new_width) // 2
        img = img.crop((left, 0, left + new_width, height))
    elif current_ratio < aspect_ratio:
        # слишком высокое — обрежем сверху и снизу
        new_height = int(width / aspect_ratio)
        top = (height - new_height) // 2
        img = img.crop((0, top, width, top + new_height))

    return img

def process_image(file_path, output_path):
    with Image.open(file_path) as img:
        img = img.convert("RGB")  # на случай PNG с альфой

        # Кадрируем до заданного соотношения (1:1 по умолчанию)
        img = crop_to_aspect(img, ASPECT_RATIO)

        # Изменяем размер
        img = img.resize((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)

        # Сохраняем с качеством и сжатием
        out_name = os.path.basename(file_path)
        name, ext = os.path.splitext(out_name)
        out_file = os.path.join(output_path, f"{name}.jpg")
        img.save(out_file, format="JPEG", quality=90, optimize=True)

def batch_process(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            in_path = os.path.join(input_folder, filename)
            try:
                process_image(in_path, output_folder)
                print(f'✅ Обработано: {filename}')
            except Exception as e:
                print(f'❌ Ошибка с {filename}: {e}')

if __name__ == '__main__':
    batch_process(INPUT_FOLDER, OUTPUT_FOLDER)
