import email
import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from util import globalVar
from toStringUtils.officeUtil import xlsx_file
from informationEngine.table_extract import single_table_sensitive_extraction

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
        # "X-Pm-Content-Encryption": decode_header(msg["X-Pm-Content-Encryption"]),
        # "X-Pm-Origin": decode_header(msg["X-Pm-Origin"]),
        "Subject": decode_header(msg["Subject"]),
        "From": decode_header(msg["From"]),
        "Date": decode_header(msg["Date"]),
        # "Mime-Version": decode_header(msg["Mime-Version"]),
        "To": decode_header(msg["To"]),
        "X-Pm-Scheduled-Sent-Original-Time": decode_header(msg["X-Pm-Scheduled-Sent-Original-Time"]),
        "X-Pm-Recipient-Authentication": decode_header(msg["X-Pm-Recipient-Authentication"]),
        "X-Pm-Recipient-Encryption": decode_header(msg["X-Pm-Recipient-Encryption"])
    }

    # 提取正文和保存附件
    attachment_file_info = []
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
                attachment_file_info = xlsx_file(attachment_path)
                logger.info(TAG+"eml_file()-eml_file_res:")
                logger.info(attachment_file_info)

    return [email_info, body, attachment_file_info]


# 解析eml中的文本中的html
def html_extract(body):
    logger.info(TAG+"html_extract():")
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
        logger.info(TAG+"html_extract():")
        logger.info(table_data)
        logger.info(TAG+"html_extract():")
        logger.info(pd_table_data)
        res = single_table_sensitive_extraction(pd_table_data)
        logger.info(TAG+"html_extract()-html-res:")
        logger.info(res)
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
def decode_header(header_value):
    decoded_parts = []
    for part, charset in email.header.decode_header(header_value):
        if isinstance(part, bytes):
            decoded_parts.append(part.decode(charset or 'utf-8'))
        else:
            decoded_parts.append(part)
    return ' '.join(decoded_parts)
