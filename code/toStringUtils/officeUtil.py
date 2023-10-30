import aspose.words as aw
import re
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


######################### pdf file ########################################


# 提取pdf文档中的文本和图片
def pdf_file(file_path):

    pdf_file_name = file_path.split("/")[-1]
    result_image_path = "../workspace/image/pdf/"+pdf_file_name+'/'
    os.makedirs(result_image_path, exist_ok=True)

    try:
        pdf = fitz.open(file_path)
        text = ""

        for itm, page in enumerate(pdf):
            try:
                tupleImage = page.get_images()
                text += page.get_text("text")
                for xref0 in tupleImage:
                    xref = xref0[0]
                    img = pdf.extract_image(xref)
                    ext = img['ext']
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
                    imageFilename = os.path.join(
                        result_image_path, f"{timestamp}_pdf_image_{itm}_{xref}.{ext}")
                    imgout = open(imageFilename, 'wb')
                    imgout.write(img["image"])
                    imgout.close()
            except:
                continue
        pdf.close()

        logger.info(TAG+"pdf_file()-文本信息-"+text)

        # 解析图片信息
        image_all_text_res = ""
        if globalVar.flag_list[0] == True:
            image_all_text = ocr_table_batch(result_image_path)
            # image_all_text = ocr_batch_textract(image_dir)
            logger.info(TAG+"pdf_file()-image_all_text: ")
            for row in image_all_text:
                # logger.info(row)
                try:
                    single_result = " ".join(
                        [element for sublist in row[1:] for element in sublist])
                    image_all_text_res += single_result
                except IndexError as e:
                    # 处理 IndexError 异常
                    logger.error(e)
            logger.info(TAG+"pdf_file()-图片文本信息-"+image_all_text_res)
        else:
            logger.info(TAG+"pdf_file()-不处理文件内部的图片!!")

        return text+"\n"+image_all_text_res
    except Exception as e:
        logger.error(e)
        return ""


######################### office/wps file ########################################


# 1-1.解析.doc/.wps/.docx
def docs_file(file_path, type):
    if type == ".doc":
        logger.info(TAG+"docs_file(): .doc")
        doc_file_dir = "../workspace/office/doc/"
        result_image_path = "../workspace/image/office/doc"
        docx_path = doc_file_dir + \
            file_path.replace(".doc", ".docx").split("/")[-1]
    elif type == ".wps":
        logger.info(TAG+"docs_file(): .wps")
        doc_file_dir = "../workspace/wps/wps/"
        result_image_path = "../workspace/image/wps/wps"
        docx_path = doc_file_dir + \
            file_path.replace(".doc", ".docx").split("/")[-1]
    elif type == ".docx":
        logger.info(TAG+"docs_file(): .docx")
        result_image_path = "../workspace/image/wps/wps"
        image_dir = f"{result_image_path}/{doc_docx_name}/"
        return docx_file_info_extract(file_path, image_dir)
    else:
        return ""

    os.makedirs(doc_file_dir, exist_ok=True)
    logger.info(TAG+"docs_file(): "+docx_path)

    os.makedirs(result_image_path, exist_ok=True)
    doc_docx_name = file_path.split("/")[-1]

    # 使用Aspose.Words将.doc转换为.docx
    try:
        doc = aw.Document(file_path)
        doc.save(docx_path, aw.SaveFormat.DOCX)
        logger.info(TAG+"docs_file(): "+"Document conversion successful!")

        image_dir = f"{result_image_path}/{doc_docx_name}/"

        return docx_file_info_extract(docx_path, image_dir)
    except Exception as e:
        logger.error(e)
        return ""


# 1-2.提取.docx中的文本和图片文本信息
def docx_file_info_extract(docx_path, image_dir):
    logger.info(TAG+"docx_file_info_extract(): "+docx_path+"  "+image_dir)
    try:
        target_docx = docx.Document(docx_path)

        # 提取文本
        target_docx_text = ""
        for paragraph in target_docx.paragraphs:
            target_docx_text += paragraph.text + "\n"

        # 保存照片
        os.makedirs(image_dir, exist_ok=True)
        dict_rel = target_docx.part.rels
        for rel in dict_rel:
            rel = dict_rel[rel]
            if "image" in rel.target_ref:
                if not os.path.exists(image_dir):
                    os.makedirs(image_dir)
                img_name = re.findall("/(.*)", rel.target_ref)[0]
                word_name = os.path.splitext(os.path.basename(docx_path))[0]
                img_name = f'{word_name}-{img_name}'
                with open(os.path.join(image_dir, img_name), "wb") as f:
                    f.write(rel.target_part.blob)
         # 去除水印文字
        target_docx_text = target_docx_text.replace("Evaluation only.", "")
        # 去除版权信息 去除含有aspose的行
        target_docx_text = target_docx_text.split("\n")
        for i in range(len(target_docx_text)):
            if "Aspose" in target_docx_text[i]:
                target_docx_text[i] = ""
        target_docx_text = "\n".join(target_docx_text)

        logger.info(TAG+"docx_file_info_extract()-文本信息-"+target_docx_text)

        # 解析图片信息
        image_all_text_res = ""
        if globalVar.flag_list[0] == True:
            image_all_text = ocr_table_batch(image_dir)
            # image_all_text = ocr_batch_textract(image_dir)
            logger.info(TAG+"docx_file_info_extract()-image_all_text: ")
            for row in image_all_text:
                # logger.info(row)
                try:
                    single_result = " ".join(
                        [element for sublist in row[1:] for element in sublist])
                    image_all_text_res += single_result
                except IndexError as e:
                    # 处理 IndexError 异常
                    logger.error(e)
            logger.info(TAG+"docx_file_info_extract()-图片文本信息-" +
                        image_all_text_res)
        else:
            logger.info(TAG+"docx_file_info_extract()-不处理文件内部的图片!!")

        return target_docx_text+"\n"+image_all_text_res
    except Exception as e:
        logger.error(e)
        return ""


