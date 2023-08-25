import yaml
import json


# 读取 YAML 文件
def yml_file(file):
    with open(file, 'r') as file:
        yml_content = file.read()
    return yml_to_json(yml_content)


# 将 YAML 转换为 JSON
def yml_to_json(yaml_content):
    try:
        yml_dict = yaml.safe_load(yaml_content)
        json_data = json.dumps(yml_dict, indent=2)
        return json_data
    except Exception as e:
        return str(e)


# 输出 JSON 数据
# print(yml_file("data/linux/application-dev.yml"))
