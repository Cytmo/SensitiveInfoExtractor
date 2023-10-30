#!/bin/bash

# 声明帮助信息
function show_usage {
    echo "Usage: $0 <options>"
    echo "Options:"
    echo "  -n: Test - Exclude images"
    echo "  -t: Test - data_test folder"
    echo "  -a: Test - all files"
    echo "  -c: Clear logs"
    echo "  -h: Show help"
    # 添加更多选项和描述
}

# 检查是否提供了选项
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

# 获取用户提供的选项
while getopts "ntach" option; do
    case "$option" in
        n)  # Test - Exclude images
            python3 main.py -f ../data -p false
            ;;
        t)  # Test - data_test folder 
            python3 main.py -f ../data_test -p false
            ;;
        a)  # Test - all files
            python3 main.py -f ../data
            ;;
        c)  # Clear logs
            rm log/*
            rm output/*
            ;;
        h)  # Show help
            show_usage
            exit 0
            ;;
        # 添加更多选项的处理
        \?) # 无效选项
            echo "Invalid option: -$OPTARG"
            exit 1
            ;;
    esac
done
