from util.logUtils import LoggerSingleton
from util import globalVar
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
from toStringUtils.officeUtil import one_table_remove_irrelevant_columns
from informationEngine import password_guesser
# 添加日志模块
TAG = "informationEngine.info_core.py: "
logger = LoggerSingleton().get_logger()
import re
from typing import Tuple

##########################全局变量###############################
# This dictionary will store placeholders and their corresponding types
placeholders_corresponding_type = {}  
# 保存易混淆内容的位置 infomaion protection
item_protection_dict = {}
# 英文关键词列表
eng_keywords_list = ["-u", "-p", "IP", "port", "-h",
                 "user", "password", "passw0rd", "address", "name", '\n']
# 英文替换词列表
eng_replacement_dict = {"-p": "password", "port": "port", "-u": "user", "user": "user", "password": "password",
                    "-h": "address", "IP":"address","address": "address", "name": "name", "passw0rd": "password"}
# 中文关键字列表
chn_keywords_list = ["账号", "IP", "端口", "名称", "地址",
                     "姓名", "学号", "用户名", "密码", "密钥为", '\n']
# 中文替换列表
chn_replacement_dict = {"账号": "user", "端口": "port", "名称": "user", "学号": "user", "用户名": "user",
                        "密钥为": "password", "密码": "password", "IP":"address","地址": "address", "姓名": "name"}
# 信息提取列表
info_pattern = {"user": "user", "password": "password",
                "address": "address", "port": "port","phonenumber":"phonenumber"}
# 信息提取替换词列表
replaced_keyword_list = ["{user}", "{password}", "{address}", "{port}", "{phonenumber}"]
# 代码提取词列表
special_keywords_list = [
    "user",
    "pass",
    "address",
    "name",
    "port",
    "key",
    "auth",
    "salt",
    "host",
    "password",
    "username",
    "url",
    "driver",
]

##########################工具函数和类###############################
# 分割字符串并移除空项
def text_split(text: str) -> list:
    logger.info(TAG + "text_split(): text split input: "+str(text))
    # 使用 \n \t 空格 分割字符串
    text = re.split(r'\n|\t| ', text)
    text = [item for item in text if item != '' and item != ' ']
    logger.info (TAG + "text_split(): text split result: "+str(text))
    return text

def is_chinese_text(text: str) -> bool:
    # pattern = re.compile(r'[\u4e00-\u9fa5]')  # 匹配中文字符的范围
    # return bool(pattern.search(text))
    return chinese_character_percentage(text) > 70.0

# 判断中文字符占比
def chinese_character_percentage(text: str) -> float:
    total_characters = 0
    chinese_characters = 0
    english_characters = 0
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            chinese_characters += 1
        if '\u0041' <= char <= '\u005a' or '\u0061' <= char <= '\u007a':
            english_characters += 1
    total_characters = chinese_characters + english_characters
    if total_characters == 0:
        return 0.0

    percentage = (chinese_characters / total_characters) * 100
    return percentage

# 使用svm分类字符串
def password_classifier(text: str) -> bool:
    result =  password_guesser.predict_password([text])
    # [[True, 0.9999999922353121]]
    if result[0][0] == True and result[0][1] > 0.9:
        return True
    else:
        return False

# 转换OCR识别中的错误符号
def convert_chinese_punctuation(text):
    # 定义一个字典来映射中文标点符号到英文标点符号
    punctuation_mapping = {
        "，": ",",
        "。": ".",
        "！": "!",
        "？": "?",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "；": ";",
        "：": ":",
        "（": "(",
        "）": ")",
        "【": "[",
        "】": "]",
        "《": "<",
        "》": ">",
        "、": ",",
        "＇": "'",
        "/**#@+ *": "",
    }

    # 使用字典进行替换
    for chinese_punctuation, english_punctuation in punctuation_mapping.items():
        text = text.replace(chinese_punctuation, english_punctuation)

    return text

