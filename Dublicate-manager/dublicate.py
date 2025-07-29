import re
from bs4 import BeautifulSoup
from collections import defaultdict

# Определяем отделы продаж
DEPARTMENTS = {
    "Первый отдел": ["Владимир Соколов", "Елена Гуйдо", "Андрей Черепович", "Карина Точилина"],
    "Второй отдел": ["Эвелина Войнович", "Юлия Пузыревич", "Арсений Падерин"],
    "Третий отдел": ["Наталья Белоус", "Татьяна Ращупкина", "Илья Погула"],
}

def get_department_by_responsible(responsible_name):
    """Возвращает название отдела, к которому относится ответственный сотрудник."""
    for department, employees in DEPARTMENTS.items():
        if responsible_name in employees:
            return department
    return "Неизвестный отдел"

def parse_html(file_path):
    # Читаем HTML из файла
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Используем BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(html_content, "html.parser")
    rows = soup.find_all("tr", class_="main-grid-row-body")

    responsibles = defaultdict(list)
    client_to_responsibles = defaultdict(set)  # Сопоставление клиента с ответственными
    client_details = {}  # Для хранения деталей клиента

    for row in rows:
        # Извлекаем ответственного сотрудника
        responsible_div = row.find("div", class_="crm-dedupe-grid-user-responsible")
        responsible_name = responsible_div.find("a", class_="crm-dedupe-grid-user-name").text if responsible_div else "Неизвестно"

        # Извлекаем имя лица
        user_div = row.find("div", class_="crm-dedupe-grid-user")
        user_name = user_div.find("a", class_="crm-dedupe-grid-user-name").text if user_div else "Неизвестно"

        # Извлекаем описание совпадения
        match_desc_div = row.find_all("td", class_="main-grid-cell")[2]
        match_description = match_desc_div.text.strip() if match_desc_div else ""

        # Извлекаем телефон
        phone_div = row.find("a", class_="crm-client-contacts-block-text-tel", href=re.compile(r"callto://"))
        phone = phone_div.text.strip() if phone_div else "Не указан"

        # Извлекаем email
        email_div = row.find("a", href=re.compile(r"mailto:"))
        email = email_div.text.strip() if email_div else "Не указан"

        # Логика для обработки совпадений
        if responsible_name == user_name:
            # Если ответственный совпадает с клиентом, отмечаем как "Собственный дубликат"
            match_description = "Собственный дубликат"
        elif not match_description or match_description == "Не указан":
            # Если совпадения нет, ищем родительскую строку
            parent_row = row.find_previous_sibling("tr")
            if parent_row:
                parent_responsible_div = parent_row.find("div", class_="crm-dedupe-grid-user-responsible")
                parent_responsible_name = parent_responsible_div.find("a", class_="crm-dedupe-grid-user-name").text if parent_responsible_div else "Неизвестно"
                match_description = f"Совпадение по телефону {phone} - ответственный {parent_responsible_name} ({get_department_by_responsible(parent_responsible_name)})"
            else:
                match_description = f"{phone} - ответственный неизвестен"

        # Сохраняем данные для ответственного
        responsibles[responsible_name].append({
            "user_name": user_name,
            "match_description": match_description,
            "phone": phone,
            "email": email,
        })

        # Сохраняем детали клиента
        client_details[user_name] = {
            "match_description": match_description,
            "phone": phone,
            "email": email,
            "responsible_name": responsible_name,
        }

        # Связываем клиента с ответственным
        client_to_responsibles[user_name].add(responsible_name)

    return responsibles, client_to_responsibles, client_details

def write_statistics_to_file(responsibles, client_to_responsibles, client_details, output_file_path):
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write("Статистика по ответственным и их дубликатам:\n")
        file.write("=" * 50 + "\n")
        for responsible, duplicates in responsibles.items():
            department = get_department_by_responsible(responsible)
            file.write(f"Ответственный: {responsible} ({department})\n")
            for idx, duplicate in enumerate(duplicates, start=1):
                file.write(f"  {idx}. {duplicate['user_name']}\n")
                file.write(f"     - Совпадение: {duplicate['match_description']}\n")
                file.write(f"     - Телефон: {duplicate['phone']}, E-mail: {duplicate['email']}\n")

                # Если клиент связан с другими ответственными
                involved_responsibles = client_to_responsibles[duplicate['user_name']]
                if len(involved_responsibles) > 1:
                    file.write("     - Связан с:\n")
                    for res in involved_responsibles:
                        if res != responsible:
                            res_department = get_department_by_responsible(res)
                            file.write(f"       - {res} ({res_department})\n")
            file.write("-" * 50 + "\n")

# Основной скрипт
if __name__ == "__main__":
    input_file = "input.txt"  # Входной файл с HTML-кодом
    output_file = "output.txt"  # Выходной файл с результатами

    print("Анализируем HTML...")
    responsible_data, client_to_responsibles, client_details = parse_html(input_file)

    print("Записываем статистику в файл...")
    write_statistics_to_file(responsible_data, client_to_responsibles, client_details, output_file)

    print(f"Статистика успешно сохранена в '{output_file}'.")