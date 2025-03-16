import queue
import os
import re
import sqlite3
import pandas as pd
import tempfile
import subprocess
from datetime import datetime

from informationEngine.table_extract import DatabaseExtractor
from util import globalVar
from toStringUtils.picUtil import *
from util.extractInfo import *
from toStringUtils.universalUtil import *

# 日志模块
from util.logUtils import LoggerSingleton
TAG = "toStringUtils.databaseUtil.py-"
logger = LoggerSingleton().get_logger()

# 提取.db中的文本
def db_file(file_path):
    """
    处理SQLite数据库文件(.db, .sqlite, .sqlite3)
    """
    logger.info(TAG+f"处理SQLite数据库文件: {file_path}")
    
    try:
        # 连接到 SQLite 数据库
        conn = sqlite3.connect(file_path)  

        # 获取所有表名
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)

        result_text = f"SQLite数据库文件: {os.path.basename(file_path)}\n"
        result_text += f"表数量: {len(tables)}\n\n"

        table_queue = queue.Queue()
        # 遍历每张表并读取数据
        for table_name in tables['name']:
            logger.debug(TAG+f"处理表: {table_name}")
            result_text += f"表名: {table_name}\n"
            
            # 获取表结构
            table_info = pd.read_sql_query(f"PRAGMA table_info({table_name});", conn)
            result_text += f"表结构:\n{table_info[['name', 'type']].to_string()}\n\n"
            
            # 获取表数据
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            table_queue.put(DatabaseExtractor(df))
            
            # 添加表的前几行数据到结果中
            if not df.empty:
                result_text += f"数据示例:\n{df.head().to_string()}\n\n"

        # 关闭数据库连接
        conn.close()

        # 提取敏感信息
        sensitive_info = []
        while not table_queue.empty():
            table = table_queue.get()
            table_result = table.extract_sensitive()
            if table_result:
                sensitive_info.append(table_result)
        
        return result_text + "\n".join(str(info) for info in sensitive_info)
    
    except Exception as e:
        logger.error(TAG+f"SQLite数据库处理错误: {str(e)}")
        return f"数据库文件处理错误: {str(e)}"