# 判断是否是被保护的信息项
def is_protected_item(item: str) -> bool:
    pattern = r'\?\d\?'
    return bool(re.search(pattern, item))


# 判断图片识别结果（表格形式）还是文本
def is_png_text(info):
    total_length = sum(len(item) for item in info[1:])
    average_length = total_length / float(len(info[1:]))
    if average_length >= 2:
        logger.info(TAG + "is_png_text(): input is [table] png ")
        return False
    logger.info(TAG + "is_png_text(): input is [text] png ")
    return True


# TODO:url和端口号成组且支持一个用户对应多个url
# 从处理过后的字符串中提取成对信息
class paired_info_pattern():

    def __init__(self):
        self.port = None
        self.address = None
        self.user = None
        self.password = None
        self.phonenumber = None

    def set_port(self, port):
        self.port = port

    def set_address(self, address):
        self.address = address

    def set_user(self, user):
        self.user = user

    def set_password(self, password):
        self.password = password

    def set_phonenumber(self, phonenumber):
        self.phonenumber = phonenumber

    def setter(self, name: str, value: Any) -> None:
        # if self.__dict__.get(name) != None and self.__dict__.get(name) != value:
        #     return False
        attr_switch = {
            "port": lambda x: self.set_port(x),
            "address": lambda x: self.set_address(x),
            "user": lambda x: self.set_user(x),
            "password": lambda x: self.set_password(x),
            "phonenumber": lambda x: self.set_phonenumber(x)
        }
        if name in attr_switch:
            # print("Setting "+str(name)+" " +str( value))
            return attr_switch[name](value)
        else:
            return False

    def output(self):
        result = {
            "user": self.user,
            "password": self.password,
            "address": self.address,
            "port": self.port,
            "phonenumber": self.phonenumber
        }
        # remove None attributes
        
        self.__init__()
        return result

    def getter(self, name: str):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            return None

    def if_same_attr(self, name: str, value: Any) -> bool:
        return self.__dict__.get(name) == value

    def is_None(self):
        return self.__dict__.get("user") == None and self.__dict__.get("password") == None and self.__dict__.get("address") == None and self.__dict__.get("port") == None

##########################预处理函数###############################
# 提取易混淆的内容并进行标记 保存email地址 url ip地址等内容，防止被替换
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
        {'pattern': r'1[3-9]\d{9}', 'type': 'phonenumber'},
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

# 防止文件名等并识别为关键字，如user.txt
def fuzz_prevention(text: str) -> str:
    # 文件后缀列表
    file_extensions = ['sys', 'htm', 'html', 'jpg', 'png', 'vb', 'scr', 'pif', 'chm',
                       'zip', 'rar', 'cab', 'pdf', 'doc', 'docx', 'ppt', 'pptx',
                       'xls', 'xlsx', 'swf', 'gif', 'txt', 'csv', 'sh', 'c', 'd', 'conf', 'exe']

    # 构建正则表达式模式，匹配文件名及其后缀
    extensions_pattern = '|'.join(file_extensions)
    file_pattern = r'\w+\.(?:' + extensions_pattern + r')\b'

    # 使用正则替换
    result = re.sub(file_pattern, 'file', text)
    result = result.replace("username", "user")
    return result

# 预处理英文自然语言文本
def eng_text_preprocessing(text: str) -> str:
    # 构建正则表达式，匹配英文字符、数字以及指定中文关键词
    pattern = f"(?:{'|'.join(eng_keywords_list)}|[a-zA-Z0-9,.;@?!\-\"'()])+"

    # 使用正则表达式进行匹配和替换
    cleaned_text = re.findall(pattern, text)

    # 将匹配到的内容重新组合成字符串
    cleaned_text = ' '.join(cleaned_text)
    # 替换中文关键词
    for keyword in eng_keywords_list:
        if keyword in eng_replacement_dict:
            cleaned_text = cleaned_text.replace(
                keyword, ' {'+eng_replacement_dict[keyword]+'} ')
    # 移除空行
    cleaned_text = '\n'.join(
        [line for line in cleaned_text.splitlines() if line.strip()])
    cleaned_text = cleaned_text.replace("{ {", "{").replace("} }", "}")
    logger.debug("Cleaned text: "+cleaned_text)
    return cleaned_text

