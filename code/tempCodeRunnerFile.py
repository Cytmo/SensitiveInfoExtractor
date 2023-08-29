# import crypt   ## 导入 Linux 口令加密库
# def testPass(cryptPass):
#     salt=cryptPass[cryptPass.find("$"):cryptPass.rfind("$")]  ## 获得盐值，包含 $id 部分
#     dictFile=open('key.txt','r')
#     for word in dictFile.readlines():
#         word=word.strip("\n")
#         cryptWord=crypt.crypt(word,salt)                   ## 将密码字典中的值和盐值一起加密
#         if (cryptWord==cryptPass):                           ## 判断加密后的数据和密码字段是否相等
#             print ("[+]Found Password:"+word+"\n" )      ## 如果相等则打印出来
#             return 
#     print ("[-] Password Not Found.\n")
#     return 

# def main():
#     passFile=open('../data/linux/etc/shadow')
#     for line in passFile.readlines():      ## 读取文件中的所有内容
#         if ":" in line:
#             user=line.split(":")[0]                     ## 获得用户名
#             cryptPass=line.split(":")[1].strip(' ')     ## 获得密码字段
#             print ("[*] Cracking Password for:"+user)
#             testPass(cryptPass)

# main()

import re

def split_string_ignore_quotes(string):
    # 匹配逗号前后的引号内的内容
    pattern = r'(?<=\")\s*,\s*(?=\")'
    split_string = re.split(pattern, string)
    return split_string

# 测试示例
my_string = 'This is "some content", and "another, example"'
result = split_string_ignore_quotes(my_string)
print(result)