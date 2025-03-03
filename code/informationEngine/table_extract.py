from collections import Counter
import pandas as pd
import queue
import yaml
import re
from informationEngine.info_core import *
from util.logUtils import LoggerSingleton
TAG = "informationEngine.table_extract-"
logger = LoggerSingleton().get_logger()


def contains_chinese(data):
    pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(pattern.search(str(data)))

def is_pure_chinese(text):
    # 使用正则表达式匹配中文字符
    pattern = re.compile('[\u4e00-\u9fa5]+')
    result = pattern.findall(str(text))
    
    # 如果匹配结果等于原始字符串，表示字符串只包含中文字符
    return ''.join(result) == text
# # print(data.shape[0])


def init_sensitive_word(yml_file_path):
    global _sensitive_word_tmp
    # 读取YAML文件
    with open(yml_file_path, 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)

    chinese_patterns = data.get('chinese_patterns', [])
    english_patterns = data.get('english_patterns', [])

    sensitive_word_origin = chinese_patterns+english_patterns

    _sensitive_word_tmp = {item.get('name'): item.get(
        'name') for item in sensitive_word_origin}


def process_bind_prase(data):

    str_list = [str(item) for item in data]

    return begin_info_extraction(" ".join(str_list))


def line_spilit_index(empty_index):
    index_single = []
    index_prase = []
    index_last = -1
    for index in empty_index:
        if index > index_last+1:
            if index == index_last+2:
                index_single.append(index_last+1)
            else:
                index_prase.append([index_last+1, index])
        index_last = index
    return index_single, index_prase


def line_spilit_index_key(empty_index):
    index_single = []
    index_prase = []
    index_last = 0
    for index in empty_index:
        if index > index_last:
            if index == index_last+1:
                index_single.append(index_last)
            else:
                index_prase.append([index_last, index])
        index_last = index
    return index_single, index_prase


def count_most_frequent_strings(data):
    counts = {}

    # 遍历每一列
    for j in range(len(data[0])):
        unique_strings = set()
        column_counts = {}

        # 遍历每一行
        for i in range(len(data)):
            element = data[i][j]
            if element != '':
                unique_strings.add(element)
                column_counts[element] = column_counts.get(element, 0) + 1

        # 找到当前列中出现最多的字符串
        most_frequent = max(column_counts, key=column_counts.get)
        counts[j] = (most_frequent, column_counts[most_frequent],
                     len(unique_strings))

    return counts

def shade_tag_sensitive(word_list):
    tag_list_tmp = []
    for item in word_list:
        if is_pure_chinese(item):
            tag_list_tmp.append(None)
        else:
            tag_list_tmp.append(find_tag_sensitive(item))
    
    filtered_list = [item for item in tag_list_tmp if item is not None]

    if not filtered_list:
        return None

    # Counting the frequency of each item
    item_counts = Counter(filtered_list)
    most_common_item, count = item_counts.most_common(1)[0]
    if count / len(word_list)>0.7:
        return most_common_item
    return None



def find_tag_sensitive(word):
    word = str(word)
    global _sensitive_word_tmp
    # print(_sensitive_word_tmp)
    result = _sensitive_word_tmp.get(word)
    if result is not None:
        return result
    for key, value in _sensitive_word_tmp.items():
        pattern = re.escape(key)
        matches = re.findall(pattern, word)

        # 如果找到匹配结果，添加到结果列表中
        if matches:
            return value
    return None


init_sensitive_word('config/sensitive_word.yml')
global _sensitive_word_tmp


