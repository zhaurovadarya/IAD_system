import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score

def SVM_1():
    # Строка подключения к базе данных
    conn_str = 'mssql+pyodbc://ZHAUROVAD\\PEP/ДТП по НСО?driver=ODBC+Driver+17+for+SQL+Server'

    # Создание объекта для подключения к базе данных
    engine = create_engine(conn_str)

    # SQL-запрос
    sql_query = """
        SELECT 
            a.Accident_Type, a.Vehicle_Count, a.Participant_Count, ad.Street_Category, v.Drive_Type, v.Technical_Faults,
            p.Alcohol_Intoxication_Degree, Participant_Category, p.Traffic_Violations, p.Severity_of_Consequences,
            i.Road_Condition, p.Driving_Experience, d.Deficiency_Name, f.Factor_Name
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

    # Преобразование категориальных признаков с помощью One-Hot Encoding
    data = pd.get_dummies(data, columns=['Accident_Type', 'Street_Category', 'Drive_Type', 'Technical_Faults',
                                         'Participant_Category', 'Traffic_Violations', 'Severity_of_Consequences',
                                         'Road_Condition', 'Deficiency_Name', 'Factor_Name'])

    # Удаление строк с отсутствующими значениями
    data.dropna(axis=0, inplace=True)

    # Фильтрация данных для учета только водителей
    driver_data = data[data['Participant_Category_Водитель'] == 1]

    # Создание копии среза driver_data
    driver_data = driver_data.copy()

    # Установка значения для столбца Drunk_Driver
    driver_data['Drunk_Driver'] = (driver_data['Alcohol_Intoxication_Degree'] > 0).astype(int)

    # Отбор признаков и целевой переменной
    features = driver_data[['Alcohol_Intoxication_Degree', 'Driving_Experience']]
    target = driver_data['Drunk_Driver']

    # Отбор категориальных признаков для One-Hot Encoding
    categorical_columns = [col for col in driver_data.columns if col.startswith(('Drive_Type_', 'Technical_Faults_','Road_Condition'))]
    categorical_features = driver_data[categorical_columns]

    # Применение One-Hot Encoding к категориальным признакам
    categorical_features_encoded = pd.get_dummies(categorical_features)

    # Объединение закодированных категориальных признаков с остальными признаками
    features = pd.concat([features, categorical_features_encoded], axis=1)

    # Разделение данных на обучающий и тестовый наборы
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

    # Масштабирование признаков
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Создание и обучение модели SVM
    svm_model = SVC(kernel='linear', random_state=42)
    svm_model.fit(X_train_scaled, y_train)

    # Предсказание на тестовом наборе
    y_pred = svm_model.predict(X_test_scaled)

    # Оценка качества модели
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    print("ВНИМАНИЕ!!! Вывод метрик для SVM: ")
    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1 Score:", f1)

    # Получение вероятностей принадлежности к положительному классу
    y_pred_prob = svm_model.decision_function(X_test_scaled)

    # Рассчитываем значения ROC кривой
    fpr, tpr, thresholds = roc_curve(y_test, y_pred_prob)

    # Рассчитываем площадь под ROC кривой (ROC AUC)
    roc_auc = roc_auc_score(y_test, y_pred_prob)

    # Построение ROC кривой
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='blue', lw=2, label=f'ROC-кривая (площадь = {roc_auc:.2f})')
    plt.scatter(fpr, tpr, color='red', marker='o')  # Добавляем точки
    plt.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--', label='Случайное угадывание')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Ложно положительный уровень (FPR)')
    plt.ylabel('Истинно положительный уровень (TPR)')
    plt.title('Кривая ROC')
    plt.legend(loc='lower right')
    plt.grid(True)
    plt.show()

