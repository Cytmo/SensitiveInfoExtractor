import os
import shutil
import spacy
from spacy.matcher import Matcher
import info_protection
from info_protection import IoCIdentifier
# import info_parser
# from info_parser import parsingModel_training, IoCNer
from spacy.tokens import Doc
from typing import Any, Tuple
import re

import log_utils
logger = log_utils.GetLog().get_log()

logger.info('Info extraction start...')

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
        {"TEXT": {"REGEX": r"^(?:(?:[0-9]{1,3}\.){3}[0-9]{1,3}|(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4})$"}}
    ]]

    # Initialize Matcher
    matcher = Matcher(nlp.vocab)
    matcher.add("IP_ADDRESS", ip_pattern)
    matcher.add("DOMAIN", [[{"ORTH": "www"}, {"ORTH": "."}, {"IS_ALPHA": True}]])
    matcher.add("EMAIL",  [[{"IS_ASCII": True}, {"ORTH": "@"}, {"IS_ASCII": True}]])

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



# 关键字列表
keywords_list = ["IP","端口","名称","地址","姓名","学号", "用户名", "密码","密钥为",'\n'] 
# 替换列表
replacement_dict = {"端口":"port","名称": "user","学号": "user", "用户名": "user","密钥为": "password", "密码": "password", "地址": "address", "姓名": "name"}
# 预处理文本，仅保留英文字符和数字，以及中文关键词（学号，用户名，密码等）
def text_preprocessing(text: str) -> str:
     # 构建正则表达式，匹配英文字符、数字以及指定中文关键词
    pattern = f"(?:{'|'.join(keywords_list)}|[a-zA-Z0-9,.;@?!\"'()])+"
    
    # 使用正则表达式进行匹配和替换
    cleaned_text = re.findall(pattern, text)
    
    # 将匹配到的内容重新组合成字符串
    cleaned_text = ' '.join(cleaned_text)
    # 替换中文关键词
    for keyword in keywords_list:
        if keyword in replacement_dict:
            cleaned_text = cleaned_text.replace(keyword, ' {'+replacement_dict[keyword]+'} ')
    # 移除空行
    cleaned_text = '\n'.join([line for line in cleaned_text.splitlines() if line.strip()])
    logger.debug(cleaned_text)
    return cleaned_text

def has_chinese(text: str) -> bool:
    pattern = re.compile(r'[\u4e00-\u9fa5]')  # 匹配中文字符的范围
    return bool(pattern.search(text))


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
        if self.__dict__.get(name) != None and self.__dict__.get(name) != value:
            return False
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
        result =  {
            "user": self.user,
            "password": self.password,
            "address": self.address,
            "port": self.port
        }
        self.__init__()
        return result
    def if_same_attr(self, name: str, value: Any) -> bool:
        return self.__dict__.get(name) == value

info_pattern = {"user":"user", "password":"password", "address":"address","port":"port"}
replaced_keyword_list = ["{user}", "{password}", "{address}"]
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
        if text[i].strip() in replaced_keyword_list and text[i+1] not in replaced_keyword_list:
            # print(text[i], text[i+1])
            if (text[i] == "{user}" and has_user) or (text[i] == "{address}" and has_address):
                # if not a_paired_info.if_same_attr(info_pattern[text[i].replace('{','').replace('}','')], text[i+1]):
                result_pair.append(a_paired_info.output())
                # print("Same,current result:"+str(result_pair))
                has_user = False
                has_address = False
            a_paired_info.setter(info_pattern[text[i].replace('{','').replace('}','')], text[i+1])
            if text[i] == "{user}":
                has_user = True
            if text[i] == "{address}":
                has_address = True
            # if not result:
            #     result_pair.append(a_paired_info.output())
    last_output = a_paired_info.output()
    if last_output["user"] != None or last_output["address"] != None:
        result_pair.append(last_output)       
    return result_pair



# 从处理过后的字符串中提取成对信息
# 输入：处理过后的字符串
# 输出：成对信息列表
def begin_info_extraction(text:str) -> list:
    if has_chinese(text):
        text = text_preprocessing(text)
    # print(text)
    paired_info = extract_paired_info(text)
    logger.info('Info extraction finished...')
    logger.info('Info extraction result: '+str(paired_info))
    return paired_info

import argparse
if __name__ == '__main__':
    # file = open("test/.bash_history", "r")
    # file = open("test/windows/system.hiv.json", "r")
    argparse = argparse.ArgumentParser()
    argparse.add_argument("-f", "--file", required=True,help="The file to be parsed")
    args = argparse.parse_args()
    with open(args.file, "r") as f:
        text = f.read()
    begin_info_extraction(text)
    exit(0)
    # yara_str_scan(text)
    # exit(0)
    text = ioc_protection(text)
    # text.check_replace_result()
    # text.display_iocs()
    # text.check_replace_result()
    # text.display_iocs()

    #删除临时文件夹
    if os.path.exists("temp"):
        shutil.rmtree("temp")
    #创建临时文件夹
    os.mkdir("temp")

    # 保存替换后的文本
    with open("temp/replaced.txt", "w") as f:
        f.write(text.replaced_text)

    # 保存替换结果
    with open("temp/ioc_list.txt", "w") as f:
        for ioc in text.replaced_ioc_list:
            f.write(str(ioc) + "\n")
    #保存结果为json
    with open("temp/ioc_list.json", "w") as f:
        f.write(text.to_jsonl())
    #保存感兴趣的内容
    print(text.display_iocs())



    # cti_doc = report_parsing(text.replaced_text)
    # # print(cti_doc[1])
    # for ent in cti_doc[1].ents:
    #     print(ent.text, ent.label_)