# 2-1.解析.ppt/.dps/.pptx
def ppts_file(file_path, type):
    if type == ".ppt":
        logger.info(TAG+"ppts_file(): .ppt")
        ppt_file_dir = "../workspace/office/ppt/"
        result_image_path = "../workspace/image/office/ppt"
        pptx_path = ppt_file_dir + \
            file_path.replace(".ppt", ".pptx").split("/")[-1]
    elif type == ".dps":
        logger.info(TAG+"ppts_file(): .dps")
        ppt_file_dir = "../workspace/wps/dps/"
        result_image_path = "../workspace/image/wps/dps"
        pptx_path = ppt_file_dir + \
            file_path.replace(".dps", ".pptx").split("/")[-1]
    elif type == ".pptx":
        logger.info(TAG+"ppts_file(): .pptx")
        ppt_file_dir = "../workspace/wps/pptx/"
        result_image_path = "../workspace/image/office/pptx"
        ppt_pptx_name = file_path.replace(".dps", ".pptx").split("/")[-1]
        return pptx_file_info_extract(file_path, result_image_path, ppt_pptx_name)
    else:
        return ""

    os.makedirs(ppt_file_dir, exist_ok=True)
    logger.info(TAG+"ppt_file(): "+pptx_path)
    os.makedirs(result_image_path, exist_ok=True)
    ppt_pptx_name = file_path.split("/")[-1]

    try:
        with slides.Presentation(file_path) as presentation:
            presentation.save(pptx_path, slides.export.SaveFormat.PPTX)
        return pptx_file_info_extract(pptx_path, result_image_path, ppt_pptx_name)
    except Exception as e:
        logger.error(e)
        return ""


# 2-2.提取.pptx中的文本和图片文本信息
def pptx_file_info_extract(pptx_path, result_image_path, ppt_pptx_name):

    logger.info(TAG+"ppts_file(): " + pptx_path + " " +
                result_image_path + " "+ppt_pptx_name)

    try:

        presentation = Presentation(pptx_path)
        slide_text = []
        for slide_number, slide in enumerate(presentation.slides, start=1):

            image_count = 0
            for shape in slide.shapes:

                # 提取文本内容
                if hasattr(shape, "text"):
                    # 去除水印文字
                    if ("Evaluation only.\nCreated with Aspose.Slides for .NET Standard" not in shape.text):
                        slide_text.append(shape.text)

                # 提取图片
                if shape.shape_type == 13:  # 13 表示图片

                    slide_text.append("$PictureIsHere$")
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

        logger.info(TAG+"pptx_file_info_extract()-文本信息:")
        logger.info(slide_text)

        text_all = " "

        # 解析图片信息
        image_all_text_res = []
        if globalVar.flag_list[0] == True:
            image_folder_path = f"{result_image_path}/{ppt_pptx_name}/"
            image_all_text = ocr_table_batch(image_folder_path)
            # image_all_text = ocr_batch_textract(image_folder_path)
            logger.info(TAG+"ppt_file(): image_all_text: ")
            for row in image_all_text:
                # logger.info(row)
                try:
                    single_result = " ".join(
                        [element for sublist in row[1:] for element in sublist])
                    image_all_text_res.append(single_result)
                except IndexError as e:
                    # 处理 IndexError 异常
                    logger.error(e)
            logger.info(TAG+"pptx_file_info_extract(): 图片文本信息:")
            logger.info(image_all_text_res)
        else:
            logger.info(TAG+"pptx_file_info_extract(): 不处理文件内部的图片!!")

        # 将图片文本信息按顺序插入到文本内部: 文本-文本-图片(如果存在)-文本
        res = replace_picture_texts(slide_text, image_all_text_res)
        res = "\n".join(res)

        return res
    except Exception as e:
        logger.error(e)
        return ""


# 将图片文本信息按顺序插入到文本内部: 文本-文本-图片(如果存在)-文本
def replace_picture_texts(text_list, image_text_list):
    i = 0  # 用于追踪image_all_text_res的索引

    while i < len(text_list):
        if text_list[i] == "$PictureIsHere$":
            if i < len(image_text_list):
                text_list[i] = image_text_list[i]
                i += 1
            else:
                del text_list[i]
        else:
            i += 1

    if i < len(image_text_list):
        text_list.extend(image_text_list[i:])

    return text_list


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
