import pandas as pd
from sqlalchemy import create_engine
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
import matplotlib.pyplot as plt

def klasterizacia():
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
        print('ВНИМАНИЕ!!! Вывод первых строк DF для проверки: ')
        print(df.head())
    except Exception as e:
        print("Ошибка при выполнении запроса:", e)
    finally:
        # Закрытие соединения с базой данных
        engine.dispose()

    # Отбираем только необходимые признаки для кластеризации
    X = df[['Gender', 'Model']]

    # Обработка пропущенных значений в столбце "Модель"
    imputer = SimpleImputer(strategy='most_frequent')
    X_imputed = imputer.fit_transform(X)

    # Преобразование категориальной переменной "Gender" в числовой формат с помощью LabelEncoder
    label_encoder = LabelEncoder()
    X_imputed[:, 0] = label_encoder.fit_transform(X_imputed[:, 0])

    # Преобразование категориальной переменной "Model" в числовой формат с помощью LabelEncoder
    X_imputed[:, 1] = label_encoder.fit_transform(X_imputed[:, 1])

    # Обработка пропущенных значений в других столбцах
    imputer = SimpleImputer(strategy='mean')
    X_imputed = imputer.fit_transform(X_imputed)

    # Стандартизация данных
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    # Выполнение кластеризации методом K-means
    kmeans = KMeans(n_clusters=4, random_state=42)
    kmeans.fit(X_scaled)

    # Получение меток кластеров для каждого наблюдения
    cluster_labels = kmeans.labels_

    # Вычисление индексов силуэта и Дэвиса-Болдуина
    silhouette = silhouette_score(X_scaled, cluster_labels)
    davies_bouldin = davies_bouldin_score(X_scaled, cluster_labels)

    print("ВНИМАНИЕ!!! Вывод метрик для КЛАСТЕРИЗАЦИИ")
    print("Индекс силуэта:", silhouette)
    print("Критерий Дэвиса-Болдуина:", davies_bouldin)

    print("ВНИМАНИЕ!!! Вывод статистики по каждому кластеру")
    df['Cluster'] = cluster_labels
    cluster_stats = df.groupby('Cluster')[['Gender', 'Model']].describe()
    print(cluster_stats)

    print("ВНИМАНИЕ!!! Вывод средних значений признаков для каждого кластера")
    means = df.groupby('Cluster')['Gender'].value_counts().unstack(fill_value=0)
    print("\nКоличество мужчин и женщин в каждом кластере:")
    print(means)

    # Разделяем данные по кластерам
    cluster_0 = df[df['Cluster'] == 1]
    cluster_1 = df[df['Cluster'] == 2]
    cluster_2 = df[df['Cluster'] == 3]
    cluster_3 = df[df['Cluster'] == 4]

    import seaborn as sns

    # Визуализация результатов кластеризации с использованием Seaborn
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=X_scaled[:, 0], y=X_scaled[:, 1], hue=cluster_labels, palette='viridis', alpha=0.7, legend='full')
    plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], marker='x', c='red', s=100, label='Центроиды кластеров')
    plt.title('Результаты кластеризации')
    plt.xlabel('Пол (стандартизированный)')
    plt.ylabel('Модель ТС (стандартизированная)')
    plt.legend(title='Кластеры')
    plt.grid(True)
    plt.show()




    # Получаем исходные категориальные данные для модели
    models_original = df[df['Cluster'] == 0]['Vehicle_Type']

    print()
    print("ВНИМАНИЕ!!! Вывод распределения типа ТС")
    model_distribution = models_original.value_counts()
    print("Распределение типов ТС в кластере 'Прочие марки и модели ТС':")
    print(model_distribution)

    # Создание столбца с номером кластера
    df['Cluster'] = cluster_labels

    # Отображение данных для ТС в кластере 'Прочие марки и модели ТС'
    other_models = df[df['Model'] == 'Прочие марки ТС Прочие марки и модели ТС']

    print()
    print("ВНИМАНИЕ!!! Вывод данных о ТС в кластере 'Прочие марки и модели ТС': ")
    print(other_models)
