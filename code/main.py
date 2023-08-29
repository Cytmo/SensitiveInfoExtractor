from util.resultUtil import ResOut
from util import globalVar
from util import processUtil
from util import spilitUtil
from util.fileUtil import File
from util import fileUtil
from informationEngine import info_core
import time
from util.logUtils import LoggerSingleton
from util.resultUtil import ResOut

# 添加日志模块
logger = LoggerSingleton().get_logger()
TAG = "main.py: "
logger.info(TAG + "************************ start *****************************")

# 添加结果输出模块
res_out = ResOut()
res_out.add_new_json(
    "main.py", "************************ start *****************************")

# 添加依赖
T1 = time.perf_counter()

globalVar._init()
globalVar.set_value("code_path", "")

# 需要扫描的文件夹列表
scan_folder = ['../data']

# 进程处理函数


def process_function(arg, file):
    spilitUtil.spilit_process_file(file, arg)

# 进程回调函数


def callback_func(result):
    return


# 将初始目录压进根目录队列
[globalVar.root_folder_list.put(folder) for folder in scan_folder]
# 添加字符串元素到队列
# root_folder_list.put("Folder1")

# 声明文件输控制类
direct_controller = fileUtil.DirectController()
# 声明进程控制类
process_manager = processUtil.ProcessManager()


# 逐个根目录执行
while not globalVar.root_folder_list.empty():
    # 取出第一个根目录
    folder = globalVar.root_folder_list.get()
    # 构建根目录的文件树
    direct_controller.head_directory = direct_controller.build_directory_tree(
        folder)
    # 可以通过下方该指令输出文件树
    # direct_controller.print_directory_tree(direct_controller.head_directory)

    # 逐个文件执行
    while not direct_controller.fileList.empty():
        # 获取一个文件File类型
        file = direct_controller.fileList.get()

        # 进程池中执行，直接添加即可，超过上限的进程会等待，自动完成分配
        process_manager.add_process(
            callback_func, process_function, args=(folder,), kwargs={"file": file, })

        # 下面指令是不开进程池顺序执行时使用的，可以切换直接使用
        # spilitUtil.spilit_process_file(file, folder)

    # 当进程池填入完毕后，阻止新进程的加入并挂起整个进程等待进程池中所有子进程结束
    process_manager.close_process_pool()
    process_manager.release_process_pool()


T2 = time.perf_counter()
logger.info(TAG+'程序运行时间:%s毫秒' % ((T2 - T1)*1000))
# 程序运行时间:0.27023641716203606毫秒
logger.info(TAG+"************************* end ******************************")
res_out.add_new_json(
    "main.py", "************************* end ******************************")
res_out.save_to_file("output/output.json")
logger.info(TAG+"result is saved to: output/output.json , total is " +
            str(len(res_out.res_json)-2) + " file")
