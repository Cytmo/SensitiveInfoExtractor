from datetime import datetime
from paddleocr import PaddleOCR
import textract
import os
import cv2
from paddleocr import PPStructure, save_structure_res
from bs4 import BeautifulSoup
# 日志模块
from util.logUtils import LoggerSingleton
TAG = "toStringUtils.picUtil.py-"
logger = LoggerSingleton().get_logger()

"""
picUtil: 图片OCR
* 主流OCR: https://www.jianshu.com/p/d19dba26f275
"""


# 1st OCR method: 使用textract中的ocr方式识别图片(tesseract-ocr)
# 效果: 表格截图中短文本识别效果较差且顺序错乱, 代码截图识别效果可以
def ocr_textract(file):
    text = textract.process(filename=file, encoding='utf-8')
    # 解码
    decoded_text = text.decode('utf-8')
    lines = decoded_text.strip().split("\n")
    # Optionally, you can convert each line to a list
    res = [item.strip() for item in lines if item.strip() != ""]
    return res


# 2nd OCR method: 使用百度PaddleOCR
# 效果: 识别率很高，但是耗时较长
def ocr_paddleocr(file):
    ocr = PaddleOCR(lang="ch",
                    use_gpu=False,
                    det_model_dir="modes/ocr/paddleORC_model/ch_ppocr_server_v2.0_det_infer/",
                    cls_model_dir="modes/ocr/paddleORC_model/ch_ppocr_mobile_v2.0_cls_infer/",
                    rec_model_dir="modes/ocr/paddleORC_model/ch_ppocr_server_v2.0_rec_infer/")
    result = ocr.ocr(file)
    # 注：
    # result是一个list，每个item包含了文本框，文字和识别置信度
    # line的格式为：
    # [[[3.0, 149.0], [43.0, 149.0], [43.0, 163.0], [3.0, 163.0]], ('人心安', 0.6762619018554688)]
    # 文字框 boxes = line[0]，包含文字框的四个角的(x,y)坐标
    # 文字 txts = line[1][0]
    # 识别置信度 scores = line[1][1]
    res = []
    for line in result:
        for x in line:
            res.append(x[1][0])
    return res


def read_all_pic(path, image_extensions=None):
    if image_extensions is None:
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

    if os.path.isdir(path):
        image_paths = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_paths.append(os.path.join(root, file))
        return image_paths
    elif os.path.isfile(path):
        _, ext = os.path.splitext(path)
        if ext.lower() in image_extensions:
            return [path]
    return []


def ocr_batch_paddle(folder_path):
    image_paths = read_all_pic(folder_path)

    ocr = PaddleOCR(lang="ch",
                    use_gpu=False,
                    det_model_dir="modes/ocr/paddleORC_model/ch_ppocr_server_v2.0_det_infer/",
                    cls_model_dir="modes/ocr/paddleORC_model/ch_ppocr_mobile_v2.0_cls_infer/",
                    rec_model_dir="modes/ocr/paddleORC_model/ch_ppocr_server_v2.0_rec_infer/")

    image_all_text = ""
    for image_path in image_paths:
        logger.info(TAG+"ppt_and_dps_file(): "+image_path)
        image_info = ocr.ocr(image_path)
        res = []
        for line in image_info:
            for x in line:
                res.append(x[1][0])

        if not len(res) == 0:
            image_string = "\n".join(res)
            image_all_text = image_all_text+"\n"+image_string
        #     logger.info(TAG+"ppt_and_dps_file(): handle " +
        #                 image_path + " is not none, str len is "+str(len(image_all_text)))
        # else:
        #     logger.info(TAG+"ppt_and_dps_file(): handle " +
        #                 image_path + " is none")
    return image_all_text


def ocr_batch_textract(folder_path):
    image_paths = read_all_pic(folder_path)

    image_all_text = ""
    for image_path in image_paths:
        logger.info(TAG+"ppt_and_dps_file(): "+image_path)
        image_info = ocr_textract(image_path)
        if not len(image_info) == 0:
            image_string = "\n".join(image_info)
            image_all_text = image_all_text+"\n"+image_string
        #     logger.info(TAG+"ppt_and_dps_file(): handle " +
        #                 image_path + " is not none, str len is "+str(len(image_all_text)))
        # else:
        #     logger.info(TAG+"ppt_and_dps_file(): handle " +
        #                 image_path + " is none")
    return image_all_text


def ocr_table_batch(folder_path):

    ocr_result = []
    table_engine = PPStructure(layout=False, show_log=True)

    image_paths = read_all_pic(folder_path)

    for image_path in image_paths:
        logger.info(TAG+"ocr_table_batch(): "+image_path)
        img = cv2.imread(image_path)
        result = table_engine(img)

        html_code = result[0]["res"]["html"]
        soup = BeautifulSoup(html_code, 'html.parser')

        table = soup.find('table')
        table_data = []
        for row in table.find_all('tr'):
            row_data = [cell.get_text(strip=True)
                        for cell in row.find_all('td')]
            if row_data:
                table_data.append(row_data)

        # 使用for循环遍历原始列表并添加非空的子列表到新列表
        filtered_list = [image_path]
        for row in table_data:
            if row != ['']:
                filtered_list.append(row)

        ocr_result.append(filtered_list)

    return ocr_result
