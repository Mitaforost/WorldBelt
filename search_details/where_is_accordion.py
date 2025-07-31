# ищет все товары в категории, для которых подробнее стоит в блоке описания (пропущена эта черточка)

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def extract_articuls_with_wrong_more(start_url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    unique_articuls = set()  # Для хранения уникальных артикулов

    try:
        print(f"🔍 Загружаем страницу: {start_url}")
        driver.get(start_url)
        time.sleep(2)

        # Нажимаем "Показать ещё", пока доступна
        while True:
            try:
                show_more = driver.find_element(By.XPATH, '//button[@radicalmart-ajax-paginaton="button"]')
                driver.execute_script("arguments[0].click();", show_more)
                time.sleep(1)
            except:
                break

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        product_links = [a['href'] for a in soup.select('a.h6.text-decoration-none') if a.get('href')]
        print(f"🔗 Найдено {len(product_links)} товаров.")

        for i, link in enumerate(product_links, 1):
            full_url = urljoin(start_url, link)
            print(f"\n🛒 [{i}/{len(product_links)}] Проверка: {full_url}")

            try:
                driver.get(full_url)
                time.sleep(1)
                product_soup = BeautifulSoup(driver.page_source, 'html.parser')

                # Находим все блоки col-md-4
                col_md_4_blocks = product_soup.find_all('div', class_='col-md-4')
                
                found_wrong = False
                
                for col_md_4 in col_md_4_blocks:
                    # Проверяем наличие аккордеона внутри текущего col-md-4
                    if col_md_4.find('div', id='rlta-podrobnee'):
                        print("❗️ Найден товар с аккордеоном в col-md-4")
                        found_wrong = True
                        break
                
                if not found_wrong:
                    print("✅ Аккордеон не найден в col-md-4 — товар правильный")
                    continue

                # Извлекаем артикул из характеристик
                articul = None
                characteristics = product_soup.find('dl', class_='product-main-fields')
                if characteristics:
                    for dt in characteristics.find_all('dt'):
                        if 'Артикул' in dt.get_text(strip=True):
                            dd = dt.find_next_sibling('dd')
                            if dd:
                                articul = dd.get_text(strip=True)
                                break

                if articul:
                    if articul not in unique_articuls:
                        unique_articuls.add(articul)
                        print(f"📌 Найден новый артикул: {articul}")
                    else:
                        print(f"ℹ️ Артикул {articul} уже был сохранен ранее")
                else:
                    print("⚠️ Артикул не найден")

            except Exception as e:
                print(f"❌ Ошибка при обработке товара: {e}")
                continue

    finally:
        driver.quit()

    # Записываем уникальные артикулы в файл
    if unique_articuls:
        with open("articuls.txt", "w", encoding="utf-8") as out_file:
            out_file.write("\n".join(sorted(unique_articuls)))
        print(f"\n📁 Готово! Найдено и записано {len(unique_articuls)} уникальных артикулов в 'articuls.txt'")
    else:
        print("\n📁 Не найдено ни одного товара с неправильным расположением аккордеона")

# Запуск
if __name__ == "__main__":
    url = input("Введите URL каталога: ").strip()
    extract_articuls_with_wrong_more(url)