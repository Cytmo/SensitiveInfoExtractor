import pandas as pd
import queue
import yaml
import re

xlsx = pd.ExcelFile('资产梳理.xlsx')
sheet_names = xlsx.sheet_names


def contains_chinese(data):
    pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(pattern.search(str(data)))

# print(data.shape[0])
def init_sensitive_word(yml_file_path):
    global _sensitive_word
    # 读取YAML文件
    with open(yml_file_path, 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)

    chinese_patterns = data.get('chinese_patterns', [])
    english_patterns = data.get('english_patterns', [])

    sensitive_word_origin = chinese_patterns+english_patterns

    _sensitive_word = {item.get('name'):item.get('name') for item in sensitive_word_origin}
    
def process_bind_prase(data):
    # TODO 提取未知单条数据
    print("处理单条数据",data)

def line_spilit_index(empty_index):
    index_single = []
    index_prase = []
    index_last = -1
    for index in empty_index:
        if index >index_last+1:
            if index == index_last+2:
                index_single.append(index_last+1)
            else:
                index_prase.append([index_last+1,index])
        index_last = index
    return index_single,index_prase

def line_spilit_index_key(empty_index):
    index_single = []
    index_prase = []
    index_last = 0
    for index in empty_index:
        if index >index_last:
            if index == index_last+1:
                index_single.append(index_last)
            else:
                index_prase.append([index_last,index])
        index_last = index
    return index_single,index_prase



init_sensitive_word('./sensitive_word.yml')
global _sensitive_word

