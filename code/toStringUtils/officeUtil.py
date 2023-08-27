import os
import docx
# import fitz
from docx import Document
from datetime import datetime
import subprocess
"""
officeUtil: 解析 docx/pdf
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



# 提取doc中的文本
def doc_file_text(doc_file_path):
    #使用antiword将doc转换为docx
    command = "antiword {}".format(doc_file_path)
    print("Running "+command)
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # 打印标准输出
    print("标准输出：")
    print(result.stdout)
    if result.stderr != "":
        print("标准错误：")
        print(result.stderr)
    return result.stdout


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




if __name__ == '__main__':
    doc_file_text("data/office/SSLVPNWindows.doc")

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
