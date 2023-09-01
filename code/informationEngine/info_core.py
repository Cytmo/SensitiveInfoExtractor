import argparse
import os
import shutil
import spacy
from spacy.matcher import Matcher
import yaml
from informationEngine import info_protection
from informationEngine.info_protection import IoCIdentifier
from spacy.tokens import Doc
from typing import Any, Tuple
import re
from pygments.lexers import guess_lexer, ClassNotFound

# 添加日志模块
from util.logUtils import LoggerSingleton
TAG = "informationEngine.info_core.py: "
logger = LoggerSingleton().get_logger()


def text_parse(file_path):
    # 加载英语语言模型
    nlp = spacy.load("en_core_web_sm")
    file = open(".bash_history", "r")

    # 读取文件内容
    text = file.read()
    # text = "Sample text containing IP addresses like 192.168.1.1 and 2001:0db8:85a3:0000:0000:8a2e:0370:7334."

    doc = nlp(text)

    # 加载英语语言模型
    nlp = spacy.load("en_core_web_sm")
    matcher = Matcher(nlp.vocab)

    # octet_rx = r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
    # ip_pattern= [ {"TEXT": {"REGEX": r"^{0}(?:\.{0}){{3}}$".format(octet_rx)}}]
    # 添加规则来匹配IP地址
    ip_pattern = [[
        {"TEXT": {
            "REGEX": r"^(?:(?:[0-9]{1,3}\.){3}[0-9]{1,3}|(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4})$"}}
    ]]

    # Initialize Matcher
    matcher = Matcher(nlp.vocab)
    matcher.add("IP_ADDRESS", ip_pattern)
    matcher.add(
        "DOMAIN", [[{"ORTH": "www"}, {"ORTH": "."}, {"IS_ALPHA": True}]])
    matcher.add(
        "EMAIL",  [[{"IS_ASCII": True}, {"ORTH": "@"}, {"IS_ASCII": True}]])

    # Process text
    doc = nlp(text)

    # Find matches
    matches = matcher(doc)

    # Extract matched IP addresses
    matched_ips = []
    for match_id, start, end in matches:
        matched_ips.append(doc[start:end].text)

    print(matched_ips)

    for ent in doc.ents:
        print(ent.text, ent.label_)

    for token in doc:
        print(token.text, token.pos_, token.dep_, token.head.text)


# def report_parsing(text: str) -> Tuple[IoCIdentifier, Doc]:
#     iid = ioc_protection(text)
#     text_without_ioc = iid.replaced_text

#     ner_model = IoCNer("./new_cti.model")
#     doc = ner_model.parse(text_without_ioc)

#     return iid, doc


def ioc_protection(text: str):
    iid = IoCIdentifier(text)
    iid.ioc_protect()
    # iid.check_replace_result()
    return iid

# import yara_scan
# def yara_str_scan(text: str):
#     pass


# 保存email地址 url ip地址等内容，防止被替换
def item_protection(text: str) -> Tuple[str, dict]:
    placeholders = {}  # This dictionary will store placeholders and their corresponding content
    placeholders_counter = 1  # Counter for generating placeholders

    # Define regular expressions for different types of items you want to replace
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

    patterns = [email_pattern, url_pattern, ip_pattern]

    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            item = match.group()
            placeholder = f'?{placeholders_counter}?'
            placeholders[placeholder] = item
            text = text.replace(item, placeholder, 1)  # Replace only the first occurrence
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

    return result


keywords_list = ["-u", "-p", "IP", "port","-h",
                 "user", "password", "address", "name", '\n']
replacement_dict = {"-p": "password", "port": "port", "-u": "user", "user": "user", "password": "password",
                    "-h":"address","address": "address", "name": "name"}


def text_preprocessing(text: str) -> str:
    text, item_protection_dict1 = item_protection(text)
    global item_protection_dict 
    item_protection_dict = item_protection_dict1
    # 构建正则表达式，匹配英文字符、数字以及指定关键词
    pattern = f"(?:{'|'.join(keywords_list)}|[a-zA-Z0-9,.;@?!\-\"'()])+"

    # 使用正则表达式进行匹配和替换
    cleaned_text = re.findall(pattern, text,re.IGNORECASE)

    # 将匹配到的内容重新组合成字符串
    cleaned_text = ' '.join(cleaned_text)
    # 替换关键词
    for keyword, replacement in replacement_dict.items():
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        cleaned_text = pattern.sub(f'{{{replacement}}}', cleaned_text)
    # 移除空行
    cleaned_text = '\n'.join(
        [line for line in cleaned_text.splitlines() if line.strip()])
    cleaned_text = cleaned_text.replace("{ {", "{").replace("} }", "}")
    logger.debug("Cleaned text: "+cleaned_text)
    return cleaned_text


