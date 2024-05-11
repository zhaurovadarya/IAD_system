# -*- coding: UTF-8 -*-
import pandas as pd
from sqlalchemy import create_engine

def load_excel_to_database(excel_file, conn_str):
    engine = create_engine(conn_str)
    # Чтение данных из каждого листа Excel и загрузка в базу данных
    for sheet_name in pd.ExcelFile(excel_file).sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        df.to_sql(sheet_name, engine, if_exists='replace', index=False)
        print(f"Данные из листа '{sheet_name}' успешно загружены в базу данных.")

# Путь к вашему файлу Excel
excel_file = 'DTP.xlsx'

# Строка подключения к базе данных
conn_str = 'mssql+pyodbc://ZHAUROVAD\\PEP/ДТП по НСО?driver=ODBC+Driver+17+for+SQL+Server'

# Вызов функции для загрузки данных из файла Excel в базу данных
load_excel_to_database(excel_file, conn_str)
