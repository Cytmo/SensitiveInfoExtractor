import queue
import os

class Directory:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.subdirectories = []
        self.files = []
    
    def __del__(self):
        for directory in self.subdirectories:
            del directory
        self.subdirectories = []
        self.files = []
        self.parent = None
        self.name = None


class File:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent

    @classmethod
    def get_parent_directory(cls,file):
        directory = file.parent
        result = file.name
        while directory is not None:
            result = directory.name + '/' +result
            directory = directory.parent
        return result
    
    @classmethod
    def spilit_file_name(cls,file):
        return os.path.splitext(file.name)[1]


class DirectController:
    
    def __init__(self) :
        self.fileList = queue.Queue()
        self.head_directory = None
        

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
    
    @classmethod
    def print_directory_tree(cls,directory, indent=''):
        print(indent + directory.name + '/')
        for subdirectory in directory.subdirectories:
            DirectController.print_directory_tree(subdirectory, indent + '  ')
        for file in directory.files:
            print(indent + '  - ' + file)
    
