#!/bin/bash

# 声明帮助信息
function show_usage {
    echo "Usage: $0 <options>"
    echo "Options:"
    echo "  -n: Test - Exclude images"
    echo "  -t: Test - data_test folder"
    echo "  -a: Test - all files"
    echo "  -c: Clear logs"
    echo "  -d: Compare the two newest files in the output folder"
    echo "  -s: standard test"
    echo "  -m: multi-process test"
    echo "  -h: Show help"
    # 添加更多选项和描述
}

# 检查是否提供了选项
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

# 获取用户提供的选项
while getopts "ntacdhsm" option; do
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
            rm -rf ../workspace/*
            ;;
        d) # Compare the two newest files in the output folder
            # 获取output文件夹中最新的两个文件
            files=($(ls -t output/* | head -n 2))
            if [ ${#files[@]} -lt 2 ]; then
                echo "There are less than 2 files in the output folder."
            else
                # 执行比较操作，这里用diff作为示例，你可以根据实际需求修改
                echo "Comparing ${files[0]} and ${files[1]}..."
                diff "${files[0]}" "${files[1]}"
                result=$?
                echo "result : $result"
                if [ "$result" -eq 0 ]; then
                    echo "The two files are the same."
                else
                    echo "The two files are different."
                fi
            fi
            ;;
        s)  # Show help
            python3 main.py -f ../data -mp false -p false 1>/dev/null
            ;;
        m)  # Show help
            python3 main.py -f ../data -mp false -p false 1>/dev/null
            ;;
        h)  # Show help
            show_usage
            exit 0
            ;;  
        \?) # 无效选项
            echo "Invalid option: -$OPTARG"
            exit 1
            ;;
    esac
done
