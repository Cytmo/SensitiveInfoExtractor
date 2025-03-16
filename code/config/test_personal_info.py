import sys
import os
import yaml
import re

# 导入当前目录下的配置文件
import info_core_config

def test_personal_info_patterns():
    """测试个人信息正则表达式是否正确加载"""
    test_cases = {
        "姓名": ["张三", "李四", "王五"],
        "身份证号": ["110101199001011234", "320123198901234567"],
        "护照号": ["E12345678", "G87654321"],
        "手机号": ["13812345678", "18912345678"],
        "电子邮箱": ["test@example.com", "user.name@domain.cn"],
        "病历": ["病历: 患者有高血压病史", "病史：糖尿病"],
        "诊断报告": ["诊断: J12.1 病毒性肺炎", "诊断：A02.1 伤寒"],
        "学籍号": ["G2022ABCDEF12", "G2023123456AB"],
        "信用卡号": ["4111111111111111", "5500000000000004"],
        "工资单": ["工资:5000元", "工资：12345.67元"]
    }
    
    # 在SENSITIVE_INFO_PATTERN中查找个人信息模式
    pattern_dict = {}
    for pattern in info_core_config.SENSITIVE_INFO_PATTERN['patterns']:
        name = pattern['pattern']['name']
        regex = pattern['pattern']['regex']
        pattern_dict[name] = regex
    
    print("已加载的个人信息模式:")
    for name, regex in pattern_dict.items():
        if name in test_cases:
            print(f"- {name}: {regex}")
    
    print("\n测试结果:")
    for name, test_data in test_cases.items():
        if name in pattern_dict:
            regex = pattern_dict[name]
            pattern = re.compile(regex)
            print(f"\n{name}:")
            for test_str in test_data:
                match = pattern.search(test_str)
                result = "匹配成功" if match else "匹配失败"
                print(f"  '{test_str}': {result}")
        else:
            print(f"\n{name}: 未找到对应的正则表达式")

if __name__ == "__main__":
    test_personal_info_patterns() 