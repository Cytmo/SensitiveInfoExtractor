import aspose.pydrawing as drawing
from pptx import Presentation
import aspose.slides as slides
import os
import docx
import fitz
from docx import Document
from datetime import datetime
import textract
"""
officeUtil: 解析 docx/pdf/wps/et
"""


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
    return decoded_text


# 提取.et中的文本
def et_file_text(et_file_path):
    if not et_file_path.endswith(".et"):
        return "not .wps file"
    et_doc_name = et_file_path.replace(".et", ".xlsx")
    os.rename(et_file_path, et_doc_name)
    text = textract.process(filename=et_doc_name, encoding='utf-8')
    os.rename(et_doc_name, et_file_path)
    decoded_text = text.decode('utf-8')
    return decoded_text


# 提取ppt中的文本和图片
def ppt_file(ppt_file_path, result_image_path):

    ppt_pptx_path = ppt_file_path.replace(".ppt", ".pptx")
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

    # 去除水印文字
    slide_text = slide_text.replace("Evaluation only.", "")
    slide_text = slide_text.replace(
        "Created with Aspose.Slides for .NET Standard 2.0 23.8.", "")
    slide_text = slide_text.replace("Copyright 2004-2023Aspose Pty Ltd.", "")

    return slide_text


# print(wps_file_text("data/wps/Android手机VPN安装指南.wps"))
# print(et_file_text("data/wps/资产梳理.et"))

# docx_file_path = 'test/test_pic_txt.docx'  # 替换为实际的 .docx 文件路径
# result_image_path = 'test/image'  # 替换为实际的图片保存路径
# docx_text = docx_file_text_and_img(docx_file_path, result_image_path)
# print("Text Content:")
# print(docx_text)

# pdf_file_path = "test/test_pdf.pdf"
# result_image_path = "test/image"
# extracted_text = pdf_file_text_and_img(pdf_file_path, result_image_path)
# print("提取的文本：")
# print(extracted_text)

# print(ppt_file("data/office/20180327081403010127.ppt", "test/image"))
# print(ppt_file("data/office/学生信息管理系统使用介绍.ppt", "test/image"))
