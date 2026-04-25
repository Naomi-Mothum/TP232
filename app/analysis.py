import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def run_full_analysis(students_df):
    if len(students_df) < 5:
        return {"error": "Pas assez de données pour l'analyse (minimum 5 enregistrements requis)"}

    # Prepare features
    # Convert categorical data if any (gender)
    df = students_df.copy()
    df['gender_numeric'] = df['gender'].map({'M': 0, 'F': 1})
    
    features = ['age', 'gender_numeric', 'study_time', 'absences', 'prev_grade']
    X = df[features]
    y = df['final_grade']

    # 1. Simple Linear Regression (Study Time -> Final Grade)
    X_simple = df[['study_time']].values
    simple_reg = LinearRegression().fit(X_simple, y)
    
    # Generate points for the regression line
    line_x = np.linspace(X_simple.min(), X_simple.max(), 100).reshape(-1, 1)
    line_y = simple_reg.predict(line_x)
    
    simple_reg_data = {
        "slope": float(simple_reg.coef_[0]),
        "intercept": float(simple_reg.intercept_),
        "r2": float(simple_reg.score(X_simple, y)),
        "line": [{"x": float(x), "y": float(y_val)} for x, y_val in zip(line_x, line_y)]
    }

    # 2. Multiple Linear Regression
    multi_reg = LinearRegression().fit(X, y)
    multi_reg_data = {
        "coefficients": dict(zip(features, multi_reg.coef_.tolist())),
        "intercept": float(multi_reg.intercept_),
        "r2": float(multi_reg.score(X, y))
    }

    # 3. PCA (Dimensionality Reduction to 2D)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(X_scaled)
    
    pca_data = [
        {"x": float(row[0]), "y": float(row[1]), "id": int(df.iloc[i]['id'])} 
        for i, row in enumerate(pca_result)
    ]

    # 4. K-Means Clustering (Student Profiling)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
    clusters = kmeans.fit_predict(X_scaled)
    cluster_data = [
        {"id": int(df.iloc[i]['id']), "cluster": int(clusters[i])}
        for i in range(len(clusters))
    ]

    # 5. Logistic Regression (Pass/Fail Prediction)
    # Define pass as final_grade >= 10
    y_binary = (y >= 10).astype(int)
    log_reg = LogisticRegression().fit(X, y_binary)
    
    pass_fail_data = {
        "accuracy": float(log_reg.score(X, y_binary)),
        "coefficients": dict(zip(features, log_reg.coef_[0].tolist())),
        "intercept": float(log_reg.intercept_[0])
    }

    return {
        "simple_regression": simple_reg_data,
        "multiple_regression": multi_reg_data,
        "pca_data": pca_data,
        "clusters": cluster_data,
        "pass_fail_prediction": pass_fail_data
    }
