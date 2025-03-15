import queue

from datetime import datetime
import sqlite3

from informationEngine.table_extract import DatabaseExtractor
from util import globalVar
from toStringUtils.picUtil import *
from util.extractInfo import *
from toStringUtils.universalUtil import *
import pandas as pd
import sqlite3

# 提取.db中的文本
def db_file(file_path):

    # 连接到 SQLite 数据库
    conn = sqlite3.connect(file_path)  

    # 获取所有表名
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)

    table_queue = queue.Queue()
    # 遍历每张表并读取数据
    for table_name in tables['name']:
        print(f"Processing table: {table_name}")
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        table_queue.put(DatabaseExtractor(df))

        print(df.head())  # 打印每张表的前几行数据

    # 关闭数据库连接
    conn.close()

    res = []
    while not table_queue.empty():
        table = table_queue.get()
        res.append(table.extract_sensitive())
    return res
 