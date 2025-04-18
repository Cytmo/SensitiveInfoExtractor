from toStringUtils.databaseUtil import sql_conn
from util.resultUtil import ResOut
from util import globalVar
from util import processUtil
from util import spilitUtil
from util import fileUtil
import time
from util.logUtils import LoggerSingleton
from util.resultUtil import ResOut
from datetime import datetime
import argparse
import subprocess
import cProfile
from util import globalVar
"""
main: 主程序执行文件
usage:
    cd code
    python main.py # 无参数默认扫描"../data"文件夹
"""

# 添加日志模块
logger = LoggerSingleton().get_logger()
TAG = "main.py: "

# 添加结果输出模块
res_out = ResOut()

# 添加依赖
globalVar._init()

# 初始化敏感词列表
globalVar.init_sensitive_word("config/sensitive_word.yml")

# 添加命令行参数, 默认扫描"../data"文件夹
argparse = argparse.ArgumentParser()
argparse.add_argument("-f", "--folder", default="../data",
                      help="The folder to be scanned")
# false 默认单进程 true 多进程
argparse.add_argument("-mp", "--multiprocess", default="false",
                      help="if use multiprocess")
# 时间输出到哪
argparse.add_argument("-t", "--time", default="output/time_info.txt",
                      help="time info output file")

# 是否处理非图片文件内部中的图片, 默认为true
argparse.add_argument("-p", "--picture", default="false",
                      help="process picture in non image files")

# 程序运行结束后是否清空workspace缓存目录
argparse.add_argument("-c", "--clean", default="true",
                      help="clean the workspace dir in the end")

# 是否输出无关联的敏感信息
argparse.add_argument("-ur", "--unrelated", default="false",
                      help="output unrelated sensitive information")

# 是否启用认证信息搜索
argparse.add_argument("-auth", "--auth_search", default="true",
                      help="enable authentication info (username/password) search mode")


# 输入扫描的路径
args = argparse.parse_args()
scan_folder = [args.folder]

# 多进程参数转换
if args.multiprocess == "true":
    logger.info(TAG+"==>多进程运行！")
    multiprocess_flag = True
else:
    logger.info(TAG+"==>(默认)单进程运行！[添加 '-m true'  进行多进程运行]")
    multiprocess_flag = False


# 文件解析处理参数
if args.picture == "true":
    logger.info(TAG+"==>处理非图片文件内部中的图片！")
    globalVar.flag_list.append(True)
else:
    logger.info(TAG+"==>(默认)处理非图片文件内部中的图片！[添加 '-p false' 可取消]")
    globalVar.flag_list.append(False)

# 是否输出无关联的敏感信息
if args.unrelated == "true":
    logger.info(TAG+"==>输出无关联的敏感信息！")
    globalVar.set_unrelated_info_flag(True)
else:
    logger.info(TAG+"==>(默认)不输出无关联的敏感信息！[添加 '-ur true' 可开启]")
    globalVar.set_unrelated_info_flag(False)

# 是否启用认证信息搜索
if args.auth_search == "true":
    logger.info(TAG+"==>(默认)启用认证信息搜索！")
    globalVar.set_auth_search_flag(True)
else:
    logger.info(TAG+"==>关闭认证信息搜索！[添加 '-auth false' 可关闭]")
    globalVar.set_auth_search_flag(False)


# 进程处理函数
def process_function(arg, file):
    spilitUtil.spilit_process_file(file, arg)
# 进程回调函数


def callback_func(result):
    return


# 将初始目录压进根目录队列
[globalVar.root_folder_list.put(folder) for folder in scan_folder]

# 声明文件输控制类
direct_controller = fileUtil.DirectController()
# 声明进程控制类
process_manager = processUtil.ProcessManager()


################################## main() #####################################
def main():
    # res_out.add_new_json('sql conn',sql_conn())
    # 逐个根目录执行
    while not globalVar.root_folder_list.empty():
        # 取出第一个根目录
        folder = globalVar.root_folder_list.get()
        # 构建根目录的文件树
        direct_controller.head_directory = direct_controller.build_directory_tree(
            folder)

        # 逐个文件执行
        while not direct_controller.fileList.empty():
            # 获取一个文件File类型
            file = direct_controller.fileList.get()
            if multiprocess_flag:
                # 进程池中执行，直接添加即可，超过上限的进程会等待，自动完成分配
                process_manager.add_process(
                    callback_func, process_function, args=(folder,), kwargs={"file": file, })
            else:
                # 下面指令是不开进程池顺序执行时使用的，可以切换直接使用
                spilitUtil.spilit_process_file(file, folder)

        # 多进程模式下当进程池填入完毕后，阻止新进程的加入并挂起整个进程等待进程池中所有子进程结束
        if multiprocess_flag:
            process_manager.close_process_pool()
            process_manager.release_process_pool()


# #性能分析工具下的执行
# profiler = cProfile.Profile()
# profiler.run('main()')
# #性能分析使用
# profiler.dump_stats('./log/profile_results.prof')


logger.info(TAG + "************************ start *****************************")
T1 = time.perf_counter()  # 计时

main()

T2 = time.perf_counter()  # 计时结束
logger.info(TAG + "************************* end ******************************")


# 清空工作区
if args.clean == "true":
    logger.info(TAG+"==>准备清空工作区")
    command = "rm -rf ../workspace/*"
    result = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        logger.info('工作区已清空')
    else:
        logger.info('工作区清空失败')
        globalVar.flag_list.append(True)
else:
    logger.info(TAG+"==>不清空工作区!!")


# 将结果写入文件
output_tile_path = "output/"+datetime.now().strftime("%Y%m%d%H%M%S%f") + \
    "_output.json"
res_out.save_to_file(output_tile_path)
logger.info(TAG+"result is saved to: "+output_tile_path+" , total is " +
            str(len(res_out.res_json)) + " term")


# 打印程序耗时
logger.info(TAG+'程序运行时间:%s毫秒' % ((T2 - T1)*1000))


# 记录程序运行时间
time_info = TAG+'程序运行时间:%s毫秒' % ((T2 - T1)*1000)
with open(args.time, "a+") as f:
    f.write(time_info+"\n")

# 记录异常
error_list = globalVar.get_error_list()
if error_list is not None and len(error_list) > 0:
    logger.critical(
        "At least one error occurred during the execution of the program, please check the error_list for details.")
    logger.critical(TAG+"error_list: "+str(error_list))