# 中文关键字列表
chn_keywords_list = ["账号","IP", "端口", "名称", "地址",
                     "姓名", "学号", "用户名", "密码", "密钥为", '\n']
# 中文替换列表
chn_replacement_dict = {"账号":"user","端口": "port", "名称": "user", "学号": "user", "用户名": "user",
                        "密钥为": "password", "密码": "password", "地址": "address", "姓名": "name"}
# 预处理文本，仅保留英文字符和数字，以及中文关键词（学号，用户名，密码等）

item_protection_dict = {}
def chn_text_preprocessing(text: str) -> str:
    text, item_protection_dict1 = item_protection(text)
    global item_protection_dict 
    item_protection_dict = item_protection_dict1
    # 构建正则表达式，匹配英文字符、数字以及指定中文关键词
    pattern = f"(?:{'|'.join(chn_keywords_list)}|[a-zA-Z0-9,.;@?!\"'()])+"

    # 使用正则表达式进行匹配和替换
    cleaned_text = re.findall(pattern, text,re.IGNORECASE)

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


def is_chinese_text(text: str) -> bool:
    # pattern = re.compile(r'[\u4e00-\u9fa5]')  # 匹配中文字符的范围
    # return bool(pattern.search(text))
    return chinese_character_percentage(text) > 70.0


# 判断中文字符占比
def chinese_character_percentage(text:str)-> float:
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


# 从处理过后的字符串中提取成对信息
class paired_info():
    def __init__(self):
        self.port = None
        self.address = None
        self.user = None
        self.password = None

    def set_port(self, port):
        self.port = port

    def set_address(self, address):
        self.address = address

    def set_user(self, user):
        self.user = user

    def set_password(self, password):
        self.password = password

    def setter(self, name: str, value: Any) -> None:
        # if self.__dict__.get(name) != None and self.__dict__.get(name) != value:
        #     return False
        attr_switch = {
            "port": lambda x: self.set_port(x),
            "address": lambda x: self.set_address(x),
            "user": lambda x: self.set_user(x),
            "password": lambda x: self.set_password(x)
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
            "port": self.port
        }
        self.__init__()
        return result
    def getter (self,name:str):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            return None

    def if_same_attr(self, name: str, value: Any) -> bool:
        return self.__dict__.get(name) == value

    def is_None(self):
        return self.__dict__.get("user") == None and self.__dict__.get("password") == None and self.__dict__.get("address") == None and self.__dict__.get("port") == None

info_pattern = {"user": "user", "password": "password",
                "address": "address", "port": "port"}
replaced_keyword_list = ["{user}", "{password}", "{address}"]




# def if_reduntant(text: str,filter_dict: dict) -> bool:
#     if filter_dict[text] > 0:
#         if text == "{user}":
#            if filter_dict["{password}"] > 0:
#                filter_dict["{password}"] -= 1
#                filter_dict["{user}"] -= 1
#         if text == "{password}":
#             if filter_dict["{user}"] > 0:
#                 filter_dict["{password}"] -= 1
#                 filter_dict["{user}"] -= 1
#     if filter_dict[text] > 0:
#         filter_dict = {"{user}": 0, "{password}": 0, "{address}": 0, "{port}": 0}
#         return True
#     else:
#         filter_dict[text] += 1
#         return False
            
# # 过滤多余的属性
# def filter_reduntant(text: list) -> str:
#     filter_dict = {"{user}": 0, "{password}": 0, "{address}": 0, "{port}": 0}
#     for i in range(len(text)-1):
#         if text[i] in filter_dict:
#             filter_dict[text[i]] += 1
#             # remove redundant attributes
#             if if_reduntant(text[i],filter_dict):
#                 text[i] = "{removed_reduntant_{}}".format(text[i].replace('{','').replace('}',''))


