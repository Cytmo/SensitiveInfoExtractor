from config.info_core_config import (
    PLACEHOLDERS_CORRESPONDING_TYPE,
    ITEM_PROTECTION_DICT,
    ENG_KEYWORDS_LIST,
    ENG_REPLACEMENT_DICT,
    CHN_KEYWORDS_LIST,
    CHN_REPLACEMENT_DICT,
    INFO_PATTERN,
    REPLACED_KEYWORDS_LIST,
    SPECIAL_KEYWORDS_LIST,
    CODE_FILE_EXTENSION,
    CONFIG_FILE_EXTENSION,
    IMAGE_FILE_EXTENSION,
    SENSITIVE_INFO_PATTERN,
    ONE_WAY_CONNECTED_INFO,
    TWO_WAY_CONNECTED_INFO,
    KEYWORDS
)
import magic
from typing import Tuple
import re
from util.logUtils import LoggerSingleton
from util import globalVar
import argparse
from typing import Any, Tuple
# from toStringUtils.officeUtil import one_table_remove_irrelevant_columns
from informationEngine import password_guesser
# 添加日志模块
TAG = "informationEngine.info_core.py: "
logger = LoggerSingleton().get_logger()
########################## 全局变量###############################
# 导入全局变量

########################## 工具函数和类###############################


def should_fuzz(text)->bool:
    # text,temp = information_protection(text)
    # text = marked_text_refinement(text)
    new_info = text.replace("/n",'')

    if not any(key in new_info for key in KEYWORDS):
        return True
    else:
        return False


# 从结果类中还原占位符


def restore_placeholders(result_dict: dict) -> dict:
    logger.debug(
        TAG + "restore_placeholders(): ITEM_PROTECTION_DICT: "+str(ITEM_PROTECTION_DICT))
    logger.debug(TAG + "restore_placeholders(): result_dict: " +
                 str(result_dict))
    # if result_dict is a list
    if isinstance(result_dict, list):
        result = []
        for item in result_dict:
            result.append(restore_placeholders(item))
        return result_dict
    elif isinstance(result_dict, dict):
        for key, value in result_dict.items():
            for placeholder, replacement in ITEM_PROTECTION_DICT.items():
                # 使用正则匹配，防止替换到错误的位置
                value = re.sub(re.escape(placeholder), replacement, value)
            result_dict[key] = value
    # 文本标记API专用，不应当在其他地方使用
    elif isinstance(result_dict, str):
        logger.warning(
            TAG + "restore_placeholders(): result_dict is str, only for text mark api")
        for placeholder, replacement in ITEM_PROTECTION_DICT.items():
            # 使用正则匹配，防止替换到错误的位置
            result_dict = re.sub(re.escape(placeholder),
                                 replacement, result_dict)
    return result_dict

# 是否是有效信息


def is_valid_info(info: str, VALID_INFO_THRESHOLD=3) -> bool:
    alphanumeric_count = len(re.findall(r'\w', info))
    return alphanumeric_count >= VALID_INFO_THRESHOLD


def determine_file_type(file_name, info):
    logger.info(TAG + "determine_file_type(): file_name: "+str(file_name))
    logger.info(TAG + "determine_file_type(): info: "+str(info))
    # TODO 完善的文件类型判断
    if "carbon" in file_name:
        return "ocr"
    if file_name.endswith(tuple(CODE_FILE_EXTENSION)) or "python" in file_name:
        return "code"
    elif file_name.endswith(tuple(CONFIG_FILE_EXTENSION)):
        return "config"
    elif file_name.endswith(tuple(IMAGE_FILE_EXTENSION)):
        result = magic.from_buffer(info, mime=True)
        logger.info(
            TAG + "determine_file_type(): image's content's file type: "+str(result))
        switch = {
            "text/plain": "code",
            "application/json": "config",
            "application/xml": "config",
            "application/yaml": "config",
            "application/x-ini": "config",
            "application/toml": "config",
            "text/x-python": "code",
            "application/javascript": "code",
            "text/x-java-source": "code",
            "text/x-go": "code",
            # Add more MIME types for code and config as needed
        }
        return switch.get(result) if switch.get(result) else "unknown"
    return "unknown"

# 分割字符串并移除空项


def text_split(text: str) -> list:
    logger.info(TAG + "text_split(): text split input: "+' '.join(text.split()))
    # 使用 \n \t 空格 分割字符串
    text = re.split(r'\n|\t| ', text)
    text = [item for item in text if item != '' and item != ' ']
    logger.info (TAG + "text_split(): text split result: "+' '.join(text))
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
    result = password_guesser.predict_password([text])
    # [[True, 0.9999999922353121]]
    if result[0][0] == True and result[0][1] > 0.9:
        return True
    else:
        return False

# 转换OCR识别中的错误符号


def fix_ocr(text):
    logger.info(TAG + "fix_ocr(): fix_ocr input: "+' '.join(text.split()))
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
    logger.info(TAG + "fix_ocr(): fix_ocr result: "+' '.join(text.split()))
    return text

# 判断是否是被保护的信息项


def is_protected_item(item: str) -> bool:
    pattern = r'\?\d\?'
    return bool(re.search(pattern, item))


def is_a_mark(item: str) -> bool:
    item = item.strip()
    pattern = r'\{.*\}'
    return bool(re.search(pattern, item))


