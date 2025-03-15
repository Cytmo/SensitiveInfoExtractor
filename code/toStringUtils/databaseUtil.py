import queue
import os
import re
import sqlite3
import pandas as pd

from informationEngine.table_extract import DatabaseExtractor
from util import globalVar
from toStringUtils.picUtil import *
from util.extractInfo import *
from toStringUtils.universalUtil import *

from util.logUtils import LoggerSingleton
TAG = "toStringUtils.databaseUtil-"
logger = LoggerSingleton().get_logger()

# SQLite数据库文件处理
def sqlite_db_file(file_path):
    """处理SQLite数据库文件
    Args:
        file_path: 数据库文件路径
    Returns:
        敏感信息结果列表
    """
    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect(file_path)
        
        # 获取所有表名
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
        
        table_queue = queue.Queue()
        # 遍历每张表并读取数据
        for table_name in tables['name']:
            logger.info(TAG + f"Processing SQLite table: {table_name}")
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                table_queue.put(DatabaseExtractor(df))
                logger.debug(TAG + f"Table {table_name} shape: {df.shape}")
            except Exception as e:
                logger.error(TAG + f"Error reading table {table_name}: {str(e)}")
        
        # 关闭数据库连接
        conn.close()
        
        res = []
        while not table_queue.empty():
            table = table_queue.get()
            extracted = table.extract_sensitive()
            if extracted:
                res.extend(extracted)
        return res
    except Exception as e:
        logger.error(TAG + f"Error processing SQLite database: {str(e)}")
        return []

# SQL脚本文件处理
def sql_script_file(file_path):
    """处理SQL脚本文件
    Args:
        file_path: SQL脚本文件路径
    Returns:
        敏感信息结果列表
    """
    try:
        # 读取SQL文件内容
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 提取CREATE TABLE语句
        create_table_statements = re.findall(r'CREATE\s+TABLE\s+[^(]+\(([^;]+)\)', content, re.IGNORECASE | re.DOTALL)
        
        # 提取INSERT语句中的值
        insert_values = re.findall(r'INSERT\s+INTO\s+[^(]+\([^)]*\)\s+VALUES\s*\(([^;]+)\)', content, re.IGNORECASE | re.DOTALL)
        
        # 组合所有文本进行分析
        combined_text = content
        if create_table_statements:
            combined_text += "\n" + "\n".join(create_table_statements)
        if insert_values:
            combined_text += "\n" + "\n".join(insert_values)
        
        # 使用通用信息提取
        return begin_info_extraction(combined_text, file_path=file_path)
    except Exception as e:
        logger.error(TAG + f"Error processing SQL script: {str(e)}")
        return []

# MySQL备份文件处理
def mysql_dump_file(file_path):
    """处理MySQL备份文件
    Args:
        file_path: MySQL备份文件路径
    Returns:
        敏感信息结果列表
    """
    # MySQL备份文件本质上是SQL脚本，使用SQL脚本处理函数
    return sql_script_file(file_path)

# PostgreSQL备份文件处理
def postgresql_dump_file(file_path):
    """处理PostgreSQL备份文件
    Args:
        file_path: PostgreSQL备份文件路径
    Returns:
        敏感信息结果列表
    """
    # PostgreSQL备份文件本质上是SQL脚本，使用SQL脚本处理函数
    return sql_script_file(file_path)

# SQL Server备份文件处理(MDF, LDF)
def sqlserver_file(file_path):
    """处理SQL Server数据库文件
    由于无法直接读取二进制MDF/LDF文件，尝试提取嵌入的文本进行分析
    """
    try:
        # 读取二进制文件
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # 尝试提取ASCII字符串
        text_content = ""
        for match in re.finditer(b'[\x20-\x7E]{5,}', content):
            text_content += match.group().decode('ascii', errors='ignore') + "\n"
        
        # 分析提取的文本
        if text_content:
            return begin_info_extraction(text_content, file_path=file_path)
        return []
    except Exception as e:
        logger.error(TAG + f"Error processing SQL Server file: {str(e)}")
        return []

# 通用数据库文件处理入口
def db_file(file_path):
    """数据库文件处理入口函数
    根据文件扩展名选择不同的处理方式
    Args:
        file_path: 数据库文件路径
    Returns:
        敏感信息结果列表
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # 根据文件扩展名选择处理函数
    if file_ext in ('.db', '.sqlite', '.sqlite3'):
        logger.info(TAG + f"处理SQLite数据库文件: {file_path}")
        return sqlite_db_file(file_path)
    elif file_ext in ('.sql'):
        logger.info(TAG + f"处理SQL脚本文件: {file_path}")
        return sql_script_file(file_path)
    elif file_ext in ('.dump'):
        logger.info(TAG + f"处理数据库备份文件: {file_path}")
        if 'postgresql' in file_path.lower():
            return postgresql_dump_file(file_path)
        else:
            return mysql_dump_file(file_path)
    elif file_ext in ('.mdf', '.ldf', '.bak'):
        logger.info(TAG + f"处理SQL Server数据库文件: {file_path}")
        return sqlserver_file(file_path)
    elif file_ext in ('.frm', '.myd', '.myi', '.ibd'):
        logger.info(TAG + f"处理MySQL数据文件: {file_path}")
        # 这些是MySQL的二进制数据文件，尝试以二进制方式提取文本
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # 尝试提取ASCII字符串
            text_content = ""
            for match in re.finditer(b'[\x20-\x7E]{5,}', content):
                text_content += match.group().decode('ascii', errors='ignore') + "\n"
            
            if text_content:
                return begin_info_extraction(text_content, file_path=file_path)
            return []
        except Exception as e:
            logger.error(TAG + f"Error processing MySQL data file: {str(e)}")
            return []
    else:
        logger.warning(TAG + f"未知数据库文件类型: {file_path}")
        # 尝试以文本方式读取
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return begin_info_extraction(content, file_path=file_path)
        except Exception:
            # 如果文本读取失败，尝试以二进制方式提取文本
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # 尝试提取ASCII字符串
                text_content = ""
                for match in re.finditer(b'[\x20-\x7E]{5,}', content):
                    text_content += match.group().decode('ascii', errors='ignore') + "\n"
                
                if text_content:
                    return begin_info_extraction(text_content, file_path=file_path)
                return []
            except Exception as e:
                logger.error(TAG + f"无法处理文件: {str(e)}")
                return []
 