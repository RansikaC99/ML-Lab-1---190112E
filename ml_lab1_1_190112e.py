# -*- coding: utf-8 -*-
"""ML-lab1-1_190112E.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HMBQkPyYIFM1Zbw_NP0-KRoOZI_igPMv

Importing libraries
"""

from google.colab import drive
drive.mount('/content/drive')

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
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, KFold  


"""Importing datasets"""

train = pd.read_csv('/content/drive/MyDrive/lab1/train.csv')
valid = pd.read_csv('/content/drive/MyDrive/lab1/valid.csv')
test = pd.read_csv('/content/drive/MyDrive/lab1/test.csv')

train.head()

"""Preprocessing Data

Remove null rows
"""

columns_to_check = ['label_1']
train = train.dropna(subset=columns_to_check, how='any')

datasets = {'train': train, 'valid': valid, 'test': test}

for name, dataset in datasets.items():
    datasets[name] = dataset.fillna(dataset.mean())

train.head()

def separate_features_labels(data):
    features = data.drop(columns=['label_1', 'label_2', 'label_3', 'label_4'])
    labels = data[['label_1']]
    return features, labels

train_X, train_y = separate_features_labels(train)
valid_X, valid_y = separate_features_labels(valid)
test_X, test_y = separate_features_labels(test)

train_X.head()

"""# 1. Label 1 without feature engineering

Duplicate the labels and features
"""

train_X_copy = train_X.copy()
valid_X_copy = valid_X.copy()
test_X_copy = test_X.copy()

train_y_copy = train_y.copy()
valid_y_copy = valid_y.copy()
test_y_copy = test_y.copy()

scaler = StandardScaler()
train_X_copy = scaler.fit_transform(train_X_copy)
valid_X_copy = scaler.transform(valid_X_copy)
test_X_copy = scaler.transform(test_X_copy)

svc_model = SVC()
svc_model.fit(train_X_copy, train_y_copy)

train_X.shape

datasets = {'train': (train_X_copy, train_y_copy), 'valid': (valid_X_copy, valid_y_copy)}

def evaluate_and_print_metrics(y_true, y_pred, prefix):
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='weighted', zero_division=1)
    recall = recall_score(y_true, y_pred, average='weighted')

    print(f"Metrics for SVC on {prefix} dataset:")
    print(f"Accuracy: {accuracy:.2f}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print("\n")

for data_name, (X, y) in datasets.items():
    y_pred = svc_model.predict(X)
    evaluate_and_print_metrics(y, y_pred, data_name)

y_pred_before_test = svc_model.predict(test_X_copy)

"""# 1. Label 1 with feature engineering

Identifying highly correlated features
"""

#Calculate the correlation matrix of features

correlation_matrix = train_X.corr()

correlation_threshold = 0.5
# Create a boolean mask indicating highly correlated features
mask = np.abs(correlation_matrix) > correlation_threshold

# Exclude the diagonal and upper triangular part to avoid redundancy
mask = np.triu(mask, k=1)

# Find column names of highly correlated features
highly_correlated = set(correlation_matrix.columns[mask.any(axis=0)])

print(highly_correlated)

"""Remove high correlated features"""

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

"""Final evaluation"""

# SVM model
svm_model = SVC()

# Train the SVM model on the training data
svm_model.fit(pca_train_features_transformed, train_y)

# Predict on the train data
y_pred_train = svm_model.predict(pca_train_features_transformed)

# Calculate metrics for classification evaluation on train data
accuracy_train = accuracy_score(train_y, y_pred_train)
precision_train = precision_score(train_y, y_pred_train, average='weighted', zero_division=1)
recall_train = recall_score(train_y, y_pred_train, average='weighted')

print("Metrics for SVM on train data:")
print(f"Accuracy: {accuracy_train:.2f}")
print(f"Precision: {precision_train:.2f}")
print(f"Recall: {recall_train:.2f}")
print("\n")

# Predict on the validation data
y_pred_valid = svm_model.predict(pca_valid_features_transformed)

# Calculate metrics for classification evaluation on validation data
accuracy_valid = accuracy_score(valid_y, y_pred_valid)
precision_valid = precision_score(valid_y, y_pred_valid, average='weighted', zero_division=1)
recall_valid = recall_score(valid_y, y_pred_valid, average='weighted')

print("Metrics for SVM on validation data:")
print(f"Accuracy: {accuracy_valid:.2f}")
print(f"Precision: {precision_valid:.2f}")
print(f"Recall: {recall_valid:.2f}")
print("\n")

# Predict on the test data
y_pred_test = svm_model.predict(pca_test_features_transformed)

#number of folds for cross-validation
num_folds = 5

# Create a KFold object
kf = KFold(n_splits=num_folds, shuffle=True, random_state=42)

# Create empty lists to store the evaluation metrics for each fold
accuracy_scores = []
precision_scores = []
recall_scores = []

# Perform k-fold cross-validation
for train_index, valid_index in kf.split(train_X, train_y):
    train_fold_X, valid_fold_X = train_X.iloc[train_index], train_X.iloc[valid_index]
    train_fold_y, valid_fold_y = train_y.iloc[train_index], train_y.iloc[valid_index]

    # Rest of your code for preprocessing and modeling within each fold
    # ...

    # At the end of each fold, evaluate the model and store the metrics
    y_pred_fold = svc_model.predict(valid_fold_X)
    accuracy_fold = accuracy_score(valid_fold_y, y_pred_fold)
    precision_fold = precision_score(valid_fold_y, y_pred_fold, average='weighted', zero_division=1)
    recall_fold = recall_score(valid_fold_y, y_pred_fold, average='weighted')

    accuracy_scores.append(accuracy_fold)
    precision_scores.append(precision_fold)
    recall_scores.append(recall_fold)

# Calculate and print the average metrics over all folds
average_accuracy = np.mean(accuracy_scores)
average_precision = np.mean(precision_scores)
average_recall = np.mean(recall_scores)

print(f"Average Accuracy: {average_accuracy:.2f}")
print(f"Average Precision: {average_precision:.2f}")
print(f"Average Recall: {average_recall:.2f}")

"""CSV Generation"""

feature_count = pca_test_features_transformed.shape[1]
feature_row = np.repeat('new_feature_', feature_count)
count_row = list(map(str, np.arange(1, feature_count+1)))
header_row = np.char.add(feature_row, count_row)

df = pd.DataFrame(pca_test_features_transformed, columns  = header_row)

df.insert(loc=0, column='Predicted labels before feature engineering', value=y_pred_before_test)
df.insert(loc=1, column='Predicted labels after feature engineering', value=y_pred_test)
df.insert(loc=2, column='No of new features', value=np.repeat(feature_count, pca_test_features_transformed.shape[0]))

df.to_csv('/content/drive/MyDrive/lab1/output/190112E_label_1.csv', index=False)