# TODO:url和端口号成组且支持一个用户对应多个url
# 从处理过后的字符串中提取成对信息
class paired_info_pattern():
    def __init__(self):
        self.data = {}
        self.result_set = []
        self.last_output = {}
        self.last_keyword = None
        # add three neccessary attributes
        self.data["user"] = None
        self.data["password"] = None
        self.data["address"] = None
        self.data["port"] = None
        self.data["phonenumber"] = None

        self.check_header = {"user": False, "address": False,'AWSaccesskey':False,'AWSsecretkey':False}

    def reset_data(self):
        # 后续可以仿照下面改成递推式
        self.data = {}
        self.data["user"] = None
        self.data["password"] = None
        self.data["address"] = None
        self.data["port"] = None
        self.data["phonenumber"] = None
        self.check_header = {"user": False, "address": False,'AWSaccesskey':False,'AWSsecretkey':False}
    def reset_headers(self):
        self.check_header.update({k: False for k, v in self.data.items()})

    # 判断是否一个对象存在关键对象
    def check_header_complete(self):
        print(self.check_header)
        return not all(value is False for value in self.check_header.values())

    def check_data_headers(self, data):
        for k, v in self.check_header.items():
            if data == "{"+k+"}" and v:
                return True
        return False

    def set_data_headers(self, data):
        for k in self.check_header.keys():
            data = data.replace("{","").replace("}","")
            if data == k:
                self.check_header[k] = True

    def remake_data(self):
        # 依赖整合
        for k, v in ONE_WAY_CONNECTED_INFO.items():
            if self.data.get(v) == None and self.data.get(k) != None:
                self.data[k] = None

        # 对称整合
        for k, v in TWO_WAY_CONNECTED_INFO.items():
            if self.data.get(v) == None and self.data.get(k) != None:
                self.data[k] = None
            if self.data.get(v) != None and self.data.get(k) == None:
                self.data[v] = None

    def setter(self, name: str, value: Any) -> None:
        # if name in self.data:
        #     self.data[name] = value
        #     return True
        # return False

        # if name in attr_switch:
        #     # print("Setting "+str(name)+" " +str( value))
        #     return attr_switch[name](value)
        # else:
        #     return False
        # TODO
        print(self.data)
        self.data[name] = value
        print(self.data)

        return True
    

    def slice_word_check(self,slice_word)->bool:
        if slice_word != self.last_keyword:
            if self.last_keyword != None:
                logger.info(TAG+"Paired_info(): different slice word detected, which are " +slice_word+self.last_keyword)
            else:
                logger.info(TAG+"Paired_info(): different slice word detected, which are " +slice_word+ " None")
 
            self.last_output = self.data
            self.reset_data()
            return False
        else:

            if self.last_output != {} and self.check_result_validity():
                # Re slice output
                self.result_regroup()
            elif self.last_output != {}:
                data_backup = self.data
                self.data = self.last_output
                self.add_to_result_set()
                self.data = data_backup
            self.last_output = {}
        return True

    def check_result_validity(self):
        result = {}
        data_tmp = self.data.copy()
        # 依赖整合
        for k, v in ONE_WAY_CONNECTED_INFO.items():
            if data_tmp.get(v) == None and data_tmp.get(k) != None:
                data_tmp[k] = None

        # 对称整合
        for k, v in TWO_WAY_CONNECTED_INFO.items():
            if data_tmp.get(v) == None and data_tmp.get(k) != None:
                data_tmp[k] = None
            if data_tmp.get(v) != None and data_tmp.get(k) == None:
                data_tmp[v] = None
        for key in data_tmp:
            if data_tmp[key] != None:
                result[key] = data_tmp[key]
        if len(result) < 2:
            return False
        return True

    def result_regroup(self):
        sliced_result_1 = {}
        sliced_result_2 = {}
        items_need_pop = []
        logger.info(TAG+"Paired_info():result_regroup(): data is " + str(self.data))
        logger.info(TAG+"Paired_info():result_regroup(): last_output is " + str(self.last_output))

        for key,value in self.data.items():
            if value != None and self.last_output.get(key) != None:
                sliced_result_1[key] = self.last_output.get(key)
                items_need_pop.append(key)
        for key in items_need_pop:
            self.last_output.pop(key)

        sliced_result_2 = self.last_output
        data_backup = self.data

        logger.info(TAG+"Paired_info():result_regroup(): data backup is " + str(data_backup))
        logger.info(TAG+"Paired_info():result_regroup(): sliced_result_1 is " + str(sliced_result_1))
        logger.info(TAG+"Paired_info():result_regroup(): sliced_result_2 is " + str(sliced_result_2))

        self.data = sliced_result_1
        self.add_to_result_set()
        self.data = sliced_result_2
        self.add_to_result_set()
        self.data = data_backup

    def output(self):
        if self.last_output != {}:
            self.data=self.last_output
            self.add_to_result_set()
        return self.result_set

    def add_to_result_set(self):
        result = {}
        for key in self.data:
            if self.data[key] != None:
                result[key] = self.data[key]
        if len(result) < 2:
            return {}
        # check if result have all needed attributes
        # TODO() 可能要修改
        # for key in ["user", "password", "address", "port", "phonenumber"]:
        #     if key not in result:
        #         result[key] = None
        self.reset_data()
    
        self.result_set.append(result)

    def getter(self, name: str):
        if name in self.data:
            return self.data[name]
        else:
            return None
    

    def if_same_attr(self, name: str, value: Any) -> bool:
        # check if name is in self.data
        if self.data.get(name) == None:
            return False
        return self.data.get(name) == value

    def is_None(self):
        # check if all attributes are None
        for key in self.data:
            if self.data[key] != None:
                return False
        return True


