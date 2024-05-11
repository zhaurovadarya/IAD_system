import pandas as pd
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer

def regression_analysis():
    # Строка подключения к базе данных
    conn_str = 'mssql+pyodbc://ZHAUROVAD\\PEP/ДТП по НСО?driver=ODBC+Driver+17+for+SQL+Server'

    # Запрос SQL для выборки данных
    query = """
        SELECT 
            a.Fatality_Count + a.Injury_Count as Total_Casualties,
            i.Weather_Condition,
            i.Road_Condition,
            i.Lighting_Condition,
            ad.Street_Category,
            v.Vehicle_Type,
            v.Model,
            v.Technical_Faults,
            p.Alcohol_Intoxication_Degree,
            p.Driving_Experience,
            d.Deficiency_Name,
            f.Factor_Name

        FROM 
            Accident a
        JOIN 
            Accident_Influence i ON a.Influence_ID = i.Influence_ID
        JOIN 
            Addres ad ON a.Address_ID = ad.Address_ID
        JOIN 
            Vehicles v ON a.Accident_ID = v.Accident_ID
        JOIN 
            Participants p ON a.Accident_ID = p.Accident_ID
        JOIN 
            Participant_Offenses po ON p.Participant_ID = po.Participant_ID
        JOIN 
            Associated_Offenses ao ON po.Violation_ID = ao.Violation_ID
        JOIN 
            Influence_Deficiency influence_deficiency ON i.Influence_ID = influence_deficiency.Influence_ID
        JOIN 
            Deficiencies d ON influence_deficiency.Deficiency_ID = d.Deficiency_ID
        JOIN 
            Influence_Factor influence_factor ON i.Influence_ID = influence_factor.Influence_ID
        JOIN 
            Factors f ON influence_factor.Factor_ID = f.Factor_ID;
    """

    # Создание подключения к базе данных
    engine = create_engine(conn_str)

    try:
        # Выполнение запроса и чтение данных в DataFrame
        df = pd.read_sql(query, engine)
        print('ВНИМАНИЕ!!! Вывод первых строк DF для проверки: ')
        print(df.head())
    except Exception as e:
        print("Ошибка при выполнении запроса:", e)
    finally:
        # Закрытие соединения с базой данных
        engine.dispose()

    # Отделяем целевую переменную (Total_Casualties) от признаков
    X = df.drop(columns=['Total_Casualties'])
    y = df['Total_Casualties']

    # Преобразуем все признаки в числовые
    X = pd.get_dummies(X)

    # Разделяем данные на обучающий и тестовый наборы
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Обработка отсутствующих значений
    imputer = SimpleImputer(strategy='mean')
    X_train_imputed = imputer.fit_transform(X_train)
    X_test_imputed = imputer.transform(X_test)

    # Создаем и обучаем модель линейной регрессии
    model = LinearRegression()
    model.fit(X_train_imputed, y_train)

    # Оцениваем качество модели на тестовом наборе данных
    score = model.score(X_test_imputed, y_test)
    print('ВНИМАНИЕ!!! Вывод метрик для РЕГРЕССИИ:')
    print("R^2 на тестовом наборе данных:", score)

    from sklearn.metrics import mean_absolute_error, mean_squared_error

    # Предсказываем значения на тестовом наборе данных
    y_pred = model.predict(X_test_imputed)

    # Вычисляем среднюю абсолютную ошибку (MAE)
    mae = mean_absolute_error(y_test, y_pred)
    print("Средняя абсолютная ошибка на тестовом наборе данных:", mae)

    # Вычисляем среднеквадратическую ошибку (MSE)
    mse = mean_squared_error(y_test, y_pred)
    print("Среднеквадратическая ошибка на тестовом наборе данных:", mse)



    import matplotlib.pyplot as plt

    # Создаем график
    plt.figure(figsize=(10, 6))

    # Добавляем точки для фактических значений
    plt.scatter(y_test, y_pred, color='blue', alpha=0.5, label='Фактические значения (синие точки)')
    plt.plot(y_test, y_test, color='red', label='Идеальная модель (красная линия)')

    # Настройка графика
    plt.title('Сравнение фактических значений и прогнозов модели', fontsize=16, fontweight='bold', color='black')
    plt.xlabel('Фактические значения', color='black')
    plt.ylabel('Прогнозы модели', color='black')
    plt.legend()

    # Устанавливаем границы для области координатной плоскости
    plt.xlim(0, max(max(y_test), max(y_pred)) + 1)
    plt.ylim(0, max(max(y_test), max(y_pred)) + 1)

    # Добавляем сетку
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray')

    # Устанавливаем лиловый цвет для фона графика
    plt.gca().set_facecolor('lavender')

    # Отображаем график
    plt.show()

