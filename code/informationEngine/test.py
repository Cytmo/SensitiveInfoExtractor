# # # # # # import yaml
# # # # # # import re

# # # # # # # 读取规则文件
# # # # # # def load_rules(filename):
# # # # # #     with open(filename, 'r') as file:
# # # # # #         rules = yaml.safe_load(file)
# # # # # #     return rules.get('patterns', [])

# # # # # # # 在文本中查找匹配的规则
# # # # # # def find_matches(text, patterns):
# # # # # #     matches = []
# # # # # #     for pattern in patterns:
# # # # # #         name = pattern['pattern']['name']
# # # # # #         regex = pattern['pattern']['regex']
# # # # # #         confidence = pattern['pattern']['confidence']

# # # # # #         # 使用正则表达式查找匹配
# # # # # #         for match in re.finditer(regex, text):
# # # # # #             matches.append({
# # # # # #                 'name': name,
# # # # # #                 'confidence': confidence,
# # # # # #                 'match_text': match.group()
# # # # # #             })

# # # # # #     return matches


# # # # # # def main():
# # # # # #     rules_filename = 'rules-stable.yml'
# # # # # #     # with open("../../data/src/python_fasts3-main/run_regression.sh", 'r') as file:
# # # # # #     # with open("../../data/linux/application.properties", 'r') as file:
# # # # # #     with open("/home/cytmo/workspace/security-text-detect-825/data/linux/root/.bash_history", 'r') as file:
# # # # # #         text_to_search = file.read()
# # # # # #     # text_to_search = "Some text containing sensitive information like admin secret and AWS API Gateway URL."

# # # # # #     # 加载规则
# # # # # #     patterns = load_rules(rules_filename)

# # # # # #     # 查找匹配
# # # # # #     matched_patterns = find_matches(text_to_search, patterns)

# # # # # #     # 打印匹配结果
# # # # # #     for match in matched_patterns:
# # # # # #         if match['confidence'] == "high":
# # # # # #             print("Matched:", match)

# # # # # # if __name__ == "__main__":
# # # # # #     main()


# # # # # # 防止文件名等并识别为关键字，如user.txt
# # # # # import re


# # # # # def fuzz_prevention(text: str) -> str:
# # # # #     # 文件后缀列表
# # # # #     file_extensions = [
# # # # #         "sys",
# # # # #         "htm",
# # # # #         "html",
# # # # #         "jpg",
# # # # #         "png",
# # # # #         "vb",
# # # # #         "scr",
# # # # #         "pif",
# # # # #         "chm",
# # # # #         "zip",
# # # # #         "rar",
# # # # #         "cab",
# # # # #         "pdf",
# # # # #         "doc",
# # # # #         "docx",
# # # # #         "ppt",
# # # # #         "pptx",
# # # # #         "xls",
# # # # #         "xlsx",
# # # # #         "swf",
# # # # #         "gif",
# # # # #         "txt",
# # # # #         "csv",
# # # # #         "sh",
# # # # #         "c",
# # # # #         "d",
# # # # #         "conf",
# # # # #         "exe",
# # # # #     ]

# # # # #     # 构建正则表达式模式，匹配文件名及其后缀
# # # # #     extensions_pattern = "|".join(file_extensions)
# # # # #     file_pattern = r"\w+\.(?:" + extensions_pattern + r")\b"

# # # # #     # 使用正则替换
# # # # #     result = re.sub(file_pattern, "file", text)

# # # # #     return result


# # # # # # 英文通用处理

# # # # # eng_keywords_list = ["user", "password", "address", "name", "port", "key"]


# # # # # def eng_text_preprocessing(text: str) -> str:
# # # # #     text = fuzz_prevention(text)
# # # # #     print(text.split("\n"))


# # # # # from whispers.cli import parse_args
# # # # # from whispers.core import run

# # # # # src = "tests/fixtures"
# # # # # configfile = "whispers/config.yml"
# # # # # args = parse_args(["-c", configfile, src])
# # # # # for secret in run(args):
# # # # #     print(secret)


# # # # # # if __name__ == "__main__":
# # # # # #     with open("/home/cytmo/workspace/security-text-detect-825/data/linux/root/.bash_history", 'r') as file:
# # # # # #         text_to_search = file.read()
# # # # # #     eng_text_preprocessing("user.txt")


# # # # def if_reduntant(text: str,filter_dict: dict) -> bool:
# # # #     if filter_dict[text] > 0:
# # # #         if text == "{user}":
# # # #            if filter_dict["{password}"] > 0:
# # # #                filter_dict["{password}"] -= 1
# # # #                filter_dict["{user}"] -= 1
# # # #         if text == "{password}":
# # # #             if filter_dict["{user}"] > 0:
# # # #                 filter_dict["{password}"] -= 1
# # # #                 filter_dict["{user}"] -= 1
# # # #     if filter_dict[text] > 0:
# # # #         filter_dict = {"{user}": 0, "{password}": 0, "{address}": 0, "{port}": 0}
# # # #         return True
# # # #     else:
# # # #         filter_dict[text] += 1
# # # #         return False