########################## 预处理函数###############################
# 提取易混淆的内容并进行标记 保存email地址 url ip地址等内容，防止被替换
placeholders = {}  # This dictionary will store placeholders and their corresponding content


def information_protection(text: str) -> Tuple[str, dict]:
    global placeholders
    placeholders = {}
    # 每次调用函数时，清空字典，防止重复
    global ITEM_PROTECTION_DICT
    ITEM_PROTECTION_DICT = {}
    placeholders_counter = 1  # Counter for generating placeholders
    global PLACEHOLDERS_CORRESPONDING_TYPE
    PLACEHOLDERS_CORRESPONDING_TYPE = {}
    # Define a list of dictionaries with patterns and their corresponding types
    patterns = [
        {'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
            'type': 'email'},
        # {'pattern': r'jdbc:mysql://[a-zA-Z0-9:/._-]+', 'type': 'jdbc_url'},
        {'pattern': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 'type': 'url'},
        {'pattern': r'(?:\d{1,3}\.){3}\d{1,3}|localhost', 'type': 'ip'},
        {'pattern': r'1[3-9]\d{9}', 'type': 'phonenumber'},
        # {'pattern': r'\b(0|6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|[0-5]?[0-9]{1,4})\b', 'type': 'port'}
    ]
    match_result = {}
    for pattern_info in patterns:
        pattern = pattern_info['pattern']
        matches = re.finditer(pattern, text, flags=re.IGNORECASE)
        for match in matches:
            item = match.group()
            placeholder = f'?{placeholders_counter}?'
            placeholders[placeholder] = item
            # if placeholder not in PLACEHOLDERS_CORRESPONDING_TYPE:
            #     PLACEHOLDERS_CORRESPONDING_TYPE[placeholder] = []
            # PLACEHOLDERS_CORRESPONDING_TYPE[placeholder].append(pattern_info['type'])  # Store the corresponding type
            # Replace only the first occurrence
            if item not in match_result:
                match_result[item] = []
            match_result[item].append(pattern_info['type'])
            text = text.replace(item, placeholder, 1)
            placeholders_counter += 1
    sensitive_info_pattern_match_result = {}
    for pattern in SENSITIVE_INFO_PATTERN['patterns']:

        name = pattern['pattern']['name']
        regex = pattern['pattern']['regex']
        confidence = pattern['pattern']['confidence']

        # 进行正则表达式匹配
        matches = re.finditer(regex, text)

        for match in matches:
            logger.info(
                TAG + "information_protection(): Matched pattern: {}".format(name))
            logger.info(
                TAG + "information_protection(): Confidence: {}".format(confidence))
            logger.info(
                TAG + "information_protection(): Matched text: {}\n".format(match.group(0)))
            # print(f"Matched pattern: {name}")
            # print(f"Confidence: {confidence}")
            # print(f"Matched text: {match.group(0)}\n")
            # if match.group(0) not in match_result:
            sensitive_info_pattern_match_result[match.group(0)] = []
            sensitive_info_pattern_match_result[match.group(0)].append(name)
    # 记录计数器位置，防止种类从0开始，取到不存在的键值
    for key in sensitive_info_pattern_match_result:
        placeholder = f'?{placeholders_counter}?'
        placeholders[placeholder] = key
        text = text.replace(key, placeholder, 1)
        placeholders_counter += 1
    match_result.update(sensitive_info_pattern_match_result)
    for key in placeholders:
        if key not in PLACEHOLDERS_CORRESPONDING_TYPE:
            PLACEHOLDERS_CORRESPONDING_TYPE[key] = []
        # print("place type:"+str(PLACEHOLDERS_CORRESPONDING_TYPE[key]))
        # print("pl    type:"+str(placeholders[key]))
        # print("match type:"+str(match_result[key]))
        # remove space in type to append
        PLACEHOLDERS_CORRESPONDING_TYPE[key].append(
            match_result[placeholders[key]])
    # 遍历字典，去除值中的空格
    for key, value in PLACEHOLDERS_CORRESPONDING_TYPE.items():
        # 使用列表解析去除值中的空格
        PLACEHOLDERS_CORRESPONDING_TYPE[key] = [
            [item[0].replace(' ', '')] for item in value]
    logger.info(TAG + "information_protection(): placeholder extract{}".format(
        str(PLACEHOLDERS_CORRESPONDING_TYPE)))
    logger.info(
        TAG + "information_protection(): placeholders{}".format(str(placeholders)))

    return text, placeholders

# 防止文件名等并识别为关键字，如user.txt


def prevent_eng_words_interference(text: str) -> str:
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


def eng_text_preprocessing(text: str, FUZZ_MARK=False) -> str:
    # text, item_protection_dict1 = information_protection(text)
    # global ITEM_PROTECTION_DICT
    # ITEM_PROTECTION_DICT = item_protection_dict1
    # 构建正则表达式，匹配英文字符、数字以及指定中文关键词
    pattern = f"(?:{'|'.join(ENG_KEYWORDS_LIST)}|[a-zA-Z0-9,.;@?!\\-\"'()])+"
    # 使用正则表达式进行匹配和替换
    cleaned_text = re.findall(pattern, text)
    # 将匹配到的内容重新组合成字符串
    cleaned_text = ' '.join(cleaned_text)
    # cleaned_text = text
    # 替换中文关键词
    if not FUZZ_MARK:
        for keyword in ENG_KEYWORDS_LIST:
            if keyword in ENG_REPLACEMENT_DICT:
                cleaned_text = cleaned_text.replace(
                    keyword, ' {'+ENG_REPLACEMENT_DICT[keyword]+'} ')
    # 移除空行
    cleaned_text = '\n'.join(
        [line for line in cleaned_text.splitlines() if line.strip()])
    cleaned_text = cleaned_text.replace("{ {", "{").replace("} }", "}")
    logger.debug(TAG + "eng_text_preprocessing(): Cleaned text: "+cleaned_text)
    return cleaned_text

