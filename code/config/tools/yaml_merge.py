import os
import yaml


def merge_and_remove_duplicates(input_directory, output_file):
    # 初始化一个空列表以存储所有规则
    all_rules = []

    # 递归扫描目录中的所有YAML文件
    for root, dirs, files in os.walk(input_directory):
        for file in files:
            if file.endswith(".yaml") or file.endswith(".yml"):
                file_path = os.path.join(root, file)
                # print("Processing file:", file_path)
                with open(file_path, 'r') as file:
                    rules = yaml.safe_load(file)
                    if 'patterns' in rules:
                        # print("Found 'patterns' in the rules file:")
                        filtered_rules = [
                            rule for rule in rules['patterns'] if 'confidence' not in rule or (rule.get('confidence') == 'high')]
                        all_rules.extend(filtered_rules)

    # 创建新的规则字典
    new_rules = {'patterns': all_rules}

    # 创建一个字典来存储已经出现的name属性值
    name_dict = {}

    # 用于存储唯一的pattern的列表
    unique_patterns = []

    # 遍历每个pattern
    for pattern_item in new_rules['patterns']:
        pattern = pattern_item['pattern']  # 获取'pattern'字典
        name = pattern.get('name')  # 从'pattern'字典中获取'name'属性

        # 如果name属性值尚未出现，将其添加到name_dict并添加该pattern到unique_patterns
        if name not in name_dict:
            name_dict[name] = 1
            unique_patterns.append(pattern_item)

    # 更新数据，只包含唯一的patterns
    new_rules['patterns'] = unique_patterns

    # 将更新后的数据保存到输出文件
    with open(output_file, 'w') as file:
        yaml.safe_dump(new_rules, file)

# 调用合并后的函数，指定输入目录和输出文件


input_directory = '../datasets'
output_file = '../rules_new.yaml'
merge_and_remove_duplicates(input_directory, output_file)
