import jieba

# file = open('test/电子邮件', 'r', encoding='utf-8')
text = '''Android手机VPN安装指南
第一步： 打开手机主菜单，选择“设置”，然后选择“无线和网络” 
 
第二步：选择“虚拟专用网设置” 
 
第三步：选择“添加虚拟专用网” 
 
第四步：选择“添加L2TP/IPSec PSK VPN” 
 
第五步：点击输入虚拟专用网名称“l2tp”（此名称可自己随便定义） 
 
第六步：点击填写您所登录的服务器地址219.26.10.120，点击“确定” 
 
第七步：选择“设置IPSec预共享密钥”，共享密钥为“123456”，（注意不要勾选 “启用L2TP密钥”） 
 
第八步： “启用L2TP密钥”不能勾上，DNS搜索范围不用填写，然后返回。
 
 
第九步：点击刚创建的VPN连接登录，用户名和密码为校园信息门户用户名（工号或学号）和密码。
（如：学号：2021140822，初始密码为123456）
 '''



file = open('test/src/main/run_regression.sh', 'r', encoding='utf-8')
text = file.read()
seg_list = jieba.cut(text, cut_all=False)
print("Default Mode: " + "/ ".join(seg_list))  # 精确模式
# for token in seg_list:
#     print(token)
