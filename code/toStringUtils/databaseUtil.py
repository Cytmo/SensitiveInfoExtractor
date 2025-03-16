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

#数据库直连
import mysql.connector

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


def sql_conn():
    """
    处理SQL数据库连接
    """
    try:
        # 数据库连接信息
        db_config = {
            'user': 'root',    # 替换为你的MySQL用户名
            'password': '123456',  # 替换为你的MySQL密码
            'host': 'localhost',        # 数据库主机地址
            'port':3307
        }

        # 连接到MySQL服务器
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        logger.info("连接到MySQL服务器成功！")

        # 获取所有数据库的名称
        cursor.execute("SHOW DATABASES;")
        databases = [item[0] for item in cursor.fetchall()]
        logger.info("可用的数据库：{}".format( databases))
        # result_text = f"SQL数据库文件: {db_config}\n"
        # 存储所有数据库和表的DataFrame
        all_dataframes = {}
        sensitive_info = []

        # 遍历每个数据库
        for db_name in databases:
            logger.info(f"\n正在处理数据库：{db_name}")
            
            # 跳过系统数据库（如mysql、information_schema、performance_schema等）
            if db_name in ['mysql', 'information_schema', 'performance_schema', 'sys']:
                logger.info(f"跳过系统数据库：{db_name}")
                continue

            # 切换到当前数据库
            cursor.execute(f"USE {db_name}")

            # 获取当前数据库中的所有表
            cursor.execute("SHOW TABLES;")
            tables = [item[0] for item in cursor.fetchall()]
            logger.info("数据库 {} 中的表：{}".format(db_name, tables))

            # 为当前数据库创建一个字典来存储表的DataFrame
            all_dataframes[db_name] = {}

            # 遍历每个表
            for table in tables:
                logger.info(f"正在处理表：{table}")
                # result_text += f"表名: {table}\n"
                query = f"SELECT * FROM {table};"
                try:
                    df = pd.read_sql(query, conn)
                    logger.info(f"表 {table} 已成功读取为DataFrame，行数：{len(df)}")
                    table_result = DatabaseExtractor(df).extract_sensitive()
                    if table_result:
                        sensitive_info.append(table_result)

                except Exception as e:
                    logger.info(f"读取表 {table} 时出错：{e}")

        # 关闭数据库连接
        cursor.close()
        conn.close()
        logger.info("数据库连接已关闭。")
        return  sensitive_info
    except Exception as e:
        logger.error(TAG+f"SQLite数据库处理错误: {str(e)}")
        return f"数据库文件处理错误: {str(e)}"

import psycopg2
def postgresql_conn():
    """
    处理PostgreSQL数据库连接
    """
    try:
        # 数据库连接信息
        db_config = {
            'user': 'your_username',    # 替换为你的PostgreSQL用户名
            'password': 'your_password',  # 替换为你的PostgreSQL密码
            'host': 'localhost',        # 数据库主机地址
            'port': '5432',            # PostgreSQL默认端口
            'database': 'your_database'  # 替换为你的数据库名称
        }

        # 连接到PostgreSQL数据库
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        logger.info("连接到PostgreSQL服务器成功！")

        # 获取所有数据库的名称（PostgreSQL中通常直接获取所有表，因为数据库切换不像MySQL那样频繁）
        # 这里假设我们只处理一个数据库，直接获取当前数据库中的所有表
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = [item[0] for item in cursor.fetchall()]
        logger.info("可用的表：{}".format(tables))

        # 存储所有表的DataFrame
        all_dataframes = {}
        sensitive_info = []

        # 遍历每个表
        for table in tables:
            logger.info(f"正在处理表：{table}")
            query = f"SELECT * FROM {table};"
            try:
                df = pd.read_sql(query, conn)
                logger.info(f"表 {table} 已成功读取为DataFrame，行数：{len(df)}")
                table_result = DatabaseExtractor(df).extract_sensitive()
                if table_result:
                    sensitive_info.append(table_result)
            except Exception as e:
                logger.error(f"读取表 {table} 时出错：{e}")

        # 关闭数据库连接
        cursor.close()
        conn.close()
        logger.info("数据库连接已关闭。")
        return sensitive_info
    except Exception as e:
        logger.error("PostgreSQL数据库处理错误: {}".format(str(e)))
        return f"数据库处理错误: {str(e)}"

