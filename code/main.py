import sys
sys.path.append('/home/sakucy/networkCopitation/2023/code/util')

import queue
import os
import time

#添加依赖
import fileUtil
from fileUtil import File
import processUtil
import spilitUtil
import globalVar

globalVar._init()
globalVar.set_value("code_path","/home/sakucy/networkCopitation/2023")

# 需要扫描的文件夹列表
scan_folder = ['/home/sakucy/networkCopitation/2023/data/rar']

# 进程处理函数
def process_function(arg,file):
    spilitUtil.spilit_process_file(file,arg)
   
# 进程回调函数
def callback_func(result):
    return 


# 创建根目睹队列
root_folder_list = queue.Queue()
# 将初始目录压进根目录队列
[root_folder_list.put(folder) for folder in scan_folder]
# 添加字符串元素到队列
# root_folder_list.put("Folder1")

# 声明文件输控制类
direct_controller = fileUtil.DirectController()
# 声明进程控制类
process_manager = processUtil.ProcessManager()


# 逐个根目录执行
while not root_folder_list.empty():
    # 取出第一个根目录
    folder = root_folder_list.get()
    # 构建根目录的文件树
    direct_controller.head_directory = direct_controller.build_directory_tree(folder)
    # 可以通过下方该指令输出文件树
    # direct_controller.print_directory_tree(direct_controller.head_directory)
    
    
    # 逐个文件执行
    while not direct_controller.fileList.empty():
        # 获取一个文件File类型
        file = direct_controller.fileList.get()

        
        # 进程池中执行，直接添加即可，超过上限的进程会等待，自动完成分配
        # process_manager.add_process(callback_func,process_function, args=(folder,),kwargs={"file":file,})

        # 下面指令是不开进程池顺序执行时使用的，可以切换直接使用
        spilitUtil.spilit_process_file(file,folder)

    # 当进程池填入完毕后，阻止新进程的加入并挂起整个进程等待进程池中所有子进程结束
    # process_manager.close_process_pool()

