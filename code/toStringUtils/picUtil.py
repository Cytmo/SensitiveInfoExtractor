import re
from util import globalVar
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
"""

# 全局OCR引擎配置
OCR_CONFIG = {
    'use_gpu': False,
    'show_log': False,
    'lang': 'ch',
    'max_batch_size': 1,
    'use_angle_cls': False,  # 关闭角度检测，提高速度
    'det': False,  # 如果只需识别文字，可关闭检测
    'rec': True,   # 开启识别
}

# 初始化OCR引擎
def init_ocr_engine():
    try:
        logger.info(TAG + "初始化OCR引擎...")
        ocr_engine = PaddleOCR(**OCR_CONFIG)
        logger.info(TAG + "OCR引擎初始化成功")
        return ocr_engine
    except Exception as e:
        logger.error(TAG + f"OCR引擎初始化失败: {str(e)}")
        # 返回None以便调用处进行错误处理
        return None

# 共享的OCR引擎实例
ocr_engine = None

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
        return image_paths
    elif os.path.isfile(path):
        _, ext = os.path.splitext(path)
        if ext.lower() in image_extensions:
            return [path]

    return []


def compress_image(image_path):
    return
    # return
    logger.debug(TAG+"compress_image(): "+image_path)
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    logger.debug(TAG+"image_width: "+str(w) + "image_height: "+str(h))

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

    # [# print(item) for item in res]
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
        logger.debug(TAG+"ppt_and_dps_file(): "+image_path)
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
        logger.debug(TAG+"ppt_and_dps_file(): "+image_path)
        image_info = ocr_textract(image_path)
        if not len(image_info) == 0:
            image_string = "\n".join(image_info)
            image_all_text = image_all_text+"\n"+image_string
    return image_all_text


def calculate_image_md5(image_path):
    try:
        # 打开图片文件并计算 MD5 哈希值
        with open(image_path, 'rb') as file:
            image_data = file.read()
            md5_hash = hashlib.md5(image_data).hexdigest()
        return md5_hash
    except FileNotFoundError:
        return None


def find_image_by_hash(hash_to_find):
    # 在全局字典中查找哈希值
    if hash_to_find in globalVar._pic_hash:
        return globalVar._pic_hash[hash_to_find]
    else:
        return False


# 定义自定义排序函数，提取文件名中的数字部分并进行比较
def custom_sort_key(filename):
    match = re.search(r'image(\d+)\.(png|jpg)', filename)
    if match:
        return int(match.group(1))
    return float('inf')  # 如果没有匹配到数字部分，默认使用正无穷大


# 使用百度PaddleOCR表格形式识别, 输入为包含图片路径的list
def ocr_table_batch(folder_path):
    ocr_result = []
    try:
        table_engine = PPStructure(show_log=False, layout=False,
                                 use_gpu=False,  # 确保使用CPU
                                 max_batch_size=1,  # 限制批处理大小
                                 lang="ch")  # 添加语言参数

        image_paths = sorted(read_all_pic(folder_path), key=custom_sort_key)

        for image_path in image_paths:

            single_pic_hash = calculate_image_md5(image_path)

            result = find_image_by_hash(single_pic_hash)

            if result == False:
                logger.debug(TAG+"ocr_table_batch() with new hash: "+image_path)
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
                    filtered_list.append(row)

                # 补全二维list
                final_list = [filtered_list[0]]+pad_2d_list(filtered_list[1:])

                logger.debug(TAG+"Picture result")
                [logger.debug(data) for data in final_list]

                globalVar._pic_hash[single_pic_hash] = final_list
                ocr_result.append(final_list)
            else:
                logger.debug(TAG+"ocr_table_batch() with old hash: "+image_path)
                ocr_result.append(result)

        return ocr_result
    except Exception as e:
        logger.error(TAG + f"表格OCR处理失败: {str(e)}")
        # 在发生错误时返回空结果，避免程序崩溃
        return []


# 补全二维list
def pad_2d_list(input_2d_list):

    # 找到最长的行的长度
    max_length = max(len(row) for row in input_2d_list)

    # 遍历二维列表并添加空格
    padded_list = []
    for row in input_2d_list:
        if len(row) < max_length:
            # 计算需要添加的空格数量
            num_spaces = max_length - len(row)
            # 添加空格到当前行
            padded_row = row + [""] * num_spaces
            padded_list.append(padded_row)
        else:
            padded_list.append(row)

    # 检查每列是否全为空字符串，如果不是则保留该列
    filtered_data = [col for col in zip(
        *padded_list) if any(col) or not all(c == "" for c in col)]

    # 转置筛选后的数据，得到二维列表
    filtered_data_transposed = [list(col) for col in zip(*filtered_data)]

    return filtered_data_transposed
