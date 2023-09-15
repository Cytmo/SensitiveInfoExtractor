from functools import lru_cache
import hashlib
from paddleocr import PaddleOCR
import textract
import os
import cv2
from paddleocr import PPStructure
from bs4 import BeautifulSoup

# 日志模块
from util.logUtils import LoggerSingleton
TAG = "toStringUtils.picUtil.py-"
logger = LoggerSingleton().get_logger()

"""
picUtil: 图片OCR
* 主流OCR: https://www.jianshu.com/p/d19dba26f275
"""


# 读取输入目录或者输入图片的路径处理
def read_all_pic(path, image_extensions=None):
    if image_extensions is None:
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

    if os.path.isdir(path):
        image_paths = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_paths.append(os.path.join(root, file))
             #compress image
        for image_path in image_paths:
            logger.info(TAG+"compress_image(): "+image_path)
            compress_image(image_path)
        return image_paths
    elif os.path.isfile(path):
        _, ext = os.path.splitext(path)
        if ext.lower() in image_extensions:
            logger.info(TAG+"compress_image(): "+path)
            compress_image(path)
            return [path]

    return []

def compress_image(image_path):
    return
    # return
    logger.debug(TAG+"compress_image(): "+image_path)
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    logger.debug(TAG+"image_width: "+str(w)+ "image_height: "+str(h))
    h, w = img.shape[:2]
    # if h > 400 or w > 300:
    #     logger.debug(TAG+"compress_image(): "+image_path)
    #     img = cv2.resize(img, (int(w / 2), int(h / 2)))
    #     # if os.path.exists(image_path):
    #     os.remove(image_path)
    #     cv2.imwrite(image_path, img)
    logger.debug(TAG+"compress_image(): "+image_path)
    max_width = 1000
    max_height = 750

    # 获取原始图像的宽度和高度
    original_height, original_width, _ = img.shape

    # 计算宽度和高度的缩放比例
    width_scale = max_width / original_width
    height_scale = max_height / original_height

    # 选择较小的缩放比例，以保持图像在指定的最大尺寸内
    scale = min(width_scale, height_scale)
    # scale = max(scale,0.7)
    # 根据缩放比例调整图像大小
    img = cv2.resize(img, None, fx=scale, fy=scale)
    # # remove color
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # # 高斯模糊去噪声
    # img = cv2.GaussianBlur(img, (5, 5), 0)
    # threshold_value = 0
    # 二值化处理
    # _, img = cv2.threshold(img, threshold_value,255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    # if os.path.exists(image_path):
    os.remove(image_path)


    cv2.imwrite(image_path, img)

# 1st OCR method: 使用textract中的ocr方式识别图片(tesseract-ocr)
def ocr_textract(file):
    text = textract.process(filename=file, encoding='utf-8')
    # 解码
    decoded_text = text.decode('utf-8')
    lines = decoded_text.strip().split("\n")
    # Optionally, you can convert each line to a list
    res = [item.strip() for item in lines if item.strip() != ""]
    return res


# 2nd OCR method: 使用百度PaddleOCR普通识别
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


# 使用百度PaddleOCR批量普通识别
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
    return image_all_text


# 使用textract_OCR批量普通识别
def ocr_batch_textract(folder_path):
    image_paths = read_all_pic(folder_path)

    image_all_text = ""
    for image_path in image_paths:
        logger.info(TAG+"ppt_and_dps_file(): "+image_path)
        image_info = ocr_textract(image_path)
        if not len(image_info) == 0:
            image_string = "\n".join(image_info)
            image_all_text = image_all_text+"\n"+image_string
    return image_all_text


# 使用百度PaddleOCR表格形式识别, 输入为包含图片路径的list
def ocr_table_batch(folder_path):
    ocr_result = []
    # show_log 打印识别日志
    table_engine = PPStructure(show_log=False,layout=False,\
                               lang="ch",use_gpu=True
                              )

    image_paths = read_all_pic(folder_path)
    # md5_list = []
    # for image_path in image_paths:
    #     # Open the image file in binary mode
    #     with open(image_path, "rb") as file:
    #         # Create an MD5 hash object
    #         md5_hash = hashlib.md5()
    #         # Read the file in chunks and update the hash object
    #         while True:
    #             data = file.read(4096)  # Read 4KB chunks of the file
    #             if not data:
    #                 break
    #             md5_hash.update(data)

    #         # Get the hexadecimal representation of the MD5 hash
    #         md5_value = md5_hash.hexdigest()

    #         # Append the MD5 hash to the list
    #         md5_list.append(md5_value)
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
        filtered_list = []
        image_path = [image_path]
        filtered_list.append(image_path)
        for row in table_data:
            if row != ['']:
                filtered_list.append(row)

        ocr_result.append(filtered_list)

    return ocr_result
