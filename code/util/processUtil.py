import os
import multiprocessing
import time


class ProcessManager:
    def __init__(self):
        self._cpu_count = os.cpu_count()-1
        self._process_pool = None
        # self._process_count = 0

    
    # def could_add_process(self):
    #     return self._process_count<self._cpu_count

    def create_process_pool(self):
        self._process_pool = multiprocessing.Pool(processes=self._cpu_count)

    def add_process(self,call_target,target, args=(), kwargs={}):
        if self._process_pool is None:
            self.create_process_pool()
        # self._process_count+=1
        self._process_pool.apply_async(target, args=args, kwds=kwargs,callback=call_target)
        

    # def get_process_count(self):
    #     if self._process_pool is not None:
    #         return self._process_count
    #     return 0
    
    # def reduce_process(self):
    #     self._process_count-=1
    #     print(self._process_count)


    def close_process_pool(self):
        if self._process_pool is not None:
            self._process_pool.close()
            self._process_pool.join()

# # 示例用法
# def process_function(arg,file_use):
#     print("Processing:", arg)

# def callback_func(result):
#     process_manager.reduce_process()

# fileNow = fileUtil.File("aa")
# process_manager = ProcessManager()
# process_manager.add_process(callback_func,process_function, args=("Task 1",), kwargs={"file_use" : fileNow,})
# process_manager.add_process(callback_func,process_function, args=("Task 2",))
# process_manager.add_process(callback_func,process_function, args=("Task 3",))
# num_processes = process_manager.get_process_count()
# print("进程数量:", num_processes)
# num_processes = process_manager.get_process_count()
# print("进程数量:", num_processes)


# process_manager.close_process_pool()
