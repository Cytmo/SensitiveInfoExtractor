import xml.etree.ElementTree as ET
import json


# 解析 XML 文件
def xml_file(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return dict_to_json(xml_to_dict(root))
    except Exception as e:
        return str(e)


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


# print(xml_file("data/linux/applicationContext.xml"))
