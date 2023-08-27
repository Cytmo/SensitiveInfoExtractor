import os
import shutil
import spacy
from spacy.matcher import Matcher
import info_protection
from info_protection import IoCIdentifier
# import info_parser
# from info_parser import parsingModel_training, IoCNer
from spacy.tokens import Doc
from typing import Tuple


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

import argparse
if __name__ == '__main__':
    # file = open("test/.bash_history", "r")
    # file = open("test/windows/system.hiv.json", "r")
    argparse = argparse.ArgumentParser()
    argparse.add_argument("-f", "--file", required=True,help="The file to be parsed")
    args = argparse.parse_args()
    with open(args.file, "r") as f:
        text = f.read()
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