# 预处理文本，仅保留英文字符和数字，以及中文关键词（学号，用户名，密码等）


def chn_text_preprocessing(text: str, FUZZ_MARK=False) -> str:
    # text, item_protection_dict1 = information_protection(text)
    # global ITEM_PROTECTION_DICT
    # ITEM_PROTECTION_DICT = item_protection_dict1
    # 构建正则表达式，匹配英文字符、数字以及指定中文关键词
    pattern = f"(?:{'|'.join(CHN_KEYWORDS_LIST)}|[a-zA-Z0-9,.;@?!\\-\"'()])+"

    # 使用正则表达式进行匹配和替换
    cleaned_text = re.findall(pattern, text, re.IGNORECASE)

    # 将匹配到的内容重新组合成字符串
    cleaned_text = ' '.join(cleaned_text)
    # 替换中文关键词
    if not FUZZ_MARK:
        for keyword in CHN_KEYWORDS_LIST:
            if keyword in CHN_REPLACEMENT_DICT:
                cleaned_text = cleaned_text.replace(
                    keyword, ' {'+CHN_REPLACEMENT_DICT[keyword]+'} ')
    # 移除空行
    cleaned_text = '\n'.join(
        [line for line in cleaned_text.splitlines() if line.strip()])
    logger.debug(TAG + "chn_text_preprocessing(): Cleaned text: "+cleaned_text)
    return cleaned_text

# 模糊标记文本中的关键词


def fuzz_mark(text: str) -> str:
    text = text_split(text)
    tagged_text = explicit_fuzz_mark(text)
    tagged_text = implicit_fuzz_mark(tagged_text)
    return " ".join(tagged_text)

# 标记可明显识别的关键词 如url port等


def explicit_fuzz_mark(text: list) -> list:
    logger.info(TAG + "placeholder_extract(): placeholder extract{}".format(
        str(PLACEHOLDERS_CORRESPONDING_TYPE)))
    logger.info(TAG + "fuzz_mark(): explicit_fuzz_mark input: {}".format(text))
    tagged_text = []
    logger.info(TAG + "explicit_fuzz mark input list: {}".format(text))
    for i in range(len(text)):
        if text[i] in PLACEHOLDERS_CORRESPONDING_TYPE:
            type_info = PLACEHOLDERS_CORRESPONDING_TYPE[text[i]][0]
            switch = {
                'email': '{user}',
                'port': '{port}',
                'url': '{address}',
                'ip': '{address}',
                'phonenumber': '{phonenumber}'
            }
            # type info looks like ['email']
            if type_info and type_info[0] in switch:
                tagged_text.append(switch[type_info[0]])
            tagged_text.append(text[i])
        else:
            tagged_text.append(text[i])
    logger.info(
        TAG + "fuzz_mark(): explicit_fuzz_mark result: {}".format(' '.join(tagged_text)))
    return tagged_text

# 标记隐式项 如用户名 密码等


def implicit_fuzz_mark(text: list) -> list:
    logger.info(TAG + "implicit_fuzz_mark(): input list: {}".format(text))
    tagged_text = []
    for i in range(len(text)):
        if is_protected_item(text[i]):
            tagged_text.append(text[i])
        elif text[i] in REPLACED_KEYWORDS_LIST:
            tagged_text.append(text[i])
        else:
            logger.info(
                TAG + "implicit_fuzz_mark(): password_classifier input: {}".format(text[i]))
            password_classifier_result = password_classifier(text[i])
            logger.info(
                TAG + "implicit_fuzz_mark(): password_classifier result: {}".format(password_classifier_result))
            if password_classifier_result:
                tagged_text.append('{password}')
            else:
                tagged_text.append('{user}')
            tagged_text.append(text[i])
    logger.info(
        TAG + "implicit_fuzz_mark(): implicit_fuzz_mark result: {}".format(' '.join(tagged_text)))
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
    # 根据 PLACEHOLDERS_CORRESPONDING_TYPE 全局变量，对文本进行调整
    for key in PLACEHOLDERS_CORRESPONDING_TYPE:
        if PLACEHOLDERS_CORRESPONDING_TYPE[key][0][0] not in INFO_PATTERN:
            replaced_content = " {" + PLACEHOLDERS_CORRESPONDING_TYPE[key][0][0] + "} "+ key + " "
            logger.debug(TAG + 'marked_text_refinement(): Replacing {} with {}'.format(key, replaced_content))
            logger.debug(TAG + 'marked_text_refinement(): Text before replacement: '+' '.join(text.split()))
            text = text.replace(key, replaced_content)
            logger.debug(TAG + 'marked_text_refinement(): Text after replacement: '+' '.join(text.split()))


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
                    logger.debug(
                        TAG + 'Swapping {} with {}'.format(text[i], text[j]))
                    text[i+1], text[j] = text[j], text[i+1]
                    break
    logger.debug(TAG + 'Text after position adjustment: '+' '.join(text))

    # 移除连续出现的，其后无有效关键词的指示词
    for i in range(len(text)-1):
        if is_a_mark(text[i]) and is_a_mark(text[i+1]):
            text[i] = ""

    # 移除指示词和其后的关键词之外的内容
    new_text = []
    for i in range(len(text)-1):
        if is_a_mark(text[i]) and not is_a_mark(text[i+1]):
            new_text.append(text[i])
            new_text.append(text[i+1])
    text = new_text

    logger.debug(TAG + 'Text after removing invalid keywords: '+' '.join(text))
    # 移除关键词无效的指示词，如 地址后不是有效地址
    for i in range(len(text)-1):
        if is_a_mark(text[i]) and not is_a_mark(text[i+1]):
            if text[i] == "{address}" and not is_valid_address(text[i+1]):
                logger.debug(
                    TAG + 'marked_text_refinement(): Removing invalid address: '+str(text[i+1]))
                text[i] = ""
                text[i+1] = ""
            if text[i] == "{port}" and not is_valid_port(text[i+1]):
                logger.debug(
                    TAG + 'marked_text_refinement(): Removing invalid port: '+str(text[i+1]))
                text[i] = ""
                text[i+1] = ""
            if text[i] == "{user}" and not is_valid_user(text[i+1]):
                logger.debug(
                    TAG + 'marked_text_refinement(): Removing invalid user: '+str(text[i+1]))
                text[i] = ""
                text[i+1] = ""
            if text[i] == "{password}" and not is_valid_password(text[i+1]):
                logger.debug(
                    TAG + 'marked_text_refinement(): Removing invalid password: '+str(text[i+1]))
                text[i] = ""
                text[i+1] = ""

    # 移除空项
    text = [item for item in text if item != ""]
    text = " ".join(text)





    logger.debug(TAG + 'Text after repeated keywords adjustment: '+' '.join(text.split()))
    return text

