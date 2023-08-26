import json
import yaml
import json
import xml.etree.ElementTree as ET

"""
configUtil: 解析 xml/yml
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
def yml_file(file):
    # 将 YAML 转换为 JSON
    def yml_to_json(yaml_content):
        try:
            yml_dict = yaml.safe_load(yaml_content)
            json_data = json.dumps(yml_dict, indent=2)
            return json_data
        except Exception as e:
            return str(e)

    # 开始解析
    with open(file, 'r') as file:
        yml_content = file.read()
    return yml_to_json(yml_content)


# print(xml_file("data/linux/applicationContext.xml"))
# print(yml_file("data/linux/application-dev.yml"))