class XlsxDevider:
    def __init__(self, data):
        self.xlsx_data = data
        self.raw_pass = False
        self.col_pass = False
        self.key_pass = False
        # 可扩展：模糊类型分割

    # 行分割
    @classmethod
    def process_raw(cls, xlsxDevider):
        queue_tmp = queue.Queue()

        empty_rows = xlsxDevider.xlsx_data.isnull().all(axis=1)
        empty_rows_index = empty_rows[empty_rows].index.to_list()

        # 所有空行数1+才有效
        if len(empty_rows_index) < 2:
            return queue_tmp

        # 空行分割计算
        empty_rows_index.insert(0, -1)
        empty_rows_index.append(len(empty_rows))
        [index_single, index_prase] = line_spilit_index(empty_rows_index)

        # 分割单行和多行
        for index in index_single:
            data_part = pd.DataFrame(
                xlsxDevider.xlsx_data.iloc[index].copy()).reset_index(drop=True)
            queue_tmp.put(XlsxDevider(data_part))

        for prases in index_prase:
            data_part = xlsxDevider.xlsx_data.iloc[prases[0]:prases[1]].copy(
            ).reset_index(drop=True)
            queue_tmp.put(XlsxDevider(data_part))

        return queue_tmp

    @classmethod
    def process_col(cls, xlsxDevider):
        queue_tmp = queue.Queue()

        empty_cols = xlsxDevider.xlsx_data.isnull().all()
        empty_cols_index = empty_cols[empty_cols].index.to_list()

        if len(empty_cols_index) < 2:
            return queue_tmp

        empty_cols_index.insert(0, -1)
        empty_cols_index.append(len(empty_cols))
        [index_single, index_prase] = line_spilit_index(empty_cols_index)

        for index in index_single:
            data_part = pd.DataFrame(
                xlsxDevider.xlsx_data.iloc[:, index].copy()).reset_index(drop=True)
            queue_tmp.put(XlsxDevider(data_part))

        for prases in index_prase:
            data_part = xlsxDevider.xlsx_data.iloc[:, prases[0]:prases[1]].copy(
            ).reset_index(drop=True)
            data_part.columns = list(range(0, prases[1]-prases[0]))
            queue_tmp.put(XlsxDevider(data_part))

        return queue_tmp

    @classmethod
    def process_key(cls, xlsxDevider):
        queue_tmp = queue.Queue()
        empty_rows_index = []
        # 行关键词检测
        for index, row in xlsxDevider.xlsx_data.iterrows():
            word_condition = [_sensitive_word_tmp.get(
                element) for element in row]
            if len(list(set([x for x in word_condition if x is not None]))) > 1:
                empty_rows_index.append(index)

        if len(empty_rows_index) > 1 or (len(empty_rows_index) == 1 and empty_rows_index[0] != 0):

            empty_rows_index.insert(0, 0)
            empty_rows_index.append(xlsxDevider.xlsx_data.shape[0])
            [index_single, index_prase] = line_spilit_index_key(
                empty_rows_index)

            for index in index_single:
                data_part = pd.DataFrame(
                    xlsxDevider.xlsx_data.iloc[index].copy()).reset_index(drop=True)
                queue_tmp.put(XlsxDevider(data_part))

            for prases in index_prase:
                data_part = xlsxDevider.xlsx_data.iloc[prases[0]:prases[1]].copy(
                ).reset_index(drop=True)
                queue_tmp.put(XlsxDevider(data_part))

            return queue_tmp

        # 列关键词检测
        empty_cols_index = []
        for index, (col_name, col) in enumerate(xlsxDevider.xlsx_data.items()):
            word_condition = [_sensitive_word_tmp.get(
                element) for element in col]
            if len(list(set([x for x in word_condition if x is not None]))) > 1:
                empty_cols_index.append(index)

        if len(empty_cols_index) > 1 or (len(empty_cols_index) == 1 and empty_cols_index[0] != 0):
            empty_cols_index.insert(0, 0)
            empty_cols_index.append(xlsxDevider.xlsx_data.shape[1])
            [index_single, index_prase] = line_spilit_index_key(
                empty_cols_index)

            # # print(empty_cols_index)

            for index in index_single:
                data_part = pd.DataFrame(
                    xlsxDevider.xlsx_data.iloc[:, index].copy()).reset_index(drop=True)
                queue_tmp.put(XlsxDevider(data_part))

            for prases in index_prase:
                data_part = xlsxDevider.xlsx_data.iloc[:, prases[0]:prases[1]].copy(
                ).reset_index(drop=True)
                data_part.columns = list(range(0, prases[1]-prases[0]))
                queue_tmp.put(XlsxDevider(data_part))

        return queue_tmp

    @classmethod
    def process_xlsx(cls, xlsxDevider):
        queue_tmp = queue.Queue()
        if xlsxDevider.xlsx_data.shape[0] == 1 or xlsxDevider.xlsx_data.shape[1] == 1:
            xlsxDevider.raw_pass = True
            xlsxDevider.col_pass = True
            xlsxDevider.key_pass = True
            return queue_tmp

        if not xlsxDevider.raw_pass:
            queue_tmp = XlsxDevider.process_raw(xlsxDevider)
            if queue_tmp.empty():
                xlsxDevider.raw_pass = True
            else:
                return queue_tmp

        if not xlsxDevider.col_pass:
            queue_tmp = XlsxDevider.process_col(xlsxDevider)
            if queue_tmp.empty():
                xlsxDevider.col_pass = True
            else:
                return queue_tmp

        if not xlsxDevider.key_pass:
            queue_tmp = XlsxDevider.process_key(xlsxDevider)
            if queue_tmp.empty():
                xlsxDevider.key_pass = True
            else:
                return queue_tmp

        return queue_tmp

    def check_Pass(self):
        return self.raw_pass and self.col_pass and self.key_pass
    
    def raw_extract(self):
        json_data = []
        # 行反向映射
        word_condition_last=[]
        use_data = self.xlsx_data.iloc[1:]
        for index, (col_name, col) in enumerate(use_data.items()):
            word_condition_last.append(shade_tag_sensitive(col))
        

        # 首行，首行校验->逐行提取
        word_condition_key = [element if find_tag_sensitive(
            element) is not None else None for element in self.xlsx_data.iloc[0]]
        
        word_condition = [b if a is None else a for a, b in zip(word_condition_last, word_condition_key)]

        word_index = [index for index, value in enumerate(
            word_condition) if value is not None]
        if len(word_index) > 1:
            use_data = self.xlsx_data.iloc[1:]
            for ind, row in use_data.iterrows():
                nan_flag = pd.isna(row)
                sub_result = {word_condition[index]: row.values[index]
                              for index in word_index if not nan_flag[index]}
                if len(sub_result) > 1:
                    json_data.append(sub_result)
        return json_data

    # 敏感数据提取
    def extract_sensitive_xlsx(self):
        json_data = []
        # if self.check_Pass():
        #     # print("处理敏感数据中，敏感数据大小为", self.xlsx_data.shape)
        # else:
        #     # print("处理敏感数据中，敏感数据大小为", self.xlsx_data.shape)
        #     # print("推荐优先处理分块以提高处理结果")
        # 单行单列的提取
        if self.xlsx_data.shape[0] < 1:
            return json_data
        elif self.xlsx_data.shape[0] == 1:
            return process_bind_prase(self.xlsx_data.iloc[0].tolist())
        if self.xlsx_data.shape[1] < 1:
            return json_data
        elif self.xlsx_data.shape[1] == 1:
            return process_bind_prase(self.xlsx_data.iloc[:, 0].tolist())

        # 行关键词映射及关键词补全
        json_data = self.raw_extract()
        if len(json_data) > 0:
            return json_data
        self.xlsx_data = self.xlsx_data.transpose()

        # 列关键词映射及关键词补全
        json_data = self.raw_extract()
        if len(json_data) > 0:
            return json_data
        self.xlsx_data = self.xlsx_data.transpose()

        # 行模糊提取
        json_data = self.xlsx_fuzz_extract()
        if len(json_data) > 0:
            return json_data
        self.xlsx_data = self.xlsx_data.transpose()

        # 列模糊提取
        json_data = self.xlsx_fuzz_extract()
        if len(json_data) > 0:
            return json_data
        self.xlsx_data = self.xlsx_data.transpose()

        str_last_in = self.xlsx_data.to_string(index=False, header=False)
        str_last_in = fix_ocr(str_last_in)
        str_last_in = str_last_in.replace("\"", " ")
        str_last_in = str_last_in.replace("'", " ")
        str_last_in = str_last_in.replace("=", " ")
        logger.debug(TAG+"testest"+str_last_in)
        return begin_info_extraction(str_last_in)

    def xlsx_fuzz_extract(self):
        json_data = []
        # 行模糊提取
        chinese_cols = self.xlsx_data.apply(
            lambda col: col.apply(contains_chinese)).any()
        chinese_columns = chinese_cols[chinese_cols].index
        # 不剩两列以上数据直接返回
        if not self.xlsx_data.shape[1]-len(chinese_columns) > 1:
            return json_data
        use_data = self.xlsx_data.drop(
            chinese_columns, axis=1).reset_index(drop=True)
        use_data.columns = list(range(0, use_data.shape[1]))
        guss_tag_list = []
        # # print(use_data)
        # 逐行扫
        for ind, row in use_data.iterrows():
            # # print(row)
            #行拼接
            str_use = row.apply(lambda x: str(x)).str.cat(sep=' ')
            # # print(str_use)
            #行提取
            text = plain_text_info_extraction(str_use, False, True, True)
            text = text.split(' ')
            #行标签
            guss_tag = []
            for i in range(len(text)-1):
                if is_a_mark(text[i]) and not is_a_mark(text[i+1]):
                    if text[i+1] == 'nan':
                        guss_tag.append('')
                    else:
                        guss_tag.append(text[i])
            guss_tag_list.append(guss_tag)
        guss_most_tag = count_most_frequent_strings(guss_tag_list)
        guss_most = [item[0] for k, item in guss_most_tag.items()]
        guss_most_unique = list(set(guss_most))
        tag_use = []
        user_label_in = False
        for index in range(len(guss_most)):
            if guss_most[index] == "{user}" and not user_label_in:
                tag_use.append(index)
                user_label_in = True
            elif guss_most[index] != "{user}":
                if guss_most[index] == "{password}" and not user_label_in:
                    continue
                tag_use.append(index)
        if len(guss_most_unique) > 1:
            # 模糊提取的输出
            for ind, row in use_data.iterrows():
                nan_flag = pd.isna(row)
                # print(row)
                sub_result = {guss_most[index].replace('{', '').replace('}', ''):row.values[index] for index in tag_use if not nan_flag[index]}
                if len(sub_result)>1:
                    json_data.append(sub_result)
        # print(json_data)
        return json_data

