#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库文件处理简化测试脚本
"""

import os
import sys
import sqlite3
import tempfile
import shutil

# 添加代码目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
code_dir = os.path.abspath(os.path.join(current_dir, '../code'))
sys.path.insert(0, code_dir)

def main():
    print("开始数据库文件处理简化测试...")
    
    # 创建临时目录
    test_dir = tempfile.mkdtemp()
    try:
        # 创建一个测试用SQLite数据库
        sqlite_db_path = os.path.join(test_dir, 'test.db')
        conn = sqlite3.connect(sqlite_db_path)
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
        sql_script_path = os.path.join(test_dir, 'test.sql')
        with open(sql_script_path, 'w') as f:
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
            ''')
        
        # 测试文件扩展名识别
        print("\n测试文件扩展名识别...")
        print(f"SQLite DB: {os.path.splitext(sqlite_db_path)[1]}")
        print(f"SQL脚本: {os.path.splitext(sql_script_path)[1]}")
        
        # 测试文件内容读取
        print("\n测试文件内容读取...")
        try:
            # 读取SQLite数据库
            conn = sqlite3.connect(sqlite_db_path)
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            print(f"SQLite数据库中的表: {tables}")
            
            users = conn.execute("SELECT * FROM users;").fetchall()
            print(f"用户数据示例: {users[0]}")
            conn.close()
            
            # 读取SQL脚本
            with open(sql_script_path, 'r') as f:
                sql_content = f.read()
            print(f"SQL脚本内容前100个字符: {sql_content[:100]}...")
            
            print("文件内容读取成功")
        except Exception as e:
            print(f"文件内容读取失败: {str(e)}")
        
        print("\n测试完成")
    finally:
        # 清理临时目录
        shutil.rmtree(test_dir)

if __name__ == "__main__":
    main() 