########################## 信息提取函数###############################
# 从预处理过后的文本中提取成对信息


def extract_paired_info(text):
    result_pair = []
    a_paired_info = paired_info_pattern()
    text = text.split()

    for i in range(len(text)-1):
        text_i_striped = text[i].strip()
        # 密码不会最先出现
        if text_i_striped == "{password}" and a_paired_info.is_None():
            continue
        # TODO change to is a mark
        if is_a_mark(text_i_striped) and not is_a_mark(text[i+1]):
            logger.info(TAG+"extract_paired_info(): current paired info data"+str(a_paired_info.data))

            if a_paired_info.check_data_headers(text_i_striped) and a_paired_info.check_result_validity():
                # logger.info(TAG+"extract_paired_info(): current paired info data"+str(a_paired_info.data))
                a_paired_info.remake_data()
                # if a_paired_info.getter("password") != None:
                if a_paired_info.slice_word_check(text_i_striped):
                    a_paired_info.add_to_result_set()
                a_paired_info.last_keyword = text_i_striped
                # else:
                #     if INFO_PATTERN.get(text_i_striped)!=None:
                #         a_paired_info.setter(INFO_PATTERN[text_i_striped.replace(
                #         '{', '').replace('}', '')], text[i+1])
                #     else:
                #         a_paired_info.setter(text_i_striped.replace(
                # '{', '').replace('}', ''),text[i+1])
            logger.debug(TAG + 'Adding attr to paired info: ' +
                         text_i_striped+" "+text[i+1])
            # logger.debug(TAG + 'extract_paired_info(): text_i_striped: ' + text_i_striped.replace("{","").replace("","}"))
            # logger.debug(TAG + 'extract_paired_info(): INFO_PATTERN: ' + str(INFO_PATTERN))
            # logger.debug(TAG + 'extract_paired_info():' +str(text_i_striped.replace("{","").replace("","}") in INFO_PATTERN))
            if text_i_striped.replace("{","").replace("}","") in INFO_PATTERN:
                logger.debug(TAG + 'extract_paired_info(): adding attr to paired info: ' +
                         INFO_PATTERN[text_i_striped.replace(
                '{', '').replace('}', '')]+" "+text[i+1])
            # if any( value in text_i_striped for value in INFO_PATTERN):
                a_paired_info.setter(INFO_PATTERN[text_i_striped.replace(
                '{', '').replace('}', '')], text[i+1])
                print(1)
                print(text_i_striped.replace('{', '').replace('}', ''))
                print(text[i+1])
                a_paired_info.set_data_headers(INFO_PATTERN[text_i_striped.replace('{', '').replace('}', '')])
            else:
                print(2)

                a_paired_info.setter(text_i_striped.replace(
                '{', '').replace('}', ''),text[i+1])
                a_paired_info.set_data_headers(text_i_striped)
    print(a_paired_info.data)
    if a_paired_info.check_header_complete():
        print(a_paired_info.data)
        a_paired_info.last_keyword = None
        a_paired_info.remake_data()
        print(a_paired_info.data)
        a_paired_info.add_to_result_set()
        print(a_paired_info.data)
    for item in a_paired_info.output():
        result_pair.append(item)
    # 移除空项
    logger.debug(TAG + 'Paired info before filtering: '+str(result_pair))
    # filtered_result_pair = []

    # 不太清楚为啥要有这个判断，不敢动，和上文的output中补充联动
    # for item in result_pair:
    #     if ("user" in item and "address" in item and "password" in item) and \
    #         (item["user"] is not None or item["address"] is not None) and \
    #             item["password"] is not None:
    #         # Remove None attributes
    #         filtered_item = {key: value for key,
    #                          value in item.items() if value is not None}
    #         filtered_result_pair.append(filtered_item)
    # result_pair = filtered_result_pair

    logger.debug(
        TAG + 'paired_info_extract(): beginning to restore replaced content')
    logger.debug(
        TAG + 'paired_info_extract(): ITEM_PROTECTION_DICT: '+str(ITEM_PROTECTION_DICT))
    # 还原被替换的内容
    result_pair = restore_placeholders(result_pair)
    for item in result_pair:
        if item == {}:
            result_pair.remove(item)
    return result_pair