class XlsxDevider:
    def __init__(self,data):
        self.xlsx_data = data
        self.raw_pass = False
        self.col_pass = False
        self.key_pass = False
        #可扩展：模糊类型分割
    
    # 行分割
    @classmethod
    def process_raw(cls,xlsxDevider):
        queue_tmp = queue.Queue()

        empty_rows = xlsxDevider.xlsx_data.isnull().all(axis=1)
        empty_rows_index = empty_rows[empty_rows].index.to_list()
        if len(empty_rows_index) < 1:
            return queue_tmp
        empty_rows_index.insert(0,-1)
        empty_rows_index.append(len(empty_rows))
        [index_single,index_prase] = line_spilit_index(empty_rows_index)
        
        for index in index_single:
            data_part = xlsxDevider.xlsx_data.iloc[index].copy().to_list()
            process_bind_prase(data_part)   

        for prases in index_prase:
            data_part = xlsxDevider.xlsx_data.iloc[prases[0]:prases[1]].copy().reset_index(drop = True)
            queue_tmp.put(XlsxDevider(data_part))

        return queue_tmp
    
    @classmethod
    def process_col(cls,xlsxDevider):
        queue_tmp = queue.Queue()

        empty_cols = xlsxDevider.xlsx_data.isnull().all()
        empty_cols_index = empty_cols[empty_cols].index.to_list()
        if len(empty_cols_index) < 1:
            return queue_tmp
        empty_cols_index.insert(0,-1)
        empty_cols_index.append(len(empty_cols))
        [index_single,index_prase] = line_spilit_index(empty_cols_index)

        for index in index_single:
            data_part = xlsxDevider.xlsx_data.iloc[:,index].copy().to_list()
            process_bind_prase(data_part)

        for prases in index_prase:
            data_part = xlsxDevider.xlsx_data.iloc[:,prases[0]:prases[1]].copy().reset_index(drop = True)
            data_part.columns = list(range(0,prases[1]-prases[0]))
            queue_tmp.put(XlsxDevider(data_part))

        #TODO 处理行分割
        return queue_tmp
    
    @classmethod
    def process_key(cls,xlsxDevider):
        queue_tmp = queue.Queue()
        empty_rows_index = []
        # 行关键词检测
        for index,row in xlsxDevider.xlsx_data.iterrows():
            word_condition = [_sensitive_word.get(element) for element in row]
            if len(list(set([x for x in word_condition if x is not None]))) > 1:
                empty_rows_index.append(index)
                

        if len(empty_rows_index)>1 or (len(empty_rows_index) == 1 and empty_rows_index[0]!=0):

            empty_rows_index.insert(0,0)
            empty_rows_index.append(xlsxDevider.xlsx_data.shape[0])
            [index_single,index_prase] = line_spilit_index_key(empty_rows_index)
            
            for index in index_single:
                data_part = xlsxDevider.xlsx_data.iloc[index].copy().to_list()
                process_bind_prase(data_part)   

            for prases in index_prase:
                data_part = xlsxDevider.xlsx_data.iloc[prases[0]:prases[1]].copy().reset_index(drop = True)
                queue_tmp.put(XlsxDevider(data_part))

            return queue_tmp

        # 列关键词检测
        empty_cols_index = []
        for index,(col_name,col) in enumerate(xlsxDevider.xlsx_data.items()):
            word_condition = [_sensitive_word.get(element) for element in col]
            if len(list(set([x for x in word_condition if x is not None]))) > 1:
                empty_cols_index.append(index)

        if len(empty_cols_index)>1 or (len(empty_cols_index) == 1 and empty_cols_index[0]!=0):
            empty_cols_index.insert(0,0)
            empty_cols_index.append(xlsxDevider.xlsx_data.shape[1])
            [index_single,index_prase] = line_spilit_index_key(empty_cols_index)

            print(empty_cols_index)

            for index in index_single:
                data_part = xlsxDevider.xlsx_data.iloc[:,index].copy().to_list()
                process_bind_prase(data_part)

            for prases in index_prase:
                data_part = xlsxDevider.xlsx_data.iloc[:,prases[0]:prases[1]].copy().reset_index(drop = True)
                data_part.columns = list(range(0,prases[1]-prases[0]))
                queue_tmp.put(XlsxDevider(data_part))

                
        #TODO 处理行分割
        return queue_tmp

    @classmethod
    def process_xlsx(cls,xlsxDevider):
        queue_tmp = None
        if not xlsxDevider.raw_pass:
            queue_tmp = XlsxDevider.process_raw(xlsxDevider)
            if queue_tmp.empty():
                xlsxDevider.raw_pass = True
            else:
                return queue_tmp
        
        print("raw_pass")
        if not xlsxDevider.col_pass:
            queue_tmp = XlsxDevider.process_col(xlsxDevider)
            if queue_tmp.empty():
                xlsxDevider.col_pass = True
            else:
                return queue_tmp
            
        print("col_pass")
        if not xlsxDevider.key_pass:
            queue_tmp = XlsxDevider.process_key(xlsxDevider)
            if queue_tmp.empty():
                xlsxDevider.key_pass = True
            else:
                return queue_tmp
        
        print("key_pass")
        return queue_tmp

    def check_Pass(self):
        return self.raw_pass and self.col_pass and self.key_pass
    
    # 敏感数据提取
    def extract_sensitive_xlsx(self):
        json_data = []
        if self.check_Pass():
            print("处理敏感数据中，敏感数据大小为",self.xlsx_data.shape)
        else:
            print("处理敏感数据中，敏感数据大小为",self.xlsx_data.shape)
            print("推荐优先处理分块以提高处理结果")
        # 单行单列的提取
        if self.xlsx_data.shape[0] < 1:
            return
        elif self.xlsx_data.shape[0]==1:
            process_bind_prase(self.xlsx_data.loc[0].tolist())
            return
        if self.xlsx_data.shape[1] <1:
            return
        elif self.xlsx_data.shape[1] == 1:
            process_bind_prase(self.xlsx_data.loc[:,0].tolist())
            return
        #TODO 处理提取分好块中的敏感数据
        # 首行，首行校验->逐行提取
        word_condition = [_sensitive_word.get(element) for element in self.xlsx_data.loc[0]]
        word_index = [index for index,value in enumerate(word_condition) if value is not None]
        if len(word_index) > 1:
            use_data = self.xlsx_data.iloc[1:]
            for ind,row in use_data.iterrows():
                nan_flag = pd.isna(row)
                sub_result = {word_condition[index]:row.values[index] for index in word_index if not nan_flag[index]}
                if len(sub_result)>1:
                    json_data.append(sub_result)
            # TODO 添加输出函数
            print(json_data)
            return
        
        # 首列，首列校验->逐列提取
        word_condition = [_sensitive_word.get(element) for element in self.xlsx_data.loc[:,0]]
        word_index = [index for index,value in enumerate(word_condition) if value is not None]
        if len(word_index) > 1:
            use_data = self.xlsx_data.iloc[:,1:]
            for index,(col_name,col) in enumerate(use_data.items()):
                nan_flag = pd.isna(col)
                sub_result = {word_condition[index]:col.values[index] for index in word_index if not nan_flag[index]}
                if len(sub_result)>1:
                    json_data.append(sub_result)
            # TODO 添加输出函数
            print(json_data)
            return           
        
        # 行模糊提取
        chinese_cols = self.xlsx_data.apply(lambda col: col.apply(contains_chinese)).any()
        chinese_columns = chinese_cols[chinese_cols].index
        use_data = self.xlsx_data.drop(chinese_columns,axis=1)

        print(json_data)
        return 

# for sheet_name in sheet_names:
#     data = xlsx.parse(sheet_name)
xlsx_queue = queue.Queue()
for name in sheet_names:
    xlsx_queue.put(XlsxDevider(xlsx.parse(name,header=None)))
# xlsx_queue.put(XlsxDevider(xlsx.parse(sheet_names[0],header=None)))

while not xlsx_queue.empty():
    xlsxDevider = xlsx_queue.get()
    que_add = XlsxDevider.process_xlsx(xlsxDevider)
    if xlsxDevider.check_Pass():
        xlsxDevider.extract_sensitive_xlsx()
    else:
        while not que_add.empty():
            xlsx_queue.put(que_add.get())




# while not que_add.empty():
#     tmp_use = que_add.get()
#     print(tmp_use.xlsx_data)
