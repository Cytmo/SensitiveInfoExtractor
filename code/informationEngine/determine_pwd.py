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

with open("passwords", "r") as file:
    passwords = file.read().splitlines()
with open("non_passwords", "r") as file:
    non_passwords = file.read().splitlines()

password_lengths = [len(password) for password in passwords]
non_password_lengths = [len(non_password) for non_password in non_passwords]

lengths_np = np.array(password_lengths+non_password_lengths)
import re
# 特征提取
# 2. 特征提取
# 添加更多特征
def extract_features(text):
    features = {}
    features['length'] = len(text)
    features['upper_count'] = sum(1 for char in text if char.isupper())
    features['lower_count'] = sum(1 for char in text if char.islower())
    features['digit_count'] = sum(1 for char in text if char.isdigit())
    features['special_count'] = len(re.findall(r'[!@#$%^&*()]', text))
    return features

vectorizer = TfidfVectorizer()
X = np.array([list(extract_features(text).values()) for text in passwords + non_passwords])
y = np.array([1] * len(passwords) + [0] * len(non_passwords))
from imblearn.over_sampling import SMOTE

# 处理数据不平衡问题（过采样）
smote = SMOTE(sampling_strategy='minority')
X_resampled, y_resampled = smote.fit_resample(X, y)

# 数据集拆分
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.1, random_state=42)

# 支持向量机分类器
svm_classifier = SVC(kernel='poly',C=10, probability=True)
svm_classifier.fit(X_train, y_train)

# 模型评估
y_pred = svm_classifier.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")


passwords1 = [
    "Pass@word!!!", "Huawei@123456", "2!Um37hvjk", "lab@998877",
    "kllsjkd!@777", "hhhlab@2022", "eNnBjPvDKQkXFvB0KMm7dyKSv7YEdt2i",
    "mHCkEvo0MounX2nNdAYy5hKImVU8ssnN", "w7iWjVrO2sr6kJbM8R718zzLCi3P3pRt",
    "mHCkEvo0MounX2nNdAYy5hKImVU8ssnN", "CeVgn705JcPDKseYzfLeVcWwqyFIzoHv",
    "7GMXOgUE2PNzyUkR3zWuxsF8b0YUUZlS", "CeVgn705JcPDKseYzfLeVcWwqyFIzoHv",
    "oVhmUA0VC36zkv1EceV4g6BFsc0ldprw", "QM1B7rBAFpXBM0GKZHmw4JinWvloTHWh",
    "QM1B7rBAFpXBM0GKZHmw4JinWvloTHWh", "aOuoMnJcWLDIH2zXHMJVh31eBF50MOgP",
    "q3dI62egikbHAAQ3yWAjkbzqilFPOy0T", "Zhyl01VUvSXXrOvIlkCUvC7dr4zr5fuZ",
    "DaLVPy081rEEXxQ4PuHevnqYcOZMrmmR", "neCTfWo5wH4Dqm3sGbvxt6I6sCvRseAH",
    "f1kfr6vJ8O4aBoSSvha16SDqCUXa78i3", "DNfUeEi65Wt7uEgAnNcDES9UKkayTZGI",
    "MnJbhF2i5DadB0MaB0IqaIf9D4XtZQ15", "OCpj00kDh6sZONWzBcNBr1fDa95zBjXe",
    "Zq8yO5u9KDxowGe3cygppfj2pkyT9YMn", "V8smxUNdyb66XalR7pHbf71QIlKsbu1J",
    "123456999", "admin@1234567890",  "admin@1234567890",
    "000000", "123456", "5C5WQI9FSzHcT4Mz", "alaFmj7SEnsiR2zW",
    "YPXOEqMIZnefe5Um", "HAkpWz0yXh9fbbCN", "xvqxPG615mh2NE6D",
    "12vQunVGdQDgUYUa", "A4SCWcwshvBDyOCw", "9odVQJM2WIQF6uBB",
    "M52QOtugwsQEjEC5", "CFRN4yltcKzbh9DF", "b506S0qUqFZMEUmY",
    "KxvFsofPLMCWIsrV", "c6mdIBIR8MDOjLDf", "GwtX2bm48sauzEK0"
]

# 非密码示例
non_passwords1 = [
    "root", "kppublic@163.com", "xxlab", "sysadmin",
    "zhangsan@xxx.edu.cn", "l2tp", "admin",
    "bj-xxlab", "vpn","dsadsadsa1313213"
]

