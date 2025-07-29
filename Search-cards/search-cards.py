"""
🌐 Парсер Страниц с Динамической Подгрузкой (Selenium + BeautifulSoup)

Этот скрипт автоматически загружает контент со страниц сайта, где используется кнопка "Показать ещё"
(динамическая подгрузка товаров), а затем извлекает названия товаров и структуру разделов.

🧠 Использует:
- Selenium (управление браузером, клик по кнопке загрузки)
- BeautifulSoup (парсинг HTML)
- Headless Chrome (работа без GUI)

📄 Что делает:
1. Переходит на указанный URL
2. Нажимает кнопку "Показать ещё", пока она доступна
3. Извлекает:
   - Заголовок страницы (`<h1>`)
   - Ссылки/названия товаров (селектор: `a.h6.text-decoration-none`)
4. Сохраняет данные:
   - `structure.txt` — список заголовков
   - `output.txt` — найденные товары с разделителями

📦 Требования:
    pip install selenium beautifulsoup4

🔧 Примечание:
- Предполагается, что используется ChromeDriver и он добавлен в PATH
- Работает в headless-режиме (без открытия окна браузера)

"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

def extract_text_and_structure(url, structure_file="structure.txt", output_file="output.txt"):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Запуск без GUI
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(2)

        click_count = 0
        while True:
            try:
                button = driver.find_element(By.XPATH, '//button[@radicalmart-ajax-paginaton="button"]')
                driver.execute_script("arguments[0].click();", button)
                time.sleep(2)  # Ждём загрузки новых данных
                click_count += 1
            except:
                print("Кнопка 'Показать ещё' больше не найдена.")
                break

        print(f"Кнопка была нажата {click_count} раз.")

        # Получаем HTML-код страницы после всех подгрузок
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Извлекаем заголовок страницы
        h1_tag = soup.find('h1')
        page_title = h1_tag.text.strip() if h1_tag else "Без названия"

        # Записываем заголовок
        with open(structure_file, "a", encoding="utf-8") as f:
            f.write(f"- {page_title}\n")

        # Извлекаем товары
        product_cards = soup.select('div.row.row-cols-2.row-cols-md-2.row-cols-lg-3 a.h6.text-decoration-none')
        products = {card.text.strip() for card in product_cards}

        # Записываем в файл
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"{'=' * 50}\n{page_title}\n\n")
            f.write("\n".join(products) + "\n" if products else "Товары отсутствуют\n")
            f.write(f"{'=' * 50}\n\n")

        print(f"Найдено {len(products)} уникальных товаров.")
        print("Сбор данных завершен!")

    finally:
        driver.quit()

if __name__ == "__main__":
    start_url = input("Введите URL сайта: ").strip()

    # Очищаем файлы перед началом
    open("structure.txt", "w", encoding="utf-8").close()
    open("output.txt", "w", encoding="utf-8").close()

    extract_text_and_structure(start_url)
    print("Сбор данных завершен!")