# 预处理文本，仅保留英文字符和数字，以及中文关键词（学号，用户名，密码等）
def chn_text_preprocessing(text: str) -> str:
    text, item_protection_dict1 = information_protection(text)
    global item_protection_dict
    item_protection_dict = item_protection_dict1
    # 构建正则表达式，匹配英文字符、数字以及指定中文关键词
    pattern = f"(?:{'|'.join(chn_keywords_list)}|[a-zA-Z0-9,.;@?!\"'()])+"

    # 使用正则表达式进行匹配和替换
    cleaned_text = re.findall(pattern, text, re.IGNORECASE)

    # 将匹配到的内容重新组合成字符串
    cleaned_text = ' '.join(cleaned_text)
    # 替换中文关键词
    for keyword in chn_keywords_list:
        if keyword in chn_replacement_dict:
            cleaned_text = cleaned_text.replace(
                keyword, ' {'+chn_replacement_dict[keyword]+'} ')
    # 移除空行
    cleaned_text = '\n'.join(
        [line for line in cleaned_text.splitlines() if line.strip()])
    logger.debug("Cleaned text: "+cleaned_text)
    return cleaned_text

# 模糊标记文本中的关键词
def fuzz_mark(text: str) -> str:
    text = text_split(text)
    tagged_text = explicit_fuzz_mark(text)
    tagged_text = implicit_fuzz_mark(tagged_text)
    return " ".join(tagged_text)

# 标记可明显识别的关键词 如url port等
def explicit_fuzz_mark(text: list) -> list:
    logger.info(TAG+ "placeholder_extract(): placeholder extract{}".format(str(placeholders_corresponding_type)))
    logger.info(TAG+ "fuzz_mark(): explicit_fuzz_mark input: {}".format(text))
    tagged_text = []
    logger.info(TAG+ "explicit_fuzz mark input list: {}".format(text))
    for i in range(len(text)):
        if text[i] in placeholders_corresponding_type:
            if placeholders_corresponding_type[text[i]] == 'url':
                tagged_text.append('{address}')
            elif placeholders_corresponding_type[text[i]] == 'port':
                tagged_text.append('{port}')
            elif placeholders_corresponding_type[text[i]] == 'email':
                tagged_text.append('{user}')
            elif placeholders_corresponding_type[text[i]] == 'ip':
                tagged_text.append('{address}')
            elif placeholders_corresponding_type[text[i]] == 'phonenumber':
                tagged_text.append('{phonenumber}')
            tagged_text.append(text[i])
        else:
            tagged_text.append(text[i])
    logger.info(TAG+ "fuzz_mark(): explicit_fuzz_mark result: {}".format(' '.join(tagged_text)))
    return tagged_text

# 标记隐式项 如用户名 密码等
def implicit_fuzz_mark(text: list) -> list:
    logger.info(TAG+ "implicit_fuzz_mark(): input list: {}".format(text))
    tagged_text = []
    for i in range(len(text)):
        if is_protected_item(text[i]):
            tagged_text.append(text[i])
        elif text[i] in replaced_keyword_list:
            tagged_text.append(text[i])
        else:
            logger.info(TAG+ "implicit_fuzz_mark(): password_classifier input: {}".format(text[i]))
            password_classifier_result = password_classifier(text[i])
            logger.info(TAG+ "implicit_fuzz_mark(): password_classifier result: {}".format(password_classifier_result))
            if password_classifier_result:
                tagged_text.append('{password}')
            else:
                tagged_text.append('{user}')
            tagged_text.append(text[i])
    logger.info(TAG+ "implicit_fuzz_mark(): implicit_fuzz_mark result: {}".format(' '.join(tagged_text)))
    return tagged_text 