def sql_file(file_path):
    """
    处理SQL脚本文件(.sql)
    """
    logger.info(TAG+f"处理SQL脚本文件: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            sql_content = f.read()
        
        result_text = f"SQL脚本文件: {os.path.basename(file_path)}\n\n"
        
        # 提取CREATE TABLE语句
        create_table_statements = re.findall(r'CREATE\s+TABLE\s+[`"]?(\w+)[`"]?\s*\((.*?)\);', 
                                           sql_content, re.DOTALL | re.IGNORECASE)
        
        if create_table_statements:
            result_text += "表结构信息:\n"
            for table_name, table_def in create_table_statements:
                result_text += f"表名: {table_name}\n"
                # 提取列定义
                columns = re.findall(r'[`"]?(\w+)[`"]?\s+(\w+)(?:\(.*?\))?', table_def)
                if columns:
                    result_text += "列定义:\n"
                    for col_name, col_type in columns:
                        result_text += f"  - {col_name}: {col_type}\n"
                result_text += "\n"
        
        # 提取INSERT语句中的数据
        insert_statements = re.findall(r'INSERT\s+INTO\s+[`"]?(\w+)[`"]?\s+(?:\((.*?)\))?\s+VALUES\s*\((.*?)\);', 
                                     sql_content, re.DOTALL | re.IGNORECASE)
        
        if insert_statements:
            result_text += "数据示例:\n"
            # 只处理前几个INSERT语句，避免文本过长
            for i, (table_name, columns, values) in enumerate(insert_statements[:5]):
                result_text += f"表 {table_name} 的数据:\n"
                result_text += f"  值: {values}\n"
                if i >= 4:  # 只显示5个INSERT语句
                    result_text += "...(更多数据已省略)\n"
                    break
        
        return result_text
    
    except Exception as e:
        logger.error(TAG+f"SQL文件处理错误: {str(e)}")
        return f"SQL文件处理错误: {str(e)}"

def mysql_dump_file(file_path):
    """
    处理MySQL转储文件(.sql, .dump)
    """
    logger.info(TAG+f"处理MySQL转储文件: {file_path}")
    return sql_file(file_path)  # 使用通用SQL文件处理方法

def postgresql_dump_file(file_path):
    """
    处理PostgreSQL转储文件(.sql, .dump)
    """
    logger.info(TAG+f"处理PostgreSQL转储文件: {file_path}")
    return sql_file(file_path)  # 使用通用SQL文件处理方法

def mssql_file(file_path):
    """
    处理Microsoft SQL Server文件(.mdf, .ldf, .bak)
    """
    logger.info(TAG+f"处理SQL Server文件: {file_path}")
    
    # 对于二进制格式的数据库文件，我们提取一些基本信息并搜索里面的可读文本
    result_text = f"SQL Server数据库文件: {os.path.basename(file_path)}\n"
    result_text += f"文件大小: {os.path.getsize(file_path)/1024/1024:.2f} MB\n\n"
    
    try:
        # 二进制读取文件
        with open(file_path, 'rb') as f:
            content = f.read()
            
        # 以文本方式搜索可能的敏感信息
        text_content = content.decode('latin-1', errors='ignore')
        
        # 提取可能的表名
        table_names = re.findall(r'CREATE\s+TABLE\s+[`"]?(\w+)[`"]?', text_content, re.IGNORECASE)
        if table_names:
            result_text += "可能的表名:\n"
            for table in set(table_names[:20]):  # 去重并限制数量
                result_text += f"  - {table}\n"
            result_text += "\n"
        
        # 提取列名和数据类型
        column_defs = re.findall(r'[`"]?(\w+)[`"]?\s+(varchar|int|date|datetime|numeric|float|text)', 
                               text_content, re.IGNORECASE)
        if column_defs:
            result_text += "可能的列定义:\n"
            for col_name, col_type in set(column_defs[:30]):  # 去重并限制数量
                result_text += f"  - {col_name}: {col_type}\n"
            result_text += "\n"
        
        return result_text
    
    except Exception as e:
        logger.error(TAG+f"SQL Server文件处理错误: {str(e)}")
        return f"SQL Server文件处理错误: {str(e)}"

def oracle_file(file_path):
    """
    处理Oracle数据库文件(.dmp, .dbf)
    """
    logger.info(TAG+f"处理Oracle数据库文件: {file_path}")
    
    # 类似于SQL Server文件处理，提取基本信息和可读文本
    result_text = f"Oracle数据库文件: {os.path.basename(file_path)}\n"
    result_text += f"文件大小: {os.path.getsize(file_path)/1024/1024:.2f} MB\n\n"
    
    try:
        # 二进制读取文件
        with open(file_path, 'rb') as f:
            content = f.read()
            
        # 以文本方式搜索可能的敏感信息
        text_content = content.decode('latin-1', errors='ignore')
        
        # 提取可能的表名
        table_names = re.findall(r'CREATE\s+TABLE\s+[`"]?(\w+)[`"]?', text_content, re.IGNORECASE)
        if table_names:
            result_text += "可能的表名:\n"
            for table in set(table_names[:20]):  # 去重并限制数量
                result_text += f"  - {table}\n"
            result_text += "\n"
        
        # 提取用户名和凭据相关信息
        user_patterns = re.findall(r'(username|user|login)[\s:=]+[\'"]?([A-Za-z0-9_-]+)[\'"]?', 
                                 text_content, re.IGNORECASE)
        if user_patterns:
            result_text += "可能的用户名信息:\n"
            for user_type, user_value in set(user_patterns[:20]):
                result_text += f"  - {user_type}: {user_value}\n"
            result_text += "\n"
        
        return result_text
    
    except Exception as e:
        logger.error(TAG+f"Oracle文件处理错误: {str(e)}")
        return f"Oracle文件处理错误: {str(e)}"

def get_database_handler(file_path):
    """
    根据文件扩展名选择合适的数据库处理函数
    """
    ext = os.path.splitext(file_path.lower())[1]
    
    # SQLite数据库
    if ext in ['.db', '.sqlite', '.sqlite3']:
        return db_file
    
    # SQL脚本文件
    elif ext == '.sql':
        # 尝试通过内容判断是哪种SQL
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            header = f.read(1000).lower()  # 读取前1000个字符判断
            
        if 'mysql' in header:
            return mysql_dump_file
        elif 'postgresql' in header or 'postgres' in header:
            return postgresql_dump_file
        else:
            return sql_file  # 默认SQL处理
    
    # MySQL特定文件
    elif ext in ['.frm', '.myd', '.myi', '.ibd']:
        return mysql_dump_file
    
    # PostgreSQL转储文件
    elif ext == '.dump':
        return postgresql_dump_file
    
    # SQL Server文件
    elif ext in ['.mdf', '.ldf', '.bak']:
        return mssql_file
    
    # Oracle数据库文件
    elif ext in ['.dmp', '.dbf']:
        return oracle_file
    
    # 默认处理函数
    else:
        logger.warning(TAG+f"未知数据库文件类型: {ext}")
        return sql_file  # 尝试作为SQL脚本处理
 