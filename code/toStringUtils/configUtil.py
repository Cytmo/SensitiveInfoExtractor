import json
import yaml
import json
import os
from regipy.registry import RegistryHive
import xml.etree.ElementTree as ET
import subprocess


"""
configUtil: 解析一些特殊配置文件 
1. xml/yml
2. Windows sam.hiv/system.hiv
"""


# 解析 XML 文件
def xml_file(file_path):

    # 将 XML 转换为字典
    def xml_to_dict(element):
        xml_dict = {}
        for child in element:
            if len(child) == 0:
                xml_dict[child.attrib['name']] = child.attrib['value']
            else:
                xml_dict[child.attrib['name']] = xml_to_dict(child)
        return xml_dict

    # 将字典转换为 JSON
    def dict_to_json(data_dict):
        return json.dumps(data_dict, indent=2)

    # 开始解析
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return dict_to_json(xml_to_dict(root))
    except Exception as e:
        return str(e)


# 解析yml文件
def yml_file(file_path):
    # 将 YAML 转换为 JSON
    def yml_to_json(yaml_content):
        try:
            yml_dict = yaml.safe_load(yaml_content)
            json_data = json.dumps(yml_dict, indent=2)
            return json_data
        except Exception as e:
            return str(e)

    # 开始解析
    with open(file_path, 'r') as file:
        yml_content = file.read()
    return yml_to_json(yml_content)


# 解析 windows registry file: sam.hiv/system.hiv/sam/system
def win_reg_file(file_path, res_path):
    # 使用samdump2解析
    command = "samdump2 {} {}".format(file_path, res_path)
    print("Running"+command)
    result = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # 打印标准输出
    print("标准输出：")
    print(result.stdout)

# 解析源码文件夹
def source_code_file(file_path, res_path=''):
    # 使用whispers解析
    command = "whispers {}".format(file_path)
    print("Running "+command)
    result = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # 打印标准输出
    print("标准输出：")
    print(result.stdout)
    print("标准错误：")
    print(result.stderr)
# print(xml_file("data/linux/applicationContext.xml"))
# print(yml_file("data/linux/application-dev.yml"))
# win_reg_file("../data/windwos/system.hiv", "../data/windwos/sam.hiv")
# win_reg_file("../data/windwos/sam/sam/system", "../data/windwos/sam/sam/sam")
if __name__ == "__main__":
    source_code_file("~/workspace/security-text-detect-825/data/src")