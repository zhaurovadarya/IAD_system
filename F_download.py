# -*- coding: UTF-8 -*-
import pandas as pd
from sqlalchemy import create_engine, inspect, text


def load_excel_to_database(excel_file, conn_str):
    engine = create_engine(conn_str)
    inspector = inspect(engine)

    # Чтение данных из каждого листа Excel и загрузка в базу данных
    for sheet_name in pd.ExcelFile(excel_file).sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        table_name = sheet_name.lower()

        # Проверка наличия таблицы в базе данных
        if inspector.has_table(table_name):
            print(f"Таблица '{table_name}' существует в базе данных.")
        else:
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"Данные из листа '{sheet_name}' успешно загружены в базу данных.")

        # Проверка наличия новых данных в таблице
        with engine.connect() as connection:
            stmt = text(f"SELECT COUNT(*) FROM {table_name}")
            result = connection.execute(stmt)
            row_count = result.scalar()

        if row_count == 0:
            print(f"В таблице '{table_name}' нет новых данных.")
        else:
            print(f"В таблице '{table_name}' обнаружены данные.")


# Путь к вашему файлу Excel
excel_file = 'DTP.xlsx'

# Строка подключения к базе данных
conn_str = 'mssql+pyodbc://ZHAUROVAD\\PEP/ДТП по НСО?driver=ODBC+Driver+17+for+SQL+Server'

# Вызов функции для загрузки данных из файла Excel в базу данных
load_excel_to_database(excel_file, conn_str)