import cx_Oracle
def oracle_conn():
    """
    处理Oracle数据库连接
    """
    try:
        # 数据库连接信息
        db_config = {
            'user': 'your_username',    # 替换为你的Oracle用户名
            'password': 'your_password',  # 替换为你的Oracle密码
            'dsn': 'localhost:1521/your_database'  # 替换为你的Oracle DSN
        }

        # 连接到Oracle数据库
        conn = cx_Oracle.connect(**db_config)
        cursor = conn.cursor()

        logger.info("连接到Oracle服务器成功！")

        # 获取所有表的名称（Oracle中需要指定用户）
        cursor.execute("SELECT table_name FROM user_tables")
        tables = [item[0] for item in cursor.fetchall()]
        logger.info("可用的表：{}".format(tables))

        # 存储所有表的DataFrame
        all_dataframes = {}
        sensitive_info = []

        # 遍历每个表
        for table in tables:
            logger.info(f"正在处理表：{table}")
            query = f"SELECT * FROM {table};"
            try:
                df = pd.read_sql(query, conn)
                logger.info(f"表 {table} 已成功读取为DataFrame，行数：{len(df)}")
                table_result = DatabaseExtractor(df).extract_sensitive()
                if table_result:
                    sensitive_info.append(table_result)
            except Exception as e:
                logger.error(f"读取表 {table} 时出错：{e}")

        # 关闭数据库连接
        cursor.close()
        conn.close()
        logger.info("数据库连接已关闭。")
        return sensitive_info
    except Exception as e:
        logger.error("Oracle数据库处理错误: {}".format(str(e)))
        return f"数据库处理错误: {str(e)}"

import pyodbc
def sqlserver_conn():
    """
    处理SQL Server数据库连接
    """
    try:
        # 数据库连接信息
        db_config = {
            'driver': '{ODBC Driver 17 for SQL Server}',  # SQL Server驱动程序
            'server': 'localhost',                       # 数据库服务器地址
            'database': 'master',                        # 初始数据库（用于列出所有数据库）
            'user': 'your_username',                    # 替换为你的SQL Server用户名
            'password': 'your_password',                # 替换为你的SQL Server密码
            'port': '1433'                             # SQL Server默认端口
        }

        # 连接到SQL Server服务器
        conn_str = f"DRIVER={db_config['driver']};SERVER={db_config['server']},{db_config['port']};DATABASE={db_config['database']};UID={db_config['user']};PWD={db_config['password']}"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        logger.info("连接到SQL Server服务器成功！")

        # 获取所有数据库的名称
        cursor.execute("SELECT name FROM sys.databases")
        databases = [item[0] for item in cursor.fetchall()]
        logger.info("可用的数据库：{}".format(databases))

        # 存储所有数据库和表的DataFrame
        all_dataframes = {}
        sensitive_info = []

        # 遍历每个数据库
        for db_name in databases:
            logger.info(f"\n正在处理数据库：{db_name}")
            
            # 跳过系统数据库（如master、model、msdb、tempdb）
            if db_name in ['master', 'model', 'msdb', 'tempdb']:
                logger.info(f"跳过系统数据库：{db_name}")
                continue

            # 切换到当前数据库
            cursor.execute(f"USE {db_name}")

            # 获取当前数据库中的所有表
            cursor.execute("SELECT name FROM sys.tables")
            tables = [item[0] for item in cursor.fetchall()]
            logger.info(f"数据库 {db_name} 中的表：{tables}")

            # 为当前数据库创建一个字典来存储表的DataFrame
            all_dataframes[db_name] = {}

            # 遍历每个表
            for table in tables:
                logger.info(f"正在处理表：{table}")
                query = f"SELECT * FROM {table};"
                try:
                    df = pd.read_sql(query, conn)
                    logger.info(f"表 {table} 已成功读取为DataFrame，行数：{len(df)}")
                    table_result = DatabaseExtractor(df).extract_sensitive()
                    if table_result:
                        sensitive_info.append(table_result)
                except Exception as e:
                    logger.error(f"读取表 {table} 时出错：{e}")

        # 关闭数据库连接
        cursor.close()
        conn.close()
        logger.info("数据库连接已关闭。")
        return sensitive_info
    except Exception as e:
        logger.error("mysql server数据库处理错误: {}".format(str(e)))
        return f"数据库处理错误: {str(e)}"

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
 