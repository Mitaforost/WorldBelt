from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def check_all_products_with_comments(start_url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    with_questions = 0
    without_questions = 0

    with open("questions.txt", "w", encoding="utf-8") as questions_file:

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
            product_links = [a['href'] for a in soup.select('a.h6.te    xt-decoration-none') if a.get('href')]
            print(f"🔗 Найдено {len(product_links)} товаров. Проверяем наличие блока вопросов...")

            for i, link in enumerate(product_links, 1):
                full_url = urljoin(start_url, link)
                print(f"\n🛒 [{i}/{len(product_links)}] Проверка: {full_url}")

                try:
                    driver.get(full_url)

                    # Ждём форму комментариев, если она появляется
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.ID, "comments-form"))
                    )

                    product_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    has_form = product_soup.find('form', id='comments-form')
                    comments_div = product_soup.find('div', id='comments')
                    has_comments = comments_div and comments_div.find()

                    if has_form and has_comments:
                        with_questions += 1
                        
                        print("✅ Вопросы есть")
                    else:
                        without_questions += 1
                        questions_file.write(full_url + "\n")
                        print("❌ Вопросов нет")

                except Exception as e:
                    without_questions += 1
                    print(f"⚠️ Нет формы или вопросы не найдены (или ошибка): {e}")

        finally:
            driver.quit()

    # Статистика
    print("\n📊 Результаты проверки:")
    print(f"— С вопросами: {with_questions}")
    print(f"— Без вопросов: {without_questions}")
    print(f"— Всего: {with_questions + without_questions}")
    print("📁 Все товары без вопросов записаны в questions.txt")

# Запуск
if __name__ == "__main__":
    url = input("Введите URL каталога с товарами: ").strip()
    check_all_products_with_comments(url)