def extract_paired_info(text):
    # print(text)
    result_pair = []
    a_paired_info = paired_info()
    text = text.split()
    # print(text)
    has_user = False
    has_address = False
    for i in range(len(text)-1):
        # print(text[i], text[i+1]) 
        # 密码不会最先出现
        if text[i].strip() == "{password}" and a_paired_info.is_None():
            continue
        if text[i].strip() in replaced_keyword_list and text[i+1] not in replaced_keyword_list:
            # print(text[i], text[i+1])
            if (text[i] == "{user}" and has_user) or (text[i] == "{address}" and has_address):
                if a_paired_info.getter("password") != None:
                    # if not a_paired_info.if_same_attr(info_pattern[text[i].replace('{','').replace('}','')], text[i+1]):
                    result_pair.append(a_paired_info.output())
                else:
                    a_paired_info.setter(info_pattern[text[i].replace(
                        '{', '').replace('}', '')], text[i+1])
                # print("Same,current result:"+str(result_pair))
                has_user = False
                has_address = False
            a_paired_info.setter(info_pattern[text[i].replace(
                '{', '').replace('}', '')], text[i+1])
            if text[i] == "{user}":
                has_user = True
            if text[i] == "{address}":
                has_address = True
            # if not result:
            #     result_pair.append(a_paired_info.output())
    last_output = a_paired_info.output()
    if last_output["user"] != None or last_output["address"] != None:
        result_pair.append(last_output)
    # Filter out dictionaries based on conditions
    logger.debug(TAG + 'Paired info before filtering: '+str(result_pair))
    filtered_result_pair = []
    for item in result_pair:
        if ("user" in item and "address" in item and "password" in item) and \
        (item["user"] is not None or item["address"] is not None) and \
        item["password"] is not None:
            # Remove None attributes
            filtered_item = {key: value for key, value in item.items() if value is not None}
            filtered_result_pair.append(filtered_item)

    result_pair = filtered_result_pair
    # 还原被替换的内容
    for item in result_pair:
        for key, value in item.items():
            if value in item_protection_dict:
                item[key] = item_protection_dict[value]
    return result_pair


# 英文通用处理

eng_keywords_list = ["user", "password", "address", "name", "port",'key']
def eng_text_preprocessing(text: str) -> str:
    text = fuzz_prevention(text)
    print(text.split('\n'))



# 从处理过后的字符串中提取成对信息
# 输入：处理过后的字符串
# 输出：成对信息列表
def begin_info_extraction(text: str) -> list:
    logger.critical(TAG + 'Text class: {}'.format(guess_lexer(text).name))
    # 移除doc提取的[pic]
    text = text.replace("[pic]", "")
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

        text = text_preprocessing(text)
    paired_info = extract_paired_info(text)
    logger.info(TAG + 'Info extraction result: '+str(paired_info))
    return paired_info


# # 对于代码，配置文件等的处理
# def find_sensitive_information(text, patterns):
#     sensitive_info = []

#     for pattern in patterns:
#         matches = re.findall(pattern["regex"], text)
#         for match in matches:
#             sensitive_info.append({
#                 "name": pattern["name"],
#                 "confidence": pattern["confidence"],
#                 "match": match
#             })

#     return sensitive_info


# # 从YAML文件加载模式
# with open("rules-stable.yml", "r") as yaml_file:
#     yaml_content = yaml.safe_load(yaml_file)

# # 示例文本
# sample_text = """
#     User: admin
#     Password: mysecretpassword123
#     API Gateway: abc123.execute-api.us-west-1.amazonaws.com
# """

# # 在示例文本中查找敏感信息
# sensitive_info_found = find_sensitive_information(sample_text, yaml_content["patterns"])

# # 打印识别到的敏感信息
# for info in sensitive_info_found:
#     print("Name:", info["name"])
#     print("Confidence:", info["confidence"])
#     print("Match:", info["match"])
#     print()


if __name__ == '__main__':
    # file = open("test/.bash_history", "r")
    # file = open("test/windows/system.hiv.json", "r")
    argparse = argparse.ArgumentParser()
    argparse.add_argument("-f", "--file", required=True,
                          help="The file to be parsed")
    args = argparse.parse_args()
    with open(args.file, "r") as f:
        text = f.read()
    begin_info_extraction(text)
    exit(0)
#     if has_chinese(text):
#         text = chn_text_preprocessing(text)
#     # print(text)
#     paired_info = extract_paired_info(text)

#     logger.info(paired_info)
#     # yara_str_scan(text)
#     # exit(0)
#     text = ioc_protection(text)
#     # text.check_replace_result()
#     # text.display_iocs()
#     # text.check_replace_result()
#     # text.display_iocs()

#     # 删除临时文件夹
#     if os.path.exists("temp"):
#         shutil.rmtree("temp")
#     # 创建临时文件夹
#     os.mkdir("temp")

#     # 保存替换后的文本
#     with open("temp/replaced.txt", "w") as f:
#         f.write(text.replaced_text)

#     # 保存替换结果
#     with open("temp/ioc_list.txt", "w") as f:
#         for ioc in text.replaced_ioc_list:
#             f.write(str(ioc) + "\n")
#     # 保存结果为json
#     with open("temp/ioc_list.json", "w") as f:
#         f.write(text.to_jsonl())
#     # 保存感兴趣的内容
#     print(text.display_iocs())