# 对标记后的字符串进行调整
def marked_text_refinement(text: str) -> str:
    def is_valid_address(address):
        if address.startswith("?") and address.endswith("?"):
            return True
        return False

    def is_valid_port(port):
        if port.isdigit() and 0 < int(port) < 65536:
            return True
        return False
    
    def is_valid_user(user):
        return True

    def is_valid_password(password):
        return True
    # 调整关键词和指示词的相对位置，保持关键词在指示词的后部
    text = text.split()
    MAX_DISTANCE = 2
    keyword = "{port}"
    
    for i in range(len(text)):
        # 处理端口号
        if text[i] == keyword:           
            for j in range(max(i - MAX_DISTANCE, 0), min(i + MAX_DISTANCE + 1, len(text))):
                if j != i and text[j].isdigit() and 0 < int(text[j]) < 65536:
                    # Swap the keyword with a valid integer within the specified distance
                    logger.debug(TAG + 'Swapping {} with {}'.format(text[i], text[j]))
                    text[i+1], text[j] = text[j], text[i+1]
                    break
    logger.debug(TAG + 'Text after position adjustment: '+str(text))


    # 移除连续出现的，其后无有效关键词的指示词
    for i in range(len(text)-1):
        if text[i] in replaced_keyword_list and text[i+1] in replaced_keyword_list:
            text[i] = ""
    
    # 移除指示词和其后的关键词之外的内容
    new_text = []
    for i in range(len(text)-1):
        if text[i] in replaced_keyword_list and text[i+1] not in replaced_keyword_list:
            new_text.append(text[i])
            new_text.append(text[i+1])
    text = new_text


    # 移除关键词无效的指示词，如 地址后不是有效地址
    for i in range(len(text)-1):
        if text[i] in replaced_keyword_list and text[i+1] not in replaced_keyword_list:
            if text[i] == "{address}" and not is_valid_address(text[i+1]):
                text[i] = ""
                text[i+1] = ""
            if text[i] == "{port}" and not is_valid_port(text[i+1]):
                text[i] = ""
                text[i+1] = ""
            if text[i] == "{user}" and not is_valid_user(text[i+1]):
                text[i] = ""
                text[i+1] = ""
            if text[i] == "{password}" and not is_valid_password(text[i+1]):
                text[i] = ""
                text[i+1] = ""

    # 移除空项
    text = [item for item in text if item != ""]
    text = " ".join(text)
    logger.debug(TAG + 'Text after repeated keywords adjustment: '+str(text))
    return text

##########################信息提取函数###############################
# 从预处理过后的文本中提取成对信息
def extract_paired_info(text):
    result_pair = []
    a_paired_info = paired_info_pattern()
    text = text.split()
    has_user = False
    has_address = False
    for i in range(len(text)-1):
        # 密码不会最先出现
        if text[i].strip() == "{password}" and a_paired_info.is_None():
            continue
        if text[i].strip() in replaced_keyword_list and text[i+1] not in replaced_keyword_list:
            if (text[i] == "{user}" and has_user) or (text[i] == "{address}" and has_address):
                if a_paired_info.getter("password") != None:
                    result_pair.append(a_paired_info.output())
                else:

                    a_paired_info.setter(info_pattern[text[i].replace(
                        '{', '').replace('}', '')], text[i+1])
                has_user = False
                has_address = False
            logger.debug(TAG + 'Adding attr to paired info: '+text[i]+" "+text[i+1])
            a_paired_info.setter(info_pattern[text[i].replace(
                '{', '').replace('}', '')], text[i+1])
            if text[i] == "{user}":
                has_user = True
            if text[i] == "{address}":
                has_address = True
    last_output = a_paired_info.output()

    if last_output["user"] != None or last_output["address"] != None:
        result_pair.append(last_output)

   # 移除没有地址的端口号
    for item in result_pair:
        if item["address"] is None and item["port"] is not None:
            item["port"] = None
    # 移除空项
    logger.debug(TAG + 'Paired info before filtering: '+str(result_pair))
    filtered_result_pair = []
    for item in result_pair:
        if ("user" in item and "address" in item and "password" in item) and \
            (item["user"] is not None or item["address"] is not None) and \
                item["password"] is not None:
            # Remove None attributes
            filtered_item = {key: value for key,
                             value in item.items() if value is not None}
            filtered_result_pair.append(filtered_item)




    result_pair = filtered_result_pair

    # 还原被替换的内容
    for item in result_pair:
        for key, value in item.items():
            if value in item_protection_dict:
                item[key] = item_protection_dict[value]
    return result_pair

