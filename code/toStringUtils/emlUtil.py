import email
import base64
import os
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup


"""
emlUtil: 解析邮件
1. 解析邮件头信息
2. 解析正文格式: "text/html", "text/plain"
3. 解析附件: xlsx
"""
from util.logUtils import LoggerSingleton
TAG = "toStringUtils.emlUtil.py-"
logger = LoggerSingleton().get_logger()


# 读取eml中的文本和附件
def eml_file(eml_file_path):
    result_image_path = "../workspace/eml"
    os.makedirs(result_image_path, exist_ok=True)
    # 读取eml文件内容
    with open(eml_file_path, 'r', encoding='utf-8') as eml_file:
        eml_content = eml_file.read()

    # 解析邮件
    msg = email.message_from_string(eml_content)

    # 提取关键信息到一个字典
    email_info = {
        "X-Pm-Content-Encryption": msg["X-Pm-Content-Encryption"],
        "X-Pm-Origin": msg["X-Pm-Origin"],
        "Subject": msg["Subject"],
        "From": msg["From"],
        "Date": msg["Date"],
        "Mime-Version": msg["Mime-Version"],
        "To": msg["To"],
        "X-Pm-Scheduled-Sent-Original-Time": msg["X-Pm-Scheduled-Sent-Original-Time"],
        "X-Pm-Recipient-Authentication": msg["X-Pm-Recipient-Authentication"],
        "X-Pm-Recipient-Encryption": msg["X-Pm-Recipient-Encryption"]
    }

    # 提取正文和保存附件
    for part in msg.walk():
        content_type = part.get_content_type()

        if content_type == "text/plain":
            body = part.get_payload(decode=True).decode('utf-8')

        elif content_type == "text/html":
            body = part.get_payload(decode=True).decode('utf-8')
            body = html_extract(body)

        elif "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in content_type:
            filename = part.get_filename()
            if filename:
                # 解码文件名
                decoded_filename = email.header.decode_header(filename)[0]
                attachment_filename, charset = decoded_filename
                if isinstance(attachment_filename, bytes):
                    attachment_filename = attachment_filename.decode(
                        charset or 'utf-8')

                # 为了确保文件名只包含合法字符，去除非法字符
                attachment_filename = re.sub(
                    r'[\/:*?"<>|]', '', attachment_filename)
                attachment_filename = attachment_filename.replace(
                    ".xl", ".xlsx")
                result_image_path += "/"
                attachment_path = os.path.join(
                    result_image_path, attachment_filename)

                # 解码并保存附件
                attachment_data = part.get_payload(decode=True)
                with open(attachment_path, 'wb') as attachment_file:
                    attachment_file.write(attachment_data)
                logger.info(TAG+f"Saved attachment: {attachment_path}")

    # print(body)
    email_info["body"] = body
    # 转换为JSON格式
    # return json.dumps(email_info, indent=4, ensure_ascii=False)
    return body


def html_extract(body):
    # 创建BeautifulSoup对象
    soup = BeautifulSoup(body, 'html.parser')
    # 找到所有的<p>标签
    p_tags = soup.find_all('p')

    # 创建一个列表来存储<p>标签中的文本
    p_text_list = []

    # 提取<p>标签中的文本并存储到列表中
    for p_tag in p_tags:
        p_text = p_tag.get_text().strip()
        p_text_list.append(p_text)

    p_text_string = '\n'.join(p_text_list)

    # 找到表格标签
    table = soup.find('table')

    if table:
        # 创建一个列表来存储表格数据
        table_data = []

        # 遍历表格行
        for row in table.find_all('tr'):
            row_data = []
            # 遍历行中的单元格
            for cell in row.find_all(['th', 'td']):
                row_data.append(cell.get_text().strip())
            table_data.append(row_data)

        # 列名列表
        columns = table_data[0]
        # 生成 JSON 格式数据
        json_data = []
        for row in table_data[1:]:
            row_dict = {}
            for i, value in enumerate(row):
                column_name = columns[i]
                row_dict[column_name] = value
            json_data.append(row_dict)

        result = {
            'text': p_text_string,
            'table': json_data
        }
    else:
        result = {
            'text': p_text_string
        }

    return json.dumps(result, indent=4, ensure_ascii=False)


# res = eml_file("data/xxx部门弱口令漏洞问题和整改 2023-05-25T17_27_32+08_00.eml", "test/eml")
# print(res)
