import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import pandas as pd


def extract_h2(url, depth=0, visited=None, rows=None, current_category=None, category_override=None):
    """
    Извлекает только H2 заголовки со страниц сайта.
    """
    if visited is None:
        visited = set()
    if rows is None:
        rows = []

    if url in visited:
        return rows
    visited.add(url)

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Ошибка при загрузке {url}")
        return rows

    soup = BeautifulSoup(response.text, 'html.parser')

    # Title страницы (тег <title>)
    title_tag = soup.find('title')
    page_title = title_tag.text.strip() if title_tag else ""

    # META Title (<meta name="title"> или <meta property="og:title">)
    meta_title = ""
    meta_title_tag = soup.find('meta', attrs={'name': 'title'})
    if meta_title_tag and meta_title_tag.get('content'):
        meta_title = meta_title_tag['content'].strip()
    else:
        og_title_tag = soup.find('meta', attrs={'property': 'og:title'})
        if og_title_tag and og_title_tag.get('content'):
            meta_title = og_title_tag['content'].strip()

    # META Description (<meta name="description">)
    meta_description = ""
    meta_description_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_description_tag and meta_description_tag.get('content'):
        meta_description = meta_description_tag['content'].strip()

    # H1 страницы
    h1_tag = soup.find('h1')
    h1_text = h1_tag.text.strip() if h1_tag else ""

    # H2 теги
    h2_tags = soup.find_all('h2')
    h2_texts = [h2.text.strip() for h2 in h2_tags if h2.text.strip()]

    # Название категории или подкатегории
    category_name = category_override or current_category or ""

    # Добавляем строку
    row = [category_name, page_title, meta_title, meta_description, h1_text, url] + h2_texts
    rows.append(row)

    # Обрабатываем подкатегории (кнопки)
    subcategories = soup.find_all('a', class_='btn btn-sm btn-outline-secondary')
    for sub in subcategories:
        sub_url = sub.get('href')
        sub_name = sub.get_text(strip=True)
        if sub_url:
            full_sub_url = urljoin(url, sub_url)
            time.sleep(1)
            extract_h2(full_sub_url, depth + 1, visited, rows, current_category=category_name, category_override=sub_name)

    # Обрабатываем категории на главной (если глубина = 0)
    if depth == 0:
        category_items = soup.select('.categories-list .card')
        for item in category_items:
            category_url = item.get('href')
            if category_url:
                full_url = urljoin(url, category_url)
                time.sleep(1)
                extract_h2(full_url, depth + 1, visited, rows)

    return rows


def extract_h3(url, h2_columns, depth=0):
    """
    Извлекает H3 заголовки со страниц сайта и добавляет их после соответствующих H2.
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Ошибка при загрузке {url}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # H2 и связанные H3
    h2_tags = soup.find_all(['h2', 'h3'])
    current_h2_index = -1
    h2_h3_structure = [[] for _ in range(h2_columns)]  # Инициализируем пустую структуру для H3

    for tag in h2_tags:
        if tag.name == 'h2':
            current_h2_index += 1
        elif tag.name == 'h3' and 0 <= current_h2_index < h2_columns:
            h2_h3_structure[current_h2_index].append(tag.text.strip())

    # Преобразуем структуру H3 в плоский список
    h3_flattened = []
    for h3_list in h2_h3_structure:
        h3_flattened.extend(h3_list)

    return h3_flattened


if __name__ == "__main__":
    # ЭТАП 1: Извлечение H2 заголовков
    start_url = input("Введите URL сайта: ").strip()
    rows = extract_h2(start_url)

    # Определяем максимальное количество H2, чтобы создать колонки
    max_h2_count = max((len(row) - 6 for row in rows), default=0)  # Учитываем 6 базовых колонок
    columns = ['Категория', 'Title страницы', 'META Title', 'META Description', 'H1', 'Ссылка на страницу'] + [f'H2_{i+1}' for i in range(max_h2_count)]

    # Выравниваем строки по количеству колонок
    for row in rows:
        while len(row) < len(columns):
            row.append("")

    df = pd.DataFrame(rows, columns=columns)
    df.to_excel("site_structure.xlsx", index=False)

    print("✅ H2 заголовки сохранены в site_structure.xlsx")

    # ЭТАП 2: Извлечение H3 заголовков
    df = pd.read_excel("site_structure.xlsx")
    h3_rows = []

    for _, row in df.iterrows():
        url = row['Ссылка на страницу']
        h2_cols = sum(1 for col in row.index if col.startswith('H2_') and pd.notna(row[col]))
        h3_texts = extract_h3(url, h2_cols)
        h3_rows.append(list(row) + h3_texts)

    # Определяем максимальное количество H3
    max_h3_count = max((len(row) - len(columns) for row in h3_rows), default=0)
    final_columns = columns + [f'H3_{i+1}' for i in range(max_h3_count)]

    # Выравниваем строки по количеству колонок
    for row in h3_rows:
        while len(row) < len(final_columns):
            row.append("")

    final_df = pd.DataFrame(h3_rows, columns=final_columns)
    final_df.to_excel("site_structure.xlsx", index=False)

    print("✅ Полная структура H2 и H3 сохранена в site_structure.xlsx")