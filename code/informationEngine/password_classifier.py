import pickle
from imblearn.over_sampling import SMOTE
from collections import Counter
import re
from matplotlib import pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline

with open("train/passwords", "r") as file:
    passwords = file.read().splitlines()
with open("train/non_passwords", "r") as file:
    non_passwords = file.read().splitlines()

password_lengths = [len(password) for password in passwords]
non_password_lengths = [len(non_password) for non_password in non_passwords]

lengths_np = np.array(password_lengths+non_password_lengths)


def extract_features(text):
    features = {}
    features['length'] = len(text)
    features['upper_count'] = sum(1 for char in text if char.isupper())
    features['lower_count'] = sum(1 for char in text if char.islower())
    features['digit_count'] = sum(1 for char in text if char.isdigit())
    features['special_count'] = len(re.findall(r'[!@#$%^&*()]', text))
    return features


vectorizer = TfidfVectorizer()
X = np.array([list(extract_features(text).values())
             for text in passwords + non_passwords])
y = np.array([1] * len(passwords) + [0] * len(non_passwords))

# 处理数据不平衡问题（过采样）
smote = SMOTE(sampling_strategy='minority')
X_resampled, y_resampled = smote.fit_resample(X, y)

# 数据集拆分
X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled, test_size=0.1, random_state=42)

# 支持向量机分类器
svm_classifier = SVC(kernel='poly', C=10, probability=True)
svm_classifier.fit(X_train, y_train)

# 模型评估
y_pred = svm_classifier.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
# print(f"Accuracy: {accuracy}")


# # 定义键盘布局
# keyboard_layout = {
#     'qwerty': 'qwertyuiopasdfghjklzxcvbnm',
#     'dvorak': 'pyfgcrlaoeuidhtns;qjkxbmwvz',
#     # 其他键盘布局
# }

# # 创建函数计算键盘布局距离
# def calculate_keyboard_distance(text, layout='qwerty'):
#     layout = keyboard_layout.get(layout, 'qwerty')  # 默认为qwerty键盘布局
#     distance = 0
#     for i in range(len(text) - 1):
#         char1, char2 = text[i], text[i+1]
#         if char1 in layout and char2 in layout:
#             index1, index2 = layout.index(char1), layout.index(char2)
#             distance += abs(index1 - index2)
#     return distance

# # 创建函数计算字符出现频率
# def calculate_character_frequency(text):
#     char_count = Counter(text)
#     total_characters = len(text)
#     char_frequency = {char: count / total_characters for char, count in char_count.items()}
#     return char_frequency

# # 更新特征提取函数
# def extract_features(text, layout='qwerty'):
#     features = {
#         'length': len(text),
#         'uppercase_count': 0,
#         'lowercase_count': 0,
#         'digit_count': 0,
#         'special_count': 0,
#         'keyboard_distance': 0,  # 初始化键盘布局距离
#     }

#     char_frequency = calculate_character_frequency(text)
#     for char in text:
#         if char.isupper():
#             features['uppercase_count'] += 1
#         elif char.islower():
#             features['lowercase_count'] += 1
#         elif char.isdigit():
#             features['digit_count'] += 1
#         elif re.match(r'[!@#$%^&*()]', char):
#             features['special_count'] += 1

#     # 添加字符出现频率特征
#     for char, frequency in char_frequency.items():
#         features[f'{char}_frequency'] = frequency

#     # 计算键盘布局距离
#     features['keyboard_distance'] = calculate_keyboard_distance(text, layout)

#     return features

# # 使用特定键盘布局（例如，'dvorak'）来提取特征
# text = "your_password_here"
# layout = 'dvorak'
# features = extract_features(text, layout)
# # print(features)

# vectorizer = TfidfVectorizer()
# X = np.array([list(extract_features(text).values()) for text in passwords + non_passwords])
# y = np.array([1] * len(passwords) + [0] * len(non_passwords))
# from imblearn.over_sampling import SMOTE

# # 处理数据不平衡问题（过采样）
# smote = SMOTE(sampling_strategy='minority')
# X_resampled, y_resampled = smote.fit_resample(X, y)

# # 数据集拆分
# X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.1, random_state=42)

# # 支持向量机分类器
# svm_classifier = SVC(kernel='poly',C=10, probability=True)
# svm_classifier.fit(X_train, y_train)

# # 模型评估
# y_pred = svm_classifier.predict(X_test)
# accuracy = accuracy_score(y_test, y_pred)
# # print(f"Accuracy: {accuracy}")


# 6. 预测新字符串

# predictions = svm_classifier.predict(X_new)

# for i, input_str in enumerate(new_input):
#     if predictions[i] == 1:
#         # print(f"'{input_str}' is a password.")
#     else:
#         # print(f"'{input_str}' is not a password.")


# 是否可视化
if (False):
    # 使用PCA降低维度到2D
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_train)

    # 创建一个网格来绘制决策边界
    h = .02  # 步长
    x_min, x_max = X_pca[:, 0].min() - 1, X_pca[:, 0].max() + 1
    y_min, y_max = X_pca[:, 1].min() - 1, X_pca[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))

    # 使用SVC进行预测
    Z = svm_classifier.predict(
        pca.inverse_transform(np.c_[xx.ravel(), yy.ravel()]))
    Z = Z.reshape(xx.shape)

    # 可视化决策边界
    plt.contourf(xx, yy, Z, cmap=plt.cm.coolwarm, alpha=0.8)
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y_train,
                cmap=plt.cm.coolwarm, marker='o')
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.title('SVC Decision Boundary')
    plt.show()


# 导出模型
with open("svm_classifier.pkl", "wb") as file:
    pickle.dump(svm_classifier, file)