def rule_based_info_extract(text: str) -> dict:
    logger.info(
        TAG + 'rule_based_info_extract(): Rule based processing for text')
    text, item_protection_dict1 = information_protection(text)
    global ITEM_PROTECTION_DICT
    ITEM_PROTECTION_DICT = item_protection_dict1
    result_dict = {}
    for key in ITEM_PROTECTION_DICT:
        item_type = PLACEHOLDERS_CORRESPONDING_TYPE[key][0][0]
        item_content = ITEM_PROTECTION_DICT[key]
        if item_type not in INFO_PATTERN:
            result_dict[item_type] = item_content
    for value in result_dict.values():
        value = "Rule based: "+value

    logger.info(
        TAG + 'rule_based_info_extract(): Rule based processing result: '+str(result_dict))
    # logger.info(TAG + 'rule_based_info_extract(): using paired_info_class to check valid info')
    # a_paired_info = paired_info_pattern()
    # for key, value in result_dict.items():
    #     if key in a_paired_info.data:
    #         a_paired_info.setter(key, value)
    # a_paired_info.remake_data()
    # result_dict = a_paired_info.output()
    # logger.info(TAG + 'rule_based_info_extract(): Rule based processing result after paired_info_class: '+str(result_dict))
    return result_dict

# 代码等文件的提取


def code_info_extract(text: str) -> dict:
    original_text = text
    logger.info(TAG + 'code_info_extract(): Code processing for text '+' '.join(text.split()))
    text, item_protection_dict1 = information_protection(text)
    global ITEM_PROTECTION_DICT
    ITEM_PROTECTION_DICT = item_protection_dict1
    text = prevent_eng_words_interference(text)
    text = text.lower()
    text = text.replace("'", '"')
    # remove outer "
    lines = text.split("\n")
    new_lines = []

    for line in lines:
        # 去除行首和行尾的双引号
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        new_lines.append(line)
    XML_FILE = False
    for line in new_lines:
        if "name" in line and "value" in line:
            XML_FILE = True
    text = '\n'.join(new_lines)
    logger.debug(TAG + 'code_info_extract(): text after removing outer " start:@@@ '+' '.join(text.split())+' end:@@@')
    # 仅保留形如 xx = "xx"的行 和含有两个字符串的行
    if XML_FILE:
        pass
    else:

        combined_regex = r'(?:.*?=\s*["\'][^"\']*["\']|["\'].*["\']\s+["\'].*["\'])'

        matches = re.finditer(combined_regex, text, re.MULTILINE)

        replacement_dict = {}

        for match in matches:
            matched_string = match.group(0)
            replacement = f"REPLACE{len(replacement_dict)}"
            replacement_dict[replacement] = matched_string
            text = text.replace(matched_string, replacement)

        # Output the restored text
        for key, value in replacement_dict.items():
            text = text.replace(key, value)

    logger.debug(TAG + 'code_info_extract(): text after removing lines without string: '+' '.join(text.split()))
    text = text.split("\n")
    lines = []
    for line in text:
        line = line.strip()
        line = line.replace("\"", " ")
        # line=line.replace("=", " ")
        lines.append(line)
    logger.info(
        TAG + 'code_info_extract(): text after removing outer " and only keeping string: '+str(lines))
    text = lines
    lines = []
    for line in text:
        line_sliced = []
        if "name" in line and "value" in line:
            logger.debug(TAG + 'Dividing by name and value: '+line)
            # 使用正则表达式匹配属性名和属性值
            pattern = r'\s*name\s*=\s*([^\s]+)\s*value\s*=\s*([^\s]+)'
            matches = re.findall(pattern, line)
            # 打印匹配结果
            for match in matches:
                line_sliced = [match[0], match[1]]
        elif "=" in line:
            line_sliced = line.strip().split("=")
        else:
            line_sliced = line.split(" ")
            # remove empty item in line_sliced
            line_sliced = [item for item in line_sliced if item != ""]
        if len(line_sliced) == 2:
            lines.append("{{{}}} {}".format(line_sliced[0], line_sliced[1]))

    logger.info(
        TAG + 'code_info_extract(): text after slicing and marking '+str(lines))
    # text = lines
    result_dict = {}
    logger.debug(TAG + 'Special processing for text: '+str(lines))
    # remove empty eng_keywords_list
    lines_temp = []
    for line in lines:
        line = line.strip()
        lines_temp.append(line)
    lines = lines_temp
    words_list = []
    for line in lines:
        words_list += line.split(" ")
    for i in range(len(words_list) - 1):
        # print(words_list[i])
        logger.debug(TAG + 'Code processing for text: ' +
                     words_list[i]+" "+words_list[i+1])
        if any(key in words_list[i] for key in SPECIAL_KEYWORDS_LIST) and not any(
            key in words_list[i + 1] for key in SPECIAL_KEYWORDS_LIST
        ):
            logger.debug(TAG + 'Extract: '+words_list[i]+" "+words_list[i+1])
            if words_list[i+1] in ITEM_PROTECTION_DICT:
                result_dict[words_list[i]
                            ] = ITEM_PROTECTION_DICT[words_list[i+1]]
            else:
                result_dict[words_list[i]] = words_list[i + 1]

    result_dict = restore_placeholders(result_dict)
    logger.info(TAG + 'Code processing result: '+str(result_dict))
    # TODO this section is just for test, remove it later
    rule_based_info_extract_result = rule_based_info_extract(original_text)
    result_dict.update(rule_based_info_extract_result)

    result_dict_temp = {}
    logger.info(TAG + 'code_info_extract(): remove invalid info')
    for key, value in result_dict.items():
        if is_valid_info(value):
            result_dict_temp[key] = value
    result_dict = result_dict_temp
    cleaned_dict = {}  # Create a new dictionary to store the cleaned key-value pairs

    for key, value in result_dict.items():
        # Remove /, space, :, {, and } from key and value
        cleaned_key = key.replace('/', '').replace(' ', '').\
            replace(':', '').replace('{', '').replace(
                '}', '').replace('\"', '').replace('\'', '')
        # cleaned_value = value.replace('/', '').replace(' ', '').\
        #     replace(':', '').replace('{', '').replace('}', '').replace('\"', '').replace('\'', '')

        # Add the cleaned key-value pair to the new dictionary
        cleaned_dict[cleaned_key] = value
    result_dict = cleaned_dict


    return re_pair_info_extract(result_dict)
