import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

def random_forest():
    # Строка подключения к базе данных
    conn_str = 'mssql+pyodbc://ZHAUROVAD\\PEP/ДТП по НСО?driver=ODBC+Driver+17+for+SQL+Server'

    # Создание объекта для подключения к базе данных
    engine = create_engine(conn_str)

    # SQL-запрос
    sql_query = """
        SELECT 
            a.Accident_Type, a.Vehicle_Count, a.Participant_Count, ad.Street_Category, v.Technical_Faults,v.Model,
            p.Alcohol_Intoxication_Degree, p.Participant_Category, p.Traffic_Violations, 
            p.Severity_of_Consequences,i.Road_Condition, i.Weather_Condition,
            p.Driving_Experience, d.Deficiency_Name, f.Factor_Name
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

    # Выполнение запроса и загрузка данных в DataFrame
    data = pd.read_sql(sql_query, engine)

    # Преобразование категориального признака 'Technical_Faults' в числовые метки
    label_encoder = LabelEncoder()
    data['Technical_Faults'] = label_encoder.fit_transform(data['Technical_Faults'])

    # Преобразование категориального признака "Weather_Condition" с помощью One-Hot Encoding
    data = pd.get_dummies(data, columns=['Weather_Condition'])
    print()
    print('ВНИМАНИЕ!!! Происходит проверка пропущенных значений для ЛЕСА')
    missing_values = data.isnull().sum()
    print(missing_values)

    # Вычисление среднего значения опыта вождения
    mean_driving_experience = data['Driving_Experience'].mean()

    # Заполнение пропущенных значений в столбце "Driving_Experience" средним значением
    data['Driving_Experience'] = data['Driving_Experience'].fillna(mean_driving_experience)

    # Удаление строк с пропущенными значениями
    data_cleaned = data.dropna()


    X = data_cleaned[['Alcohol_Intoxication_Degree','Driving_Experience', 'Technical_Faults'] + list(data_cleaned.filter(regex='Weather_Condition_'))]
    y = data_cleaned['Severity_of_Consequences']

    # Разделение данных на обучающий и тестовый наборы
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


    import numpy as np

    # Создание и обучение модели случайного леса
    rf_model = RandomForestClassifier(random_state=42)
    rf_model.fit(X_train, y_train)

    # Прогнозирование на тестовом наборе
    y_pred = rf_model.predict(X_test)



    # Прогнозирование вероятностей классов на тестовом наборе
    y_probs = rf_model.predict_proba(X_test)[:, 1]
    print()
    print('ВНИМАНИЕ!!! Вывод формы массива вероятностей классов')
    print("Форма y_probs:", y_probs.shape)

    import matplotlib.pyplot as plt
    from sklearn.metrics import precision_recall_fscore_support
    print()
    print('ВНИМАНИЕ!!! Вывод метрик')
    precision, recall, f1_score, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted', zero_division=1)
    print("Полнота (Recall):", recall)
    print("Точность (Precision):", precision)
    print("F1-мера:", f1_score)




    from sklearn import tree
    import graphviz

    # Установка переменной среды PATH
    import os
    os.environ["PATH"] += os.pathsep + "C:/Users/Дарья/Desktop/Полетайкин/windows_10_cmake_Release_Graphviz-10.0.1-win64/Graphviz-10.0.1-win64/bin"

    # Построение деревьев в модели
    for i in range(10):  # Первые 10 деревьев
        dot_data = tree.export_graphviz(rf_model.estimators_[i], out_file=None,
                                        feature_names=X_train.columns,
                                        class_names=y_train.unique(),
                                        filled=True)
        graph = graphviz.Source(dot_data)
        graph.render("tree{}".format(i + 1), format='png', engine='dot', directory='.', view=False)
        # Получение значимости признаков из обученной модели случайного леса
        feature_importance = rf_model.feature_importances_

        # Создание DataFrame для наглядного представления значимости признаков
        feature_importance_df = pd.DataFrame({'Feature': X_train.columns, 'Importance': feature_importance})

        # Сортировка признаков по значимости
        feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

        print()
        print('ВНИМАНИЕ!!! Вывод значимости признаков: ')
        print(feature_importance_df)

