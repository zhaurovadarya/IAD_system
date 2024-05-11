import pandas as pd
from sqlalchemy import create_engine
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def method_loctya():
    # Строка подключения к базе данных
    conn_str = 'mssql+pyodbc://ZHAUROVAD\\PEP/ДТП по НСО?driver=ODBC+Driver+17+for+SQL+Server'

    # Запрос SQL для выборки данных
    query = """
        SELECT   
            p.Alcohol_Intoxication_Degree,
            p.Gender,
            p.Driving_Experience,
            v.Vehicle_Type,
            v.Model,
            v.Technical_Faults,
            v.Year_of_Manufacture,
            v.Ownership_Form
        FROM 
            Participants p
        JOIN 
            Accident acc ON p.Accident_ID = acc.Accident_ID
        JOIN 
            Vehicles v ON acc.Accident_ID = v.Accident_ID;
    """

    # Создание подключения к базе данных
    engine = create_engine(conn_str)

    try:
        # Выполнение запроса и чтение данных в DataFrame
        df = pd.read_sql(query, engine)
    except Exception as e:
        print("Ошибка при выполнении запроса:", e)
    finally:
        # Закрытие соединения с базой данных
        engine.dispose()

    # Преобразование категориальной переменной "Model" в числовой формат с помощью LabelEncoder
    label_encoder = LabelEncoder()
    df['Model'] = label_encoder.fit_transform(df['Model'])

    label_encoder = LabelEncoder()
    df['Gender'] = label_encoder.fit_transform(df['Gender'])

    # Отбираем только необходимые признаки для кластеризации
    X = df[['Gender', 'Model']]

    # Обработка пропущенных значений
    imputer = SimpleImputer(strategy='mean')
    X_imputed = imputer.fit_transform(X)

    # Стандартизация данных
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    # Определяем диапазон количества кластеров для проверки
    clusters_range = range(1, 11)
    inertia = []

    # Обучаем модели K-means для разного количества кластеров и оцениваем их инерцию
    for n_clusters in clusters_range:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(X_scaled)
        inertia.append(kmeans.inertia_)

    # Строим график метода локтя
    plt.figure(figsize=(10, 6))
    plt.plot(clusters_range, inertia, marker='o', linestyle='-')
    plt.title('Метод локтя для определения оптимального количества кластеров')
    plt.xlabel('Количество кластеров')
    plt.ylabel('Сумма квадратов внутриклассовых расстояний')
    plt.xticks(clusters_range)
    plt.grid(True)
    plt.show()