# # # # # 过滤多余的属性
# # # # def filter_reduntant(text: list) -> str:
# # # #     filter_dict = {"{user}": 0, "{password}": 0, "{address}": 0, "{port}": 0}
# # # #     for i in range(len(text)-1):
# # # #         if text[i] in filter_dict:
# # # #             filter_dict[text[i]] += 1
# # # #             # remove redundant attributes
# # # #             if if_reduntant(text[i],filter_dict):
# # # #                 text[i] = "{removed_reduntant_{}}".format(text[i].replace('{','').replace('}',''))
# # # #     return text

# # # # text = '''sqlmap -r file --force-ssl --random-agent --dbms PostgreSQL - {password} roxy "socks5 ?22? 4781" -D public -T BH CONFIG --dump
# # # # cd Desktop
# # # # cat file
# # # # vim file
# # # # cd etc nginx file
# # # # vim file
# # # # service nginx start
# # # # vim file
# # # # service nginx re
# # # # service nginx restart
# # # # vim file
# # # # service nginx restart
# # # # vim file
# # # # nginx -t
# # # # service nginx restart
# # # # apt-get install cmake-curses-gui
# # # # apt-get update
# # # # apt-get install cmake-curses-gui
# # # # exit
# # # # service ssh start
# # # # systemctl enable ssh
# # # # java -jar JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar -C "file"
# # # # service apache2 start
# # # # ifconfig
# # # # cd var www html
# # # # open .
# # # # service apache2 start
# # # # service nginx status
# # # # cd etc nginx
# # # # netstat -ntlp
# # # # service apache2 stop
# # # # cd file
# # # # vim file
# # # # ifconfig
# # # # whaomi
# # # # cat etc passwd
# # # # passwd zther0
# # # # ifconfig
# # # # nmap ?23?  {password}  4780
# # # # ping cip.cc
# # # # sqlmap - {address} elp
# # # # ifconfig
# # # # cd Desktop
# # # # vim file
# # # # touch file
# # # # ifconfig
# # # # apt-get install redis-cli
# # # # . file TestUser900 TestUser900
# # # # sqlmap  {user}  "?1?" --batch --level 5 --risk 3 --output-dir root sql re --dbs
# # # # sqlmap  {user}  "?2?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql --tabels
# # # # sqlmap  {user}  "?3?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql --tables
# # # # sqlmap  {user}  "?4?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T mysql --columns
# # # # sqlmap  {user}  "?5?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T User --columns
# # # # sqlmap  {user}  "?6?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --columns
# # # # sqlmap  {user}  "?7?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}   {address}
# # # # sqlmap  {user}  "?8?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}   {address} h
# # # # sqlmap  {user}  "?9?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump
# # # # ls
# # # # cd dump
# # # # ls
# # # # cd mysql
# # # # ls
# # # # cat file
# # # # sqlmap  {user}  "?10?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump-file
# # # # sqlmap  {user}  "?11?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --batch 3
# # # # ls
# # # # cat file
# # # # cat file.1
# # # # sqlmap  {user}  "?12?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 1
# # # # ls
# # # # rm file
# # # # rm file.1
# # # # sqlmap  {user}  "?13?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 1
# # # # cat file
# # # # sqlmap  {user}  "?14?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 0 --stop 1
# # # # sqlmap  {user}  "?15?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 2
# # # # ls
# # # # cat file
# # # # sqlmap  {user}  "?16?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 2 --dump-format
# # # # sqlmap  {user}  "?17?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 2  {address} h
# # # # sqlmap  {user}  "?18?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 2  {address} h grep dump
# # # # sqlmap  {user}  "?19?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 2 --dump-format SQLITE
# # # # sqlmap  {user}  "?20?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 2 --dump-format CSV
# # # # sqlmap  {user}  "?21?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 200 --dump-format CSV
# # # # mysql  {address}  ?24?  {user} root  {password} 123456999'''
# # # # text = filter_reduntant(text)
# # # # print(text)


# # # from pygments.lexers import guess_lexer, ClassNotFound

# # # def is_code(text):
# # #     try:
# # #         lexer = guess_lexer(text)
# # #         return True, lexer.name
# # #     except ClassNotFound:
# # #         return False, None

# # # text1 = "print('Hello, world!')"
# # # text2 = '''

# # # 研发区
# # # Pass@word!!!


