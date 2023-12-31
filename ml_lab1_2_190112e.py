# -*- coding: utf-8 -*-
"""ML-lab1-2_190112E.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1c2-ylGMmup5GXesJT9Zb-cmRoHJK0voT

Connecting drive
"""

from google.colab import drive
drive.mount('/content/drive')

"""Importing libraries"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score

"""Importing datasets"""

train = pd.read_csv('/content/drive/MyDrive/lab1/train.csv')
valid = pd.read_csv('/content/drive/MyDrive/lab1/valid.csv')
test = pd.read_csv('/content/drive/MyDrive/lab1/test.csv')

train.head()

"""Preprocessing Data"""

columns_to_check = ['label_2']
train = train.dropna(subset=columns_to_check, how='any')
valid = valid.dropna(subset=columns_to_check, how='any')

datasets = {'train': train, 'valid': valid, 'test': test}

for name, dataset in datasets.items():
    datasets[name] = dataset.fillna(dataset.mean())

valid.head()

"""Separate labels and features"""

def separate_features_labels(data):
    features = data.drop(columns=['label_1', 'label_2', 'label_3', 'label_4'])
    labels = data[['label_2']]
    return features, labels

train_X, train_y = separate_features_labels(train)
valid_X, valid_y = separate_features_labels(valid)
test_X, test_y = separate_features_labels(test)

train_X.head()

"""# 1. Label 2 without feature engineering

Duplicate the labels and features
"""

train_X_copy = train_X.copy()
valid_X_copy = valid_X.copy()
test_X_copy = test_X.copy()

train_y_copy = train_y.copy()
valid_y_copy = valid_y.copy()
test_y_copy = test_y.copy()

"""Standardization"""

scaler = StandardScaler()
train_X_copy = scaler.fit_transform(train_X_copy)
valid_X_copy = scaler.transform(valid_X_copy)
test_X_copy = scaler.transform(test_X_copy)

knn_model = KNeighborsRegressor()
knn_model.fit(train_X_copy, train_y_copy)

datasets = {'train': (train_X_copy, train_y_copy),
            'valid': (valid_X_copy, valid_y_copy)}

for data_name, (X, y) in datasets.items():
    y_pred = knn_model.predict(X)

    mse = mean_squared_error(y, y_pred)
    r2s = r2_score(y, y_pred)

    print(f"Metrics for KNeighborsRegressor on {data_name} data:")
    print(f"Mean Squared Error: {mse:.2f}")
    print(f"R-squared Score: {r2s:.2f}")
    print("\n")

y_pred_before_test = knn_model.predict(test_X_copy)

"""# 1. Label 1 with feature engineering

Identifying highly correlated features
"""

#Calculate the correlation matrix of features

correlation_matrix = train_X.corr()

correlation_threshold = 0.45
# Create a boolean mask indicating highly correlated features
mask = np.abs(correlation_matrix) > correlation_threshold

# Exclude the diagonal and upper triangular part to avoid redundancy
mask = np.triu(mask, k=1)

# Find column names of highly correlated features
highly_correlated = set(correlation_matrix.columns[mask.any(axis=0)])

print(highly_correlated)

"""Remove highly correlated features"""

train_X = train_X.drop(columns=highly_correlated)
valid_X = valid_X.drop(columns=highly_correlated)
test_X = test_X.drop(columns=highly_correlated)

"""Standaridization of features"""

scaler = StandardScaler()

train_features_standardized = scaler.fit_transform(train_X)
valid_features_standardized = scaler.transform(valid_X)
test_features_standardized = scaler.transform(test_X)

"""Extracting features"""

# Set the variance threshold for PCA
variance_threshold = 0.95

# Create a PCA transformer with the specified variance threshold
pca_transformer = PCA(n_components=variance_threshold, svd_solver='full')

# Apply PCA transformation to standardized features
pca_train_features_transformed = pca_transformer.fit_transform(train_features_standardized)
pca_valid_features_transformed = pca_transformer.transform(valid_features_standardized)
pca_test_features_transformed = pca_transformer.transform(test_features_standardized)

"""Model prediction"""

datasets = {'train': (pca_train_features_transformed, train_y),
            'valid': (pca_valid_features_transformed, valid_y)}
model = KNeighborsRegressor()
model.fit(pca_train_features_transformed, train_y)

for data_name, (X, y) in datasets.items():
    y_pred = model.predict(X)

    mse = mean_squared_error(y, y_pred)
    r2s = r2_score(y, y_pred)

    print(f"Metrics for KNeighborsRegressor on {data_name} data:")
    print(f"Mean Squared Error: {mse:.2f}")
    print(f"R-squared Score: {r2s:.2f}")
    print("\n")

y_pred_test = model.predict(pca_test_features_transformed)

"""CSV Generation"""



feature_count = pca_test_features_transformed.shape[1]
feature_row = np.repeat('new_feature_', feature_count)
count_row = list(map(str, np.arange(1, feature_count+1)))
header_row = np.char.add(feature_row, count_row)

df = pd.DataFrame(pca_test_features_transformed, columns  = header_row)

df.insert(loc=0, column='Predicted labels before feature engineering', value=y_pred_before_test)
df.insert(loc=1, column='Predicted labels after feature engineering', value=y_pred_test)
df.insert(loc=2, column='No of new features', value=np.repeat(feature_count, pca_test_features_transformed.shape[0]))

df.to_csv('/content/drive/MyDrive/lab1/output/190112E_label_2.csv', index=False)