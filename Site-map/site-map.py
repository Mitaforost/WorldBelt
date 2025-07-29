# 📄 Этот скрипт автоматически обходит сайт, начиная с указанной главной страницы:
# - Извлекает заголовки и описания категорий и подкатегорий
# - Сохраняет структуру сайта в файл `structure.txt`
# - Сохраняет тексты и описания в файл `output.txt`
# - Работает рекурсивно и избегает повторного посещения одних и тех же страниц
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin


def extract_text_and_structure(url, depth=0, visited=None, structure_file="structure.txt", output_file="output.txt"):
    if visited is None:
        visited = set()

    if url in visited:
        return
    visited.add(url)

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Ошибка при загрузке {url}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    if depth == 0:
        # Извлекаем заголовок h1 для начальной страницы
        h1_tag = soup.find('h1')
        category_name = h1_tag.text.strip() if h1_tag else "Без названия"

        # Записываем заголовок в structure.txt
        with open(structure_file, "a", encoding="utf-8") as struct_file:
            struct_file.write(f"- {category_name}\n")

        # Извлекаем описание из div с нужным классом
        description = []
        info_div = soup.find('div', class_='category info text-left')
        if info_div:
            paragraphs = info_div.find_all('p')
            description = [p.text.strip() for p in paragraphs if p.text.strip()]

        # Записываем заголовок и описание в output.txt
        with open(output_file, "a", encoding="utf-8") as out_file:
            out_file.write(f"{'=' * 50}\n")
            out_file.write(f"{category_name}\n\n")
            out_file.write("\n".join(description) + "\n" if description else "Описание отсутствует\n")
            out_file.write(f"{'=' * 50}\n\n")

        # Ищем все категории на главной странице
        category_items = soup.select('.categories-list .card')
        for item in category_items:
            category_url = urljoin(url, item.get('href'))
            category_name = item.select_one('.card-title').text.strip()

            # Записываем категорию в structure.txt
            with open(structure_file, "a", encoding="utf-8") as struct_file:
                struct_file.write(f"  - {category_name}\n")

            # Переходим в категорию
            time.sleep(1)  # Даем паузу, чтобы не перегружать сайт
            extract_text_and_structure(category_url, depth + 1, visited, structure_file, output_file)
    else:
        # Для подкатегорий используем текст ссылки
        category_name = soup.find('title').text.strip()

    # Ищем подкатегории (ссылки с нужным классом)
    subcategories = soup.find_all('a', class_='btn btn-sm btn-outline-secondary')
    for sub in subcategories:
        sub_url = sub.get('href')
        sub_name = sub.text.strip()

        if sub_url:
            # Преобразуем относительную ссылку в абсолютную
            full_sub_url = urljoin(url, sub_url)

            if full_sub_url not in visited:
                # Записываем подкатегорию в structure.txt
                indent = "  " * (depth + 1)
                with open(structure_file, "a", encoding="utf-8") as struct_file:
                    struct_file.write(f"{indent}- {sub_name}\n")

                # Извлекаем описание из div с нужным классом
                description = []
                info_div = soup.find('div', class_='category info text-left')
                if info_div:
                    paragraphs = info_div.find_all('p')
                    description = [p.text.strip() for p in paragraphs if p.text.strip()]

                # Записываем заголовок (текст ссылки) и описание в output.txt
                with open(output_file, "a", encoding="utf-8") as out_file:
                    out_file.write(f"{'=' * 50}\n")
                    out_file.write(f"{sub_name}\n\n")
                    out_file.write("\n".join(description) + "\n" if description else "Описание отсутствует\n")
                    out_file.write(f"{'=' * 50}\n\n")

                # Переходим в подкатегорию
                time.sleep(1)  # Даем паузу, чтобы не перегружать сайт
                extract_text_and_structure(full_sub_url, depth + 1, visited, structure_file, output_file)


if __name__ == "__main__":
    start_url = input("Введите URL сайта: ").strip()

    # Очищаем файлы перед началом работы
    open("structure.txt", "w", encoding="utf-8").close()
    open("output.txt", "w", encoding="utf-8").close()

    extract_text_and_structure(start_url)
    print("Сбор данных завершен!")