# 配置文件的提取

def re_pair_info_extract(result_dict: dict) -> dict:
    text = ""
    logger.debug(TAG + "code_info_extract(): raw_result_dict is "+ str(result_dict))
    if type(result_dict) == dict and result_dict != {}:
        for key, value in result_dict.items():  # Use items() to iterate through key-value pairs
            text += "{"+key + "} "+value+"\n"
        extract_paired_info_result = extract_paired_info(text)
        return extract_paired_info_result
    elif type(result_dict) == list and result_dict != []:
        for item in result_dict:
            for key, value in item.items():
                text += "{"+key + "} "+value+"\n"
        extract_paired_info_result = extract_paired_info(text)
        return extract_paired_info_result
    return {}

def config_info_extract(text: str) -> dict:
    return code_info_extract(text)


def ocr_code_processing(text: str) -> dict:
    logger.info(TAG + 'ocr_code_processing(): processing for text: '+' '.join(text.split()))
    text, item_protection_dict1 = information_protection(text)
    global ITEM_PROTECTION_DICT
    ITEM_PROTECTION_DICT = item_protection_dict1
    # text = fuzz_prevention(text)
    text = text.lower()
    text = fix_ocr(text)
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

    logger.debug(TAG + 'Special processing for text: '+str(lines))
    # remove empty eng_keywords_list
    lines_temp = []
    for line in lines:
        line = line.strip()
        lines_temp.append(line)
    lines = lines_temp
    words_list = []
    for line in lines:
        words_list += line.split(" ")
    processed_words_list = []
    result_dict = {}
    for i in range(len(words_list) - 1):
        # print(words_list[i])
        if words_list[i] in processed_words_list:
            continue
        logger.debug(TAG + 'Special processing for text: ' +
                     words_list[i]+" "+words_list[i+1])
        if any(key in words_list[i] for key in SPECIAL_KEYWORDS_LIST) and not any(
            key in words_list[i + 1] for key in SPECIAL_KEYWORDS_LIST
        ):
            logger.debug(TAG + 'Extract: '+words_list[i]+" "+words_list[i+1])

            result_dict[words_list[i]] = words_list[i + 1]
            processed_words_list.append(words_list[i])
            processed_words_list.append(words_list[i+1])
    result_dict = restore_placeholders(result_dict)
    logger.info(TAG + 'Special processing result: '+str(result_dict))
    return result_dict


########################## 入口函数###############################
# 从处理过后的纯文本字符串中提取成对信息
# 输入：处理过后的字符串
# 输出：成对信息列表
# RETURN_TYPE_DICT 为True时返回字典
# FUZZ_MARK 为True时进行模糊标记
# RETURN_MARKED_TEXT 为True时返回标记后的文本
def plain_text_info_extraction(text: str, RETURN_TYPE_DICT=False, FUZZ_MARK=False, RETURN_MARKED_TEXT=False) -> list:
    original_text = text
    global ITEM_PROTECTION_DICT
    logger.debug(
        TAG + 'plain_text_info_extraction():ITEM_PROTECTION_DICT before fuzz extract: '+str(ITEM_PROTECTION_DICT))
    logger.debug(
        TAG + 'plain_text_info_extraction(): Text before sensitive info protection: '+text)
    text, item_protection_dict1 = information_protection(text)
    logger.debug(
        TAG + 'plain_text_info_extraction():ITEM_PROTECTION_DICT after fuzz extract: '+str(ITEM_PROTECTION_DICT))
    new_info=text.replace("\n",'')
    # if any("{"+key+"}" in new_info for key in KEYWORDS):
    #     FUZZ_MARK = False
    if is_chinese_text(text):
        logger.info(TAG + 'This is a Chinese text.')
        text = chn_text_preprocessing(text, FUZZ_MARK)
    else:
        logger.info(TAG + 'This is an English text.')
        text = prevent_eng_words_interference(text)
        logger.debug(TAG + 'Text after fuzz protection: '+text)
        text = eng_text_preprocessing(text, FUZZ_MARK)
    if ITEM_PROTECTION_DICT == {}:
        ITEM_PROTECTION_DICT = item_protection_dict1
    if FUZZ_MARK:
        text = fuzz_mark(text)
    if RETURN_MARKED_TEXT:
        # 还原保护时被替换的内容
        text = restore_placeholders(text)
        return text
    text = marked_text_refinement(text)
    # TODO:传回对应类别的字典
    if RETURN_TYPE_DICT:
        text = text.split()
        result_dict = {}
        for i in range(len(text)-1):
            if text[i] in REPLACED_KEYWORDS_LIST and text[i+1] not in REPLACED_KEYWORDS_LIST:
                result_dict[text[i]] = text[i+1]
                i = i+1
        return result_dict
    paired_info = extract_paired_info(text)
    logger.info(TAG + 'Info extraction result: '+str(paired_info))
    return paired_info


