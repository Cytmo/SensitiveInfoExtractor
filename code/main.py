import sys
sys.path.append('/home/sakucy/networkCopitation/2023/code/util')

import queue
import os
import time

import fileUtil
from fileUtil import File
import processUtil
import spilitUtil

#需要扫描的文件夹列表
scan_folder = ['/home/sakucy/networkCopitation/2023']

# 示例用法
def process_function(arg,file):
    spilitUtil.spilit_process_file(file,arg)
    

def callback_func(result):
    return 


# 创建队列
root_folder_list = queue.Queue()
[root_folder_list.put(folder) for folder in scan_folder]

direct_controller = fileUtil.DirectController()

# 添加字符串元素到队列
# root_folder_list.put("Folder1")

process_manager = processUtil.ProcessManager()

folder = None

# 示例用法：遍历并打印队列中的元素
while not root_folder_list.empty():
    folder = root_folder_list.get()
    direct_controller.head_directory = direct_controller.build_directory_tree(folder)
    # direct_controller.print_directory_tree(direct_controller.head_directory)
    
    # while not direct_controller.fileList.empty():
    #     file = direct_controller.fileList.get()
    #     file_path = File.get_parent_directory(file)
    #     spilitUtil.spilit_process_file(file,folder)
    while not direct_controller.fileList.empty():
        file = direct_controller.fileList.get()
        process_manager.add_process(callback_func,process_function, args=(folder,),kwargs={"file":file,})
    process_manager.close_process_pool()

