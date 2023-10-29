import yaml
import re

import yaml
import re


def match_rules(input_string, rules_file):
    try:
        # 读取规则文件
        with open(rules_file, 'r') as file:
            rules_data = yaml.load(file, Loader=yaml.FullLoader)

        # 创建一个字典来存储规则名称和对应的正则表达式
        regex_patterns = {}
        for pattern in rules_data['patterns']:
            name = pattern['pattern'].get('name')
            regex = pattern['pattern'].get('regex')
            if regex:
                regex_patterns[name] = regex

        # 遍历规则并尝试匹配输入的字符串
        matches = []
        for name, regex in regex_patterns.items():
            match = re.search(regex, input_string)
            if match:
                matched_string = match.group(0)  # 获取匹配的字符串
                matches.append((name, matched_string))  # 存储规则名称和匹配的字符串

        # 输出匹配的规则名称和匹配的字符串
        if matches:
            for name, matched_string in matches:
                print(f"匹配规则 '{name}'，匹配的字符串: '{matched_string}'")
            return [name for name, _ in matches]
        else:
            print("没有匹配到规则")
            return []
    except Exception as e:
        return []


# 输入的字符串
input_string = ["ACCESSKEY='AKIAIOSFODMM7EXAMPLE'",
                'SECRETKEY="wJalrXUtnFEMI/K7MDENG/bQxRfiCYEXAMPLEKEY"',]
input_string = [
    'AKIAIOSFODMM7EXAMPLE',
    'wJalrXUtnFEMI/K7MDENG/bQxRfiCYEXAMPLEKEY',
    'cytmo@qq.com'
    ]
# input_string = [""]
rules_file = 'rules-stable.yml'
# rules_file = '../rules/rules_stable.yml'


# 调用函数并输出匹配的规则名称
for item in input_string:
    print()
    print("==>"+item)
    matched_rules = match_rules(item, rules_file)