# # # 163邮箱
# # # kppublic@163.com
# # # 13666628123
# # # Huawei@123456


# # # 172.36.219.13
# # # root
# # # 2!Um37hvjk
# # # '''

# # # is_code_1, lang_1 = is_code(text1)
# # # is_code_2, lang_2 = is_code(text2)

# # # if is_code_1:
# # #     print("Text 1 is code written in", lang_1)
# # # else:
# # #     print("Text 1 is not code")

# # # if is_code_2:
# # #     print("Text 2 is code written in", lang_2)
# # # else:
# # #     print("Text 2 is not code")
# # # def chinese_character_percentage(text):
# # #     total_characters = len(text)
# # #     chinese_characters = 0

# # #     for char in text:
# # #         if '\u4e00' <= char <= '\u9fff':
# # #             chinese_characters += 1

# # #     if total_characters == 0:
# # #         return 0.0

# # #     percentage = (chinese_characters / total_characters) * 100
# # #     return percentage

# # # text = "这是一个示例文本，包。T"
# # # percentage = chinese_character_percentage(text)

# # # print(f"中文字符占比：{percentage:.2f}%")


# def convert_chinese_punctuation(text:str):
#     # 定义一个字典来映射中文标点符号到英文标点符号
#     punctuation_mapping = {
#         "，": ",",
#         "。": ".",
#         "！": "!",
#         "？": "?",
#         "“": '"',
#         "”": '"',
#         "‘": "'",
#         "’": "'",
#         "；": ";",
#         "：": ":",
#         "（": "(",
#         "）": ")",
#         "【": "[",
#         "】": "]",
#         "《": "<",
#         "》": ">",
#         "、": ",",
#         "＇": "'",
#         "/**#@+ *": "",
#     }

#     # 使用字典进行替换
#     for chinese_punctuation, english_punctuation in punctuation_mapping.items():
#         text = text.replace(chinese_punctuation, english_punctuation)

#     return text

# import re
# # # todo
# # # 特殊处理
# # eng_keywords_list = [
# #     "user",
# #     "pass",
# #     "address",
# #     "name",
# #     "port",
# #     "key",
# #     "auth",
# #     "salt",
# #     "host",
# # ]


# # def special_processing(text: str) -> str:
# #     # text = fuzz_prevention(text)
# #     text = text.lower()
# #     text = convert_chinese_punctuation(text)
# #     text = text.replace("'", '"')
# #     text = text.split("\n")
# #     lines = []
# #     # 用于分割的符号
# #     split_symbols = [":", "=", '"']
# #     # remove outer "
# #     for line in text:
# #         if line.startswith('"') and line.endswith('"'):
# #             line = line[1:-1]
# #         lines.append(line)
# #     text = lines
# #     lines = []
# #     # only  keep each eng_keywords_list between ""
# #     for line in text:
# #         new_line = ""
# #         if ":" in line:
# #             line = line.split(":")
# #         elif "=" in line:
# #             line = line.split("=")
# #         elif '"' in line:
# #             line = line.split('"')
# #         for i in range(len(line)):
# #             if i % 2 == 1:
# #                 new_line += "{} ".format(line[i])
# #         lines.append(new_line)
# #     result_dict = {}
# #     # remove empty eng_keywords_list
# #     lines_temp = []
# #     for line in lines:
# #         line = line.strip()
# #         lines_temp.append(line)
# #     lines = lines_temp
# #     print(lines)
# #     words_list = []
# #     for line in lines:
# #         words_list += line.split(" ")
# #     for i in range(len(words_list) - 1):
# #         print(words_list[i])
# #         if any(key in words_list[i] for key in eng_keywords_list) and not any(
# #             key in words_list[i + 1] for key in eng_keywords_list
# #         ):
# #             result_dict[words_list[i]] = words_list[i + 1]

# #     print(result_dict)

# #     print(lines)


# text = '''"define（'DB_NAME'，'db_＇。‘d41d8'）；／/数据库名"
# "define（'DB_USER'，‘user_＇·'a42f8')；//数据库用户名"
# "define（‘DB_PASSW0RD'，‘b8921hs90a')；// 数据库密码"
# "define（‘DB_HOsT'，'localhost’)；//数据库主机地址"
# '/**#@+ * Authentication Unique Keys and Salts.'
# "def ine( 'AUTH_KEYssssssssssss', '3b365d019564585107cf79c67f06ca6d' ); 
# define('SECURE_AUTH_KEY',"
# "'d32e5d0189b9b0c5503c70b18f9e9715');"
# "define('LOGGED_IN_KEY', '4c85fbbfaadea04db992ec6c0f7988b8'); def ine( 'NONCE_KEY',"
# "'8c449f8a50768189727baf688a5fbbe9');"
# "define('AUTH_SALT' '81f9d54f5b7d7917d6f3a2e6ad64b8fa');"
# "define('SECURE_AUTH_SALT', '51e59e1d1c0db3ebd1cb48f03d0e3971');"
# "define('LOGGED_IN_SALT' 'fdbc2dc7d40ef9e4bb353c6b6740097e');"
# "define('NONCE_SALT', '53ed4eb34cfbfae4d8574967e7c97d3f');"
# "$table_prefix='wp_'；// 表前缀"
# "define('WP_DEBUG'，false）;//调试模式"
# "/** WordPress 设置－可以通过访问您的网页来进行修改。 define( 'ABSPATH', dirname( -_FILE_- ）.'/' );"
# "require_once( ABSPATH . 'wp-settings.php' ); ？>"'''
# # # special_processing(text)

