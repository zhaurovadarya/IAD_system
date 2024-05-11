# -*- coding: UTF-8 -*-
import pandas as pd
import json

def process_json_to_excel(json_file, excel_file):
    print("Начало обработки данных из файла JSON...")
    # Загрузка данных из файла JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Распаковка JSON строки из объекта "data"
    data = json.loads(data["data"])

    # Преобразование данных в DataFrame
    df = pd.DataFrame(data["cards"])

    # Сохранение данных в файл Excel
    df.to_excel(excel_file, index=False)
    print(f"Данные успешно сохранены в файле {excel_file}")

# Путь к вашему файлу JSON
json_file_path = r'C:\Users\Дарья\Desktop\Полетайкин\!Анализ на ПАЙТОНЕ\курсач\IAD-main\IAD-main\IAD\50 Новосибирская область 1-12.2024.json'

# Путь для сохранения файла Excel
excel_file_path = r'C:\Users\Дарья\Desktop\Полетайкин\!Анализ на ПАЙТОНЕ\курсач\IAD-main\IAD-main\IAD\DTP_NSO.xlsx'

# Вызов функции для обработки файла JSON и сохранения данных в Excel
process_json_to_excel(json_file_path, excel_file_path)