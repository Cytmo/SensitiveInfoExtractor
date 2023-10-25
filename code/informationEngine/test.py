
import argparse
import os
import shutil
import yaml
# from informationEngine import info_protection
# from informationEngine.info_protection import IoCIdentifier
from typing import Any, Tuple
import re
import re
from pygments.lexers import guess_lexer, ClassNotFound
# from toStringUtils.officeUtil import one_table_remove_irrelevant_columns
# from informationEngine import password_guesser
# # 添加日志模块
# TAG = "informationEngine.info_core.py: "
# logger = LoggerSingleton().get_logger()

# 保存email地址 url ip地址等内容，防止被替换
import re
from typing import Tuple


placeholders_corresponding_type = {}  # This dictionary will store placeholders and their corresponding types

def information_protection(text: str) -> Tuple[str, dict]:
    placeholders = {}  # This dictionary will store placeholders and their corresponding content
    placeholders_counter = 1  # Counter for generating placeholders
    global placeholders_corresponding_type
    placeholders_corresponding_type = {}
    # Define a list of dictionaries with patterns and their corresponding types
    patterns = [
        {'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', 'type': 'email'},
        {'pattern': r'jdbc:mysql://[a-zA-Z0-9:/._-]+', 'type': 'jdbc_url'},
        {'pattern': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 'type': 'url'},
        {'pattern': r'(?:\d{1,3}\.){3}\d{1,3}|localhost', 'type': 'ip'},
        {'pattern': r'1[3-9]\d{9}', 'type': 'phone_number'},
        # {'pattern': r'\b(0|6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|[0-5]?[0-9]{1,4})\b', 'type': 'port'}
    ]



    for pattern_info in patterns:
        pattern = pattern_info['pattern']
        matches = re.finditer(pattern, text, flags=re.IGNORECASE)
        for match in matches:
            item = match.group()
            placeholder = f'?{placeholders_counter}?'
            placeholders[placeholder] = item
            placeholders_corresponding_type[placeholder] = pattern_info['type']  # Store the corresponding type
            # Replace only the first occurrence
            text = text.replace(item, placeholder, 1)
            placeholders_counter += 1

    return text, placeholders

item = '''

13666628123
'''
item_protection, placeholders = information_protection(item)
print(item_protection)
print(placeholders)
print(placeholders_corresponding_type)