from typing import Tuple
import yaml
import re

# 读取YAML文件
with open('../config/rules-stable.yml', 'r') as yaml_file:
    sensitive_info_pattern = yaml.safe_load(yaml_file)

# 使用规则库对文本进行标记
def sensitive_pattern_matcher(text: str) -> str:
    # {"location":[matched_names,...]}
    result = {}

    for pattern in sensitive_info_pattern['patterns']:

        name = pattern['pattern']['name']
        regex = pattern['pattern']['regex']
        confidence = pattern['pattern']['confidence']

        # 进行正则表达式匹配
        match = re.search(regex, text)

        if match:
            print(f"Matched pattern: {name}")
            print(f"Confidence: {confidence}")
            print(f"Matched text: {match.group(0)}\n")
            if match.group(0) not in result:
                result[match.group(0)] = []
                result[match.group(0)].append(name)
            
    print(result)
    number = "1"
    for key in result:
        text = text.replace(key, "?"+number+"?")
        number = str(int(number)+1)

    print(text)
text = '''#!/bin/bash

IMG="pyo3-test"
MINIO_IMG=quay.io/minio/minio

ACCESSKEY="AKIAIOSFODMM7EXAMPLE"
SECRETKEY="wJalrXUtnFEMI/K7MDENG/bQxRfiCYEXAMPLEKEY"

echo "Starting local minio instance"
docker run --rm -d --name local-minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e "MINIO_ROOT_USER=$ACCESSKEY" \
  -e "MINIO_ROOT_PASSWORD=$SECRETKEY" \
  $MINIO_IMG server /data --console-address ":9001"

echo "Starting fasts3 test client"
docker run -it --rm  --name fasts3-test \
    --link local-minio:local-minio \
    -e "AWS_ACCESS_KEY_ID=$ACCESSKEY" \
    -e "AWS_SECRET_ACCESS_KEY=$SECRETKEY" \
    $IMG \
    python3 /regression_test.py
10.1.1.1
echo "Finished, now shutting down local minio."
docker stop local-minio
'''
# TODO 修改混淆信息保护函数，加入以上内容，修改混淆信息保护函数输出的字典格式，type改为列表
def information_protection(text: str) -> Tuple[str, dict]:
    placeholders = {}  # This dictionary will store placeholders and their corresponding content
    placeholders_counter = 1  # Counter for generating placeholders
    global PLACEHOLDERS_CORRESPONDING_TYPE
    PLACEHOLDERS_CORRESPONDING_TYPE = {}
    # Define a list of dictionaries with patterns and their corresponding types
    patterns = [
        {'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', 'type': 'email'},
        {'pattern': r'jdbc:mysql://[a-zA-Z0-9:/._-]+', 'type': 'jdbc_url'},
        {'pattern': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 'type': 'url'},
        {'pattern': r'(?:\d{1,3}\.){3}\d{1,3}|localhost', 'type': 'ip'},
        {'pattern': r'1[3-9]\d{9}', 'type': 'phonenumber'},
        # {'pattern': r'\b(0|6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|[0-5]?[0-9]{1,4})\b', 'type': 'port'}
    ]

    for pattern_info in patterns:
        pattern = pattern_info['pattern']
        matches = re.finditer(pattern, text, flags=re.IGNORECASE)
        for match in matches:
            item = match.group()
            placeholder = f'?{placeholders_counter}?'
            placeholders[placeholder] = item
            if placeholder not in PLACEHOLDERS_CORRESPONDING_TYPE:
                PLACEHOLDERS_CORRESPONDING_TYPE[placeholder] = []
            PLACEHOLDERS_CORRESPONDING_TYPE[placeholder].append(pattern_info['type'])  # Store the corresponding type
            # Replace only the first occurrence
            text = text.replace(item, placeholder, 1)
            placeholders_counter += 1

    match_result = {}

    for pattern in sensitive_info_pattern['patterns']:

        name = pattern['pattern']['name']
        regex = pattern['pattern']['regex']
        confidence = pattern['pattern']['confidence']

        # 进行正则表达式匹配
        match = re.search(regex, text)

        if match:
            print(f"Matched pattern: {name}")
            print(f"Confidence: {confidence}")
            print(f"Matched text: {match.group(0)}\n")
            if match.group(0) not in match_result:
                match_result[match.group(0)] = []
                match_result[match.group(0)].append(name)

    print(match_result)
    for key in match_result:
        placeholder = f'?{placeholders_counter}?'
        placeholders[placeholder] = key
        text = text.replace(key, placeholder, 1)
        placeholders_counter += 1
    print(placeholders)
    for key in placeholders:
        if key not in PLACEHOLDERS_CORRESPONDING_TYPE:
            PLACEHOLDERS_CORRESPONDING_TYPE[key] = []
        PLACEHOLDERS_CORRESPONDING_TYPE[key].append(match_result[placeholders[key]])
    print(text)
    print(PLACEHOLDERS_CORRESPONDING_TYPE)
    return text, placeholders

text, placeholders = information_protection(text)

print(placeholders)