class DatabaseExtractor:
    def __init__(self,data):
        self.data = data
        #可扩展：模糊类型分割
    
    
    # 敏感数据提取
    def extract_sensitive(self):
        json_data = []
   
        print("处理敏感数据中，敏感数据大小为",self.data.shape)

        # 单行单列的提取
        if self.data.shape[0] < 1:
            return json_data
        elif self.data.shape[0]==1:
            return process_bind_prase(self.data.iloc[0].tolist())
        if self.data.shape[1] <1:
            return json_data
        elif self.data.shape[1] == 1:
            return process_bind_prase(self.data.iloc[:,0].tolist())
        #TODO 处理提取分好块中的敏感数据
        # 首行，首行校验->逐行提取
        word_condition = [_sensitive_word_tmp.get(col_name) for col_name in self.data.columns]
        word_index = [index for index,value in enumerate(word_condition) if value is not None]
        if len(word_index) > 1:
            use_data = self.data.iloc[0:]
            for ind,row in use_data.iterrows():
                nan_flag = pd.isna(row)
                sub_result = {word_condition[index]:row.values[index] for index in word_index if not nan_flag[index]}
                if len(sub_result)>1:
                    json_data.append(sub_result)
            return json_data
        

        # 行模糊提取
        json_data = self.fuzz_extract()
        if len(json_data)>0:
            return json_data
        # self.xlsx_data = self.xlsx_data.transpose()

        # # 列模糊提取
        # json_data = self.xlsx_fuzz_extract()
        # if len(json_data)>0:
        #     return json_data
        # self.xlsx_data = self.xlsx_data.transpose()

        return begin_info_extraction(self.data.to_string(index = False,header = False))


    def fuzz_extract(self):
        json_data = []
        # 行模糊提取
        chinese_cols = self.data.apply(lambda col: col.apply(contains_chinese)).any()
        chinese_columns = chinese_cols[chinese_cols].index
        # 不剩两列以上数据直接返回
        if not self.data.shape[1]-len(chinese_columns)>1:
            return json_data
        use_data = self.data.drop(chinese_columns,axis=1).reset_index(drop = True)
        use_data.columns = list(range(0,use_data.shape[1]))
        guss_tag_list = []
        print(use_data)
        for ind,row in use_data.iterrows():
            print(row)
            str_use = row.apply(lambda x: str(x)).str.cat(sep=' ')
            print(str_use)
            text = plain_text_info_extraction(str_use,False,True,True)
            text = text.split(' ')
            guss_tag = []
            for i in range(len(text)-1):
                if is_a_mark(text[i]) and not is_a_mark(text[i+1]):
                    if text[i+1] == 'nan':
                        guss_tag.append('')
                    else:
                        guss_tag.append(text[i])
            guss_tag_list.append(guss_tag)
        guss_most_tag = count_most_frequent_strings(guss_tag_list)
        guss_most = [item[0] for k, item in guss_most_tag.items()]
        guss_most_unique = list(set(guss_most))
        tag_use = []
        user_label_in = False
        for index in range(len(guss_most)):
            if guss_most[index] == "{user}" and not user_label_in:
                tag_use.append(index)
                user_label_in = True
            elif guss_most[index] != "{user}":
                if guss_most[index] == "{password}" and not user_label_in:
                    continue
                tag_use.append(index)
        if len(guss_most_unique) > 1:
            # 模糊提取的输出
            for ind, row in use_data.iterrows():
                nan_flag = pd.isna(row)
                #print(row)
                str_use = row.apply(lambda x: str(x)).str.cat(sep=' ')
                text = str_use.split(' ')
                sub_result = {guss_most[index].replace('{', '').replace('}', ''):text[index] for index in tag_use if index<len(text) }
                if len(sub_result)>1:
                    json_data.append(sub_result)
        # print(json_data)
        return json_data

