import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import pandas as pd
from datetime import datetime


def fetch_soup(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Ошибка загрузки {url}")
        return None
    return BeautifulSoup(response.text, 'html.parser')


def extract_data(soup):
    data = []
    articles = soup.select('div.article-list div.article')
    for article in articles:
        title_tag = article.select_one('div.article-header h2 a')
        date_tag = article.select_one('div.article-info span.published time')

        if title_tag and date_tag:
            title = title_tag.text.strip()
            date = date_tag['datetime']
            data.append({'title': title, 'date': date})
    return data


def get_pagination_links(soup, base_url):
    pagination = soup.select_one('nav.pagination-wrapper')
    if not pagination:
        return []

    links = []
    for a in pagination.select('ul.pagination a.page-link'):
        if 'href' in a.attrs:
            full_url = urljoin(base_url, a['href'])
            if full_url not in links:
                links.append(full_url)
    return links


def scrape_news_data(start_url, output_file="news_data.xlsx"):
    visited_pages = set()
    to_visit = [start_url]
    all_data = []

    while to_visit:
        current_url = to_visit.pop(0)
        if current_url in visited_pages:
            continue

        visited_pages.add(current_url)
        print(f"Парсим страницу: {current_url}")

        soup = fetch_soup(current_url)
        if not soup:
            continue

        data = extract_data(soup)
        all_data.extend(data)

        new_links = get_pagination_links(soup, start_url)
        to_visit.extend([link for link in new_links if link not in visited_pages and link not in to_visit])
        time.sleep(1)  # Пауза для снижения нагрузки на сервер

    # Сохранение данных в Excel
    df = pd.DataFrame(all_data)
    df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_convert(None)
    df = df.sort_values(by='date', ascending=False)
    df.to_excel(output_file, index=False)

    # Подсчет статей
    total_articles = len(df)
    today = datetime.now().date()
    today_articles = df[df['date'].dt.date == today].shape[0]

    print(f"Всего статей: {total_articles}")
    print(f"Статей за сегодня: {today_articles}")

    print("Парсинг завершен! Все данные сохранены в", output_file)


if __name__ == "__main__":
    start_url = input("Введите URL страницы с новостями: ").strip()
    scrape_news_data(start_url)