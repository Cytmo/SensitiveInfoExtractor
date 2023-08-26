import jieba

file = open('test/电子邮件', 'r', encoding='utf-8')
text = file.read()

seg_list = jieba.cut(text, cut_all=False)
print("Default Mode: " + "/ ".join(seg_list))  # 精确模式
# for token in seg_list:
#     print(token)