regular_words = "The DASS is a 42-item self-report instrument designed to measure the three related negative emotional states of depression, anxiety and tension/stress. The DASS questionnaire is in the public domain, and may be downloaded from this website.".split(" ")
regular_words = [ "admin",
    "user",
    "guest",
    "root",
    "test",
    "webmaster",
    "manager",
    "support",
    "system",
    "developer",
    "anonymous",
    "default",
    "ftp",
    "administrator",
    "info",
    "demo",
    "login",
    "oracle",
    "mysql",
    "sql",
    "postgres",
    "git",
    "svn",
    "apache",
    "nginx",
    "tomcat",
    "joomla",
    "wordpress",
    "drupal",
    "magento",
    "phpmyadmin",
    "guest",
    "12345",
    "password",
    "123456",
    "123456789",
    "qwerty",
    "letmein",
    "welcome",
    "1234",
    "123",
    "123321",
    "654321",
    "password1",
    "iloveyou",
    "admin123",
    "sunshine",
    "admin1234",
    "abc123",
    "admin1",
    "monkey",
    "1q2w3e4r",
    "superadmin",
    "master",
    "guest123",
    "test123",
    "admin12345",
    "1234567",
    "123123",
    "adminadmin",
    "password123",
    "hello",
    "123qwe",
    "welcome1",
    "12345678",
    "letmein123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",
    "admin1234",
    "admin1",
    "admin12345",
    "admin123456",
    "adminadmin",
    "password123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",
    "admin1234",
    "admin1",
    "admin12345",
    "admin123456",
    "adminadmin",
    "password123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",
    "admin1234",
    "admin1",
    "admin12345",
    "admin123456",
    "adminadmin",
    "password123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",
    "admin1234",
    "admin1",
    "admin12345",
    "admin123456",
    "adminadmin",
    "password123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",
    "admin1234",
    "admin1",
    "admin12345",
    "admin123456",
    "adminadmin",
    "password123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",
    "admin1234",
    "admin1",
    "admin12345",
    "admin123456",
    "adminadmin",
    "password123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",
    "admin1234",
    "admin1",
    "admin12345",
    "admin123456",
    "adminadmin",
    "password123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",
    "admin1234",
    "admin1",
    "admin12345",
    "admin123456",
    "adminadmin",
    "password123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",
    "admin1234",
    "admin1",
    "admin12345",
    "admin123456",
    "adminadmin",
    "password123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",
    "admin1234",
    "admin1",
    "admin12345",
    "admin123456",
    "adminadmin",
    "password123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",
    "admin1234",
    "admin1",
    "admin12345",
    "admin123456",
    "adminadmin",
    "password123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",
    "admin1234",
    "admin1",
    "admin12345",
    "admin123456",
    "adminadmin",
    "password123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",
    "admin1234",
    "admin1",
    "admin12345",
    "admin123456",
    "adminadmin",
    "password123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",
    "admin1234",
    "admin1",
    "admin12345",
    "admin123456",
    "adminadmin",
    "password123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",
    "admin1234",
    "admin1",
    "admin12345",
    "admin123456",
    "adminadmin",
    "password123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",
    "admin1234",
    "admin1",
    "admin12345",
    "admin123456",
    "adminadmin",
    "password123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",
    "admin1234",
    "admin1",
    "admin12345",
    "admin123456",
    "adminadmin",
    "password123",
    "admin888",
    "root123",
    "1234567890",
    "passw0rd",
    "admin99",
    "password1234",
    "root1",
    "welcome123",
    "admin123456",
    "password1",
    "qazwsx",]

# Predict new strings and print probabilities

# Predict new strings and print probabilities
new_input = passwords1 + non_passwords1 + regular_words
X_new = np.array([list(extract_features(text).values()) for text in new_input])
probabilities = svm_classifier.predict_proba(X_new)  # Use predict_proba to get probabilities

for i, input_str in enumerate(new_input):
    prediction = svm_classifier.predict([X_new[i]])
    probability = probabilities[i]
    
    if prediction[0] == 1:
        print(f"'{input_str}' is a password with probability {probability[1]:.2f}")
    else:
        print(f"'{input_str}' is not a password with probability {probability[0]:.2f}")
# 6. 预测新字符串

# predictions = svm_classifier.predict(X_new)

# for i, input_str in enumerate(new_input):
#     if predictions[i] == 1:
#         print(f"'{input_str}' is a password.")
#     else:
#         print(f"'{input_str}' is not a password.")

# 使用PCA降低维度到2D
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_train)

# 创建一个网格来绘制决策边界
h = .02  # 步长
x_min, x_max = X_pca[:, 0].min() - 1, X_pca[:, 0].max() + 1
y_min, y_max = X_pca[:, 1].min() - 1, X_pca[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

# 使用SVC进行预测
Z = svm_classifier.predict(pca.inverse_transform(np.c_[xx.ravel(), yy.ravel()]))
Z = Z.reshape(xx.shape)

# 可视化决策边界
plt.contourf(xx, yy, Z, cmap=plt.cm.coolwarm, alpha=0.8)
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y_train, cmap=plt.cm.coolwarm, marker='o')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('SVC Decision Boundary')
plt.show()