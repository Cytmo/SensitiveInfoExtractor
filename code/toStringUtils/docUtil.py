import os
import docx
from docx import Document


# 提取docx里面的文本与图片
def read_docx_text_and_pic(file_path, result_path):
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
                img_name = os.path.basename(rel.target_ref)
                img_data = rel.target_part.blob
                img_path = os.path.join(result_path, img_name)

                with open(img_path, "wb") as f:
                    f.write(img_data)

                print(f"Image '{img_name}' saved to '{result_path}'")

        return '\n'.join(text)

    except Exception as e:
        print("Error:", e)


# docx_file_path = 'data/office/test_pic_txt.docx'  # 替换为实际的 .docx 文件路径
# result_image_path = 'test/image'  # 替换为实际的图片保存路径
# docx_text = read_docx_text_and_pic(docx_file_path, result_image_path)
# print("Text Content:")
# print(docx_text)