# info_core入口 根据输入内容的类型（表格，文本）进行不同的处理
# flag: 0: text 1: table
IS_CONFIG_FILE = 1


def begin_info_extraction(info, flag=0, file_path='') -> dict:
    switch = {
        'code': code_info_extract,
        'config': config_info_extract,
        'ocr': ocr_code_processing
    }
    logger.info(TAG + "begin_info_extraction(): input is {}".format(info))
    if flag == IS_CONFIG_FILE:
        return config_info_extract(info)
    # 纯文本
    if isinstance(info, str):
        # 若文本中不存在中文和英文关键词，进行模糊提取
        new_info = info.replace("\n", "")
        file_type = determine_file_type(file_path, info)
        logger.info(
            TAG + "begin_info_extraction(): input type is {}".format(file_type))
        if file_type in switch:
            logger.info(TAG + "begin_info_extraction(): input is code/config")
            # result = code_info_extract(info)
            result = switch[file_type](info)
            return result_manager(result,info,file_path,IS_CODE_OR_CONFIG=True)
        else:
            # TODO
            if False:
            # if should_fuzz(new_info):
                logger.info(TAG + "info_extraction(): fuzz extract")
                # 判断是否中文
                if is_chinese_text(info):
                    logger.info(TAG + 'This is a Chinese text.')
                    result = plain_text_info_extraction(info)
                    logger.info(TAG + "info_extraction(): plain text info extract result: {}".format(str(result)))
                    
                result = plain_text_info_extraction(info,FUZZ_MARK=True)
            else:
                logger.info(TAG + "begin_info_extraction(): unknown input")
                result = plain_text_info_extraction(info)
                logger.info(
                    TAG + "begin_info_extraction(): fuzz_extract result: {}".format(str(result)))
        return result_manager(result, info, file_path)
    # 表格
    elif isinstance(info, list):
        logger.info(TAG + "info_extraction(): input is ordinary picture")
        text = ""
        for item in info[1:]:
            item_to_string = "\n".join(item)
            text = text+"\n"+item_to_string
        text = fix_ocr(text)
        result = begin_info_extraction(text, file_path=file_path)
        return result_manager(result, text, file_path)


def result_filter(result,VALID_RESULT_THRESHOLD=2) -> dict:
    if result == [] or result == {}:
        logger.warning(TAG + 'result_filter(): skip empty result')
        return result
    logger.info(TAG + "result_filter(): extract result: {}".format(str(result)))
    if isinstance(result, dict):
    # if IS_CODE_OR_CONFIG or isinstance(result, dict):
        # TODO 代码文件的结果过滤
        filtered_item = {}
        for key, value in result.items():
            if is_valid_info(value) and is_valid_info(key):
                filtered_item[key] = value
        if len(filtered_item) >= VALID_RESULT_THRESHOLD:
            result = filtered_item

    else:
        filtered_result = []
        for item in result:
            filtered_item = {}
            for key, value in item.items():
                if is_valid_info(value) and is_valid_info(key):
                    filtered_item[key] = value
            if len(filtered_item) >= VALID_RESULT_THRESHOLD:
                filtered_result.append(filtered_item)
        result = filtered_result
    logger.info(TAG + "result_filter(): filtered result: {}".format(str(result)))
    return result

# 在常规提取失败后，使用特殊方法提取信息
def result_manager(result,info,file_path,IS_CODE_OR_CONFIG=False) -> dict:
    logger.info(TAG + "result_manager(): extract result: {}".format(str(result)))
    result = result_filter(result)
    # result = re_pair_info_extract(result)
    # file_extension = file_path.split(".")[-1]
    file_type = determine_file_type(file_path,info)
    switch = {
        'code': code_info_extract,
        'config': config_info_extract,
        'ocr': ocr_code_processing
    }
    if result == []:
        logger.warning(
            TAG + 'No paired info extracted during plain text info extraction!')
        logger.info(
            TAG + "result_manager(): input type is {}".format(file_type))
        if file_type in switch:
            logger.info(TAG + "result_manager(): input is code/config")
            # result = code_info_extract(info)
            result = switch[file_type](info)
        else:
            logger.info(TAG + "result_manager(): unknown input")
            result = plain_text_info_extraction(info, FUZZ_MARK=True)
            logger.info(
                TAG + "result_manager(): fuzz_extract result: {}".format(str(result)))
    result = result_filter(result)
    # result = re_pair_info_extract(result)
    return result


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
    code_info_extract(text)
    exit(0)
