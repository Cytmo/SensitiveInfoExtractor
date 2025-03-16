#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交互式运行脚本，用于设置参数并运行main.py
"""

import os
import subprocess
import sys


def confirm_action(prompt="是否继续?", default="y"):
    """请求用户确认操作
    
    Args:
        prompt: 提示信息
        default: 默认选项，可以是'y'或'n'
    
    Returns:
        boolean: 用户确认结果
    """
    valid_yes = ['y', 'yes', '是', '是的', '确定', '确认', 'true', 't']
    valid_no = ['n', 'no', '否', '不', '不是', 'false', 'f']
    
    if default.lower() in valid_yes:
        prompt_text = f"{prompt} [Y/n]: "
    elif default.lower() in valid_no:
        prompt_text = f"{prompt} [y/N]: "
    else:
        prompt_text = f"{prompt} [y/n]: "
        default = None
        
    while True:
        choice = input(prompt_text).lower().strip()
        
        # 如果用户直接按回车，使用默认值
        if not choice and default:
            return default.lower() in valid_yes
            
        if choice in valid_yes:
            return True
        elif choice in valid_no:
            return False
        else:
            print(f"请输入有效的选择: 'y'/'yes'/'是' 表示确认，'n'/'no'/'否' 表示拒绝")


def print_header():
    """打印脚本头部信息"""
    print("\n" + "=" * 60)
    print("安全文本检测交互式运行脚本")
    print("=" * 60)


def get_folder_path():
    """获取用户想要扫描的文件夹路径"""
    default_path = "../data"
    user_input = input(f"请输入要扫描的文件夹路径 [默认: {default_path}]: ")
    return user_input if user_input.strip() else default_path


def get_yes_no_option(prompt, default="false"):
    """获取用户的是/否选项"""
    default_display = "否" if default == "false" else "是"
    default_choice = "n" if default == "false" else "y"
    
    result = confirm_action(f"{prompt} [默认: {default_display}]", default=default_choice)
    return "true" if result else "false"


def get_time_file():
    """获取时间信息输出文件路径"""
    default_path = "output/time_info.txt"
    user_input = input(f"请输入时间信息输出文件路径 [默认: {default_path}]: ")
    return user_input if user_input.strip() else default_path


def run_main_with_args(args):
    """使用给定参数运行main.py"""
    # 确保在code目录下运行
    current_dir = os.path.basename(os.getcwd())
    
    if current_dir != "code":
        if os.path.exists("code"):
            os.chdir("code")
        else:
            print("警告: 无法找到'code'目录。请确保从正确的目录运行此脚本。")
    
    cmd = [sys.executable, "main.py"] + args
    print("\n" + "=" * 60)
    print(f"执行命令: {' '.join(cmd)}")
    print("=" * 60 + "\n")
    
    if confirm_action("是否执行上述命令?", default="y"):
        try:
            subprocess.run(cmd)
        except Exception as e:
            print(f"运行出错: {e}")
    else:
        print("已取消执行")


def get_predefined_mode():
    """让用户选择预定义的工作模式"""
    print("\n预定义工作模式:")
    print("1. 全功能模式 - 检测所有类型的敏感信息")
    print("2. 纯正则匹配模式 - 仅使用正则表达式匹配，关闭认证信息搜索（默认）")
    print("3. 仅认证信息模式 - 只检测用户名和密码信息")
    print("4. 全量输出模式 - 输出所有匹配到的信息，包括无关联信息")
    print("5. 自定义模式 - 手动设置所有参数")
    
    while True:
        choice = input("\n请选择工作模式 [默认: 2]: ").strip()
        if not choice:
            choice = "2"
            
        if choice in ["1", "2", "3", "4", "5"]:
            return choice
        else:
            print("无效的选择，请输入1-5之间的数字")


def main():
    """主函数"""
    print_header()
    
    # 让用户选择预定义模式或自定义模式
    mode = get_predefined_mode()
    
    # 收集参数
    args = []
    
    # 根据选择的模式设置默认参数
    if mode == "2":  # 纯正则匹配模式
        # 扫描文件夹
        folder = get_folder_path()
        args.extend(["-f", folder])
        
        # 时间信息输出文件
        time_file = get_time_file()
        args.extend(["-t", time_file])
        
        # 固定参数: 关闭认证信息搜索，启用无关联信息输出
        args.extend(["-mp", "false"])
        args.extend(["-p", "false"])
        args.extend(["-c", "true"])
        args.extend(["-ur", "true"])
        args.extend(["-auth", "false"])
        
        print("\n已选择【纯正则匹配模式】：将使用纯正则表达式匹配敏感信息，不进行其他过滤和分析")
        
    elif mode == "3":  # 仅认证信息模式
        # 扫描文件夹
        folder = get_folder_path()
        args.extend(["-f", folder])
        
        # 时间信息输出文件
        time_file = get_time_file()
        args.extend(["-t", time_file])
        
        # 固定参数: 启用认证信息搜索，关闭无关联信息输出
        args.extend(["-mp", "false"])
        args.extend(["-p", "false"])
        args.extend(["-c", "true"])
        args.extend(["-ur", "false"])
        args.extend(["-auth", "true"])
        
        print("\n已选择【仅认证信息模式】：只检测用户名和密码相关信息")
        
    elif mode == "4":  # 全量输出模式
        # 扫描文件夹
        folder = get_folder_path()
        args.extend(["-f", folder])
        
        # 时间信息输出文件
        time_file = get_time_file()
        args.extend(["-t", time_file])
        
        # 固定参数: 启用认证信息搜索，启用无关联信息输出
        args.extend(["-mp", "false"])
        args.extend(["-p", "true"])
        args.extend(["-c", "true"])
        args.extend(["-ur", "true"])
        args.extend(["-auth", "true"])
        
        print("\n已选择【全量输出模式】：输出所有匹配到的敏感信息，包括无关联信息")
        
    else:  # 全功能模式或自定义模式
        # 扫描文件夹
        folder = get_folder_path()
        args.extend(["-f", folder])
        
        if mode == "1":  # 全功能模式
            # 固定默认参数
            args.extend(["-mp", "false"])
            args.extend(["-t", "output/time_info.txt"])
            args.extend(["-p", "false"])
            args.extend(["-c", "true"])
            args.extend(["-ur", "false"])
            args.extend(["-auth", "true"])
            
            print("\n已选择【全功能模式】：使用默认配置检测所有敏感信息")
        else:  # 自定义模式
            # 是否使用多进程
            multiprocess = get_yes_no_option("是否使用多进程?", default="false")
            args.extend(["-mp", multiprocess])
            
            # 时间信息输出文件
            time_file = get_time_file()
            args.extend(["-t", time_file])
            
            # 是否处理非图片文件内部中的图片
            process_picture = get_yes_no_option("是否处理非图片文件内部中的图片?", default="false")
            args.extend(["-p", process_picture])
            
            # 是否清空workspace缓存目录
            clean_workspace = get_yes_no_option("程序运行结束后是否清空workspace缓存目录?", default="true")
            args.extend(["-c", clean_workspace])
            
            # 是否输出无关联的敏感信息
            unrelated_info = get_yes_no_option("是否输出无关联的敏感信息?", default="false")
            args.extend(["-ur", unrelated_info])
            
            # 是否启用认证信息搜索模式
            auth_search = get_yes_no_option("是否启用认证信息(用户名/密码)搜索模式?", default="true")
            args.extend(["-auth", auth_search])
            
            print("\n已选择【自定义模式】：使用自定义参数配置")
    
    # 运行main.py
    run_main_with_args(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        print("\n程序已结束") 