# from typing import Tuple
# # import re
# # # 保存email地址 url ip地址等内容，防止被替换
# def item_protection(text: str) -> Tuple[str, dict]:
#     placeholders = {}  # This dictionary will store placeholders and their corresponding content
#     placeholders_counter = 1  # Counter for generating placeholders

#     # Define regular expressions for different types of items you want to replace
#     email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
#     url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
#     ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b|localhost\b'


#     patterns = [email_pattern, url_pattern, ip_pattern]

#     for pattern in patterns:
#         matches = re.finditer(pattern, text)
#         for match in matches:
#             item = match.group()
#             placeholder = f'?{placeholders_counter}?'
#             placeholders[placeholder] = item
#             text = text.replace(item, placeholder, 1)  # Replace only the first occurrence
#             placeholders_counter += 1

#     return text, placeholders


# # a,b = item_protection(text)
# # print(a)
# # print(b)

# # 特殊处理
# eng_keywords_list = [
#     "user",
#     "pass",
#     "address",
#     "name",
#     "port",
#     "key",
#     "auth",
#     "salt",
#     "host",
# ]


# def special_processing(text: str) -> str:
#     # logger.info(TAG + 'Special processing for text')
#     text, item_protection_dict1 = item_protection(text)
#     print(item_protection_dict1)
#     print(text)
#     global item_protection_dict 
#     item_protection_dict = item_protection_dict1
#     # text = fuzz_prevention(text)
#     text = text.lower()
#     text = convert_chinese_punctuation(text)
#     print(text)
#     text = text.replace("'", '"')
#     text = text.split("\n")
#     lines = []
#     # 用于分割的符号
#     split_symbols = [":", "=", '"']
#     # remove outer "
#     for line in text:
#         if line.startswith('"') and line.endswith('"'):
#             line = line[1:-1]
#         lines.append(line)
#     text = lines
#     lines = []
#     # only  keep each eng_keywords_list between ""
#     for line in text:
#         new_line = ""
#         if ":" in line:
#             line = line.split(":")
#         elif "=" in line:
#             line = line.split("=")
#         elif '"' in line:
#             line = line.split('"')
#         for i in range(len(line)):
#             if i % 2 == 1:
#                 new_line += "{} ".format(line[i])
#         lines.append(new_line)
#     result_dict = {}
#     # remove empty eng_keywords_list
#     lines_temp = []
#     for line in lines:
#         line = line.strip()
#         lines_temp.append(line)
#     lines = lines_temp
#     print(lines)
#     words_list = []
#     for line in lines:
#         words_list += line.split(" ")
#     for i in range(len(words_list) - 1):
#         # print(words_list[i])
#         if any(key in words_list[i] for key in eng_keywords_list) and not any(
#             key in words_list[i + 1] for key in eng_keywords_list
#         ):
#             if words_list[i+1] in item_protection_dict:
#                 result_dict[words_list[i]] = item_protection_dict[words_list[i+1]]
#             else:
#                 result_dict[words_list[i]] = words_list[i + 1]
#     #  # 还原被替换的内容
#     # for item in result_dict:
#     #     for key, value in item:
#     #         if value in item_protection_dict:
#     #             item[key] = item_protection_dict[value]
#     # logger.info(TAG + 'Special processing result: '+str(result_dict))
#     return result_dict
# # {'?1?': 'localhost'}
# a =special_processing(text)
# print(a)



def has_only_one_column(lst):
    # 检查列表是否为空
    if not lst:
        return False
    
    # 遍历列表中的每个元素
    for item in lst:
        # 如果元素不是列表，或者子列表的长度不等于1，则返回False
        if not isinstance(item, list) or len(item) != 1:
            return False
    
    # 如果所有元素都是单列子列表，返回True
    return True

# 示例列表
my_list = ["dasd", "dasdad", "dasd"]

# 判断是否只有一列
result = has_only_one_column(my_list)

if result:
    print("列表只有一列")
else:
    print("列表不只有一列")