#代码等文件的提取
def special_processing(text: str) -> dict:
    logger.info(TAG + 'Special processing for text')
    text, item_protection_dict1 = information_protection(text)
    global item_protection_dict
    item_protection_dict = item_protection_dict1
    text = fuzz_prevention(text)
    text = text.lower()
    text = convert_chinese_punctuation(text)
    text = text.replace("'", '"')
    # text = text.replace(":", "\"")
    # text = text.replace("=", "\"")

    text = text.split("\n")
    lines = []
    # 用于分割的符号
    split_symbols = [":", "=", '"']
    # remove outer "
    for line in text:
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        lines.append(line)
    text = lines
    lines = []
    # only  keep each eng_keywords_list between ""
    for line in text:
        new_line = ""
        if ":" in line:
            line = line.split(":")
        elif "=" in line:
            line = line.split("=")
        elif '"' in line:
            line = line.split('"')
        for i in range(len(line)):
            if i % 2 == 1:
                new_line += "{} ".format(line[i])
        lines.append(new_line)
    result_dict = {}
    logger.debug(TAG + 'Special processing for text: '+str(lines))
    # remove empty eng_keywords_list
    lines_temp = []
    for line in lines:
        line = line.strip()
        lines_temp.append(line)
    lines = lines_temp
    print(lines)
    words_list = []
    for line in lines:
        words_list += line.split(" ")
    for i in range(len(words_list) - 1):
        # print(words_list[i])
        logger.debug(TAG + 'Special processing for text: '+words_list[i]+" "+words_list[i+1])
        if any(key in words_list[i] for key in special_keywords_list) and not any(
            key in words_list[i + 1] for key in special_keywords_list
        ):
            logger.debug(TAG + 'Extract: '+words_list[i]+" "+words_list[i+1])
            if words_list[i+1] in item_protection_dict:
                result_dict[words_list[i]
                            ] = item_protection_dict[words_list[i+1]]
            else:
                result_dict[words_list[i]] = words_list[i + 1]
    #  # 还原被替换的内容
    # for item in result_dict:
    #     for key, value in item:
    #         if value in item_protection_dict:
    #             item[key] = item_protection_dict[value]
    logger.info(TAG + 'Special processing result: '+str(result_dict))
    return result_dict

