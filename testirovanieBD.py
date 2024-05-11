from sqlalchemy import create_engine, MetaData, Table

def testirovanieBD():
    # Строка подключения к базе данных
    conn_str = 'mssql+pyodbc://ZHAUROVAD\\PEP/ДТП по НСО?driver=ODBC+Driver+17+for+SQL+Server'

    # Создание объекта для работы с базой данных
    engine = create_engine(conn_str)

    # Создание объекта метаданных
    metadata = MetaData()

    # Связывание метаданных с базой данных
    metadata.reflect(bind=engine)

    # Список таблиц
    tables = ['Accident', 'Addres', 'Vehicles', 'Participants', 'Associated_Offenses', 'Participant_Offenses',
              'Accident_Influence', 'Deficiencies', 'Factors', 'Influence_Deficiency', 'Influence_Factor',
              'Objects_Accident_Site', 'Objects_Near_Accident_Site', 'Address_Objects_Accident_Site',
              'Address_Objects_Near_Accident_Site']

    # Перебор таблиц и выполнение запросов SELECT
    for table_name in tables:
        # Получение объекта таблицы
        table = Table(table_name, metadata, autoload=True, autoload_with=engine)

        # Установка соединения с базой данных
        conn = engine.connect()

        # Выполнение запроса SELECT
        query = table.select()

        # Выполнение запроса и получение результатов
        results = conn.execute(query)

        # Вывод результатов на экран
        print(f"Результаты для таблицы '{table_name}':")
        for row in results:
            print(row)

        # Закрытие соединения
        conn.close()
