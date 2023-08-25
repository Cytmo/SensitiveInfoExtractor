import queue
import os

# 目录类
class Directory:
    def __init__(self, name, parent=None):
        self.name = name
        # 父级目录
        self.parent = parent
        # 子目录列表（可删）
        self.subdirectories = []
        # 子文件列表（可删）
        self.files = []
    
    # 迭代释放的析构函数
    def __del__(self):
        for directory in self.subdirectories:
            del directory
        self.subdirectories = []
        self.files = []
        self.parent = None
        self.name = None

# 文件类
class File:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent

    # 类方法：获取一个file文件的路径，拼接根目录后能直接通过目录索引文件
    @classmethod
    def get_parent_directory(cls,file):
        directory = file.parent
        result = file.name
        while directory is not None:
            result = directory.name + '/' +result
            directory = directory.parent
        return result
    
    # 类方法：获取文件名后缀
    @classmethod
    def spilit_file_name(cls,file):
        return os.path.splitext(file.name)[1]

# 目录树类：存储根目录类和其下所有子文件队列
class DirectController:
    
    def __init__(self) :
        self.fileList = queue.Queue()
        self.head_directory = None
        
    # 读取根目录下的所有目录和文件
    def build_directory_tree(self,root_folder, parent=None):
        directory = Directory(os.path.basename(root_folder), parent=parent)
        for item in os.listdir(root_folder):
            item_path = os.path.join(root_folder, item)
            if os.path.isdir(item_path):
                if parent is not None:
                    parent.subdirectories.append(directory)
                self.build_directory_tree(item_path, parent=directory)
            else:
                file = File(item, parent=directory)
                self.fileList.put(file)
                # path_tmp = get_parent_directory(file)
                # print(path_tmp)
                directory.files.append(file.name)
        return directory
    
    # 输出目录下的目录树（可删）
    @classmethod
    def print_directory_tree(cls,directory, indent=''):
        print(indent + directory.name + '/')
        for subdirectory in directory.subdirectories:
            DirectController.print_directory_tree(subdirectory, indent + '  ')
        for file in directory.files:
            print(indent + '  - ' + file)
    