# 配置文件的提取
def config_processing(text: str) -> dict:
    logger.info(TAG + 'Special processing for config')
    text, item_protection_dict1 = information_protection(text)
    global item_protection_dict
    item_protection_dict = item_protection_dict1
    text = fuzz_prevention(text)
    text = text.lower()
    text = convert_chinese_punctuation(text)
    text = text.replace("'", '"')
    # text = text.replace(":", "\"")
    # text = text.replace("=", "\"")

    text = text.split("\n")
    lines = []
    # 用于分割的符号
    split_symbols = [":", "=", '"']
    # remove outer "
    for line in text:
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        lines.append(line)
    text = lines
    # lines = []
    matches_result = {}
    # only  keep each eng_keywords_list between ""
    for line in text:
        line= line.lower()
        new_line = ""
        if "=\"" in line:
            # 使用正则表达式匹配属性名和属性值
            pattern = r'\s*name\s*=\s*"([^"]+)"\s*value\s*=\s*"([^"]+)"'
            matches = re.findall(pattern, line)
            # 打印匹配结果
            for match in matches:
                matches_result[match[0]] = match[1]
        elif "=" in line:
            # logger.debug(TAG + 'Dividing by =: '+line)
            parts = line.strip().split('=')
            if len(parts) == 2:
                key, value = parts
                key = key.strip()
                value = value.strip()
                if key and value:
                    matches_result[key] = value
        elif ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip()
            if key and value:
                matches_result[key] = value
        # for i in range(len(line)):
        #     if i % 2 == 1:
        #         new_line += "{} ".format(line[i])
        # lines.append(new_line)
    result_dict = {}
    logger.debug(TAG + 'Special processing for text: '+str(lines))
    # remove empty eng_keywords_list
    for key in matches_result:
        if any(key1 in key for key1 in special_keywords_list):
            result_dict[key] = matches_result[key]

    # 还原被替换的内容
    # new_result_dict = {}
    # for key, value in result_dict.items():
    #     logger.debug(TAG + 'Restoring: '+key+" "+value)
    #     for key1, value1 in item_protection_dict.items():
    #         logger.debug(TAG + 'Restoring: '+key1+" "+value1)
    #         if key1 in value:
    #             logger.debug(TAG + 'Restoring: '+key1+" "+value1)
    #             value = value.replace(key1, value1)
    #     new_result_dict[key] = value
        # 还原被替换的内容
    for key, value in result_dict.items():
        if value in item_protection_dict:
            result_dict[key] = item_protection_dict[value]
    logger.info(TAG + 'Special processing result: '+str(result_dict))
    return result_dict

# 使用模糊识别的方法提取信息，打关键词,抽取在之后做
def fuzz_extract(text: str) -> dict:
    original_text = text
    # logger.critical(TAG + 'Text class: {}'.format(guess_lexer(text).name))
    # 移除代码注释 // # 等
    # 已移除，影响地址的提取
    # text = re.sub(r'//.*', '', text)
    logger.debug(TAG + 'Text before IoC protection: '+text)
    if is_chinese_text(text):
        logger.info(TAG + 'This is a Chinese text.')
        text = chn_text_preprocessing(text)
    else:
        logger.info(TAG + 'This is an English text.')
        text = fuzz_prevention(text)
        logger.debug(TAG + 'Text after IoC protection: '+text)
        text = eng_text_preprocessing(text)
    text, item_protection_dict1 = information_protection(text)
    global item_protection_dict
    item_protection_dict = item_protection_dict1
    text = fuzz_mark(text)
    text = marked_text_refinement(text)
    paired_info = extract_paired_info(text)
    logger.info(TAG + 'Info extraction result: '+str(paired_info))
    return paired_info    
    logger.info(TAG + "fuzz_extract(): fuzz extract")
    result_dict = {}
    result=[]
    
    lines = text.split("\n")
    a_paired_info = paired_info_pattern()
    for line in lines:
        # # 若含有中文
        # if re.search(r'[\u4e00-\u9fa5]', line):
        #     continue
        # 若该行为IP地址
        if re.match(r'\b(?:\d{1,3}\.){3}\d{1,3}\b|localhost\b', line):
            if a_paired_info.getter("user") != None and a_paired_info.getter("password") != None:
                result.append(a_paired_info.output())
                a_paired_info = paired_info_pattern()
            logger.info(TAG + "fuzz_extract(): input is IP address")
            a_paired_info.set_address(line.strip())
        # 若该行仅含有字母和数字
        elif re.match(r'[a-zA-Z0-9]+', line):


            # 是否是电话号码
            if re.match(r'^1[3-9]\d{9}$', line):
                logger.info(TAG + "fuzz_extract(): input is phone number")
                a_paired_info.setter("phonenumber", line.strip())
            elif a_paired_info.getter("user") == None:
                a_paired_info.setter("user", line.strip())
            elif a_paired_info.getter("password") == None:
                a_paired_info.setter("password", line.strip())
            else:
                result.append(a_paired_info.output())
                a_paired_info = paired_info_pattern()
    if a_paired_info.getter("user") != None and a_paired_info.getter("password") != None:
        result.append(a_paired_info.output())

    # remove None attributes
    filtered_result = []
    for item in result:
        if ("user" in item and "password" in item) and \
            (item["user"] is not None or item["password"] is not None):
            # Remove None attributes
            filtered_item = {key: value for key,
                             value in item.items() if value is not None}
            filtered_result.append(filtered_item)

    logger.info(TAG + "fuzz_extract(): fuzz extract result: "+str(filtered_result))
    # logger.info(TAG + "fuzz_extract(): fuzz extract result: "+str(result))
    return filtered_result 

