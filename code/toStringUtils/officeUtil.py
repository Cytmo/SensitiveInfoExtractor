import xlrd
from pptx import Presentation
import aspose.slides as slides
import os
import docx
import fitz
from datetime import datetime
import textract
from util import globalVar
from toStringUtils.picUtil import *


"""
officeUtil: 解析 docx/pdf/wps/et
"""


# 日志模块
from util.logUtils import LoggerSingleton
TAG = "toStringUtils.officeUtil.py-"
logger = LoggerSingleton().get_logger()


# 提取docx里面的文本与图片
def docx_file_text_and_img(file_path, result_path):
    try:
        doc = docx.Document(file_path)
        dict_rel = doc.part._rels

        if not os.path.exists(result_path):
            os.makedirs(result_path)

        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)

        for rel_id, rel in dict_rel.items():
            if "image" in rel.target_ref:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
                img_name = timestamp+"_docx_"+os.path.basename(rel.target_ref)
                img_data = rel.target_part.blob
                img_path = os.path.join(result_path, img_name)

                with open(img_path, "wb") as f:
                    f.write(img_data)

        return '\n'.join(text)

    except Exception as e:
        print("Error:", e)


# 提取pdf文档中的文本和图片
def pdf_file_text_and_img(pdf_file_path, result_image_path):
    doc = fitz.open(pdf_file_path)
    text = ""
    for itm, page in enumerate(doc):
        try:
            tupleImage = page.get_images()
            text += page.get_text("text")
            for xref0 in tupleImage:
                xref = xref0[0]
                img = doc.extract_image(xref)
                ext = img['ext']
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
                imageFilename = os.path.join(
                    result_image_path, f"{timestamp}_pdf_image_{itm}_{xref}.{ext}")
                imgout = open(imageFilename, 'wb')
                imgout.write(img["image"])
                imgout.close()
        except:
            continue
    doc.close()
    return text


# 提取.wps中的文本
def wps_file_text(wps_file_path):
    if not wps_file_path.endswith(".wps"):
        return "not .wps file"
    wps_doc_name = wps_file_path.replace(".wps", ".doc")
    os.rename(wps_file_path, wps_doc_name)
    text = textract.process(filename=wps_doc_name, encoding='utf-8')
    os.rename(wps_doc_name, wps_file_path)
    decoded_text = text.decode('utf-8')
    decoded_text = decoded_text.replace("[pic]", "")
    return decoded_text


# 提取.ppt和.wps中的文本和图片
def ppt_and_dps_file(ppt_file_path):
    if ppt_file_path.endswith(".ppt"):
        ppt_file_dir = "../workspace/ppt/"
        ppt_pptx_path = ppt_file_dir + \
            ppt_file_path.replace(".ppt", ".pptx").split("/")[-1]

    if ppt_file_path.endswith(".dps"):
        ppt_file_dir = "../workspace/dps/"
        ppt_pptx_path = ppt_file_dir + \
            ppt_file_path.replace(".dps", ".pptx").split("/")[-1]

    os.makedirs(ppt_file_dir, exist_ok=True)
    logger.info(TAG+"ppt_and_dps_file(): "+ppt_pptx_path)
    result_image_path = "../workspace/image"
    os.makedirs(result_image_path, exist_ok=True)
    ppt_pptx_name = ppt_file_path.split("/")[-1]
    with slides.Presentation(ppt_file_path) as presentation:
        presentation.save(ppt_pptx_path, slides.export.SaveFormat.PPTX)

    presentation = Presentation(ppt_pptx_path)
    slide_text = ""
    for slide_number, slide in enumerate(presentation.slides, start=1):
        # 提取文本内容
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                slide_text += shape.text + "\n"

        image_count = 0
        for shape in slide.shapes:
            if shape.shape_type == 13:  # 13 表示图片
                # 提取图片
                image_dir = f"{result_image_path}/{ppt_pptx_name}/"
                os.makedirs(image_dir, exist_ok=True)
                image_count += 1
                image = shape.image
                image_bytes = image.blob
                image_ext = image.ext
                image_filename = image_dir + \
                    f"{ppt_pptx_name}_slide_{slide_number}_image_{image_count}.{image_ext}"

                with open(image_filename, "wb") as img_file:
                    img_file.write(image_bytes)

    # 解析图片信息
    image_folder_path = f"{result_image_path}/{ppt_pptx_name}/"

    image_all_text = ocr_table_batch(image_folder_path)
    # image_all_text = ocr_batch_textract(image_folder_path)
    logger.info(TAG+"ppt_and_dps_file(): image_all_text: ")
    for row in image_all_text:
        logger.info(row)
    image_all_text = ""

    # 去除水印文字
    slide_text = slide_text.replace("Evaluation only.", "")
    slide_text = slide_text.replace(
        "Created with Aspose.Slides for .NET Standard 2.0 23.8.", "")
    slide_text = slide_text.replace(
        "Copyright 2004-2023Aspose Pty Ltd.", "")

    return slide_text+"\n"+image_all_text


