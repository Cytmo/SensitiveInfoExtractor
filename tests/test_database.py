#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库文件处理测试脚本
"""

import os
import sys
import shutil
import unittest
import sqlite3
import tempfile

# 添加代码目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
code_dir = os.path.abspath(os.path.join(current_dir, '../code'))
sys.path.insert(0, code_dir)

# 切换到代码目录运行，确保相对导入正确
os.chdir(code_dir)

# 在导入任何模块前，创建一个简单的配置模块
if not os.path.exists(os.path.join(code_dir, 'config')):
    os.makedirs(os.path.join(code_dir, 'config'))

# 确保config/__init__.py存在
with open(os.path.join(code_dir, 'config/__init__.py'), 'a'):
    pass

# 如果config/info_core_config.py不存在，创建一个简单的版本
info_core_config_path = os.path.join(code_dir, 'config/info_core_config.py')
if not os.path.exists(info_core_config_path):
    with open(info_core_config_path, 'w') as f:
        f.write("""
# 最小化配置文件
INFO_PATTERN = set(["name", "address", "phone", "email", "id_card", "password"])
COMMON_PATTERN = set(["username", "password"])
IS_CONFIG_FILE = 1
IS_RULE_BASED = 2
IS_TEXT = 3
IS_PURE_KEY_VALUE = 4
IS_CODE_FILE = 5
DEFAULT_VALID_LEN = 4
""")

# 初始化敏感词配置文件
sensitive_word_path = os.path.join(code_dir, 'config/sensitive_word.yml')
if not os.path.exists(sensitive_word_path):
    os.makedirs(os.path.dirname(sensitive_word_path), exist_ok=True)
    with open(sensitive_word_path, 'w') as f:
        f.write("""
chinese_patterns:
  - name: 用户名
    regex: username|user|name
  - name: 密码
    regex: password|pass
  - name: 电子邮件
    regex: email|mail
  - name: 电话
    regex: phone|mobile|tel
    
english_patterns:
  - name: username
    regex: username|user|name
  - name: password
    regex: password|pass
  - name: email
    regex: email|mail
  - name: phone
    regex: phone|mobile|tel
""")

# 初始化必要的全局变量
from util import globalVar
globalVar._init()
globalVar.init_sensitive_word("config/sensitive_word.yml")
globalVar.set_auth_search_flag(True)

# 导入测试所需模块
from toStringUtils.databaseUtil import *
from util.logUtils import LoggerSingleton

# 设置日志
logger = LoggerSingleton().get_logger()

class TestDatabaseUtils(unittest.TestCase):
    """测试数据库文件处理功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.test_dir = tempfile.mkdtemp()
        
        # 创建一个测试用SQLite数据库
        self.sqlite_db_path = os.path.join(self.test_dir, 'test.db')
        conn = sqlite3.connect(self.sqlite_db_path)
        cursor = conn.cursor()
        
        # 创建测试表
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            phone TEXT
        )
        ''')
        
        # 插入测试数据
        cursor.execute('''
        INSERT INTO users (username, password, email, phone)
        VALUES 
        ('admin', 'admin123', 'admin@example.com', '13800138000'),
        ('user1', 'password123', 'user1@example.com', '13900139000'),
        ('test_user', 'test@password', 'test@example.com', '13700137000')
        ''')
        
        conn.commit()
        conn.close()
        
        # 创建一个测试用SQL脚本文件
        self.sql_script_path = os.path.join(self.test_dir, 'test.sql')
        with open(self.sql_script_path, 'w') as f:
            f.write('''
            -- 创建用户表
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                password VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(20)
            );
            
            -- 插入测试数据
            INSERT INTO users (username, password, email, phone)
            VALUES 
            ('admin', 'admin123', 'admin@example.com', '13800138000'),
            ('user1', 'password123', 'user1@example.com', '13900139000'),
            ('test_user', 'test@password', 'test@example.com', '13700137000');
            
            -- 创建配置表
            CREATE TABLE settings (
                key VARCHAR(50) PRIMARY KEY,
                value TEXT NOT NULL
            );
            
            -- 插入配置数据
            INSERT INTO settings (key, value)
            VALUES 
            ('api_key', 'sk_test_abcdefghijklmnopqrstuvwxyz123456'),
            ('secret_key', 'sk_live_abcdefghijklmnopqrstuvwxyz123456'),
            ('database_url', 'mysql://user:password@localhost:3306/dbname');
            ''')
    
    def tearDown(self):
        """测试后的清理工作"""
        shutil.rmtree(self.test_dir)
    
    def test_sqlite_db_file(self):
        """测试SQLite数据库文件处理"""
        print("\n测试SQLite数据库文件处理...")
        result = sqlite_db_file(self.sqlite_db_path)
        
        # 验证结果
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        
        # 打印结果
        print(f"提取到 {len(result)} 个敏感信息项：")
        for item in result:
            print(f"  {item}")
        
        # 验证是否检测到敏感信息
        found_username = False
        found_password = False
        found_email = False
        
        for item in result:
            for key, value in item.items():
                if 'username' in str(key).lower() and 'admin' in str(value).lower():
                    found_username = True
                if 'password' in str(key).lower() and 'password123' in str(value).lower():
                    found_password = True
                if 'email' in str(key).lower() and '@example.com' in str(value).lower():
                    found_email = True
        
        self.assertTrue(found_username, "未检测到用户名")
        self.assertTrue(found_password, "未检测到密码")
        self.assertTrue(found_email, "未检测到邮箱")
    
    def test_sql_script_file(self):
        """测试SQL脚本文件处理"""
        print("\n测试SQL脚本文件处理...")
        result = sql_script_file(self.sql_script_path)
        
        # 验证结果
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        
        # 打印结果
        print(f"提取到 {len(result)} 个敏感信息项：")
        for item in result:
            print(f"  {item}")
        
        # 验证是否检测到敏感信息
        found_api_key = False
        found_password = False
        found_database_url = False
        
        for item in result:
            for key, value in item.items():
                if 'api' in str(key).lower() and 'sk_' in str(value).lower():
                    found_api_key = True
                if 'password' in str(key).lower() or 'password' in str(value).lower():
                    found_password = True
                if 'database_url' in str(key).lower() or 'mysql://' in str(value).lower():
                    found_database_url = True
        
        self.assertTrue(found_api_key, "未检测到API密钥")
        self.assertTrue(found_password, "未检测到密码")
        self.assertTrue(found_database_url, "未检测到数据库URL")
    
    def test_db_file(self):
        """测试通用数据库文件处理入口"""
        print("\n测试通用数据库文件处理入口...")
        
        # 测试SQLite数据库
        result_sqlite = db_file(self.sqlite_db_path)
        self.assertIsInstance(result_sqlite, list)
        self.assertTrue(len(result_sqlite) > 0)
        
        # 测试SQL脚本
        result_sql = db_file(self.sql_script_path)
        self.assertIsInstance(result_sql, list)
        self.assertTrue(len(result_sql) > 0)
        
        print("通用数据库文件处理入口测试通过")


if __name__ == '__main__':
    unittest.main() 