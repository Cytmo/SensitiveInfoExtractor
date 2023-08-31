# # import yaml
# # import re

# # # 读取规则文件
# # def load_rules(filename):
# #     with open(filename, 'r') as file:
# #         rules = yaml.safe_load(file)
# #     return rules.get('patterns', [])

# # # 在文本中查找匹配的规则
# # def find_matches(text, patterns):
# #     matches = []
# #     for pattern in patterns:
# #         name = pattern['pattern']['name']
# #         regex = pattern['pattern']['regex']
# #         confidence = pattern['pattern']['confidence']

# #         # 使用正则表达式查找匹配
# #         for match in re.finditer(regex, text):
# #             matches.append({
# #                 'name': name,
# #                 'confidence': confidence,
# #                 'match_text': match.group()
# #             })

# #     return matches


# # def main():
# #     rules_filename = 'rules-stable.yml'
# #     # with open("../../data/src/python_fasts3-main/run_regression.sh", 'r') as file:
# #     # with open("../../data/linux/application.properties", 'r') as file:
# #     with open("/home/cytmo/workspace/security-text-detect-825/data/linux/root/.bash_history", 'r') as file:
# #         text_to_search = file.read()
# #     # text_to_search = "Some text containing sensitive information like admin secret and AWS API Gateway URL."

# #     # 加载规则
# #     patterns = load_rules(rules_filename)

# #     # 查找匹配
# #     matched_patterns = find_matches(text_to_search, patterns)

# #     # 打印匹配结果
# #     for match in matched_patterns:
# #         if match['confidence'] == "high":
# #             print("Matched:", match)

# # if __name__ == "__main__":
# #     main()


# # 防止文件名等并识别为关键字，如user.txt
# import re


# def fuzz_prevention(text: str) -> str:
#     # 文件后缀列表
#     file_extensions = [
#         "sys",
#         "htm",
#         "html",
#         "jpg",
#         "png",
#         "vb",
#         "scr",
#         "pif",
#         "chm",
#         "zip",
#         "rar",
#         "cab",
#         "pdf",
#         "doc",
#         "docx",
#         "ppt",
#         "pptx",
#         "xls",
#         "xlsx",
#         "swf",
#         "gif",
#         "txt",
#         "csv",
#         "sh",
#         "c",
#         "d",
#         "conf",
#         "exe",
#     ]

#     # 构建正则表达式模式，匹配文件名及其后缀
#     extensions_pattern = "|".join(file_extensions)
#     file_pattern = r"\w+\.(?:" + extensions_pattern + r")\b"

#     # 使用正则替换
#     result = re.sub(file_pattern, "file", text)

#     return result


# # 英文通用处理

# eng_keywords_list = ["user", "password", "address", "name", "port", "key"]


# def eng_text_preprocessing(text: str) -> str:
#     text = fuzz_prevention(text)
#     print(text.split("\n"))


# from whispers.cli import parse_args
# from whispers.core import run

# src = "tests/fixtures"
# configfile = "whispers/config.yml"
# args = parse_args(["-c", configfile, src])
# for secret in run(args):
#     print(secret)


# # if __name__ == "__main__":
# #     with open("/home/cytmo/workspace/security-text-detect-825/data/linux/root/.bash_history", 'r') as file:
# #         text_to_search = file.read()
# #     eng_text_preprocessing("user.txt")




def if_reduntant(text: str,filter_dict: dict) -> bool:
    if filter_dict[text] > 0:
        if text == "{user}":
           if filter_dict["{password}"] > 0:
               filter_dict["{password}"] -= 1
               filter_dict["{user}"] -= 1
        if text == "{password}":
            if filter_dict["{user}"] > 0:
                filter_dict["{password}"] -= 1
                filter_dict["{user}"] -= 1
    if filter_dict[text] > 0:
        filter_dict = {"{user}": 0, "{password}": 0, "{address}": 0, "{port}": 0}
        return True
    else:
        filter_dict[text] += 1
        return False
            
# 过滤多余的属性
def filter_reduntant(text: list) -> str:
    filter_dict = {"{user}": 0, "{password}": 0, "{address}": 0, "{port}": 0}
    for i in range(len(text)-1):
        if text[i] in filter_dict:
            filter_dict[text[i]] += 1
            # remove redundant attributes
            if if_reduntant(text[i],filter_dict):
                text[i] = "{removed_reduntant_{}}".format(text[i].replace('{','').replace('}',''))
    return text

text = '''sqlmap -r file --force-ssl --random-agent --dbms PostgreSQL - {password} roxy "socks5 ?22? 4781" -D public -T BH CONFIG --dump
cd Desktop
cat file
vim file
cd etc nginx file
vim file
service nginx start
vim file
service nginx re
service nginx restart
vim file
service nginx restart
vim file
nginx -t
service nginx restart
apt-get install cmake-curses-gui
apt-get update
apt-get install cmake-curses-gui
exit
service ssh start
systemctl enable ssh 
java -jar JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar -C "file"
service apache2 start
ifconfig
cd var www html
open . 
service apache2 start
service nginx status
cd etc nginx
netstat -ntlp
service apache2 stop
cd file
vim file
ifconfig
whaomi
cat etc passwd
passwd zther0
ifconfig
nmap ?23?  {password}  4780
ping cip.cc
sqlmap - {address} elp
ifconfig
cd Desktop
vim file
touch file
ifconfig
apt-get install redis-cli
. file TestUser900 TestUser900
sqlmap  {user}  "?1?" --batch --level 5 --risk 3 --output-dir root sql re --dbs
sqlmap  {user}  "?2?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql --tabels
sqlmap  {user}  "?3?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql --tables
sqlmap  {user}  "?4?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T mysql --columns
sqlmap  {user}  "?5?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T User --columns
sqlmap  {user}  "?6?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --columns
sqlmap  {user}  "?7?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}   {address} 
sqlmap  {user}  "?8?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}   {address} h
sqlmap  {user}  "?9?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump 
ls
cd dump
ls
cd mysql
ls
cat file
sqlmap  {user}  "?10?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump-file
sqlmap  {user}  "?11?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --batch 3
ls
cat file
cat file.1
sqlmap  {user}  "?12?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 1
ls
rm file
rm file.1
sqlmap  {user}  "?13?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 1
cat file
sqlmap  {user}  "?14?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 0 --stop 1
sqlmap  {user}  "?15?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 2
ls
cat file
sqlmap  {user}  "?16?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 2 --dump-format
sqlmap  {user}  "?17?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 2  {address} h 
sqlmap  {user}  "?18?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 2  {address} h grep dump
sqlmap  {user}  "?19?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 2 --dump-format SQLITE
sqlmap  {user}  "?20?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 2 --dump-format CSV
sqlmap  {user}  "?21?" --batch --level 5 --risk 3 --output-dir root sql re -D mysql -T  {user}  --dump --start 1 --stop 200 --dump-format CSV
mysql  {address}  ?24?  {user} root  {password} 123456999'''
text = filter_reduntant(text)
print(text)


