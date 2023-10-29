import yaml


# 去除带问号的正则表达式
def simplify_rules(input_filename, output_filename):
    # 清空输出文件内容
    open(output_filename, 'w').close()

    # 读取输入文件并添加错误处理
    try:
        with open(input_filename, 'r') as file:
            rules_data = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"File '{input_filename}' not found.")
        return
    except yaml.YAMLError as e:
        print(f"Error loading YAML from '{input_filename}': {e}")
        return

    # 定义条件，比如包含"?"的正则项需要被删除
    def should_remove(rule):
        return "?" in rule['pattern']['regex']

    # 使用列表推导来筛选出不需要删除的正则项
    filtered_rules = [rule for rule in rules_data['patterns']
                      if not should_remove(rule)]

    # 调整字段顺序并创建新的规则列表
    new_rules = []
    for rule in filtered_rules:
        new_rule = {
            'pattern': {
                'name': rule['pattern']['name'],
                'regex': rule['pattern']['regex'],
                'confidence': rule['pattern']['confidence'],
            }
        }
        new_rules.append(new_rule)

    # 创建一个新的 YAML 数据字典
    new_rules_data = {'patterns': new_rules}

    # 保存到输出文件并保持格式
    with open(output_filename, 'w') as file:
        yaml.dump(new_rules_data, file, default_flow_style=False)

    print(f"Filtered rules saved to {output_filename}")


# 目前只删除了带?的
# 调用函数并传递输入和输出文件名
input_file = '../rules-stable.yml'
output_file = '../rules/rules_simple.yml'
simplify_rules(input_file, output_file)
