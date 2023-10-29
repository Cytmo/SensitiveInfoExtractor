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
            if re.search(regex, input_string):
                matches.append(name)

        # 输出匹配的规则名称
        if matches:
            return matches
        else:
            return ["没有匹配的规则"]
    except Exception as e:
        return [f"发生错误: {str(e)}"]


# 输入的字符串
input_string = "myapi.execute-api.us-east-1.amazonaws.com"
rules_file = '../rules-stable.yml'

# 调用函数并输出匹配的规则名称
matched_rules = match_rules(input_string, rules_file)
for rule in matched_rules:
    print(rule)
