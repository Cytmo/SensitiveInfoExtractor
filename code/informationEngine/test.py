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

echo "Finished, now shutting down local minio."
docker stop local-minio
'''
sensitive_info_pattern = sensitive_pattern_matcher(text)





# TODO
'''
修改混淆信息保护函数，加入以上内容，修改混淆信息保护函数输出的字典格式，type改为列表



'''