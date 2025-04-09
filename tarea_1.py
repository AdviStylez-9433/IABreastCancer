# -*- coding: utf-8 -*-
"""TAREA 1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/19n-IbKroeQ_I3s2o6q-w6HsvZVsd9Apy
    INTEGRANTES: Fabian Ferrada, Matias Urrutia, Fabian Ferrada
"""

# Commented out IPython magic to ensure Python compatibility.
# Importar librerías necesarias
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score, roc_curve
from sklearn.model_selection import GridSearchCV

# Configuración de visualización
plt.style.use('ggplot')
# %matplotlib inline

# Cargar el dataset
data = load_breast_cancer()
X = pd.DataFrame(data.data, columns=data.feature_names)
y = pd.Series(data.target)

# Ver información básica
print("Dimensiones del dataset:", X.shape)
print("\nPrimeras filas de los datos:")
display(X.head())

print("\nDistribución de clases:")
print(y.value_counts())
print("\n0 = Maligno, 1 = Benigno")

# Análisis exploratorio
plt.figure(figsize=(12, 6))
sns.countplot(x=y)
plt.title('Distribución de clases (0: Maligno, 1: Benigno)')
plt.show()

# Visualización de algunas características
plt.figure(figsize=(15, 10))
for i, feature in enumerate(['mean radius', 'mean texture', 'mean perimeter', 'mean area']):
    plt.subplot(2, 2, i+1)
    sns.boxplot(x=y, y=X[feature])
    plt.title(f'Distribución de {feature}')
plt.tight_layout()
plt.show()

# Dividir en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# Escalar las características
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"Tamaño del conjunto de entrenamiento: {X_train.shape}")
print(f"Tamaño del conjunto de prueba: {X_test.shape}")

def evaluate_model(model, X_train, X_test, y_train, y_test):
    # Entrenar modelo
    model.fit(X_train, y_train)

    # Predecir
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    y_test_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None

    # Calcular métricas
    metrics = {
        'Accuracy': accuracy_score(y_test, y_test_pred),
        'Precision': precision_score(y_test, y_test_pred),
        'Recall': recall_score(y_test, y_test_pred),
        'F1-score': f1_score(y_test, y_test_pred),
        'ROC AUC': roc_auc_score(y_test, y_test_prob) if y_test_prob is not None else None
    }

    # Matriz de confusión
    cm = confusion_matrix(y_test, y_test_pred)

    # Curva ROC (si hay probabilidades)
    if y_test_prob is not None:
        fpr, tpr, _ = roc_curve(y_test, y_test_prob)
        plt.figure()
        plt.plot(fpr, tpr, label=f'ROC curve (AUC = {metrics["ROC AUC"]:.2f})')
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic')
        plt.legend()
        plt.show()

    # Mostrar resultados
    display(pd.DataFrame([metrics], index=[model.__class__.__name__]))

    plt.figure()
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Maligno', 'Benigno'],
                yticklabels=['Maligno', 'Benigno'])
    plt.title('Matriz de Confusión')
    plt.ylabel('Verdadero')
    plt.xlabel('Predicho')
    plt.show()

    return metrics

# Crear y evaluar modelo de Regresión Logística
lr = LogisticRegression(max_iter=1000, random_state=42)
print("=== Regresión Logística ===")
lr_metrics = evaluate_model(lr, X_train_scaled, X_test_scaled, y_train, y_test)

# Crear y evaluar modelo de Árbol de Decisión
dt = DecisionTreeClassifier(random_state=42)
print("=== Árbol de Decisión ===")
dt_metrics = evaluate_model(dt, X_train_scaled, X_test_scaled, y_train, y_test)

# Optimización de hiperparámetros para Árbol de Decisión
param_grid_dt = {
    'max_depth': [3, 5, 7, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

grid_dt = GridSearchCV(DecisionTreeClassifier(random_state=42), param_grid_dt, cv=5, scoring='f1')
grid_dt.fit(X_train_scaled, y_train)

print("Mejores parámetros para Árbol de Decisión:", grid_dt.best_params_)
dt_optimized = grid_dt.best_estimator_
print("\n=== Árbol de Decisión Optimizado ===")
dt_opt_metrics = evaluate_model(dt_optimized, X_train_scaled, X_test_scaled, y_train, y_test)

# Crear y evaluar modelo de Random Forest
rf = RandomForestClassifier(random_state=42)
print("=== Random Forest ===")
rf_metrics = evaluate_model(rf, X_train_scaled, X_test_scaled, y_train, y_test)

# Optimización de hiperparámetros para Random Forest
param_grid_rf = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 5, 10],
    'min_samples_split': [2, 5]
}

grid_rf = GridSearchCV(RandomForestClassifier(random_state=42), param_grid_rf, cv=5, scoring='f1')
grid_rf.fit(X_train_scaled, y_train)

print("Mejores parámetros para Random Forest:", grid_rf.best_params_)
rf_optimized = grid_rf.best_estimator_
print("\n=== Random Forest Optimizado ===")
rf_opt_metrics = evaluate_model(rf_optimized, X_train_scaled, X_test_scaled, y_train, y_test)

# Recolectar métricas de todos los modelos
metrics_df = pd.DataFrame([
    lr_metrics,
    dt_metrics,
    dt_opt_metrics,
    rf_metrics,
    rf_opt_metrics
], index=[
    'Regresión Logística',
    'Árbol de Decisión',
    'Árbol de Decisión (Optimizado)',
    'Random Forest',
    'Random Forest (Optimizado)'
])

# Mostrar comparación
print("=== Comparación de Modelos ===")
display(metrics_df)

# Visualización comparativa
plt.figure(figsize=(12, 6))
metrics_df[['Accuracy', 'Precision', 'Recall', 'F1-score']].plot(kind='bar')
plt.title('Comparación de Métricas entre Modelos')
plt.ylabel('Puntaje')
plt.xticks(rotation=45)
plt.legend(loc='lower right')
plt.tight_layout()
plt.show()

# Análisis de características importantes (para modelos que lo permiten)
if hasattr(rf_optimized, 'feature_importances_'):
    feature_imp = pd.DataFrame({
        'Feature': X.columns,
        'Importance': rf_optimized.feature_importances_
    }).sort_values('Importance', ascending=False)

    plt.figure(figsize=(12, 8))
    sns.barplot(x='Importance', y='Feature', data=feature_imp.head(10))
    plt.title('Top 10 Características más Importantes (Random Forest)')
    plt.show()

# Identificar el mejor modelo basado en F1-score (equilibrio entre precisión y recall)
best_model_name = metrics_df['F1-score'].idxmax()
best_model = {
    'Regresión Logística': lr,
    'Árbol de Decisión': dt,
    'Árbol de Decisión (Optimizado)': dt_optimized,
    'Random Forest': rf,
    'Random Forest (Optimizado)': rf_optimized
}[best_model_name]

print(f"\nEl mejor modelo es: {best_model_name}")
print(f"F1-score: {metrics_df.loc[best_model_name, 'F1-score']:.4f}")
print(f"Accuracy: {metrics_df.loc[best_model_name, 'Accuracy']:.4f}")

# Guardar el mejor modelo (opcional)
import joblib
joblib.dump(best_model, 'mejor_modelo.pkl')
