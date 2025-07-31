# рандомно отбирает 3 товара без вопросов

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import random

def collect_random_no_question_links(start_url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        print(f"🔍 Загружаем страницу: {start_url}")
        driver.get(start_url)
        time.sleep(2)

        # Нажимаем кнопку "Показать ещё", пока доступна
        while True:
            try:
                show_more = driver.find_element(By.XPATH, '//button[@radicalmart-ajax-paginaton="button"]')
                driver.execute_script("arguments[0].click();", show_more)
                time.sleep(1)
            except:
                break

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        product_links = [urljoin(start_url, a['href']) for a in soup.select('a.h6.text-decoration-none') if a.get('href')]
        print(f"🔗 Найдено {len(product_links)} товаров.")

        # Перемешиваем список
        random.shuffle(product_links)

        found = 0
        max_needed = 3

        with open("questions.txt", "w", encoding="utf-8") as questions_file:
            for i, full_url in enumerate(product_links, 1):
                if found >= max_needed:
                    break

                print(f"\n🛒 Проверка: {full_url}")

                try:
                    driver.get(full_url)

                    # Ждём, но не обязательно — не все товары его имеют
                    try:
                        WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.ID, "comments-form"))
                        )
                    except:
                        pass  # форма может не загрузиться — это нормально

                    product_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    has_form = product_soup.find('form', id='comments-form')
                    comments_div = product_soup.find('div', id='comments')
                    has_comments = comments_div and comments_div.find()

                    if not (has_form and has_comments):
                        questions_file.write(full_url + "\n")
                        print("✅ Добавлено (вопросов нет)")
                        found += 1
                    else:
                        print("⏭️ Вопросы есть — пропускаем")

                except Exception as e:
                    print(f"⚠️ Ошибка: {e}")
                    continue

        print(f"\n📁 Готово! Найдено {found} товаров без вопросов. Ссылки записаны в questions.txt")

    finally:
        driver.quit()


# Запуск
if __name__ == "__main__":
    url = input("Введите URL каталога с товарами: ").strip()
    collect_random_no_question_links(url)
