import email
import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from util import globalVar
from informationEngine.table_extract import single_table_sensitive_extraction
from email.header import decode_header
from email.utils import parseaddr
import base64
from datetime import datetime

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
    time = datetime.now().strftime("%Y%m%d%H%M%S%f")
    result_attach_file_path = "../workspace/eml/" + \
        time+"_"+os.path.basename(eml_file_path)+"/"
    os.makedirs(result_attach_file_path, exist_ok=True)

    # 读取eml文件内容
    with open(eml_file_path, 'r', encoding='utf-8') as eml_file:
        eml_content = eml_file.read()

    # 解析邮件
    msg = email.message_from_string(eml_content)

    # 提取关键信息到一个字典
    email_info = {}
    try:
        email_info = {
            # "X-Pm-Content-Encryption": decode_header(msg["X-Pm-Content-Encryption"]),
            # "X-Pm-Origin": decode_header(msg["X-Pm-Origin"]),
            "Subject": decode_headers(msg["Subject"]),
            "From": decode_headers(msg["From"]),
            "Date": decode_headers(msg["Date"]),
            # "Mime-Version": decode_header(msg["Mime-Version"]),
            "To": decode_headers(msg["To"]),
            "X-Pm-Scheduled-Sent-Original-Time": decode_headers(msg["X-Pm-Scheduled-Sent-Original-Time"]),
            "X-Pm-Recipient-Authentication": decode_headers(msg["X-Pm-Recipient-Authentication"]),
            "X-Pm-Recipient-Encryption": decode_headers(msg["X-Pm-Recipient-Encryption"])
        }
    except Exception as e:
        logger.error(e)

    body = ""
    # 提取正文
    try:
        for part in msg.walk():
            content_type = part.get_content_type()

            if content_type == "text/html":
                body = part.get_payload(decode=True).decode('utf-8')
                body = html_extract(body)
    except Exception as e:
        logger.error(e)

    # 和保存附件
    attach_files_list = []
    try:
        for part in msg.walk():
            if part.get("Content-Disposition"):
                attach_files_list.append(
                    save_attachment(part, result_attach_file_path))
    except Exception as e:
        logger.error(e)

    return [email_info, body, attach_files_list]


# 解析eml中的文本中的html
def html_extract(body):
    logger.debug(TAG+"html_extract():")
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

    table_data = []
    if table:
        # 遍历表格行
        for row in table.find_all('tr'):
            row_data = []
            # 遍历行中的单元格
            for cell in row.find_all(['th', 'td']):
                row_data.append(cell.get_text().strip())
            table_data.append(row_data)
        pd_table_data = pd.DataFrame(table_data)
        logger.debug(TAG+"html_extract():")
        logger.debug(table_data)
        logger.debug(TAG+"html_extract():")
        logger.debug(pd_table_data)
        res = single_table_sensitive_extraction(pd_table_data)
        logger.debug(TAG+"html_extract()-html-res:")
        logger.debug(res)
        result = {
            'text': p_text_string,
            'table': res
        }
    else:
        result = {
            'text': p_text_string
        }

    return result


# 解析eml中的邮件头信息
def decode_headers(header_value):
    decoded_parts = []
    for part, charset in email.header.decode_header(header_value):
        if isinstance(part, bytes):
            decoded_parts.append(part.decode(charset or 'utf-8'))
        else:
            decoded_parts.append(part)
    return ' '.join(decoded_parts)


def save_attachment(part, output_dir):

    file_extension = {"xl": 'xlsx'}

    if part.get_content_maintype() == "multipart":
        for subpart in part.get_payload():
            save_attachment(subpart, output_dir)
    elif part.get("Content-Disposition"):
        filename = part.get_filename()
        if filename:
            decoded_filename, encoding = decode_header(filename)[0]
            if encoding is not None:
                if encoding.lower() in ('b', 'q'):
                    decoded_filename = decoded_filename.encode(
                        encoding).decode('utf-8')
                else:
                    decoded_filename = decoded_filename.decode(encoding)

            # 获取文件名的扩展名  检查是否需要替换扩展名
            extension = decoded_filename.split(".")[-1]
            if extension in file_extension:
                new_extension = file_extension[extension]
                decoded_filename = decoded_filename.replace(
                    extension, new_extension)

            file_path = os.path.join(output_dir, decoded_filename)

            with open(file_path, "wb") as f:
                f.write(part.get_payload(decode=True))
            return file_path