# 提取.xlsx中的文本
# TODO:需要更新
def xlsx_file(file_path):
    # 打开 Excel 文件
    workbook = xlrd.open_workbook(file_path)

    # 获取所有工作簿的名称
    sheet_names = workbook.sheet_names()

    # 遍历工作簿并读取内容
    workbook_contents = []

    for sheet_name in sheet_names:
        worksheet = workbook.sheet_by_name(sheet_name)

        # 读取工作簿的内容行
        rows = [worksheet.row_values(row_num)
                for row_num in range(worksheet.nrows)]

        workbook_contents.append((sheet_name, rows))

    # 关闭工作簿
    workbook.release_resources()
    del workbook

    res = xlsx_format(workbook_contents)

    if len(res) == 1:
        return res[0]
    return res


# 对提取.xlsx中的文本进行格式化成表格数据结构
def xlsx_format(workbook_contents):
    xlsx_file_info = []

    for sheet_name, rows in workbook_contents:
        sheet_data = []

        for row in rows:
            row_data = []

            for value in row:
                if value is None:
                    row_data.append("none")
                elif isinstance(value, datetime):
                    row_data.append(handle_datetime(value))
                else:
                    row_data.append(value)

            if len(row_data) > 0:
                sheet_data.append(row_data)

        xlsx_file_info.append(sheet_data)

    xlsx_file_info = xlsx_remove_irrelevant_columns(xlsx_file_info)

    return xlsx_file_info


# 对提取.xlsx中的多张表格信息进行敏感信息匹配和提取
def xlsx_remove_irrelevant_columns(xlsx_file_info):

    sensitive_word = globalVar.get_sensitive_word()

    res = []

    for item in xlsx_file_info:

        res_one_item = one_table_remove_irrelevant_columns(
            sensitive_word, item)

        if not len(res_one_item) == 0:
            res.append(res_one_item)

    return res


# 对提取.xlsx中的单张表格信息进行敏感信息匹配和提取
def one_table_remove_irrelevant_columns(sensitive_word, item):
    column_names = item[0]
    # 用于存储要保留的列索引
    valid_columns = []
    # 遍历每一列
    for idx, column_name in enumerate(column_names):
        # 遍历敏感词列表
        for word in sensitive_word:
            # 如果列名是敏感词的子字符串，则保留该列
            if word['name'] in column_name:
                valid_columns.append(idx)
                break

    filtered_info = []

    # 重新构建info，只包括要保留的列
    if len(valid_columns) != 0:
        filtered_info = [[row[i] for i in valid_columns] for row in item]
        # filtered_info = [[item for item in row if item != ""]
        #                  for row in filtered_info]

        # 提取列名
        column_names = filtered_info[0]
        # 初始化一个空的 JSON 列表
        json_data = []

        # 遍历行数据，将每一行转换为字典
        for row in filtered_info[1:]:
            row_dict = {}
            for i, value in enumerate(row):
                # 使用列名作为键，行中的值作为值
                if value != "":
                    row_dict[column_names[i]] = value
            json_data.append(row_dict)
        filtered_info = json_data

    return filtered_info


# 对xlsx中的时间进行格式化
def handle_datetime(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    return None