# 传入pandas中dataframe类型的 2维列表
def single_table_sensitive_extraction(data):
    xlsx_queue = queue.Queue()

    xlsx_queue.put(XlsxDevider(data))
    # xlsx_queue.put(XlsxDevider(xlsx.parse(sheet_names[5],header=None)))
    res = []
    while not xlsx_queue.empty():
        xlsxDevider = xlsx_queue.get()
        que_add = XlsxDevider.process_xlsx(xlsxDevider)
        if xlsxDevider.check_Pass():
            res_tmp = xlsxDevider.extract_sensitive_xlsx()
            if len(res_tmp)>0:
                res.append(res_tmp)
        else:
            while not que_add.empty():
                xlsx_queue.put(que_add.get())
    return res
# xlsx = pd.ExcelFile('/home/sakucy/networkCopitation/2023/data/tmp/资产梳理.xlsx')
# sheet_names = xlsx.sheet_names
# # for sheet_name in sheet_names:
# #     data = xlsx.parse(sheet_name)
# xlsx_queue = queue.Queue()
# # for name in sheet_names:
# #     xlsx_queue.put(XlsxDevider(xlsx.parse(name,header=None)))
# xlsx_queue.put(XlsxDevider(xlsx.parse(sheet_names[5],header=None)))

# while not xlsx_queue.empty():
#     xlsxDevider = xlsx_queue.get()
#     que_add = XlsxDevider.process_xlsx(xlsxDevider)
#     if xlsxDevider.check_Pass():
#         xlsxDevider.extract_sensitive_xlsx()
#     else:
#         while not que_add.empty():
#             xlsx_queue.put(que_add.get())


# while not que_add.empty():
#     tmp_use = que_add.get()
#     # print(tmp_use.xlsx_data)
