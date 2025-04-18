import pickle
import numpy as np
import re
from util import globalVar
TAG = "informationEngine.password_guesser.py: "

from util.logUtils import LoggerSingleton
logger = LoggerSingleton().get_logger()
# 读取模型
with open('informationEngine/svm_classifier.pkl', 'rb') as f:
    svm_classifier = pickle.load(f)
# 2. 特征提取
# 添加更多特征
def extract_features(text):
    # 初始化特征字典
    features = {
        'length': len(text),
        'uppercase_count': 0,
        'lowercase_count': 0,
        'digit_count': 0,
        'special_count': 0
    }

    # 统计特征
    for char in text:
        if char.isupper():
            features['uppercase_count'] += 1
        elif char.islower():
            features['lowercase_count'] += 1
        elif char.isdigit():
            features['digit_count'] += 1
        elif re.match(r'[!@#$%^&*()]', char):
            features['special_count'] += 1

    return features


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




def effectiveness(passwords, non_passwords, regular_words):
    X = np.array([list(extract_features(text).values()) for text in passwords + non_passwords + regular_words])
    y = np.array([1] * len(passwords) + [0] * len(non_passwords) + [0] * len(regular_words))
    svm_classifier.fit(X, y)
    # print("Accuracy:", svm_classifier.score(X, y))



# 预测新字符串
# 输入格式 ["123456","123456789"]
def predict_password(string_to_guess:list)->list:
    # Predict new strings and print probabilities
    # new_input = passwords1 + non_passwords1 + regular_words
    new_input = string_to_guess
    X_new = np.array([list(extract_features(text).values()) for text in new_input])
    # # print(X_new)
    results = []
    probabilities = svm_classifier.predict_proba(X_new)  # Use predict_proba to get probabilities

    for i, input_str in enumerate(new_input):
        prediction = svm_classifier.predict([X_new[i]])
        probability = probabilities[i]
        # print(f"String: '{input_str}' with probability {probability} and prediction {prediction}")
        if prediction[0] == 1:
            # print(f"'{input_str}' is a password with probability {probability[1]:.2f}")
            results.append([True, probability[1]])
        else:
            # print(f"'{input_str}' is not a password with probability {probability[0]:.2f}")
            results.append([False, probability[0]])
    return results

if __name__ == "__main__":
    # effectiveness(passwords1, non_passwords1, regular_words)
    results = predict_password(["123456","123456789"])
    # print(results)