##########################入口函数###############################
# 从处理过后的字符串中提取成对信息
# 输入：处理过后的字符串
# 输出：成对信息列表
def begin_info_extraction(text: str) -> dict:
    original_text = text
    # logger.critical(TAG + 'Text class: {}'.format(guess_lexer(text).name))
    # 移除代码注释 // # 等
    # 已移除，影响地址的提取
    # text = re.sub(r'//.*', '', text)
    logger.debug(TAG + 'Text before IoC protection: '+text)
    if is_chinese_text(text):
        logger.info(TAG + 'This is a Chinese text.')
        text = chn_text_preprocessing(text)
    else:
        logger.info(TAG + 'This is an English text.')
        text = fuzz_prevention(text)
        logger.debug(TAG + 'Text after IoC protection: '+text)

        text = eng_text_preprocessing(text)
    text = marked_text_refinement(text)
    paired_info = extract_paired_info(text)
    logger.info(TAG + 'Info extraction result: '+str(paired_info))
    if paired_info == []:
        logger.warning(TAG + 'No paired info extracted!')
        paired_info = special_processing(original_text)
    # if paired_info == {}:
    #     logger.warning(TAG + 'No paired info extracted!')
    #     paired_info = fuzz_extract(original_text)
    return paired_info

# info_core入口
# flag: 0: text 1: table
SPECIAL = 1
def info_extraction(info,flag=0) -> dict:
    if flag == SPECIAL:
        return config_processing(info)
    if isinstance(info, str):
        # 若文本中不存在中文和英文关键词，进行模糊提取
        new_info = info.replace("\n", "")
        if not any(key in new_info for key in eng_keywords_list) and not any(key in new_info for key in chn_keywords_list):
            logger.info(TAG + "info_extraction(): fuzz extract")
            # 判断是否中文
            if is_chinese_text(info):
                return begin_info_extraction(info)
            return fuzz_extract(info)
        logger.info(TAG + "info_extraction(): input is string")
        return begin_info_extraction(info)
    elif isinstance(info, list):
        if is_png_text(info):
            text = ""
            for item in info[1:]:
                item_to_string = "\n".join(item)
                text = text+"\n"+item_to_string
            return begin_info_extraction(text)
        else:
            result_table = one_table_remove_irrelevant_columns(
                globalVar.get_sensitive_word(), info[1:])
            return result_table

if __name__ == '__main__':
    # file = open("test/.bash_history", "r")
    # file = open("test/windows/system.hiv.json", "r")
    argparse = argparse.ArgumentParser()
    argparse.add_argument("-f", "--file", required=True,
                          help="The file to be parsed")
    args = argparse.parse_args()
    with open(args.file, "r") as f:
        text = f.read()
    # begin_info_extraction(text)
    special_processing(text)
    exit(0)
